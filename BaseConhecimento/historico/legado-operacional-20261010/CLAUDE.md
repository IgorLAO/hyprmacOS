> Arquivo histórico anterior à consolidação de 2026-10-10. Consulte STATUS.md e o SQLite para o estado atual.

# Knowledge Base & Project Guidelines — Apple macOS Tahoe / macOS 27 Design System

Official Apple design references **indexed** to guide the `hyprmac` project.
Goal: Transform Linux (Hyprland + Wayland) into a pixel-perfect, 1:1 behavioral and visual replica of macOS Tahoe / macOS 27 (Liquid Glass). The only acceptable divergence is window tiling.

---

## ⚡ Quick Querying (`consultar.py`)

The fastest way to look up Apple specifications, design tokens, colors, and guidelines:

```bash
B=~/Projects/hyprmac/BaseConhecimento/ferramentas
$B/consultar.py "notification radius"        # Full search (SQLite FTS5, BM25 ranking, unaccented)
$B/consultar.py "liquid glass" -t hig        # By type: componente, padrao, hig, wwdc, dev, pdf, contorno, token, tela, suporte
$B/consultar.py "menu hover" --completo      # Print full section text
$B/consultar.py --estilo "glass/dark/menus"  # Material and glass recipes from kit
$B/consultar.py --cor blue                   # Colors (Light, Dark, Vibrant)
$B/consultar.py --tipografia body            # Typography and text styles
$B/consultar.py --imagem "control center"    # UI screens and figures by description
$B/consultar.py --sql "SELECT nome, hex FROM cores WHERE grupo LIKE '%Labels/Dark%'"
$B/indexar.py                                # Rebuilds base.db after updating docs
```

The database (`BaseConhecimento/base.db`) contains:
- `trechos`: ~7,800 indexed documentation snippets with FTS5.
- `cores`: 127 color swatches from macOS and visionOS UI kits.
- `tipografia`: 207 text styles.
- `estilos`: 300 layer and material styles (glass, blur, saturation, specular).
- `imagens`: Indexed UI screenshots, kit symbols, and cursors.
- `parametros`: Real-time compliance status vs Apple standards.

---

## 📊 Comparison with hyprmac (`comparar.py`)

