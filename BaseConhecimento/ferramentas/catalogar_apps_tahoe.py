#!/usr/bin/env python3
"""Cataloga os 70 apps da mineração Tahoe 26.6.1 sem alterar curadorias antigas.

O estado de implementação é uma triagem conservadora, não valida fidelidade.
Execute novamente após atualizar a mineração; a operação é idempotente.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
from collections import Counter
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
DEFAULT_MINING = Path.home() / ".local/share/hyprmac-pesquisa/macos-26.6.1/minerar/codex-2026-10-11"
OUTPUT = BASE / "referencias/tahoe-apps-70.json"
DB = BASE / "base.db"
BUILD = "25G76"

# Nomes dos arquivos da mineração, não nomes de bundles nem nomes traduzidos.
GROUPS = {
    "A": "Finder|Dock|Spotlight|ControlCenter|NotificationCenter|Mission Control|System Settings|Calculator|Journal|Notes|Photos|Preview|Screenshot|TextEdit|Photo Booth".split("|"),
    "B": "Activity Monitor|Apps|Audio MIDI Setup|Automator|Bluetooth File Exchange|Chess|Clock|ColorSync Utility|Console|Dictionary|Digital Color Meter|Disk Utility|Font Book|Grapher|Image Capture|Magnifier|Print Center|QuickTime Player|Screen Sharing|Script Editor|Stickies|System Information|Terminal|Tips|VoiceMemos|VoiceOver Utility".split("|"),
    "C": "Books|Calendar|Contacts|Freeform|Games|Image Playground|Mail|Maps|Music|News|Passwords|Podcasts|Reminders|Shortcuts|Stocks|Time Machine|TV|Weather".split("|"),
    "D": "AirPort Utility|App Store|Boot Camp Assistant|FaceTime|FindMy|Home|iPhone Mirroring|Messages|Migration Assistant|Phone|Siri".split("|"),
}


def read_json(path: Path):
    with path.open(encoding="utf-8") as stream:
        return json.load(stream)


def catalog(mining: Path) -> list[dict]:
    progress = read_json(mining / "progresso.json")
    expected = {name: group for group, names in GROUPS.items() for name in names}
    if len(expected) != 70 or sum(map(len, GROUPS.values())) != 70:
        raise ValueError("grupos não contêm 70 nomes distintos")
    paths = {p.stem: p for p in (mining / "menus").glob("*.json")}
    if set(paths) != set(expected):
        raise ValueError(f"menus divergentes: ausentes={sorted(set(expected)-set(paths))}; extras={sorted(set(paths)-set(expected))}")
    counts = progress.get("contagens", {})
    required = {"arquivos_menus": 70, "nibs_menus": 40, "menus_estruturados": 38, "menus_incertos": 2}
    if any(counts.get(key) != value for key, value in required.items()):
        raise ValueError(f"contagens do progresso divergentes: {counts}")
    if progress.get("status") != "concluido":
        raise ValueError("mineração não está concluída")
    referenced = {
        result["arquivo"]
        for package in progress.get("pacotes", {}).values()
        for result in [package.get("resultados", {}).get("menus", {})]
        if "arquivo" in result
    }
    actual = {"menus/" + path.name for path in paths.values()}
    if referenced != actual:
        raise ValueError("referências de menus no progresso não correspondem aos JSONs")

    rows = []
    bundle_ids = set()
    for name in sorted(paths):
        path = paths[name]
        data = read_json(path)
        resources = data.get("recursos")
        if not isinstance(resources, list) or len(resources) > 1:
            raise ValueError(f"recursos inesperados: {path}")
        if data.get("pacote", "").split("/")[-1] != name + ".app":
            raise ValueError(f"pacote não corresponde ao nome: {path}")
        bundle = data.get("bundle_id")
        if not isinstance(bundle, str) or not bundle or bundle in bundle_ids:
            raise ValueError(f"bundle ID ausente/duplicado: {path}")
        bundle_ids.add(bundle)
        menu = "absent"
        source = None
        if resources:
            resource = resources[0]
            if not isinstance(resource.get("estrutura_incerta"), bool):
                raise ValueError(f"incerteza ausente: {path}")
            menu = "uncertain" if resource["estrutura_incerta"] else "structured"
            source = resource.get("fonte")
            if not isinstance(source, str) or not source.startswith(data["pacote"] + "/"):
                raise ValueError(f"fonte inválida: {path}")
        rows.append({
            "nome": name,
            "bundle_id": bundle,
            "grupo": expected[name],
            "implementacao": "PARCIAL" if expected[name] == "A" else "AUSENTE",
            "menu": menu,
            "pacote": data["pacote"],
            "fonte_menu": source,
            "fonte_extracao": str(path),
            "sha256_extracao": hashlib.sha256(path.read_bytes()).hexdigest(),
        })
    observed = Counter(row["menu"] for row in rows)
    if observed != {"structured": 38, "uncertain": 2, "absent": 30}:
        raise ValueError(f"distribuição de menus divergente: {observed}")
    return rows


def save_db(rows: list[dict], database: Path):
    with sqlite3.connect(database) as db:
        db.execute("PRAGMA foreign_keys=ON")
        for row in rows:
            title = f"{row['nome']}: matriz de implementação Tahoe 26"
            summary = (f"Grupo {row['grupo']}; triagem HyprMac {row['implementacao']}; "
                       f"menu estático {row['menu']}. Estado de implementação não certifica fidelidade.")
            evidence = (f"Mineração macOS Tahoe 26.6.1 build {BUILD}; idioma en/Base; "
                        f"bundle {row['bundle_id']}; SHA-256 JSON {row['sha256_extracao']}; "
                        f"NIB {row['fonte_menu'] or 'não encontrado'}. "
                        "Menus estáticos não demonstram aparência ou comportamento em execução.")
            source = row["fonte_extracao"]
            digest = hashlib.sha256(json.dumps([title, summary, evidence, source, None], ensure_ascii=False).encode()).hexdigest()
            db.execute("""INSERT INTO registros
                (id,tipo,componente,estado,versao_macos,titulo,resumo,evidencia,
                 fonte_caminho,confianca,implementacao,sha256)
                VALUES (?,?,?,?,?,?,?,?,?,?,?,?)
                ON CONFLICT(id) DO UPDATE SET
                 tipo=excluded.tipo, componente=excluded.componente, estado=excluded.estado,
                 versao_macos=excluded.versao_macos, titulo=excluded.titulo,
                 resumo=excluded.resumo, evidencia=excluded.evidencia,
                 fonte_caminho=excluded.fonte_caminho, confianca=excluded.confianca,
                 implementacao=excluded.implementacao, sha256=excluded.sha256,
                 atualizado_em=CURRENT_TIMESTAMP""",
                ("tahoe26:matriz70:" + row["bundle_id"], "inventario_app", row["nome"],
                 "experimental", "Tahoe 26.6.1 (25G76)", title, summary, evidence,
                 source, "experimental", row["implementacao"], digest))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mining", type=Path, default=DEFAULT_MINING)
    parser.add_argument("--database", type=Path, default=DB)
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--check", action="store_true", help="valida sem escrever")
    args = parser.parse_args()
    rows = catalog(args.mining)
    if not args.check:
        payload = {"schema": 1, "versao": "macOS Tahoe 26.6.1", "build": BUILD,
                   "idiomas": ["en", "Base"], "confianca": "experimental",
                   "observacao": "Triagem de implementação; menus estáticos não certificam interface ou comportamento em execução.",
                   "apps": rows}
        args.output.parent.mkdir(parents=True, exist_ok=True)
        temp = args.output.with_suffix(".json.tmp")
        temp.write_text(json.dumps(payload, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
        temp.replace(args.output)
        save_db(rows, args.database)
    print(f"{len(rows)} apps: {dict(Counter(row['menu'] for row in rows))}; "
          f"{dict(Counter(row['implementacao'] for row in rows))}")


if __name__ == "__main__":
    main()
