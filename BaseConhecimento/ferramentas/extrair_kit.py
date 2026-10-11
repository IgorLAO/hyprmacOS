#!/usr/bin/env python3
"""Extrai os tokens de design de um kit do Sketch descompactado (Apple macOS UI Kit).

  extrair_kit.py <pasta-do-kit> <pasta-de-saida>

Gera em <saida>/:
  cores.json / cores.md           swatches nomeados (sistema, rótulos, preenchimentos…)
  tipografia.json / tipografia.md estilos de texto (fonte, tamanho, entrelinha, cor)
  estilos.json / estilos.md       estilos de camada (preenchimentos, bordas, sombras,
                                  desfoques, modo de mistura) — materiais, controles…
O .sketch é um zip; a pasta do kit é ele descompactado (document.json, pages/, meta.json).
"""
import json
import os
import sys

BLEND = {0: "normal", 1: "darken", 2: "multiply", 3: "color-burn", 4: "lighten", 5: "screen",
         6: "color-dodge", 7: "overlay", 8: "soft-light", 9: "hard-light", 10: "difference",
         11: "exclusion", 12: "hue", 13: "saturation", 14: "color", 15: "luminosity",
         16: "plus-darker", 17: "plus-lighter"}
BLUR = {0: "gaussian", 1: "motion", 2: "zoom", 3: "background", 4: "glass"}
FILL = {0: "cor", 1: "gradiente", 4: "padrão", 5: "ruído"}
BORDER_POS = {0: "centro", 1: "dentro", 2: "fora"}


def hexa(c):
    if not c:
        return None
    r, g, b, a = (c.get(k, 0) for k in ("red", "green", "blue", "alpha"))
    h = f"#{round(r * 255):02X}{round(g * 255):02X}{round(b * 255):02X}"
    return h if a >= 0.999 else f"{h}/{a:.2f}"


def css_rgba(c):
    r, g, b, a = (c.get(k, 0) for k in ("red", "green", "blue", "alpha"))
    return f"rgba({round(r * 255)}, {round(g * 255)}, {round(b * 255)}, {a:.2f})"


def gradient(g):
    stops = [f"{hexa(s['color'])} {s.get('position', 0):.2f}" for s in g.get("stops", [])]
    kind = {0: "linear", 1: "radial", 2: "angular"}.get(g.get("gradientType"), "?")
    return f"{kind}({g.get('from')}→{g.get('to')}: {', '.join(stops)})"


def style_summary(st):
    out = {}
    ctx = st.get("contextSettings") or {}
    if ctx.get("opacity", 1) < 0.999:
        out["opacidade"] = round(ctx["opacity"], 3)
    if ctx.get("blendMode"):
        out["mistura"] = BLEND.get(ctx["blendMode"], ctx["blendMode"])
    fills = []
    for f in st.get("fills", []):
        if not f.get("isEnabled", True):
            continue
        item = {"tipo": FILL.get(f.get("fillType"), f.get("fillType"))}
        if f.get("fillType") == 1:
            item["gradiente"] = gradient(f.get("gradient", {}))
        else:
            item["cor"] = hexa(f.get("color"))
        fc = f.get("contextSettings") or {}
        if fc.get("blendMode"):
            item["mistura"] = BLEND.get(fc["blendMode"], fc["blendMode"])
        if fc.get("opacity", 1) < 0.999:
            item["opacidade"] = round(fc["opacity"], 3)
        fills.append(item)
    if fills:
        out["preenchimentos"] = fills
    borders = []
    for b in st.get("borders", []):
        if not b.get("isEnabled", True):
            continue
        item = {"cor": hexa(b.get("color")), "espessura": b.get("thickness"),
                "posição": BORDER_POS.get(b.get("position"), b.get("position"))}
        if b.get("fillType") == 1:
            item["gradiente"] = gradient(b.get("gradient", {}))
        bc = b.get("contextSettings") or {}
        if bc.get("blendMode"):
            item["mistura"] = BLEND.get(bc["blendMode"], bc["blendMode"])
        borders.append(item)
    if borders:
        out["bordas"] = borders
    for key, name in (("shadows", "sombras"), ("innerShadows", "sombras_internas")):
        sh = [{"cor": hexa(s.get("color")), "x": s.get("offsetX"), "y": s.get("offsetY"),
               "desfoque": s.get("blurRadius"), "espalhamento": s.get("spread")}
              for s in st.get(key, []) if s.get("isEnabled", True)]
        if sh:
            out[name] = sh
    blurs = st.get("blurs") or ([st["blur"]] if st.get("blur") else [])
    bl = []
    for b in blurs:
        if b and b.get("isEnabled"):
            item = {"tipo": BLUR.get(b.get("type"), b.get("type")), "raio": b.get("radius")}
            if b.get("saturation") not in (None, 1):
                item["saturação"] = b.get("saturation")
            for extra in ("brightness", "distortion", "depth", "chromaticAberrationMultiplier",
                          "isCustomGlass", "specularOpacity"):
                if extra in b:
                    item[extra] = b[extra]
            bl.append(item)
    if bl:
        out["desfoques"] = bl
    cc = st.get("colorControls") or {}
    if cc.get("isEnabled") and any(cc.get(k) not in (None, d) for k, d in
                                   (("brightness", 0), ("contrast", 1), ("hue", 0), ("saturation", 1))):
        out["ajustes_cor"] = {k: cc.get(k) for k in ("brightness", "contrast", "hue", "saturation")}
    return out