- [BaseConhecimento/comparacao/MATRIZ.md](file:///home/igor/Projects/hyprmac/BaseConhecimento/comparacao/MATRIZ.md) — Compliance matrix generated from [BaseConhecimento/comparacao/parametros.json](file:///home/igor/Projects/hyprmac/BaseConhecimento/comparacao/parametros.json).
- Each parameter defines: target area, Apple value + reference source, current hyprmac value, source file, automated regex inspection, status (✅ conformant, 🟡 near, 🔴 divergent, ⬜ missing, ➖ system limitation), priority (P1–P3), and weight.
- Numeric values are **dynamically parsed from actual code** (regex) on every execution, keeping the compliance score automated and truthful.

```bash
$B/comparar.py              # Re-inspects hyprmac code, recalculates and updates MATRIZ.md + SQLite
$B/comparar.py --resumo     # Prints compliance score summary by area (currently 94%)
$B/comparar.py --pendentes  # Lists pending tasks sorted by priority (P1 -> P3)
$B/consultar.py --sql "SELECT id, parametro, status FROM parametros WHERE prioridade='P1'"
```

To add a new parameter: add an entry to `parametros.json` with `leitura` + `alvo`/`tolerancia` (or `igual`) when measurable in code; otherwise set `hyprmac` + `status` manually.

---

## 🎯 Golden Rules for AI Agents

1. **Absolute Source of Truth is Real Code**:
   - `shell/style.css` is the source of truth for styles, colors, transitions, and shadows.
   - `shell/hyprmac-shell` is the source of truth for shell components (Dock, Control Center, Spotlight, Widgets, Notifications).
   - `hypr/hyprmac.lua` is the source of truth for Hyprland window rules, squircle rounding, shadows, and blur.
   - Do NOT guess numbers or trust unreferenced notes. Always inspect the code or check `parametros.json`.
2. **Apple Parity Over Approximation**:
   - The design must be identical to macOS Tahoe / macOS 27, not an approximation.
   - Concentricity rule: $\text{inner radius} = \text{outer radius} - \text{margin}$.
   - Squircle rule: Hyprland `rounding_power = 3.2` for continuous curvature.
   - Gaps rule: `gaps_in = 0`, `gaps_out = 0`. Windows touch the menu bar and screen edges just like macOS with margins disabled.
   - Glass rules: Liquid Glass lives on the control layer only; NO glass-on-glass blur; tinting instead of solid fill; Clear glass uses 35% darkening overlay.
3. **Preserve System Integrity**:
   - Never break `install.sh`, `indexar.py`, or `comparar.py`.
   - All Python scripts must compile cleanly (`python3 -m py_compile`).

---

## 📚 Core Distilled Knowledge

### Cross-Cutting Patterns ([`BaseConhecimento/padroes/`](file:///home/igor/Projects/hyprmac/BaseConhecimento/padroes))
- [liquid-glass.md](file:///home/igor/Projects/hyprmac/BaseConhecimento/padroes/liquid-glass.md): Rules + exact recipes (menus, notifications, popovers, Dock, materials) + GTK/Hyprland mapping.
- [liquid-glass-hyprland.md](file:///home/igor/Projects/hyprmac/BaseConhecimento/padroes/liquid-glass-hyprland.md): Optical Liquid Glass (lens refraction, specular highlights, bevel) via `hyprglass` plugin + mask shader patch.
- [forma-e-espacamento.md](file:///home/igor/Projects/hyprmac/BaseConhecimento/padroes/forma-e-espacamento.md): Concentricity, radius table, metrics, margins.
- [cores-e-tipografia.md](file:///home/igor/Projects/hyprmac/BaseConhecimento/padroes/cores-e-tipografia.md): Tahoe/27 color palette, labels, vibrancy, SF Pro fonts.
- [movimento-escrita-e-principios.md](file:///home/igor/Projects/hyprmac/BaseConhecimento/padroes/movimento-escrita-e-principios.md): Motion principles, popins, spring physics, copywriting.
- [atalhos-de-teclado.md](file:///home/igor/Projects/hyprmac/BaseConhecimento/padroes/atalhos-de-teclado.md): macOS standard keyboard shortcuts.
- [interacao-entre-objetos-e-layout.md](file:///home/igor/Projects/hyprmac/BaseConhecimento/padroes/interacao-entre-objetos-e-layout.md): Glass-on-glass interaction (fusion, union, metamorphosis, materialization), HIG 2026 layout.

### UI Components ([`BaseConhecimento/componentes/`](file:///home/igor/Projects/hyprmac/BaseConhecimento/componentes))
- [barra-de-menus.md](file:///home/igor/Projects/hyprmac/BaseConhecimento/componentes/barra-de-menus.md) (Menu Bar)
- [menus.md](file:///home/igor/Projects/hyprmac/BaseConhecimento/componentes/menus.md) (Context & Dropdown Menus)
- [central-de-controle.md](file:///home/igor/Projects/hyprmac/BaseConhecimento/componentes/central-de-controle.md) (Control Center)
- [notificacoes.md](file:///home/igor/Projects/hyprmac/BaseConhecimento/componentes/notificacoes.md) (Notification Center & Banners)
- [dock.md](file:///home/igor/Projects/hyprmac/BaseConhecimento/componentes/dock.md) (Dock)
- [janelas-popovers-alertas.md](file:///home/igor/Projects/hyprmac/BaseConhecimento/componentes/janelas-popovers-alertas.md) (Windows, Popovers, Alerts)
- [controles.md](file:///home/igor/Projects/hyprmac/BaseConhecimento/componentes/controles.md) (Controls, Sliders, Toggles)
- [sistema-e-recursos.md](file:///home/igor/Projects/hyprmac/BaseConhecimento/componentes/sistema-e-recursos.md) (Spotlight, Widgets, Lock Screen, Multitasking, Screenshots, Cursors)

---

## 🎨 Key Design Specs (macOS Tahoe / 27)

1. **Color Palette**: System Blue is **#0088FF / #0091FF**, Destructive Red is **#FF383C** (replaces old `#007AFF` / `#0A84FF`).
2. **Menu Bar**: **34 pt** height (matching Retina display reference), Body **Semibold 13 pt**, App Name **Heavy 13 pt**, selection capsule radius **13 pt**.
3. **Menus**: Glass radius **12 pt**, padding **6/16/5/16**, item height **24 pt**, hover `#0069F9` radius **8 pt**, shortcuts in subdued gray.
4. **Corner Radii**: Window **16–22 pt**, notification **20 pt**, popover **20 pt**, alert **26 pt**, menu **12 pt**; strictly concentric.
5. **Materials**: Blur **60**, saturation **1.45–2.0**; Dock is almost blur-free.
6. **Liquid Glass**: Only on control layer; no glass-on-glass blur; tinting over solid fill; Clear glass uses 35% background dimming.
7. **Control Center**: Grid of circles (gap $\approx 0.2 \cdot d$), active = white background + blue glyph, edit mode with "−" badges and ghost circles, gallery with 3 sizes; sliders with glass knob in light mode.
8. **Spotlight**: 4 modes (⌘1–⌘4), quick action keys, system indexing, math evaluation, and search history.
9. **Primary Visual Reference**: `referencias/telas/safari-escuro-barra-de-menus-abas.png`.
   - Windows touch the menu bar and sides (`gaps_in = 0`, `gaps_out = 0`).
   - Window contour: 1px outer black stroke (`rgba(0,0,0,0.50)`) + 1px inner white glow at 20% on active window (`rgba(255,255,255,0.40)`).
