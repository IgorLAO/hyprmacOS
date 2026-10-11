#!/usr/bin/env python3
"""Auditoria leve de integridade, proveniência e links operacionais."""
from __future__ import annotations

import hashlib
import json
import re
import sqlite3
from collections import Counter
from pathlib import Path
from urllib.parse import unquote, urlsplit

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parent
OPERACIONAIS = ("AGENTS.md", "ARCHITECTURE.md", "STATUS.md", "README.md",
                "CLAUDE.md", "ONBOARDING.md", "TODO.md")


def abrir(path: Path):
    return sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True)


def links_quebrados(path: Path):
    text = path.read_text(encoding="utf-8", errors="replace")
    for raw in re.findall(r"!?\[[^\]]*\]\(([^)]+)\)", text):
        ref = raw.strip().split(' "', 1)[0].strip("<>")
        if not ref or ref.startswith(("https://", "http://", "mailto:", "#", "data:")):
            continue
        if ref.startswith("file://"):
            target = Path(urlsplit(ref).path)
        elif ref.startswith("/"):
            target = Path(ref.split("#")[0])
        else:
            target = path.parent / unquote(ref.split("#")[0])
        if not target.exists():
            yield {"arquivo": str(path.relative_to(ROOT)), "destino": ref}


def main():
    report = {"bancos": {}, "documentos": {}, "links_quebrados": [], "hash_divergente": []}
    with abrir(BASE / "base.db") as db:
        for name, path in (("geral", BASE / "base.db"),
                           ("tahoe_local", BASE / "MacTahoe/base.db")):
            if not path.exists():
                continue
            with abrir(path) as con:
                report["bancos"][name] = {
                    "bytes": path.stat().st_size,
                    "integridade": con.execute("PRAGMA integrity_check").fetchone()[0],
                    "erros_fk": len(con.execute("PRAGMA foreign_key_check").fetchall()),
                }
                if name == "tahoe_local":
                    fontes = ("descobertas", "investigacoes", "mapeamento_hyprmac")
                    falhas = 0
                    for tabela in fontes:
                        faltantes = con.execute(
                            f"SELECT count(*) FROM {tabela} s LEFT JOIN classificacao_registros c "
                            "ON c.origem=? AND c.origem_id=s.id WHERE c.origem_id IS NULL",
                            (tabela,)).fetchone()[0]
                        orfaos = con.execute(
                            f"SELECT count(*) FROM classificacao_registros c LEFT JOIN {tabela} s "
                            "ON s.id=c.origem_id WHERE c.origem=? AND s.id IS NULL",
                            (tabela,)).fetchone()[0]
                        falhas += faltantes + orfaos
                    report["bancos"][name]["classificacao_sem_fonte_ou_ausente"] = falhas
        rows = db.execute("SELECT caminho,sha256,presente,estado FROM documentos").fetchall()
        report["documentos"]["estados"] = dict(Counter(r[3] for r in rows))
        report["documentos"]["fontes_ausentes_preservadas"] = sum(not r[2] for r in rows)
        report["documentos"]["duplicatas_exatas"] = db.execute(
            "SELECT count(*) FROM (SELECT sha256 FROM documentos WHERE presente=1 AND sha256 IS NOT NULL "
            "GROUP BY sha256 HAVING count(*)>1)").fetchone()[0]
        report["registros_duplicados"] = db.execute(
            "SELECT count(*) FROM (SELECT sha256 FROM registros WHERE sha256 IS NOT NULL "
            "GROUP BY sha256 HAVING count(*)>1)").fetchone()[0]
        report["trechos_sem_documento"] = db.execute(
            "SELECT count(*) FROM (SELECT DISTINCT t.caminho FROM trechos t "
            "LEFT JOIN documentos d ON d.caminho=t.caminho WHERE d.caminho IS NULL)").fetchone()[0]
        active = [ROOT / p for p in OPERACIONAIS]
        for rel, digest, present, state in rows:
            path = BASE / rel
            if not present:
                continue
            if not path.exists() or (digest and hashlib.sha256(path.read_bytes()).hexdigest() != digest):
                report["hash_divergente"].append(rel)
            if state in ("verified", "experimental") and path.suffix == ".md" and path.exists():
                active.append(path)
        for path in active:
            if path.exists():
                report["links_quebrados"].extend(links_quebrados(path))
    print(json.dumps(report, ensure_ascii=False, indent=2))
    bad = any(x["integridade"] != "ok" or x["erros_fk"] or
              x.get("classificacao_sem_fonte_ou_ausente", 0) for x in report["bancos"].values())
    duplicados = report["documentos"]["duplicatas_exatas"] or report["registros_duplicados"]
    return 1 if bad or duplicados or report["trechos_sem_documento"] or report["links_quebrados"] or report["hash_divergente"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
