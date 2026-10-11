#!/usr/bin/env python3
"""Inspeção lazy de um plist, recurso ou binário já inventariado."""
from __future__ import annotations

import argparse
import hashlib
import plistlib
import re
import subprocess
from datetime import datetime, timezone

from common import connect, source_path

SAFE_PLIST_KEYS = re.compile(r"(Bundle|Identifier|Feature|Appearance|Menu|Control|Preference|Setting|Sidebar|Toolbar|Material|State)", re.I)
IDENTIFIER = re.compile(r"^[A-Za-z_][A-Za-z0-9_.$:+ /-]{3,199}$")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path")
    parser.add_argument("--component", required=True)
    parser.add_argument("--keywords", help="regex direcionada para strings de binário")
    parser.add_argument("--deep", action="store_true")
    parser.add_argument("--refresh", action="store_true", help="reler mesmo que a análise equivalente exista")
    parser.add_argument("--hash", action="store_true")
    args = parser.parse_args()
    path = source_path(args.path)
    conn = connect()
    component = conn.execute("SELECT id FROM componentes WHERE nome=? COLLATE NOCASE", (args.component,)).fetchone()
    if not component:
        parser.error(f"componente desconhecido: {args.component}")
    row = conn.execute("SELECT id,analysis_level FROM arquivos WHERE path=?", (str(path),)).fetchone()
    if not row:
        parser.error("arquivo ausente do inventário; execute scan.py primeiro")
    level = "strings" if args.keywords else ("deep" if args.deep else "metadata")
    if row["analysis_level"] == level and not args.refresh:
        print(f"Já analisado em nível {level}; use query.py ou --refresh.")
        return
    findings: list[tuple[str, str, str, str]] = []
    if path.suffix.lower() == ".plist":
        with path.open("rb") as handle:
            data = plistlib.load(handle)
        if isinstance(data, dict):
            for key, value in data.items():
                if SAFE_PLIST_KEYS.search(str(key)) and isinstance(value, (str, int, float, bool)):
                    findings.append(("config", str(key), str(value), "CONFIG"))
    elif args.keywords:
        pattern = re.compile(args.keywords, re.I)
        output = subprocess.run(["strings", "-a", str(path)], text=True, errors="replace", capture_output=True, check=True).stdout
        useful = []
        for line in output.splitlines():
            line = line.strip()
            if pattern.search(line) and IDENTIFIER.fullmatch(line) and line not in useful:
                useful.append(line)
            if len(useful) >= 40:
                break
        for value in useful:
            findings.append(("simbolo", value, "Nome encontrado por consulta direcionada de strings.", "SIMBOLO"))
    else:
        findings.append(("estrutura", "arquivo", f"{path.name}: {path.stat().st_size} bytes", "DIRETO"))
    for kind, key, value, confidence in findings:
        conn.execute("""INSERT OR IGNORE INTO descobertas(componente_id,arquivo_id,tipo,chave,valor,evidencia,confianca)
                        VALUES(?,?,?,?,?,?,?)""", (component[0], row["id"], kind, key, value, str(path), confidence))
    digest = hashlib.sha256(path.read_bytes()).hexdigest() if args.hash else None
    conn.execute("""UPDATE arquivos SET analisado=1,analysis_level=?,motivo_analise=?,analisado_em=?,
                    componente_id=?,sha256=COALESCE(?,sha256) WHERE id=?""",
                 (level, f"inspeção lazy: {args.component}", datetime.now(timezone.utc).isoformat(), component[0], digest, row["id"]))
    conn.execute("INSERT INTO analises(arquivo_id,nivel,motivo,ferramenta) VALUES(?,?,?,?)",
                 (row["id"], level, f"investigação de {args.component}", "inspect.py"))
    conn.commit()
    print(f"{len(findings)} descobertas registradas; análise={level}; arquivo={path}")


if __name__ == "__main__":
    main()
