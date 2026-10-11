#!/usr/bin/env python3
"""Mostra a árvore de camadas de uma página do kit do Sketch, com medidas.

  contorno_kit.py <pasta-do-kit> <nome-da-página (parte)> [profundidade] [filtro-de-artboard]

Cada linha: classe, nome, LxA em (x,y), raio dos cantos, estilo compartilhado e,
para textos, fonte/tamanho/conteúdo. Serve para tirar medidas exatas dos componentes.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extrair_kit import style_summary  # noqa: E402


def load_styles(kit):
    d = json.load(open(os.path.join(kit, "document.json")))
    names = {}
    for key in ("layerStyles", "layerTextStyles"):
        for s in d.get(key, {}).get("objects", []):
            names[s["do_objectID"]] = s["name"]
    return names


def radius(layer):
    pts = layer.get("points") or []
    rs = sorted({round(p.get("cornerRadius", 0), 1) for p in pts if p.get("cornerRadius")})
    if layer.get("fixedRadius"):
        rs = rs or [layer["fixedRadius"]]
    style = layer.get("style") or {}
    if layer.get("_class") == "rectangle" and layer.get("hasConvertedToNewRoundCorners") is False:
        pass
    smooth = layer.get("pointRadiusBehaviour")
    corners = (layer.get("style") or {}).get("corners")
    if corners and corners.get("radii") and any(corners["radii"]):
        rs = rs or sorted({round(r, 1) for r in corners["radii"]})
        if corners.get("smoothing"):
            smooth = 2
        if corners.get("prefersConcentric"):
            rs = [f"{r}*concêntrico" for r in rs]
    out = "/".join(str(r) for r in rs)
    if out and smooth == 2:
        out += " (contínuo)"
    return out


def text_info(layer):
    a = layer.get("attributedString") or {}
    s = a.get("string", "")
    font = ""
    for attr in a.get("attributes", [])[:1]:
        f = attr.get("attributes", {}).get("MSAttributedStringFontAttribute", {}).get("attributes", {})
        font = f"{f.get('name')} {f.get('size')}"
        col = attr.get("attributes", {}).get("MSAttributedStringColorAttribute")
        if col:
            from extrair_kit import hexa
            font += f" {hexa(col)}"
    return f'«{s[:40]}» {font}'


SHOW_STYLE = os.environ.get("ESTILO", "1") == "1"


def walk(layer, styles, depth, maxdepth, out):
    f = layer.get("frame", {})
    cls = layer.get("_class")
    name = layer.get("name", "")
    bits = [f"{cls}", f"'{name}'", f"{f.get('width', 0):g}x{f.get('height', 0):g} @({f.get('x', 0):g},{f.get('y', 0):g})"]
    r = radius(layer)
    if r:
        bits.append(f"r={r}")
    pads = [layer.get(k) for k in ("topPadding", "rightPadding", "bottomPadding", "leftPadding")]
    if any(pads):
        bits.append("pad=" + "/".join(f"{p or 0:g}" for p in pads))
    gl = layer.get("groupLayout") or {}
    if gl.get("_class") == "MSImmutableFlexGroupLayout":
        bits.append(f"flex({'col' if gl.get('flexDirection') == 1 else 'row'} gap={gl.get('allGuttersGap', 0):g})")
    sid = layer.get("sharedStyleID")
    if sid and sid in styles:
        bits.append(f"[{styles[sid]}]")
    elif cls not in ("symbolMaster", "artboard", "group", "symbolInstance") and SHOW_STYLE:
        st = style_summary(layer.get("style") or {})
        st.pop("ajustes_cor", None)
        if st:
            bits.append(json.dumps(st, ensure_ascii=False))
    if cls == "text":
        bits.append(text_info(layer))
    if cls == "symbolInstance":
        bits.append("(instância)")
    if not layer.get("isVisible", True):
        bits.append("(oculto)")
    out.append("  " * depth + " ".join(bits))
    if depth < maxdepth:
        for ch in layer.get("layers", []):
            walk(ch, styles, depth + 1, maxdepth, out)


def main():
    kit, page = sys.argv[1], sys.argv[2]
    maxdepth = int(sys.argv[3]) if len(sys.argv) > 3 else 3
    filt = sys.argv[4] if len(sys.argv) > 4 else None
    meta = json.load(open(os.path.join(kit, "meta.json")))
    styles = load_styles(kit)
    for pid, p in meta["pagesAndArtboards"].items():
        if page.lower() not in p["name"].lower():
            continue
        data = json.load(open(os.path.join(kit, "pages", pid + ".json")))
        out = [f"# página {p['name']!r}"]
        for art in data.get("layers", []):
            if filt and not re.search(filt, art.get("name", ""), re.I):
                continue
            walk(art, styles, 0, maxdepth, out)
        print("\n".join(out))


if __name__ == "__main__":
    main()
