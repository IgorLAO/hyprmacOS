# Liquid Glass on Hyprland (hyprglass) — Architecture and Usage

> Validated on 2026-10-03 on Hyprland **0.56.2** with hyprglass **v0.9.0**.  
> Related Design Tokens: [liquid-glass.md](liquid-glass.md). Apple Technical Reference: WWDC25 Sessions [219](../hig/wwdc/219-meet-liquid-glass.txt) and [356](../hig/wwdc/356-new-design-system.txt).

---

## ⚡ Quick Reference

```bash
~/Projects/hyprmac/scripts/vidro instalar     # Compiles hyprglass against matching Hyprland tag (~20s)
~/Projects/hyprmac/scripts/vidro carregar     # Loads plugin + applies layer rules and window whitelist
~/Projects/hyprmac/scripts/vidro lab          # Interactive laboratory: floating GTK4 window with live sliders
~/Projects/hyprmac/scripts/vidro status       # Displays loaded version, tag, and .so path
~/Projects/hyprmac/scripts/vidro descarregar  # Unloads the hyprglass plugin
```

### Python API Integration
```python
import sys; sys.path.insert(0, "/home/igor/Projects/hyprmac/shell")
import vidro

vidro.garantir()                                  # Ensures plugin is compiled & loaded
vidro.janela("dev.hyprmac.Target", preset="pomme") # Binds glass shader to window class/app_id
vidro.config(refraction_strength=1.4)             # Sets live global shader parameters
```

*Note: Changes applied dynamically via `vidro.py` do not overwrite `hyprland.lua` or `hyprmac.lua`. They persist until compositor restart or explicit reload.*

---

## 💎 The Golden Optical Rule: Glass Behaves Identically in Light and Dark Modes

Measured directly in `referencias/telas/tahoe-dark.jpeg`, native Control Center screens, `osd-volume-arrastando.png`, and `cc-edicao-galeria-sobre-azul.png`:

* **Luminance and Saturation Tracking:** Real Liquid Glass maintains roughly the same luminance as the backdrop while dramatically increasing saturation.
  * Over dark backdrops, it softly lifts brightness (Finder 34 → ~65).
  * Over pure white backdrops (luminance > 0.90), it darkens moderately for contrast (242 → 153–208 via `adaptive_dim = 0.32`).
* **Never apply heavy dark gray fills:** Solid dark grays kill background vibrancy. CSS layers apply a minimal veil of 4–5% opacity (just above the shader `mask_threshold = 0.025`).
* **Kit "Dark" tokens** (`Liquid Glass/Dark/*`) use a *luminosity* blend mode: they compress contrast toward the midpoint rather than painting an opaque dark color.
* **Control Surfaces (Control Center, OSD, Spotlight):** Use preset `hyprmac-painel` — bright, saturated glass with `adaptive_dim = 0.30` reserved for white content.
* **Spotlight & Text Panels:** In light mode, measures ~60% tinted white; in dark mode, uses preset `hyprmac-texto` with placeholder `#FFFFFF8C`.

---

## 🔍 Why GTK Alone Cannot Render Liquid Glass

