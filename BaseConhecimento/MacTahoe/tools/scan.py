#!/usr/bin/env python3
"""Inventário leve e idempotente do Tahoe: caminhos e metadados, sem conteúdo."""
from __future__ import annotations

import argparse
import os
import plistlib
import sqlite3
from xml.parsers.expat import ExpatError
from datetime import datetime, timezone
from pathlib import Path

from common import DB, SOURCE, connect, init_db

PACKAGE_SUFFIXES = {".app", ".framework", ".bundle", ".appex", ".xpc", ".plugin", ".prefpane", ".menu"}
FILE_SUFFIXES = {".nib", ".storyboard", ".storyboardc", ".plist", ".strings", ".car", ".icns", ".png", ".pdf"}
SKIP_DIRS = {"dev", "Volumes", ".Spotlight-V100", ".DocumentRevisions-V100", ".Trashes", "cores"}
PRIORITY = {
    "controlcenter": "Control Center", "system settings": "System Settings",
    "dock": "Dock", "systemuiserver": "Top Bar / SystemUIServer",
    "appkit": "AppKit", "coreui": "CoreUI",
}
COMPONENTS = [
    ("Control Center", "sistema", "Painel de controles rápidos e seus módulos.", 1, "PARCIAL"),
    ("System Settings", "aplicativo", "Aplicativo de preferências do sistema.", 1, "PARCIAL"),
    ("Dock", "sistema", "Dock, tiles, indicadores e gerenciamento visual de apps.", 1, "PARCIAL"),
    ("Top Bar / SystemUIServer", "sistema", "Barra superior, menus e extras de estado.", 1, "PARCIAL"),
    ("AppKit", "framework", "Framework de interface nativa macOS.", 1, "NAO_APLICAVEL"),
    ("CoreUI", "framework", "Renderização e catálogos de assets do sistema.", 1, "NAO_APLICAVEL"),
    ("CoreMaterial", "framework", "Materiais visuais e vibrancy.", 2, "PARCIAL"),
    ("SystemAppearance", "framework", "Aparência e temas do sistema.", 2, "PARCIAL"),
    ("Finder", "aplicativo", "Gerenciador de arquivos do macOS.", 2, "DIFERENTE"),
    ("Notifications", "sistema", "Central e banners de notificações.", 2, "PARCIAL"),
    ("Spotlight", "sistema", "Busca e lançador do sistema.", 2, "PROXIMO"),
    ("Now Playing", "sistema", "Estado e controles de mídia.", 2, "PARCIAL"),
    ("Window Management", "sistema", "Janelas, sheets, dialogs e estados.", 2, "PARCIAL"),
]


def kind(path: Path) -> str:
    suffix = path.suffix.lower()
    return suffix[1:] if suffix else "arquivo"


def likely_component(path: Path) -> str | None:
    lower = str(path).lower()
    for needle, component in PRIORITY.items():
        if needle in lower:
            return component
    return None


def plist_metadata(package: Path) -> tuple[str | None, str | None, str | None]:
    candidates = [package / "Contents/Info.plist", package / "Resources/Info.plist", package / "Info.plist"]
    for candidate in candidates:
        try:
            if candidate.stat().st_size > 2_000_000:
                continue
            with candidate.open("rb") as handle:
                data = plistlib.load(handle)
            return data.get("CFBundleIdentifier"), data.get("CFBundleExecutable"), data.get("CFBundleShortVersionString")
        except (OSError, ValueError, plistlib.InvalidFileException, ExpatError):
            pass
    return None, None, None


