# Windows, Popovers, Panels, Alerts, and Dialogs

> Sources: macOS 27 UI Kit layer outlines (*Windows*, *Titlebars and Toolbars*, *Sidebars*, *Popovers*, *Alerts*, *Dialogs*, *Tooltips*, *Scrollbars*); Apple HIG [windows](../hig/windows.md), [popovers](../hig/popovers.md), [panels](../hig/panels.md), [alerts](../hig/alerts.md), [sheets](../hig/sheets.md), [toolbars](../hig/toolbars.md), [sidebars](../hig/sidebars.md).

---

## Windows
* **Corner Radius:** **16–22 pt** (continuous squircle); background `#1E1E1E` (Dark) / `#FFFFFF` (Light); 1px inner border `#FFFFFF33` in dark mode.
* **Drop Shadows:**
  * **Active Focused:** `0 36 100 #00000066` + hairline `0 0 1 #000000CC`.
  * **Inactive Unfocused:** `0 16 32 #00000033` + hairline outline.
* **Traffic Lights (Stoplight):** 14 pt circles, 9 pt gap; Close `#FF5C60`, Minimize `#FAC800`, Zoom `#35C759` (0.5 pt rim `#00000073`). Inactive windows: all three dimmed to `#00000026`. Positions: `(9, 9)` simple bar, `(13, 13)` compact bar, `(18, 19)` expanded toolbar.
* **Window Toolbars:** Default, **Unified Toolbar**, **Unified Compact Toolbar**, **Expanded Toolbar**.
* **Floating Sidebar:** Inset translucent glass sidebar with stoplights nested inside; content scrolls behind it.
* **Toolbar Controls:** Grouped into segmented glass capsules; primary action receives vibrant tint.
* **Zoom Button (Green):** Hover menu reveals tiling shortcuts (Tile Left/Right, Quarters, Fullscreen).

---

## Popovers
* Material: **Regular – Medium Liquid Glass**; container **radius 20 pt**; pointing arrow ("cartouche") 46×10.5 pt directed at the invoking trigger.
* 12 spatial docking positions (North/South/East/West × start/center/end). Can detach into floating utility panels.

---

## Utility Panels
* Radius: 15 pt; styling: `#1E1E1E` + `#FFFFFF33` inner glow + shadow `0 16 33 #00000066`.

---

## Modal Alerts
* **Width:** **260 pt**; material: **Regular – Large Liquid Glass**, **radius 26 pt**; padding **20/16/16/16 pt**, vertical gap 14 pt.
* Optional 72 pt icon · **Title: Bold 13 pt** · Description: Regular 13 pt.
* **Buttons:** **28 pt height capsules**: side-by-side (110 pt width each, 8 pt gap) or stacked (228 pt width, 6 pt gap).
  * Default: Vibrant blue fill with white text.
  * Cancel: Subdued Medium 13 pt text.
  * Destructive: Red fill at 25% (*plus-lighter*) + red text.
* Window modal overlay dims background content by 35%.

---

## Dialogs (e.g., Save Sheet)
* Width: 390 pt, radius 26 pt, padding 20 pt; window-sheet styling; leading icon (92 pt column), Title: Bold 14 pt, Body: Medium 11 pt; form fields 230 pt wide; action buttons 76×24 pt aligned bottom-right.

---

## Tooltips & Scrollbars
* **Tooltips:** Padding 3/6 pt; typography: **Medium 11 pt**; height: 19 pt.
* **Scrollbars:** 6 pt wide capsule thumb inside a 12 pt track; `#00000080` (Light) / `#FFFFFF8C` (Dark).
