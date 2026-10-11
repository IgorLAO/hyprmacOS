# Menus: Dropdowns, Submenus, and Context Menus

> Sources: macOS 27 UI Kit *Menus* outline (`referencias/kit/contornos/Menus.txt`), style `Liquid Glass/*/Menus`, Apple HIG [menus](../hig/menus.md), [context-menus](../hig/context-menus.md), [edit-menus](../hig/edit-menus.md), [the-menu-bar](../hig/the-menu-bar.md).

---

## Menu Container Geometry & Materials
* **Liquid Glass Menu Recipe:** Dark `#5A5A5A/0.50` *luminosity*, Light `#E6E6E6/0.55`; glass radius 20 pt; elevation shadow `0 4 24 #0000004D` + dark perimeter outline + inner bevels.
* **Geometry:** Container **radius 12 pt** (continuous 0.6 squircle); **padding 6 pt (top) / 16 pt (horizontal) / 5 pt (bottom)**.
* **Submenus:** Shares identical glass material; opens aligned to the invoking parent item.

---

## Menu Items (Regular Size)

| Element | Dimension / Typography / Styling |
|---|---|
| **Item Height** | **24 pt** (Small: 22 pt, Mini: 19 pt) |
| Checkmark Column (`✓`) | 4 pt width column (glyph: SF Bold 13 pt) |
| Optional Leading Icon | 11×16 pt bounding area |
| Primary Label | **SF Pro Medium 13 pt**, `#FFFFFFFA` 96% (Dark) / `#000000D9` 85% (Light) |
| Shortcut Glyphs | Aligned right (66 pt column); modifiers `⌃ ⌥ ⇧ ⌘` + key; Medium 13 pt **`#4C4C4C`** |
| Submenu Chevron | SF Symbol `chevron.right` Bold 13 pt gray |
| **Hover Selection Pill** | Background **`#0069F9`**, **radius 8 pt**, extends 11 pt beyond text horizontally; white text |
| Submenu Open Indicator | Inactive open state: subtle pill `#FFFFFF14` (8%), radius 8 pt |
| Disabled State | Label text dimmed to `#4C4C4C` (40% opacity) |
| Section Header | Bold 13 pt, `#8A8A8A` |
| Section Separator | 11 pt height container with a centered 1px hairline (`#FFFFFF14` in dark mode) |

---

## Behavioral Standards (Apple HIG)
* Use Title Case without articles; append "…" exclusively if further configuration is needed before execution.
* Shortcuts remain visible in menu bar dropdowns; unavailable items are dimmed rather than hidden.
* Context menus: Omit keyboard shortcuts; hide unavailable items rather than dimming; limit to $\le 3$ functional groups.