def text_summary(st):
    ea = (st.get("textStyle") or {}).get("encodedAttributes", {})
    font = ea.get("MSAttributedStringFontAttribute", {}).get("attributes", {})
    para = ea.get("paragraphStyle", {})
    out = {"fonte": font.get("name"), "tamanho": font.get("size")}
    if para.get("maximumLineHeight"):
        out["entrelinha"] = para["maximumLineHeight"]
    if ea.get("kerning") not in (None, 0):
        out["espaçamento"] = ea["kerning"]
    col = ea.get("MSAttributedStringColorAttribute")
    if col:
        out["cor"] = hexa(col)
    feats = font.get("variation") or ea.get("MSAttributedStringFontAttribute", {}).get("attributes", {}).get("featureSettings")
    if feats:
        out["variação"] = feats
    return out


def main(kit, out):
    global KIT
    KIT = os.path.basename(os.path.normpath(kit))
    os.makedirs(out, exist_ok=True)
    d = json.load(open(os.path.join(kit, "document.json")))

    swatches = sorted(((s["name"], hexa(s["value"]), css_rgba(s["value"]))
                       for s in d.get("sharedSwatches", {}).get("objects", [])), key=lambda x: x[0])
    json.dump([{"nome": n, "hex": h, "css": c} for n, h, c in swatches],
              open(os.path.join(out, "cores.json"), "w"), ensure_ascii=False, indent=1)
    with open(os.path.join(out, "cores.md"), "w") as f:
        f.write(f"# Cores — {KIT}\n\n"
                "Extraído de `document.json` (sharedSwatches). `/0.85` = alfa.\n"
                "\"use plus lighter/darker\" = aplicar com o modo de mistura *plus-lighter* "
                "(escuro) ou *plus-darker* (claro): é a cor **vibrante** sobre material.\n\n")
        group = None
        for n, h, c in swatches:
            g = n.rsplit("/", 1)[0]
            if g != group:
                f.write(f"\n## {g}\n\n| Nome | Hex | CSS |\n|---|---|---|\n")
                group = g
            f.write(f"| {n.rsplit('/', 1)[-1]} | `{h}` | `{c}` |\n")

    texts = sorted(((s["name"], text_summary(s["value"]))
                    for s in d.get("layerTextStyles", {}).get("objects", [])), key=lambda x: x[0])
    json.dump([{"nome": n, **v} for n, v in texts], open(os.path.join(out, "tipografia.json"), "w"),
              ensure_ascii=False, indent=1)
    with open(os.path.join(out, "tipografia.md"), "w") as f:
        f.write(f"# Tipografia — {KIT}\n\nExtraído de `layerTextStyles` (pt = px em 1×).\n\n"
                "| Estilo | Fonte | Tamanho | Entrelinha | Cor |\n|---|---|---|---|---|\n")
        for n, v in texts:
            f.write(f"| {n} | {v.get('fonte')} | {v.get('tamanho')} | {v.get('entrelinha', '')} | "
                    f"`{v.get('cor', '')}` |\n")

    styles = sorted(((s["name"], style_summary(s["value"]))
                     for s in d.get("layerStyles", {}).get("objects", [])), key=lambda x: x[0])
    json.dump([{"nome": n, **v} for n, v in styles], open(os.path.join(out, "estilos.json"), "w"),
              ensure_ascii=False, indent=1)
    with open(os.path.join(out, "estilos.md"), "w") as f:
        f.write(f"# Estilos de camada — {KIT}\n\n"
                "Extraído de `layerStyles`: materiais, vidro, controles, sombras.\n")
        group = None
        for n, v in styles:
            g = n.rsplit("/", 1)[0] if "/" in n else "(raiz)"
            if g != group:
                f.write(f"\n## {g}\n")
                group = g
            f.write(f"\n### {n.rsplit('/', 1)[-1]}\n")
            for k, val in v.items():
                f.write(f"- **{k}**: `{json.dumps(val, ensure_ascii=False)}`\n")
    print(f"{len(swatches)} cores, {len(texts)} estilos de texto, {len(styles)} estilos de camada → {out}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
