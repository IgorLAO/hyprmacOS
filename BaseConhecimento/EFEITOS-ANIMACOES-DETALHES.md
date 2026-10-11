# Visual Effects, Animations, and Micro-Interactions: macOS Tahoe / 27

**Focus:** Optical feedback, fluid timing curves, and Liquid Glass micro-interactions.  
**Sources:** WWDC25 Session 219 ("Meet Liquid Glass"), 4K video frame analysis, and `shell/style.css`.  
**Updated:** 2026-10-03  

---

## 🎬 Core Animations & Timing Curves

### 1. Window Materialization & Dematerialization
* Windows in macOS Tahoe avoid abrupt opacity cuts.
* Instead, windows materialize and dematerialize smoothly via subtle scale and opacity transitions, giving the perception that the surface is synthesized from ambient light.
* **Duration:** ~250–320ms spring curve (`macPop`).
* **Hyprland Configuration:** Handled via custom bezier curves in `hypr/hyprmac.lua`.

### 2. Menu Bar Capsule Selection
* Hovering or activating top menu bar items highlights the item inside an elongated capsule (13 pt radius).
* **Color shift:** Transitions from standard white (70%) to active pill background (`rgba(255, 255, 255, 0.18)`).
* **Timing:** `transition: background-color 160ms ease-out, color 160ms ease-out;`.

### 3. Window Traffic Lights (Stoplight Hover)
* Standard state: Flat colored circles (Close `#FF5C60`, Minimize `#FAC800`, Zoom `#35C759`).
* Hover state: Inactive monochrome symbols (`×`, `−`, `+`) appear inside the circles with a subtle edge glow.

### 4. Liquid Glass Inner Specular Glow ("Illuminates from Within")
* Apple HIG explicitly describes Liquid Glass interactive states as "illuminating from within".
* Implemented via inset lighting shadows:
```css
/* Standard Rest */
box-shadow: inset 0 1px 1px rgba(255, 255, 255, 0.22),
            inset 0 -1px 1px rgba(0, 0, 0, 0.04);
transition: background-color 160ms ease-out, box-shadow 260ms ease-out;

/* Active Press */
box-shadow: inset 0 0 18px rgba(255, 255, 255, 0.34),
            inset 0 1px 1px rgba(255, 255, 255, 0.30);
transition: background-color 40ms ease-out, box-shadow 40ms ease-out;
```

### 5. Scroll Edge Fading
* Scrollable containers (such as System Settings sidebar or long dropdown menus) apply a linear mask fade at the top and bottom scroll boundaries rather than an abrupt hard cut.
* Implemented via CSS mask-image gradients or GTK overlay fading.

---

## 🎨 Lighting & Bevel Highlights

1. **Top Specular Edge:**
   `border-top: 1px solid rgba(255, 255, 255, 0.55);`
   Simulates light striking the top chamfer of the glass plane.
2. **Side Edges:**
   `border-left: 1px solid rgba(255, 255, 255, 0.18);`
   `border-right: 1px solid rgba(255, 255, 255, 0.18);`
3. **Bottom Ambient Shadow:**
   `border-bottom: 1px solid rgba(255, 255, 255, 0.08);`
   `box-shadow: inset 0 -1px 1px rgba(0, 0, 0, 0.04);`
