# Shape, Radii, and Spacing

> Sources: WWDC25 Session 356 ("Get to Know the New Design System"), macOS 27 UI Kit changelog, Apple HIG [layout](../hig/layout.md), [buttons](../hig/buttons.md).

---

## Concentricity (The Golden Geometric Rule)

* **$\text{Inner Radius} = \text{Outer Radius} - \text{Margin}$**: Nested elements share the exact same geometric center of curvature.
* Three primary shape types:
  1. **Fixed**: Constant explicit radius (e.g., standard window corners).
  2. **Capsule**: Radius equals half the component height ($r = h / 2$).
  3. **Concentric**: Radius dynamically computed from parent radius minus padding; uses fallback fallback radius when rendered standalone.
* Visual warning signs: "Pinched" corners (inner radius excessively large) or "hollow" corners (inner radius excessively small).
* **Optical Centering**: Mathematical center by default, with slight vertical optical compensation for glyphs and labels.

---

## Continuous Curvature (Squircles)
All corner radii in macOS 27 are **continuous superellipses** (`smoothing 0.6`), not simple circular arcs. In Hyprland, this is rendered via:
```lua
rounding = 22,
rounding_power = 3.2,
```

---

## Radius Table (macOS 27 UI Kit)

| Element | Radius (pt) | Notes |
|---|---|---|
| Regular Windows | **16–22 pt** | 22 pt on unified toolbars |
| Utility Panels | 15 pt | |
| Dialogs / Alerts | **26 pt** | Large modal card |
| Popovers | **20 pt** | Includes pointing arrow ("cartouche") |
| Notification Banners | **20 pt** | Floating toast card |
| Stacked Notification (Background) | 16–22 pt | Inset 16px on each side |
| Dropdown Menus (Container) | **12 pt** | Padding 6/16/5/16 pt |
| Menu Item Selection Pill | **8 pt** | 24 pt item height |
| Menu Bar Active Pill | **13 pt** | 25 pt height capsule |
| Notification App Icon | 6 pt | 32×32 pt square |
| Toggles, Switches, Sliders | Capsule ($r = h/2$) | |
| Extra-Large Controls | Capsule | Liquid Glass styled |

---

## Standard Spacing Metrics

| Component | Dimensions & Padding |
|---|---|
| Menu Bar | 34 pt height on Retina reference screens (24 pt base) |
| Menus | 24 pt item height (regular), 11 pt separator height |
| Notification Banners | 344 pt width; padding 12/14/12/10 pt; 8 pt inter-element gap |
| Notification Stack | 16 pt between groups; 16 pt margin from right display edge; 15 pt below menu bar |
| Modal Alerts | 260 pt width; padding 20/16/16/16 pt; 14 pt vertical gap |
| Save Dialogs | 390 pt width; 20 pt padding |
| Dock | 58 pt height; 36 pt icons with 45 pt pitch; 4×4 pt indicator dots |
| Window Stoplights | 14 pt diameter circles, 9 pt gap between buttons |
| Tooltips | Padding 3/6 pt; Medium 11 pt text |

Standard 4pt / 8pt spatial grid (typical increments: 4, 8, 12, 16, 20, 24 pt).
