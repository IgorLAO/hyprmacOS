# Gap Analysis (P3): Customizable Appearance (SIS-07)

**Status:** 🟡 NEAR CONFORMITY  
**References:** Apple HIG, macOS Tahoe appearance screenshots (`clear-dark-1.webp`, `dark-icons-widgets`), `scripts/accent`, `scripts/theme`, `shell/hyprmac-ajustes`

---

## 1. Apple Reference Specifications

### 1.1 System Settings ▸ Appearance
* **Appearance Mode:** Auto / Light / Dark (scheduled or manual override).
* **Accent Color:** 9 options (Multicolor, Blue `#0088FF`, Purple `#AF52DE`, Pink `#FF2D55`, Red `#FF383C`, Orange `#FF9500`, Yellow `#FFD60A`, Green `#34C759`, Graphite `#A1A1A6`).
* **Highlight Color:** Selection highlight conforming to chosen accent.
* **Icon and Widget Style:** Default / Dark / Clear / Tinted.
* **Folder Color:** Continuous spectrum or palette of custom folder hues.
* **Window Tinting:** "Tint window background with wallpaper color" toggle, softly bleeding ambient desktop luminance into glass containers.

### 1.2 Icon & Widget Variants
1. **Default:** Standard full-color iconography.
2. **Dark:** Desaturated dark mode variants designed for low-light legibility.
3. **Clear:** Frosted translucent monochromatic glass finish.
4. **Tinted:** Monochromatic icons tinted with the system's selected accent color.

---

## 2. hyprmac Implementation Status

**Source:** `scripts/accent`, `scripts/theme`, `shell/hyprmac-ajustes`, `shell/hyprmac-shell`

### Working:
* ✅ System Light / Dark mode toggling via `scripts/theme`.
* ✅ 8 system accent colors applied across GTK 3/4, Waybar, Wofi, and shell CSS.
* ✅ Icon & widget style switching (Default, Dark, Clear, Tinted) rendered in Cairo for Dock icons and via CSS classes for widgets.
* ✅ Settings UI panel in `hyprmac-ajustes` mirroring macOS Tahoe Appearance preferences.
* ✅ Folder color picker in `hyprmac-ajustes` (options: Automatic, 8 kit colors, custom color).

### Pending Polish:
* [ ] Propagating selected folder color down to file managers (nautilus/Nautilus icon emblems).
* [ ] Dynamic window background tinting derived from active wallpaper color.
