# Control Center

> Sources: Geometrically measured from official screens: `Apple-WWDC25-macOS-Tahoe-26-Control-Center-250609`, `Edit-Controls-in-macOS-Control-Center`, `macos-tahoe-home-screen`, `tahoe-dark` ([index](../referencias/telas/INDICE.md)); Apple HIG [controls](../hig/controls.md); macOS Tahoe release documentation.

---

## Grid Architecture
* 4-column concentric circle grid; gap $\approx \mathbf{0.2 \times \text{diameter}}$ (e.g., 104 pt diameter circle has a 21 pt gap).
* Standard control footprints:
  * **Small:** 1×1 circle.
  * **Medium:** 2×1 capsule (leading circular icon + title + state).
  * **Large:** 2×2 block (Now Playing, Home scenes).
  * **Wide:** 4×1 wide card (Display and Sound sliders).
* Default Tahoe configuration: Wi-Fi (Medium) · Now Playing (2×2) · Bluetooth · AirDrop · Focus (Medium) · Stage Manager · Screen Mirroring · Display (Wide) · Sound (Wide) · 4 Small controls (Dark Mode, Calculator, Timer, Screenshot) · **Edit Controls** pill button.

---

## Visual Styling & Materials
* Tiles rendered in **Clear Liquid Glass**: Translucent, tinted by wallpaper luminance, top ambient bevel specular highlight.
* **Active / Enabled State:** Solid **white circular background** with **blue icon glyph** (`#0088FF`). Disabled: Translucent glass circle with white icon glyph. Active timer: Glass tinted in system blue.
* **Medium Tile:** Left icon circle + **Semibold Title** + **State Sublabel** ("Home", "Off", "On").
* **Sliders (Final macOS Tahoe Specification — Measured in `tahoe-dark.jpeg`, 291×63.5 pt card):**
  * Semibold label positioned 16.5 pt from edge (8.5 pt cap-height).
  * **4 pt thin line without resting knob**, centered 42 pt from card top; filled in `#F8F8F8`, track is 10% black over glass.
  * Flanking SF Symbols **outside the track line**: `sun.min` / `sun.max` for brightness; `speaker.fill` / `speaker.wave.3.fill` for volume.
  * Sound card: AirPlay audio button (blue glyph inside 25.5 pt white circle) positioned on the right.
  * **Draggable Knob:** Floating capsule knob (20×16 pt) only appears when hovered or dragged (`osd-volume-arrastando.png`). Continuous squircle corners (~22 pt).
* **Now Playing:** Large album cover art in upper-left corner, track title, artist name, and playback transport buttons (◀◀ ▶ ▶▶). Empty state: Neutral gray card + "Not Playing".
* **Trigger Pill:** While Control Center is open, the menu bar toggle is enclosed in an active glass pill.

---

## Edit Mode (Tahoe)
* Clicking **"Edit Controls"**:
  * Each existing control reveals a **"−" badge in its top-left corner**.
  * Empty grid slots materialize as **dashed/ghost circles**.
* Opens the **Controls Gallery** alongside:
  * Search bar, category sidebar (All Controls, Battery, Clock, Connectivity, Display, Focus, Home, Notes, Now Playing, Shortcuts, Sound, Stage Manager, Utilities).
  * "Drag a control to place it in Control Center or Menu Bar…" + blue **Done** button.
* Reordering and resizing: Controls dynamically fuse or separate based on proximity.

---

## Optical Glass Calibration Curve (Measured 2026-10-04)

Cross-referenced across 5 references in light and dark modes:
$$\text{Tile Luminance} \approx 0.53 \cdot \text{Backdrop Luminance} + 58$$
* Over dark backgrounds, tiles softly illuminate; over bright backgrounds, tiles darken gently to preserve text contrast.
* In `hyprglass` (`preset hyprmac-central` in `hypr/vidro-presets.lua`):
  * **Brightness:** 1.0
  * **Contrast:** 0.61
  * **Saturation:** 1.7
  * **CSS Veil:** 5% translucent white (`shell/vidro-camadas.css`).
* Measured bevel values: Top +46, bottom +37, sides +28.
