#!/usr/bin/env python3
"""Converte páginas da documentação da Apple (formato DocC em JSON) em Markdown.

  docc_md.py <caminho-da-doc> <pasta-de-saída> [nome.md]
  docc_md.py swiftui/glasseffectcontainer dev/

<caminho-da-doc> é o que vem depois de developer.apple.com/documentation/ (o JSON fica em
developer.apple.com/tutorials/data/documentation/<caminho>.json — o mesmo de onde vieram as
páginas do HIG). Também aceita um arquivo .json local ou a URL completa do JSON (páginas do HIG:
developer.apple.com/tutorials/data/design/human-interface-guidelines/<página>.json). Gera título, resumo, seções,
listas, avisos ("Note", "Important"), código e as referências com o título legível.
"""
import json
import os
import re
import sys
import urllib.request

BASE_URL = "https://developer.apple.com/tutorials/data/documentation/"


def load(src):
    if os.path.exists(src):
        with open(src, encoding="utf-8") as f:
            return json.load(f), src
    url = src if src.startswith("http") else BASE_URL + src.strip("/") + ".json"
    with urllib.request.urlopen(url, timeout=30) as r:
        return json.load(r), url


def inline(nodes, refs):
    out = []
    for n in nodes or []:
        t = n.get("type")
        if t == "text":
            out.append(n["text"])
        elif t == "codeVoice":
            out.append(f"`{n['code']}`")
        elif t in ("emphasis", "strong", "newTerm"):
            mark = "**" if t == "strong" else "*"
            out.append(mark + inline(n.get("inlineContent"), refs) + mark)
        elif t == "reference":
            r = refs.get(n.get("identifier"), {})
            title = n.get("overridingTitle") or r.get("title") or n.get("identifier", "").split("/")[-1]
            out.append(f"`{title}`" if r.get("kind") == "symbol" else title)
        elif t == "link":
            out.append(n.get("title") or n.get("destination", ""))
        elif t == "image":
            r = refs.get(n.get("identifier"), {})
            alt = r.get("alt") or ""
            out.append(f"[imagem: {alt}]" if alt else "")
        elif "inlineContent" in n:
            out.append(inline(n["inlineContent"], refs))
    return "".join(out)


def blocks(nodes, refs, depth=0):
    out = []
    pad = "  " * depth
    for n in nodes or []:
        t = n.get("type")
        if t == "heading":
            out.append("#" * min(6, n.get("level", 2) + 1) + " " + n.get("text", ""))
        elif t == "paragraph":
            out.append(pad + inline(n.get("inlineContent"), refs))
        elif t in ("unorderedList", "orderedList"):
            for i, it in enumerate(n.get("items", []), 1):
                body = blocks(it.get("content"), refs, depth + 1).strip()
                mark = f"{i}." if t == "orderedList" else "-"
                out.append(f"{pad}{mark} {body.lstrip()}")
        elif t == "aside":
            body = blocks(n.get("content"), refs).strip().replace("\n", "\n> ")
            out.append(f"> **{n.get('name') or n.get('style', 'Note').title()}:** {body}")
        elif t == "codeListing":
            out.append("```" + (n.get("syntax") or "") + "\n" + "\n".join(n.get("code", [])) + "\n```")
        elif t == "table":
            rows = n.get("rows", [])
            for k, row in enumerate(rows):
                cells = [blocks(c, refs).strip().replace("\n", " ") for c in row]
                out.append("| " + " | ".join(cells) + " |")
                if k == 0:
                    out.append("|" + "---|" * len(cells))
        elif t == "termList":
            for it in n.get("items", []):
                term = inline(it.get("term", {}).get("inlineContent"), refs)
                out.append(f"- **{term}**: " + blocks(it.get("definition", {}).get("content"), refs).strip())
        elif t == "links":
            for ident in n.get("items", []):
                out.append(f"- {refs.get(ident, {}).get('title', ident)}")
        elif "content" in n:
            out.append(blocks(n["content"], refs, depth))
        elif "inlineContent" in n:
            out.append(pad + inline(n["inlineContent"], refs))
    return "\n\n".join(x for x in out if x.strip())


def convert(doc, origin):
    refs = doc.get("references", {})
    meta = doc.get("metadata", {})
    title = meta.get("title") or doc.get("identifier", {}).get("url", "").split("/")[-1]
    md = [f"<!-- fonte: {origin} -->", "", f"# {title}", ""]
    role = meta.get("roleHeading") or meta.get("role")
    if role:
        md.append(f"*{role}*" + (f" · {', '.join(p['name'] for p in meta.get('platforms', []) if p.get('name'))}"
                                  if meta.get("platforms") else ""))
        md.append("")
    abstract = inline(doc.get("abstract"), refs)
    if abstract:
        md += [abstract, ""]
    for sec in doc.get("primaryContentSections", []):
        kind = sec.get("kind")
        if kind == "declarations":
            for d in sec.get("declarations", []):
                code = "".join(tok.get("text", "") for tok in d.get("tokens", []))
                md += ["```swift", code, "```", ""]
        elif kind == "parameters":
            md += ["## Parameters", ""]
            for p in sec.get("parameters", []):
                md.append(f"- **{p['name']}**: " + blocks(p.get("content"), refs).strip())
            md.append("")
        elif kind == "content":
            md += [blocks(sec.get("content"), refs), ""]
    for sec in doc.get("topicSections", []):
        md += [f"## {sec.get('title', 'Topics')}", ""]
        for ident in sec.get("identifiers", []):
            r = refs.get(ident, {})
            line = f"- `{r.get('title', ident)}`"
            ab = inline(r.get("abstract"), refs)
            md.append(line + (f" — {ab}" if ab else ""))
        md.append("")
    return re.sub(r"\n{3,}", "\n\n", "\n".join(md)).strip() + "\n", title


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    src, out_dir = sys.argv[1], sys.argv[2]
    doc, origin = load(src)
    md, title = convert(doc, origin)
    name = sys.argv[3] if len(sys.argv) > 3 else \
        re.sub(r"[^a-z0-9]+", "-", os.path.splitext(os.path.basename(src))[0].lower()).strip("-") + ".md"
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"{path}  ({title}, {len(md)} caracteres)")


if __name__ == "__main__":
    main()
