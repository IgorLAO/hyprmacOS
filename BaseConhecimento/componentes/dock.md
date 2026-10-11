# Dock

> Sources: macOS 27 UI Kit *Menu Bar and Dock* layer outline (`referencias/kit/contornos/Menu_Bar_and_Dock.txt`), style `Liquid Glass/*/Dock`, Apple HIG [dock-menus](../hig/dock-menus.md), MacMost Tahoe Course Guide, official UI screenshots.  
> App Icons: `referencias/kit/icones-apps/` (95 native app icons in light and dark variants).

---

## Dimensions (Kit Reference at 1×)
* **Dock Height:** **58 pt**.
* **Icon Footprint:** **36×36 pt**; icon pitch: **45 pt** (9 pt horizontal gap).
* **Margins:** 8 pt at ends, 11 pt top margin.
* **Running App Indicator:** **4×4 pt** white capsule, positioned 3 pt below icon.
* **Section Divider:** Vertical line **1×41 pt** (`#404040` *plus-lighter*) centered in an 11 pt column.

---

## Visual Styling
* **Liquid Glass Clear Variant:** Minimal blur radius (1 pt), high transparency leaving desktop wallpaper sharply visible.
* **Borders:** Ultra-fine dark outline + subtle white specular top/bottom highlights.
* **Sections:** Pinned applications | Recent unpinned applications | Pinned folders, documents, and Trash.
* **Badges:** Circular red notification count badges anchored to the top-right corner of icons.
* **Icon Variations:** Default (full color), Dark, Clear (monochromatic frosted glass), Tinted (accent color).

---

## Behavioral Specifications
* Single click launches or focuses application.
* Right-click / `⌃click`: Invokes native Dock menu (Open Windows list, Keep in Dock, Open at Login, Show in Finder, Quit).
* Drag out to remove; drag items over pinned folders to copy or move.
* Auto-hide toggling via `⌥⌘D`.
* Fluid spring-curve icon magnification on hover.
