# Video Insights: macOS 27 Golden Gate

**Source:** Official feature reveal breakdown & 4K video analysis  
**Transcript:** `video/transcripr.txt`  
**Frames:** `video/frames2/` (199+ 4K frames)  
**Updated:** 2026-10-03  

---

## 🎯 Critical Discoveries

### 1. Liquid Glass — Transparency Slider
* Located in **Settings ▸ Appearance ▸ Liquid Glass**.
* Continuous slider adjusting glass intensity from **Fully Transparent** to **Frosted Glass**.
* Implies the glass opacity across the entire desktop environment is user-configurable rather than hardcoded.
* In hyprmac: Parametric alpha scaling across `shell/style.css`.

### 2. Show Borders — Accessibility Option
* Located in **Settings ▸ Accessibility ▸ Display ▸ Show Borders**.
* Injects a subtle 1px luminous stroke around menus, cards, and interactive UI surfaces.
* Dramatically enhances edge contrast when Liquid Glass is configured with high translucency.
* In hyprmac: Toggleable via `scripts/acessibilidade` and CSS class `.a11y-contrast`.

### 3. Integrated Window Canvas ("Floating Windows are Gone")
* Windows no longer appear detached with exaggerated drop shadows.
* Instead, window margins integrate tightly against screen bounds and the top menu bar (`gaps_in = 0`, `gaps_out = 0`).
* Liquid Glass reflections visually ground windows into desktop depth.

### 4. Control Center Architecture (Verified in Frame 0020)
* Left sidebar containing functional categories (Battery, Clock, Connectivity, Desktop, Display, Focus, Home).
* Central concentric tile grid featuring high-transparency glass surfaces.
* Sliders: Display slider in vibrant system blue (`#0088FF`), Sound slider in monochromatic light glass.
* Active status indicators: Circular capsules with solid white fills and blue iconography.

### 5. Native System Audio Recording
* Built-in support for capturing internal desktop audio without third-party loopback drivers.
* In hyprmac: Powered by PipeWire (`pw-record`) and `wf-recorder` via `scripts/gravacao`.

---

## 📐 Frame 0020 Technical Breakdown (Control Center)

```
┌─────────────────────────────────────────────────────────┐
│ SIDEBAR (Left)                          │ CENTRAL GRID  │
│ ┌──────────────────┐                    │ ┌───────────┐ │
│ │ Battery          │                    │ │Now Playing│ │
│ │ Clock            │                    │ └───────────┘ │
│ │ Connectivity     │                    │ ┌────┐ ┌────┐ │
│ │ Desktop & Finder │                    │ │Disp│ │Vol │ │
│ │ Display ✓        │                    │ └────┘ └────┘ │
│ └──────────────────┘                    │               │
│                                         │ [Done] Button │
└─────────────────────────────────────────────────────────┘
```

* **Translucency:** High background visibility with fine specular edge highlights.
* **Inner Glow:** Concentric inset shadow illuminating upon pointer activation.
