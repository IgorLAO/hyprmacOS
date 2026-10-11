#!/usr/bin/env python3
"""Gera um índice leve de arquivos de código para recuperação progressiva.

O índice contém metadados, símbolos, imports, resumo curto, tags e hash. Ele
permite localizar candidatos sem carregar o conteúdo completo no contexto.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

BASE = Path(__file__).resolve().parents[1]
ROOT = BASE.parent
OUT = BASE / "codigo.json"
MD = BASE / "INDICE-CODIGO-AGENTES.md"

EXTENSIONS = {
    ".py": "python", ".lua": "lua", ".css": "css", ".sh": "bash",
    ".json": "json", ".jsonc": "jsonc", ".js": "javascript", ".md": "markdown",
}
SKIP_PARTS = {".git", ".obsidian", "__pycache__", ".venv", ".backups", "models", "base.db", "backup", "video", "images"}
ROOTS = {"shell", "hypr", "waybar", "scripts", "gtk", "kde", "kitty", "ghostty", "wofi", "cursores", "tests"}


def digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def language_for(path: Path) -> str | None:
    language = EXTENSIONS.get(path.suffix.lower())
    if language:
        return language
    if path.suffix:
        return None
    # Shell daemons e scripts do projeto não têm extensão. Evite binários sem shebang.
    with path.open("rb") as f:
        first = f.readline(160).lower()
    if not first.startswith(b"#!"):
        return None
    if b"python" in first:
        return "python"
    if b"bash" in first or b"/sh" in first:
        return "bash"
    return None


def symbols(text: str, language: str) -> list[str]:
    patterns = {
        "python": r"^\s*(?:async\s+)?(?:def|class)\s+([A-Za-z_]\w*)",
        "lua": r"^\s*(?:local\s+)?function\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)",
        "bash": r"^\s*(?:function\s+)?([A-Za-z_]\w*)\s*\(\)\s*\{?",
        "css": r"^\s*([^/@][^{]{1,100})\s*\{",
    }
    pat = patterns.get(language)
    if not pat:
        return []
    out = []
    for line in text.splitlines():
        m = re.search(pat, line)
        if m:
            values = [m.group(1).strip()]
            if language == "css":
                values = [re.sub(r"\s+", " ", x).strip() for x in m.group(1).split(",")]
            for value in values:
                if value and value not in out and len(out) < 120:
                    out.append(value[:100])
    return out


def imports(text: str, language: str) -> list[str]:
    patterns = {
        "python": r"^\s*(?:from\s+([^\s]+)\s+import|import\s+([^\s#]+))",
        "lua": r"require\s*[\(\"]([^\)\"]+)",
        "javascript": r"(?:from|require\s*\()\s*[\"']([^\"']+)",
        "css": r"@import\s+[\"']([^\"']+)",
    }
    pat = patterns.get(language)
    if not pat:
        return []
    out = []
    for line in text.splitlines():
        m = re.search(pat, line)
        if m:
            value = next((x for x in m.groups() if x), "")
            if value and value not in out and len(out) < 40:
                out.append(value)
    return out


def summary(text: str, path: Path) -> str:
    lines = [re.sub(r"^\s*(#|//|--|/\*+|\*+)\s?", "", x).strip()
             for x in text.splitlines() if x.strip() and not x.lstrip().startswith("#!")]
    useful = [x for x in lines if not x.startswith(("#!", "{", "}", "import ", "from "))]
    return (" ".join(useful[:2]) or path.name)[:280]


def tags(path: Path, text: str) -> list[str]:
    parts = path.parts
    out = []
    for tag in ("shell", "hypr", "waybar", "scripts", "tests", "gtk", "kde", "kitty", "ghostty", "wofi"):
        if tag in parts:
            out.append(tag)
    low = f"{path.name} {text}".lower()
    for word in ("dock", "control center", "spotlight", "notification", "lock", "menu", "glass", "theme", "window"):
        if word in low and word not in out:
            out.append(word)
    if any(x in low for x in ("central de controle", "hyprmac-cc", ".cc", "control center")):
        for word in ("control", "center", "control_center"):
            if word not in out:
                out.append(word)
    return out


def collect() -> list[dict]:
    out = []
    for root_name in sorted(ROOTS):
        root = ROOT / root_name
        if not root.exists():
            continue
        for path in sorted(p for p in root.rglob("*") if p.is_file()):
            if any(part in SKIP_PARTS for part in path.parts):
                continue
            language = language_for(path)
            if not language:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            rel = path.relative_to(ROOT).as_posix()
            syms = symbols(text, language)
            imps = imports(text, language)
            out.append({
                "path": rel, "language": language, "bytes": path.stat().st_size,
                "lines": len(text.splitlines()), "summary": summary(text, path),
                "symbols": syms, "imports": imps, "tags": tags(path, text),
                "sha256": digest(path),
            })
    return out


def write_markdown(items: list[dict]) -> None:
    lines = ["# Índice de código para agentes", "",
             "Metadados para localizar candidatos antes de ler arquivos completos.", "",
             "| Caminho | Linguagem | Linhas | Tags | Resumo |", "|---|---|---:|---|---|"]
    for x in items:
        lines.append(f"| `{x['path']}` | {x['language']} | {x['lines']} | {', '.join(x['tags'][:6])} | {x['summary'].replace('|', '/')} |")
    lines += ["", "## Recuperação progressiva", "",
              "1. filtre por caminho, linguagem ou tag;", "2. leia `summary` e `symbols`;",
              "3. recupere um trecho relevante;", "4. carregue o arquivo completo somente quando necessário.", ""]
    MD.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    items = collect()
    OUT.write_text(json.dumps({"schema": 1, "items": items}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(items)
    print(f"{len(items)} arquivos indexados → {OUT}")


if __name__ == "__main__":
    main()
