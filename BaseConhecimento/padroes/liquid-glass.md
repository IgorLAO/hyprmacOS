# Liquid Glass and Materials

> Sources: macOS 27 UI Kit (Styles `Liquid Glass/*`, `Materials/*`, `Panels`, `Windows/*` → [tokens/macos27/estilos.md](../tokens/macos27/estilos.md)), Apple HIG [materials](../hig/materials.md) and [color](../hig/color.md), WWDC25 Sessions [219 Meet Liquid Glass](../hig/wwdc/219-meet-liquid-glass.txt) and [356 New design system](../hig/wwdc/356-new-design-system.txt).

---

## Overview

Two distinct material families define the macOS Tahoe visual hierarchy:

| Dimension | Liquid Glass | Standard Materials |
|---|---|---|
| **Layer** | **Functional** (controls, navigation bars, and overlays floating over content) | **Content** (window backdrops, cards, content sidebars) |
| **Optical Effect** | Lens refraction: dynamically curves and concentrates light; specular edge highlights; contextual drop shadows | Background blur + vibrancy (lightens/darkens and saturates underlying content) |
| **macOS Examples** | Menu bar selection pills, dropdown menus, Dock, notifications, Control Center, popovers, modal alerts | Window canvasses, sidebars, utility panels, desktop widgets |

### Golden Rules of Usage (HIG + WWDC):
1. **Confined to Functional Layers:** Applies strictly to navigation, toolbars, and controls. Never use Liquid Glass as a scrollable content background.
2. **No Glass on Glass:** Elements placed on top of glass use translucency, fills, and vibrancy (*plus-lighter* / *plus-darker*), never a nested second layer of blurred glass.
3. **Two Distinct Variants:**
   - **Regular:** Context-adaptive, balanced opacity, universally legible. Mandatory for alerts, popovers, sidebars, and text-dense surfaces.
   - **Clear:** High optical translucency; strictly reserved for media-rich environments (photos/video) with a **35% darkening underlay** on light backgrounds.
4. **Color as Tint, Not Solid Fill:** Color over glass is an ethereal translucent tint preserving background refraction. Opaque solid colors break the optical illusion.
5. **Dynamic Scale:** Small elements (capsules, buttons) flip light/dark based on local backdrop luminance; large surfaces (menus, sidebars) remain stable with deeper shadows.
6. **Materialization vs. Fading:** Surfaces materialize by growing lens refractive power from the invoking click point rather than cross-fading.
7. **Internal Glow:** Interactive elements illuminate from within upon click or hover. Inactive windows recede visually with lowered contrast.
8. **Modality Dimming:** Interrupted modal tasks require a 35% background dimming layer; parallel non-interrupting workflows do not dim the desktop.
9. **Accessibility Overrides:** *Reduce Transparency* increases opacity; *Increase Contrast* adds prominent high-contrast borders; *Reduce Motion* disables spring physics.

---

## Exact Kit Recipes (macOS 27, `Liquid Glass/*`)

*Notation: `#RRGGBB/alpha`; shadows formatted as `x y blur spread`.*

### Dropdown Menus (Dark / Light)
* **Fill:** `#5A5A5A/0.50` *luminosity* (Dark) · `#E6E6E6/0.55` *luminosity* (Light)
* **Glass:** Radius **20 pt**, saturation **1.2** (Dark) / **0.8** (Light), distortion 0.3, depth 0.9
* **Elevation Shadow:** `0 4 24 #0000004D` + outline `0 0 0 0.5 #000000CC` (Dark; Light `#00000033`)
* **Inner Bevel Rim:** `0 ±4 8 -4 #0D0D0D`, `0 ±0.5 0 0 #262626`, `0 0 0 1 #66666666`
* **Geometry:** Container radius **12 pt**, continuous smoothing 0.6, padding **6 / 16 / 5 / 16 pt**