def scan(source: Path, db: Path) -> None:
    conn = connect(db)
    init_db(conn)
    conn.executemany("""INSERT INTO componentes(nome,categoria,descricao,prioridade,status_hyprmac)
                        VALUES(?,?,?,?,?) ON CONFLICT(nome) DO UPDATE SET
                        categoria=excluded.categoria,descricao=excluded.descricao,
                        prioridade=excluded.prioridade,status_hyprmac=excluded.status_hyprmac""", COMPONENTS)
    components = {row["nome"]: row["id"] for row in conn.execute("SELECT id,nome FROM componentes")}
    bundle_paths: dict[Path, int] = {}
    file_batch = []
    seen_files = seen_bundles = 0
    started = datetime.now(timezone.utc).isoformat()

    for root, dirs, files in os.walk(source, topdown=True, followlinks=False):
        base = Path(root)
        dirs[:] = [d for d in dirs if d not in SKIP_DIRS]
        for dirname in dirs:
            path = base / dirname
            if path.suffix.lower() not in PACKAGE_SUFFIXES and path.suffix.lower() != ".storyboardc":
                continue
            component_name = likely_component(path)
            component_id = components.get(component_name) if component_name else None
            bundle_id, executable, version = plist_metadata(path) if path.suffix.lower() in PACKAGE_SUFFIXES else (None, None, None)
            conn.execute(
                """INSERT INTO bundles(bundle_id,nome,path,tipo,executavel,versao,componente_id)
                   VALUES(?,?,?,?,?,?,?) ON CONFLICT(path) DO UPDATE SET
                   bundle_id=excluded.bundle_id, executavel=excluded.executavel,
                   versao=excluded.versao, componente_id=COALESCE(excluded.componente_id,bundles.componente_id)""",
                (bundle_id, path.stem, str(path), kind(path), executable, version, component_id),
            )
            row = conn.execute("SELECT id FROM bundles WHERE path=?", (str(path),)).fetchone()
            bundle_paths[path] = row[0]
            seen_bundles += 1
        for filename in files:
            path = base / filename
            suffix = path.suffix.lower()
            is_executable = base.name == "MacOS"
            if suffix not in FILE_SUFFIXES and not is_executable:
                continue
            try:
                stat = path.stat()
            except OSError:
                continue
            owner = next((bundle_paths[p] for p in reversed(path.parents) if p in bundle_paths), None)
            component_name = likely_component(path)
            component_id = components.get(component_name) if component_name else None
            category = "interface" if suffix in {".nib", ".storyboard", ".storyboardc"} else "recurso" if suffix in {".car", ".icns", ".png", ".pdf"} else "config" if suffix in {".plist", ".strings"} else "binario"
            relevance = 5 if component_id else (2 if suffix in {".nib", ".storyboard", ".car"} else 1)
            file_batch.append((str(path), filename, "executavel" if is_executable else kind(path), suffix[1:] if suffix else None, stat.st_size, int(stat.st_mtime), owner, category, component_id, relevance))
            if len(file_batch) >= 2000:
                upsert_files(conn, file_batch); seen_files += len(file_batch); file_batch.clear()
        if (seen_bundles + seen_files) % 10000 == 0:
            conn.commit()
    upsert_files(conn, file_batch); seen_files += len(file_batch)
    conn.execute("INSERT OR REPLACE INTO meta(chave,valor) VALUES('source_root',?),('inventory_started_at',?),('inventory_finished_at',?),('inventory_file_count',?),('inventory_bundle_count',?)",
                 (str(source), started, datetime.now(timezone.utc).isoformat(), str(seen_files), str(seen_bundles)))
    conn.commit()
    print(f"Inventário concluído: {seen_bundles} pacotes; {seen_files} arquivos relevantes; banco {db}")


def upsert_files(conn: sqlite3.Connection, rows: list[tuple]) -> None:
    conn.executemany(
        """INSERT INTO arquivos(path,nome,tipo,extensao,tamanho,mtime,bundle_id,categoria,componente_id,relevancia)
           VALUES(?,?,?,?,?,?,?,?,?,?) ON CONFLICT(path) DO UPDATE SET
           tamanho=excluded.tamanho,mtime=excluded.mtime,bundle_id=excluded.bundle_id,
           componente_id=COALESCE(excluded.componente_id,arquivos.componente_id),relevancia=MAX(arquivos.relevancia,excluded.relevancia)""", rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=SOURCE)
    parser.add_argument("--db", type=Path, default=DB)
    args = parser.parse_args()
    if not args.source.is_dir():
        parser.error(f"fonte indisponível: {args.source}")
    scan(args.source.resolve(), args.db.resolve())


if __name__ == "__main__":
    main()
