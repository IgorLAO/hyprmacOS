# Critical Gap Analysis: Dock (SIS-01)

**Status:** 🟡 NEAR CONFORMITY (P1 CRITICAL)  
**Last Updated:** 2026-10-03  
**References:** Safari-Tahoe reference screens, Menu Bar and Dock UI Kit, WWDC Liquid Glass specifications

---

## 1. Apple Reference Specifications

### 1.1 Verified Dimensions on Native Screens
* **Total Height:** **58 pt**
* **Icon Size:** **36×36 pt** (vertically centered in Dock)
* **Icon Pitch (Spacing):** **45 pt** (9 pt gap between icons)
* **Side Margins:** **8 pt** (left/right)
* **Top Margin:** **11 pt**
* **Bottom Margin:** ~15 pt

**Active Application Indicator:**
* **Shape:** Miniature capsule **4×4 pt**
* **Position:** **3 pt below icon**
* **Color:** Solid white

**Section Divider:**
* **Shape:** Vertical line **1×41 pt**
* **Color:** `#404040` (*plus-lighter* subtle white on dark gray)
* **Column Width:** 11 pt (5 pt padding on each side)

### 1.2 Glass Material — Liquid Glass Clear Variant
* **Blur Radius:** Minimal (~1 pt)
* **Translucency:** Extremely high (>95% of wallpaper visible)
* **Specular Highlights:** Ambient top rim lighting
* **Outlines:** Subtle 1px dark bottom outline + 1px soft white top highlight

### 1.3 Icon Styles
All 4 Appearance variants supported:
* **Default:** Full color original app icons
* **Dark:** Dark mode variants
* **Clear:** Monochromatic glass/white styling
* **Tinted:** Monochromatic styled with system accent color

---

## 2. hyprmac Implementation Status

**Source:** `shell/hyprmac-shell` (`class Dock`) and `shell/style.css`

### Working:
* ✅ 4 icon styles (Default/Dark/Clear/Tinted)
* ✅ White indicator dots under active apps
* ✅ Section dividers
* ✅ Dock context menus (Keep in Dock, Hide, Quit)
* ✅ Auto-hide support (`⌥⌘D`)
* ✅ Red notification count badges

### Target Refinements:
1. **Glass Material:** Keep blur minimal and translucency high (`rgba(128,128,142,0.15–0.22)`).
2. **Icon Scaling:** Validate user display resolution scaling (36 pt vs 46 pt).
3. **Hover Magnification:** Implement smooth spring-curve magnification on hover.
4. **Window Minimization Animation:** Implement genie / scale transform when minimizing to Dock.

---

## 3. Comparison Matrix

| Parameter | Apple Specification | hyprmac Implementation | Target |
|---|---|---|---|
| Height | 58 pt | 58–64 pt | 58 pt |
| Icon Size | 36×36 pt | 46×46 pt | 36×36 pt (or 1× scaled) |
| Pitch | 45 pt | 57 pt | 45 pt |
| Radius | ~13–16 pt | 19 pt | 16 pt continuous squircle |
| Glass Alpha | 0.05–0.15 | 0.22 | 0.15–0.20 |
| Blur Radius | ~1 pt | Minimal | ~1 pt |
| Specular Highlight | 1px top white | CSS border highlight | 1px subtle white |

---

## 4. Implementation Plan

1. **Material Calibration:** Maintain high optical transparency and top specular bevel highlight.
2. **Hover Magnification:** Calculate Gaussian magnification curve on mouse move.
3. **Genie / Minimization Effect:** Implement Hyprland animation trigger or layer-shell visual effect.
4. **Dock Tooltip:** Render floating frosted glass bubble with arrow pointing to icon on hover.