1. **GTK Lacks `backdrop-filter`:** GTK CSS cannot sample or refract pixels beneath a window. Setting `background-color: rgba(...)` only yields flat translucency.
2. **The Compositor Samples the Backdrop:** Hyprland's native renderer only supports flat Dual-Kawase blur (`decoration.blur`). It does **not** simulate optical refraction, Fresnel reflections, or specular bevels.
3. **The Solution:** The **[hyprglass](https://github.com/hyprnux/hyprglass)** plugin implements a custom Wayland window/layer decorator rendering optical refraction shaders over sampled backdrops.
4. **Architectural Separation:** GTK applications remain completely transparent where glass should appear; Hyprland and `hyprglass` render the continuous squircle corners, lens refraction, and lighting highlights.

---

## 🍎 Apple Optical Model (Measured from iOS 27 / macOS Tahoe)

From WWDC25 Session 219 ("Meet Liquid Glass") and reverse-engineering research:

| Optical Layer | Apple Behavior |
|---|---|
| **Lensing / Refraction** | Bends light at geometry perimeters, defining shapes without muddying contrast. |
| **Specular Bevel Highlights** | Environment lights illuminate surface geometry; reflections travel along contours during interaction. |
| **Adaptive Shadow** | Dense and legible over text; subtle and diffused over bright flat backdrops. |
| **Adaptive Tinting** | Translucent tint dynamically tracks background dynamic range. |
| **Internal Glow** | Elements illuminate from within upon click or touch. |
| **Materialization** | Elements enter and exit by modulating lens curvature rather than linear alpha fading. |

### Mathematical Formulation
* **Quarter-circle bevel curve:** $\text{offset} = \text{amount} \cdot (1 - \sqrt{1 - x^2})$, where $x = 1 - d / \text{height}$ ($d$ = distance to boundary).
* **Regular Glass & Buttons:** Height 20 pt, displacement amount 60 pt.
* **Zero Chromatic Dispersion:** Red, green, and blue wavelengths refract uniformly. (Faux rainbow effects are avoided).

---

## 🛠️ Patch histórico: `forma-pela-mascara.patch`

> Estado em 2026-10-10: o arquivo foi removido do checkout antes da
> consolidação. A cópia abaixo preserva a proposta para investigação, mas
> `scripts/vidro` não a aplica no estado atual. As capacidades desta seção
> não devem ser tratadas como verificadas no runtime.

In the standard upstream `hyprglass` plugin, LayerShell surfaces are treated as a single bounding rectangle (radius 0), blurring entire windows.

O [patch arquivado](../historico/legado-operacional-20261010/forma-pela-mascara.patch) propunha:
1. **Alpha Mask SDF Raymarching:** Measures distance to the nearest transparent pixel across 16 radial directions with bisection search. Every opaque widget inside a transparent surface becomes its **own distinct optical glass object**.
2. **Quarter-Circle Bevel Optics:** Matches Apple's measured formula ($1 - \sqrt{1 - x^2}$).
3. **Popup Support for Menus:** Intercepts popup surfaces (`waybar:popups`, `hyprmac-menu:popups`), enabling true optical glass on dropdown menus.
4. **Window Shape Protocol:** Supports passing explicit squircle coordinates (`hyprctl hyprglass shape <address> x,y,w,h,r`) for native multi-pane glass layouts (used by `hyprmac-ajustes`).
5. **Animation Synchronization (Materialize):** Hooks into surface appearance uniforms (`appear`), animating lens refraction alongside spring scale transitions.
6. **Glyph Preservation:** Strokes thinner than 7 px are excluded from bevel distortion, preventing text labels from getting warped.

---

## 📋 Layer Assignment in `hypr/vidro-presets.lua`

| Layer Namespace | Preset | `mask_threshold` |
|---|---|---|
| Control Center (`hyprmac-cc`) & Gallery (`hyprmac-cc-gallery`) | `hyprmac-painel` | 0.04 (tiles at 0.06 alpha) |
| Notification Center (`hyprmac-nc`), Media Player (`hyprmac-media`), AppSwitcher (`hyprmac-switcher`) | `hyprmac-painel` | 0.15 |
| Spotlight (`hyprmac-spotlight`), Clipboard (`hyprmac-clipboard`) | `hyprmac-painel` | 0.35 |
| Notifications (`hyprmac-notifications`), Volume/Brightness OSD (`hyprmac-osd`) | `hyprmac-pequeno` | 0.15 |

---

## 🧪 Interactive Laboratory (`scripts/vidro lab`)

Launch the floating GTK4 laboratory window:
```bash
~/Projects/hyprmac/scripts/vidro lab
```
* **Sliders:** Adjust lens refraction, specular highlights, bevel angles, and blur in real time.
* **Drop-Down:** Switch between official Apple UI Kit fill recipes.
* **Auto-Save:** Closing the lab writes values to `~/.config/hyprmac/glass-lab.json` and prints the `hg.preset(...)` configuration ready for production use.
