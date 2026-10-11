> Arquivo histórico anterior à consolidação de 2026-10-10.

# Knowledge Base — Apple Design System (macOS Tahoe / 27)

Official Apple design references **indexed** to guide the `hyprmac` project.

---

## ⚡ Querying the Base (`consultar.py`)

```bash
B=~/Projects/hyprmac/BaseConhecimento/ferramentas
$B/consultar.py "notification radius"        # Search all records (FTS5, BM25 ranking, unaccented)
$B/consultar.py "liquid glass" -t hig        # By type: componente, padrao, hig, wwdc, dev, pdf, contorno, token, tela, suporte
$B/consultar.py "menu hover" --completo      # Full section snippet
$B/consultar.py --estilo "glass/dark/menus"  # Material/glass layer style recipe from kit
$B/consultar.py --cor blue                   # Colors (Light, Dark, Vibrant)
$B/consultar.py --tipografia body            # Typography and text styles
$B/consultar.py --imagem "control center"    # UI screens and figures by description
$B/consultar.py --sql "SELECT nome, hex FROM cores WHERE grupo LIKE '%Labels/Dark%'"
$B/indexar.py                                # Rebuilds base.db after modifying documentation files
```

The database (`base.db`, SQLite) indexes:
- `trechos`: FTS5 full-text search across ~7,800 sections.
- `cores`: Color tokens.
- `tipografia`: Typography styles.
- `estilos`: Layer and material styles.
- `imagens`: UI screens, figures, and cursors.

---

## 📊 Comparison with hyprmac (`comparar.py`)

- [comparacao/MATRIZ.md](../../comparacao/MATRIZ.md) — Matrix generated from [comparacao/parametros.json](../../comparacao/parametros.json).
- Each parameter defines: target area, Apple value + source, current hyprmac value, code file, automated regex inspection, status (✅, 🟡, 🔴, ⬜, ➖), priority (P1–P3), and weight.
- Numeric parameters are **read directly from the code** via regex on each execution, so compliance scores update automatically.

```bash
$B/comparar.py              # Re-inspects hyprmac, recalculates score, and regenerates MATRIZ.md
$B/comparar.py --resumo     # Summary score by area
$B/comparar.py --pendentes  # Pending items sorted by priority
$B/consultar.py --sql "SELECT id, parametro, status FROM parametros WHERE prioridade='P1'"
```

To add a parameter: insert a new entry into `parametros.json` (with `leitura` + `alvo`/`tolerancia` or `igual` if measurable in code; otherwise set `hyprmac` + `status` manually).

---

## 🧭 Start Here (Distilled Knowledge)

### For AI agents

Start with [`INDICE-AGENTES.md`](../../INDICE-AGENTES.md). It is the operational
index for routing a task to the right source file, reference, query, and
validation command. The project requires **MÁXIMA FIDELIDADE** visual e
comportamental com as referências do macOS Tahoe / macOS 27; “parecido” ou
“inspirado” não é um critério de aceite.

For bounded context retrieval, use [`GERENCIAMENTO-CONTEXTO.md`](../../GERENCIAMENTO-CONTEXTO.md),
[`codigo.json`](../../codigo.json), `consultar.py --codigo` and the visual catalog.

### Core Patterns ([`padroes/`](../../padroes/))
- [liquid-glass.md](../../padroes/liquid-glass.md) — Rules + **exact recipes** (menus, notifications, popovers, Dock, materials) + GTK/Hyprland translation
- [liquid-glass-hyprland.md](../../padroes/liquid-glass-hyprland.md) — **True Optical Liquid Glass** (lens, specular, bevel) via `hyprglass` plugin: `scripts/vidro`, `shell/vidro.py`, Apple optical model, live vs config-only adjustments
- [forma-e-espacamento.md](../../padroes/forma-e-espacamento.md) — Concentricity, radius table, dimensions
- [cores-e-tipografia.md](../../padroes/cores-e-tipografia.md) — Tahoe/27 palette, labels, vibrancy, SF Pro
- [movimento-escrita-e-principios.md](../../padroes/movimento-escrita-e-principios.md) — Principles, motion, copywriting, menus, popovers, modals
- [atalhos-de-teclado.md](../../padroes/atalhos-de-teclado.md) — Standard keyboard shortcuts
- [interacao-entre-objetos-e-layout.md](../../padroes/interacao-entre-objetos-e-layout.md) — Glass-on-glass interaction (fusion, union, metamorphosis, materialization), grouping, HIG layout, drag & drop