### Notification Banners
* **Dark:** `#666666/0.10` *lighten*; glass radius 10 pt, distortion 0.1
* **Light:** `#BFBFBF/0.25` *lighten* + `#1A1A1A` *plus-lighter*; glass radius 15 pt
* **Shadow:** `0 4 16 #0000001A` + hairline `#ABABAB 0.3` + bevels `0 ±6 4 -6 #222222`
* **Geometry:** Continuous radius **20 pt**

### Regular – Large / Medium (Popovers, Alerts, Glass Panels)
* **Dark:** `#1A1A1A/0.50` + `#1A1A1A/0.50` *luminosity* + `#1A1A1A` *lighten*
* **Light:** `#FFFFFF/0.70` *lighten* + `#BFBFBF/0.10` *darken*
* **Glass:** Radius **30 pt**, saturation 1.2 (Dark) / 1.4 (Light), distortion 0.3
* **Elevation Shadow:** `0 18 48 #00000073` (Dark) · `0 18 46 #00000040` (Light)

### Regular – Small (Glass Buttons & Controls)
* **Dark:** `#000000` *screen* + `#999999/0.17`
* **Light:** `#000000/0.25` + `#FFFFFF/0.25` + `#444444/0.60` *plus-lighter*
* **Glass:** Radius **6 pt**, saturation 2.0 (Light), distortion 0.4, depth 0.8
* **Tinted (Primary Action):** `#FFFFFF/0.96` + system accent in *plus-darker* (e.g., `#FF383C`)

### Dock
* **Dark:** `#454545/0.50` *luminosity* + `#1A1A1A/0.10` *plus-darker* + `#FFFFFF/0.08` *lighten*
* **Light:** `#4D4D4D/0.30` *luminosity* + identical blend
* **Glass:** Radius **1 pt** (minimal blur, highly translucent)
* **Shadows:** Hairline `0 0 0 0.5 #00000040`, inner shadow `0 -12 12 -12`, top highlights `0 ±1 0.5 -0.5 #FFFFFF`

---

## Standard Materials (`Materials/*`) — Background Blur 60

| Thickness | Dark Fill | Light Fill | Saturation (Dark/Light) |
|---|---|---|---|
| Ultra Thin | `#292929/0.40` | `#ECECEC/0.38` | 1.8 / 1.45 |
| Thin | `#292929/0.49` | `#ECECEC/0.50` | 1.9 / 1.45 |
| **Regular** | `#2C2C2C/0.61` | `#ECECEC/0.63` | 1.9 / 1.45 |
| Thick | `#2C2C2C/0.71` | `#ECECEC/0.76` | 1.9 / 2.0 |
| Ultra Thick | `#2C2C2C/0.82` | `#ECECEC/0.88` | 1.9 / 2.0 |

---

## Linux Translation Matrix (GTK3 + Hyprland)

| Apple HIG Property | GTK3 CSS / Hyprland Equivalent | Technical Notes |
|---|---|---|
| Background Blur & Saturation | Hyprland `decoration.blur` (`size`, `passes`, `vibrancy`) + Layer rules | Blur is managed by the compositor; `vibrancy` provides extra saturation |
| Alpha masking (`ignore_alpha`) | `layerrule = ignorealpha [val], [namespace]` | Disables blur for transparent cutouts |
| *Luminosity* / *plus-lighter* blending | `background-color: rgba(...)` | Approximated via computed RGBA alpha blending |
| Multi-level bevel highlights | Multi-layer CSS `box-shadow: inset ...` | GTK3 accepts comma-separated inset and drop shadows |
| Specular edge gradient | Linear gradient borders | `border-top` brighter, `border-bottom` darker |
| Elevation shadows | `box-shadow` or Hyprland `decoration.shadow` | LayerShell surfaces require bounding margins for shadows |
| Continuous curvature (Squircles) | Hyprland `rounding_power = 3.2` | GTK renders circular radii; Hyprland applies squircle math to window boundaries |
| Optical refraction, lens, and specular bevels | `hyprglass` plugin + mask patch | See [liquid-glass-hyprland.md](liquid-glass-hyprland.md) |
