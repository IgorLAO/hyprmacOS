#!/usr/bin/env python3
"""Gera um catálogo leve e uma visão de triagem das telas de referência.

Saídas:
  referencias/telas/catalogo.json       metadados estruturados por imagem
  referencias/telas/CATALOGO-AGENTES.md índice legível por agentes
  referencias/telas/atlas/*.jpg         miniaturas agrupadas para triagem visual

O catálogo guarda dimensões, proporção, hash, categoria, estado, âncoras
visuais e uso recomendado. Agentes consultam primeiro o JSON/Markdown/atlas e
carregam o original somente quando precisam medir ou conferir um detalhe.
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont, ImageOps
except ImportError:  # metadados ainda podem ser gerados sem miniaturas
    Image = ImageDraw = ImageFont = ImageOps = None

BASE = Path(__file__).resolve().parents[1]
TELAS = BASE / "referencias" / "telas"
CATALOGO = TELAS / "catalogo.json"
INDICE = TELAS / "INDICE.md"
ATLAS = TELAS / "atlas"
EXTS = {".png", ".jpg", ".jpeg", ".webp", ".avif"}

SEED = {
    "safari-escuro-barra-de-menus-abas.png": {
        "categoria": "menu_bar",
        "estado": ["dark", "safari", "window", "tabs"],
        "prioridade": "golden",
        "uso": ["menu bar", "window geometry", "tabs", "active capsule", "window gaps"],
        "ancoras": ["menu bar 34 pt", "Safari Heavy 13 pt", "active lilac capsule", "window touches edges", "22 pt squircle"],
    },
    "cc-tahoe-alvo-usuario.png": {
        "categoria": "control_center", "estado": ["light", "target"], "prioridade": "golden",
        "uso": ["Control Center layout", "tile proportions", "sliders", "target comparison"],
        "ancoras": ["Wi-Fi/Bluetooth/AirDrop", "Not Playing", "Focus", "Display/Keyboard/Sound sliders", "Edit Controls"],
    },
    "cc-comparacao-hyprmac-x-tahoe.png": {
        "categoria": "comparison", "estado": ["light", "side_by_side"], "prioridade": "golden",
        "uso": ["visual regression", "side-by-side review"],
        "ancoras": ["native Tahoe versus hyprmac", "composition", "proportions", "material"],
    },
    "tahoe-dark.jpeg": {
        "categoria": "desktop", "estado": ["dark", "desktop", "finder"], "prioridade": "canonical",
        "uso": ["dark theme", "window decoration", "Dock", "Control Center", "widgets"],
        "ancoras": ["dark Control Center", "Finder sidebar", "Dock badges", "menu bar extras"],
    },
    "macos-tahoe-home-screen.jpg": {
        "categoria": "control_center", "estado": ["light", "edit", "widgets", "dock"], "prioridade": "canonical",
        "uso": ["edit mode", "ghost slots", "widget layout", "Dock"],
        "ancoras": ["minus badges", "ghost/dashed circles", "weather widget", "running dots"],
    },
    "Apple-WWDC25-macOS-Tahoe-26-Lock-Screen-250609.jpg": {
        "categoria": "lock_screen", "estado": ["light", "lock_screen"], "prioridade": "canonical",
        "uso": ["lock screen geometry", "clock", "avatar", "status icons"],
        "ancoras": ["large glass clock", "date", "avatar", "Touch ID or Enter Password"],
    },
    "ajustes-general-escuro-aguas-vivas.png": {
        "categoria": "settings", "estado": ["dark", "settings"], "prioridade": "secondary",
        "uso": ["System Settings layout", "sidebar", "dark materials"],
        "ancoras": ["Settings sidebar", "General pane", "wallpaper behind window", "dark glass"],
    },
    "ajustes-wallpaper-clock-appearance-escuro.png": {
        "categoria": "settings", "estado": ["dark", "popover", "lock_screen"], "prioridade": "canonical",
        "uso": ["Clock Appearance popover", "weight slider", "lock screen settings"],
        "ancoras": ["six clock styles", "Weight slider", "On Lock Screen", "dark settings"],
    },
    "ajustes-wallpaper-clock-appearance-pequeno.png": {
        "categoria": "settings", "estado": ["light", "popover", "lock_screen"], "prioridade": "secondary",
        "uso": ["Clock Appearance controls", "popover proportions"],
        "ancoras": ["Show large clock", "clock style selector", "Weight slider", "Done"],
    },
    "bloqueio-relogio-data-por-extenso.png": {
        "categoria": "lock_screen", "estado": ["light", "clock_style"], "prioridade": "secondary",
        "uso": ["lock screen typography", "date format", "large clock"],
        "ancoras": ["long date", "large translucent clock", "wallpaper contrast"],
    },
    "cc-edicao-galeria-sobre-azul.png": {
        "categoria": "control_center", "estado": ["light", "edit", "gallery"], "prioridade": "canonical",
        "uso": ["Controls Gallery", "edit mode", "glass panel"],
        "ancoras": ["gallery beside Control Center", "search", "categories", "Done"],
    },
    "cc-sobre-janela-clara.png": {
        "categoria": "control_center", "estado": ["light", "overlay"], "prioridade": "secondary",
        "uso": ["Control Center over window", "layer contrast"],
        "ancoras": ["vertical Control Center", "clear glass", "underlying app window"],
    },
}

SEQUENCE_RANGES = {
    "spotlight-abrir": 2,
    "spotlight-controles": 6,
    "spotlight-clique-modo": 5,
    "spotlight-modo-apps": 9,
}


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def category(text: str) -> tuple[str, list[str]]:
    s = text.lower()
    if any(x in s for x in ("apple-music", "shortcuts-notes", "looking-good-in-black", "live-translation")):
        return "app_window", ["application window", "toolbar", "window chrome"]
    if "spotlight" in s:
        return "spotlight", ["spotlight", "search", "overlay"]
    if "bloqueio" in s or "lock-screen" in s or "lock_screen" in s:
        return "lock_screen", ["lock screen", "clock", "authentication"]
    if "control" in s or s.startswith("cc-") or "edit-controls" in s:
        return "control_center", ["Control Center", "tiles", "sliders"]
    if "osd" in s or "volume" in s:
        return "osd", ["OSD", "slider", "system feedback"]
    if "ajustes" in s:
        return "settings", ["System Settings", "popover", "form"]
    if "menu" in s or "safari" in s:
        return "menu_bar", ["menu bar", "menus", "window"]
    if "dock" in s or "desktop" in s or "tahoe-dark" in s:
        return "desktop", ["desktop", "Dock", "widgets"]
    if "incoming" in s or "call" in s or "translation" in s:
        return "notification", ["notification", "banner", "status"]
    if "comparison" in s or "comparacao" in s:
        return "comparison", ["comparison", "visual regression"]
    return "desktop", ["desktop", "macOS Tahoe"]


def parse_index() -> dict[str, dict]:
    """Lê descrições manuais do INDICE.md; expansões de sequências viram itens."""
    out: dict[str, dict] = {}
    if not INDICE.exists():
        return out
    for line in INDICE.read_text(encoding="utf-8").splitlines():
        m = re.match(r"\| `([^`]+)` \| (.*?) \| (.*?) \|$", line)
        if not m:
            continue
        name, title, obs = m.groups()
        seq = re.search(r"(\S+)-(\d+)\.png.*?(?:…|\.\.\.) .*?(\S+)-(\d+)\.png", name)
        if seq:
            prefix, first, last_prefix, last = seq.groups()
            if prefix != last_prefix:
                continue
            for n in range(int(first), int(last) + 1):
                fn = f"{prefix}-{n}.png"
                out[fn] = {"titulo": title, "observacoes": obs,
                           "sequencia": {"grupo": prefix, "ordem": n, "total": int(last)}}
        else:
            out[name] = {"titulo": title, "observacoes": obs}
    return out


def infer_states(name: str, title: str) -> list[str]:
    s = f"{name} {title}".lower()
    states = []
    for key, label in (("escuro", "dark"), ("dark", "dark"), ("claro", "light"), ("light", "light"),
                       ("beta", "beta"), ("edit", "edit"), ("edicao", "edit"), ("animation", "animation"),
                       ("anim", "animation"), ("sobre", "overlay"), ("comparison", "comparison")):
        if key in s and label not in states:
            states.append(label)
    return states or ["reference"]


def sequence_for(name: str) -> dict | None:
    m = re.match(r"(.+)-(\d+)\.png$", name)
    if not m or m.group(1) not in SEQUENCE_RANGES:
        return None
    return {"grupo": m.group(1), "ordem": int(m.group(2)), "total": SEQUENCE_RANGES[m.group(1)]}


def record(path: Path, indexed: dict[str, dict]) -> dict:
    name = path.name
    manual = indexed.get(name, {})
    title = re.sub(r"\*+", "", manual.get("titulo", name.rsplit(".", 1)[0].replace("-", " "))).strip()
    cat, anchors = category(f"{name} {title}")
    seed = SEED.get(name, {})
    cat = seed.get("categoria", cat)
    anchors = seed.get("ancoras", anchors)
    use = seed.get("uso", [cat.replace("_", " ")])
    states = seed.get("estado", infer_states(name, title))
    observations = manual.get("observacoes", "")
    if observations and observations not in anchors:
        anchors = anchors + [observations]
    with Image.open(path) if Image else _NoImage() as im:
        width, height = im.size if Image else (None, None)
    rel = path.relative_to(BASE).as_posix()
    slug = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    seq = manual.get("sequencia") or sequence_for(name)
    if seq and "animation" not in states:
        states = states + ["animation"]
    origem_classificacao = "manual_index" if name in indexed else "curated_seed" if name in SEED else "filename_inference"
    return {
        "id": f"ref-{slug}", "arquivo": rel, "categoria": cat,
        "classificacao_fonte": origem_classificacao,
        "confianca": "alta" if origem_classificacao != "filename_inference" else "media",
        "estado": states, "prioridade": seed.get("prioridade", "secondary"),
        "titulo": title, "descricao": observations or title,
        "ancoras_visuais": anchors, "usar_para": use, "sequencia": seq,
        "dimensoes_px": {"largura": width, "altura": height},
        "proporcao": round(width / height, 4) if width and height else None,
        "bytes": path.stat().st_size, "sha256": sha256(path),
        "triagem": f"atlas/{cat}.jpg",
    }


class _NoImage:
    def __enter__(self): return self
    def __exit__(self, *_): return False
    size = (None, None)


def make_atlas(items: list[dict]) -> None:
    if Image is None:
        print("Pillow ausente: atlas não gerado")
        return
    if ATLAS.exists():
        shutil.rmtree(ATLAS)
    ATLAS.mkdir(parents=True)
    groups: dict[str, list[dict]] = {}
    for item in items:
        groups.setdefault(item["categoria"], []).append(item)
    font = ImageFont.load_default()
    for cat, rows in sorted(groups.items()):
        cols, thumb_w, thumb_h, label_h, gap = 4, 280, 180, 42, 12
        cell_h = thumb_h + label_h + gap
        rows_n = (len(rows) + cols - 1) // cols
        sheet = Image.new("RGB", (cols * (thumb_w + gap) + gap, rows_n * cell_h + gap), "#202124")
        draw = ImageDraw.Draw(sheet)
        for i, item in enumerate(rows):
            src = BASE / item["arquivo"]
            with Image.open(src).convert("RGB") as im:
                thumb = ImageOps.contain(im, (thumb_w, thumb_h))
            x = gap + (i % cols) * (thumb_w + gap)
            y = gap + (i // cols) * cell_h
            sheet.paste(thumb, (x + (thumb_w - thumb.width) // 2, y))
            label = item["arquivo"].split("/")[-1]
            if item["sequencia"]:
                label += f" [{item['sequencia']['ordem']}/{item['sequencia']['total']}]"
            draw.text((x, y + thumb_h + 4), label[:43], fill="#ffffff", font=font)
            draw.text((x, y + thumb_h + 18), item["prioridade"], fill="#9ad1ff", font=font)
        sheet.save(ATLAS / f"{cat}.jpg", quality=84, optimize=True)


def write_markdown(items: list[dict]) -> None:
    lines = ["# Catálogo visual para agentes", "",
             "Consulte este arquivo e os atlas antes de abrir originais. O JSON contém metadados estáveis; "
             "os atlas são miniaturas para triagem visual. Abra o original apenas para medir ou validar um detalhe.", "",
             "## Protocolo multimodal", "",
             "A descrição textual é um índice, não uma substituição da imagem. Use a sequência abaixo para reduzir custo sem perder informação visual:", "",
             "```text", "catálogo semântico → atlas → original → implementação → comparação", "```", "",
             "O atlas permite reconhecer a tela, o estado e a composição em uma única leitura visual. "
             "O original é necessário para texto pequeno, alinhamento, alpha, blur, raio, espessura, tipografia, "
             "ícones e comparação de pixels. Para uma animação, abra os frames pelo grupo e pela ordem `1/N`, "
             "`2/N`, `3/N`…; a relação entre os elementos ao longo dos frames faz parte da referência comportamental.", "",
             "Prioridades: `golden` = referência principal; `canonical` = referência ampla; `secondary` = apoio.", "",
             "`confianca=alta` indica classificação curada; `confianca=media` indica inferência pelo nome/estrutura "
             "e exige confirmação no atlas ou original antes de uma decisão visual crítica.", "",
             "| Categoria | Prioridade | Arquivo | Estado | Uso recomendado | Dimensão |", "|---|---|---|---|---|---|"]
    for x in items:
        states = ", ".join(x["estado"])
        use = ", ".join(x["usar_para"][:3])
        d = x["dimensoes_px"]
        lines.append(f"| `{x['categoria']}` | **{x['prioridade']}** | [`{x['arquivo'].split('/')[-1]}`]({x['arquivo'].split('/')[-1]}) | {states} | {use} | {d['largura']}×{d['altura']} |")
    lines += ["", "## Como um agente usa o catálogo", "",
              "1. Busque por categoria/estado/uso no `catalogo.json` ou com `consultar.py --imagem`.",
              "2. Abra o atlas indicado em `triagem` para reconhecer rapidamente a tela.",
              "3. Abra o arquivo original somente quando a tela for a referência escolhida.",
              "4. Para sequências, leia `sequencia.grupo`, `ordem` e `total` na ordem numérica.",
              "5. `golden` é referência principal; `canonical` é referência ampla; `secondary` é apoio.", "",
              "## Categorias", "",
              "`app_window` · `control_center` · `desktop` · `lock_screen` · `menu_bar` · `notification` · `osd` · `settings` · `spotlight` · `comparison`", ""]
    (TELAS / "CATALOGO-AGENTES.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    indexed = parse_index()
    files = sorted(p for p in TELAS.iterdir() if p.is_file() and p.suffix.lower() in EXTS)
    items = [record(p, indexed) for p in files]
    CATALOGO.write_text(json.dumps({"schema": 1, "base": "macOS Tahoe / 27", "items": items},
                                   ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_markdown(items)
    make_atlas(items)
    print(f"{len(items)} imagens catalogadas → {CATALOGO}")
    print(f"atlas → {ATLAS if Image else '(Pillow indisponível)'}")


if __name__ == "__main__":
    main()