### UI Components ([`componentes/`](../../componentes/))
[barra-de-menus](../../componentes/barra-de-menus.md) · [menus](../../componentes/menus.md) ·
[central-de-controle](../../componentes/central-de-controle.md) · [notificacoes](../../componentes/notificacoes.md) ·
[dock](../../componentes/dock.md) · [janelas-popovers-alertas](../../componentes/janelas-popovers-alertas.md) ·
[controles](../../componentes/controles.md) · [sistema-e-recursos](../../componentes/sistema-e-recursos.md)
(Spotlight, widgets, lock screen, multitasking, screenshots, appearance, media, cursors)

---

## 📦 Raw Materials & Assets

| Directory | Content |
|---|---|
| [tokens/macos27](../../tokens/macos27/) | **110 colors, 67 text styles, 285 layer styles** extracted from *Apple macOS 27 UI Kit* (Sketch) — `.md` + `.json` |
| [tokens/visionos](../../tokens/visionos/) | Extracted tokens from *VisionUIs* UI kit (glass with specular highlights) |
| [referencias/kit/contornos](../../referencias/kit/contornos/) | Layer tree with measurements, radii, padding, and colors of **all 35 pages** of the macOS 27 kit |
| [referencias/kit-visionos/contornos](../../referencias/kit-visionos/contornos/) | Same for the visionOS kit |
| [referencias/kit](../../referencias/kit/) | Official macOS 27 wallpapers, **SF Pro fonts**, 95 app icons, 22 SVG cursors, icon template, previews |
| [referencias/telas](../../referencias/telas/) | 65 Tahoe screenshots with [agent catalog](../../referencias/telas/CATALOGO-AGENTES.md), JSON metadata, and triage atlases |
| [referencias/pdfs](../../referencias/pdfs/) | PDF transcripts (Tahoe new features, course textbook, HIG quick index) |
| [dev/](../../dev/) | Apple developer documentation on Liquid Glass (`GlassEffectContainer`, union, transitions, *Adopting Liquid Glass*) |
| [hig/](../../hig/) | **49 HIG pages** in Markdown (11 with figures) + 2 WWDC25 transcripts |
| [ferramentas/](../../ferramentas/) | Helper scripts: `indexar.py`, `indexar_codigo.py`, `catalogar_imagens.py`, `consultar.py`, `comparar.py`, and extraction tools |

---

## 💡 Key Design Takeaways

1. **New Palette**: System Blue is **#0088FF / #0091FF**, Destructive Red is **#FF383C** (replaces old `#007AFF` / `#0A84FF`).
2. **Menu Bar**: **24 pt** (base) / **34 pt** (Retina reference screen), menus **Semibold 13**, app **Heavy 13**, capsule selection radius 13.
3. **Menus**: Glass radius 12, padding 6/16/5/16, item height 24, hover **#0069F9** radius 8, shortcuts in subdued gray.
4. **Radii**: Window **16–22 pt**, notification **20 pt**, popover **20 pt**, alert **26 pt**, menu **12 pt**; strictly **concentric** and continuous.
5. **Materials**: Blur 60, saturation 1.45–2.0; menu glass radius 20; **Dock is almost blur-free**.
6. **Liquid Glass**: Only on the control layer, no glass on glass, color applied as tinting, Clear variant with 35% dimming.
7. **Control Center**: Circle grid (gap $\approx 0.2 \cdot d$), active = white background + blue glyph, edit mode with "−" badges and ghost slots, gallery with 3 sizes; sliders with glass knob in light mode.
8. **Spotlight**: 4 modes (⌘1–⌘4), quick action keys, system actions, and search history.
9. **Primary Reference Screen:** `referencias/telas/safari-escuro-barra-de-menus-abas.png`.
   - Windows touch the menu bar and sides (`gaps_in = 0`, `gaps_out = 0`).
   - Window contour: 1px black outline on exterior + 1px white glow at 20% on the active window interior.
