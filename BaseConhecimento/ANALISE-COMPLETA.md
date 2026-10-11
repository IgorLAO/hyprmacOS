# Comprehensive Analysis: macOS Tahoe × hyprmac

**Objective:** Maximum fidelity and structural parity with Apple macOS Tahoe / 27.  
**Reference Sources:** WWDC25 Sessions 219 & 356, MacMost Tahoe Guide, Apple HIG, UI Screenshots, Sketch macOS 27 UI Kit.  
**Updated:** 2026-10-03  

---

## 1. Foundational Design Principles (WWDC)

### 1.1 Liquid Glass — The Digital Meta-Material
* **Definition:** A dynamic digital material that bends, refracts, and concentrates light in real time. Rather than simulating physical frosted acrylic, it synthesizes optical glass physics with the fluid dynamics of liquids.
* **Optical Lensing:** Deforms background luminance to communicate spatial depth, edge boundaries, and elevation.
* **Touch & Pointer Responsiveness:** Flexes and energizes with inner illumination upon pointer interaction, returning smoothly to rest.
* **Metamorphosis:** Smooth transitions between geometric states (capsule expansion, mode switching) preserving the perception of a unified floating glass layer.
* **Materialization:** Enters and exits by modulating light and lens power rather than applying abrupt alpha fades.
* **Hierarchy Invariant:** Liquid Glass lives strictly on the **functional control layer**. Never nest glass within glass; elements resting on glass use vibrancy or translucent color fills.

### 1.2 Unified Design System
* **Concentricity Rule:** $\text{inner radius} = \text{outer radius} - \text{margin}$.
  * Fixed: Constant explicit radius.
  * Capsule: Radius equals half the component height ($r = h / 2$).
  * Concentric: Nested children dynamically derive curvature from their parent container.
* **Continuous Squircles:** macOS Tahoe avoids simple circular arcs in favor of superellipses with continuous curvature (Hyprland `rounding_power = 3.2`).
* **Spatial Origin:** Modals, sheets, popovers, and menus materialize outward from their invoking element.

---

## 2. Component Design Specifications

### 2.1 Menu Bar (`waybar/`)
* **Height:** **34 pt** on scaled Retina reference screens (24 pt standard base).
* **Apple Logo:** 20 pt font size (13×16 pt glyph footprint), 23 pt margin from left display edge.
* **Focused Application Name:** Heavy 13 pt (weight 800–900), positioned ~58 pt from Apple logo.
* **Menu Titles:** Semibold 13 pt, 26 pt horizontal spacing between items.
* **Hover / Selection Pill:** 24 pt height capsule, 13 pt radius, `rgba(255, 255, 255, 0.18)` in dark mode.
* **Right Status Extras:** ~16 pt glyph footprints with ~39 pt horizontal pitch.
* **Clock Format:** "Sun 12:07", Semibold 13 pt, ~23 pt from right edge.

### 2.2 Menus & Popovers
* **Container Radius:** **12 pt** continuous curvature.
* **Item Height:** **24 pt**.
* **Container Padding:** 6 pt (top) / 16 pt (horizontal) / 5 pt (bottom).
* **Hover Selection Pill:** **8 pt** radius, colored `#0069F9` (Tahoe selection blue).
* **Shortcuts:** Subdued gray typography aligned right; disabled items remain visible but dimmed.

### 2.3 Windows & Compositor Geometry (`hypr/hyprmac.lua`)
* **Corner Radius:** **16–22 pt** with `rounding_power = 3.2`.
* **Zero Margins:** Windows touch the top menu bar and screen edges (`gaps_in = 0`, `gaps_out = 0`), mimicking macOS tiled mode.
* **Contour Lighting:**
  * 1px subtle dark outline on exterior (`rgba(0, 0, 0, 0.50)`).
  * 1px inner white glow at 20% luminance (`rgba(255, 255, 255, 0.40)`) present exclusively on the active focused window in dark mode.
* **Drop Shadows:** Range 50, render power 3, offset `0 18`, color `rgba(0, 0, 0, 0.40)`.

### 2.4 Control Center (`shell/hyprmac-shell`)
* **Grid Geometry:** Concentric arrangement of circular buttons and rectangular tiles (tile gap $\approx 0.2 \cdot d$).
* **Active State:** White background with blue icon glyph.
* **Sliders:** Display slider in system accent blue with integrated SF brightness icons; volume slider in neutral glass.
* **Inline Sub-Popovers:** Secondary settings (Bluetooth devices, audio outputs, Wi-Fi networks) expand inline within the card rather than launching external windows.

### 2.5 Dock (`shell/hyprmac-shell`)
* **Height:** 58 pt base.
* **Icon Size:** 36×36 pt (scaled to 46×46 pt on higher resolution displays).
* **Glass Translucency:** Clear variant with minimal blur (`alpha 0.15–0.22`), leaving desktop wallpaper clearly visible.
* **Indicators:** 4×4 pt capsule dot positioned 3 pt below active app icons.
* **Context Menus:** Keep in Dock, Hide, Quit (`⌘Q`).

---

## 3. Compliance Summary

Audited automatically via `BaseConhecimento/ferramentas/comparar.py`:
* **Overall Compliance:** **94%**
* **100% Areas:** Menus, Colors, Typography, Glass & Materials, Keyboard Shortcuts, Notifications.
* **Active Areas of Refinement:** Control Center inline expansion, Dock magnification & minimization, Finder visual identity, and System Settings completeness.
