# Gap Analysis (P2): Lock Screen (SIS-03)

**Status:** 🟡 NEAR CONFORMITY | **Verification Target:** PAM unlock feedback and display sleep  
**Reference:** Official Apple WWDC25 macOS Tahoe Lock Screen capture (`2637×1712 px` Retina = `1512×982 pt`, scale 1.744 px/pt), Apple HIG

---

## 1. Apple Reference Specifications

### 1.1 Verified Dimensions on Native Screens
* **Date:** 27 pt, weight $\approx 560$, tracking $+0.29$, cap-height from top: **95.3 pt**. Color in `plus-lighter #646464` (additive luminance blend with wallpaper).
* **Clock:** 138 pt, weight $\approx 647$, tracking $-5.9$, top ink line at **132.2 pt**. Liquid Glass styling.
* **User Avatar:** **49 pt** diameter circle (bottom edge at 119 pt from screen foot).
* **User Name:** **15 pt**, weight $\approx 560$, pure white without shadow, baseline at **88.9 pt** from screen foot.
* **Unlock Prompt:** **12 pt** vibrant text (`plus-lighter #999999`), no bounding capsule in rest state, baseline at **59.0 pt** from screen foot.
* **Corner Status Icons (Top-Right):**
  * Input source: "U.S." 13 Regular
  * Keyboard glyph: 16.2×10 pt
  * Battery: 22.5×11.6 pt (translucent border) + terminal pole
  * Wi-Fi: 14.6×10.4 pt
  * Center line at 13.8 pt from top, 22.4 pt margin from right edge.

### 1.2 Layout Diagram
```
┌────────────────────────────────────────────────────────┐
│                                                        │
│                  [ Tuesday, Oct 4 ]                    │  ← 27 pt Date (plus-lighter)
│                                                        │
│                        09:41                           │  ← 138 pt Glass Clock
│                                                        │
│                         👤                             │  ← 49 pt Avatar
│                     User Name                          │  ← 15 pt Name
│             Touch ID or Enter Password                 │  ← 12 pt Vibrant Prompt
│                                                        │
│                                           🔋 🌐 ⌨️ U.S. │  ← Top-Right Status Extras
└────────────────────────────────────────────────────────┘
```

---

## 2. hyprmac Implementation Status

**Source:** `shell/hyprmac-lock` (GTK4 + Wayland `ext-session-lock-v1` + PAM) and `shell/lock.css`

### Working:
* ✅ Layout, positions, and font metrics configured 1:1 in pt (Retina matched).
* ✅ Additive vibrant typography (`VibrantLabel` with `CAIRO_OPERATOR_ADD` / `plus-lighter`).
* ✅ Interactive password capsule that appears dynamically when keystrokes are registered.
* ✅ Visual error feedback: password capsule shakes horizontally on invalid credentials.
* ✅ Multi-monitor support: one lock surface per connected Wayland output.
* ✅ Integration with `shell/ocioso/hyprmac-ocioso` for display sleep at 10 minutes and automatic screen locking.
* ✅ Wallpaper & lock appearance integration with `shell/hyprmac-ajustes` (clock weight, font styling).

---

## 3. Implementation Verification Checklist

- [x] Date positioned at 95.3 pt with `plus-lighter` additive rendering
- [x] Large clock rendered with variable SF Pro font weight
- [x] Avatar and username positioned with exact vertical baselines
- [x] Dynamic password shake animation on PAM authentication failure
- [x] Corner status glyphs (battery, Wi-Fi, input source) drawn in Cairo
- [ ] Direct credential verification and session unlock across multiple PAM profiles
