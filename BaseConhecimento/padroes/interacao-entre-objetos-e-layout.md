# Object Interaction, Layout Hierarchy, and Glass Dynamics

> Sources: Apple Developer Documentation (`dev/`) — [Applying Liquid Glass to custom views](../dev/applying-liquid-glass-to-custom-views.md), [Adopting Liquid Glass](../dev/adopting-liquid-glass.md), [GlassEffectContainer](../dev/glasseffectcontainer.md), [glassEffectUnion](../dev/glasseffectunion-id-namespace.md), [glassEffectID](../dev/glasseffectid-in.md), [GlassEffectTransition](../dev/glasseffecttransition.md); Apple HIG [layout](../hig/layout.md), [drag-and-drop](../hig/drag-and-drop.md), [toolbars](../hig/toolbars.md), [buttons](../hig/buttons.md); WWDC25 Sessions 219 and 356.

---

## 1. Glass on Glass: Containers, Fusion, Union, and Metamorphosis

In Liquid Glass, adjacent glass elements **communicate and visually interact**:

| Concept | Architectural Behavior | Practical Implementation Rule |
|---|---|---|
| **Container** (`GlassEffectContainer`) | Nested glass shapes are composited together in a single optical pass over the sampled backdrop. | Group related glass controls in a unified container to conserve GPU bandwidth. |
| **Proximity Fusion** (`spacing`) | When distance between perimeters $\le \text{spacing}$, shapes **fuse together like fluid droplets**. | If layout gap $\ge \text{spacing}$, shapes remain distinct; moving closer triggers dynamic necking/fusion. |
| **Union** (`glassEffectUnion(id:)`) | Disparate elements sharing the same ID merge into a **single continuous glass capsule** spanning them. | Shared background pill for segmented toolbars and media control groups. |
| **Metamorphosis** (`glassEffectID` + matched geometry) | An element appearing or dismissing within proximity emerges from and collapses into its neighbor. | A button seamlessly morphing into a menu or expanded slider panel. |
| **Materialization** (`materialize`) | Standalone elements appear by dynamically scaling lens refraction strength from zero. | Panels and menus expand and intensify lens refraction simultaneously rather than fading. |

### Interactive Micro-Behaviors:
* **Point-of-contact Illumination:** Internal glow originates under the pointer and radiates outward across adjacent glass elements.
* **Transient Control Glass:** Slider knobs and switches temporarily transform into clear Liquid Glass exclusively while being dragged.
* **Material Thickness:** Expanding glass surfaces (e.g., button morphing into menu) simulate thicker glass with deeper refraction.
* **No Glass-on-Glass Blur:** Overlaid controls use vibrancy fills and transparency, never an additional backdrop blur.
* **Focus States:** Unfocused windows visually recede with softened contrast and attenuated highlights.

---

## 2. Control Grouping & Toolbar Organization

* Group controls strictly by **functionality and usage frequency** on shared glass platters.
* **Never mix icons and text in the same shared capsule** (e.g., an icon alongside a text label looks like a single ambiguous button). Text buttons maintain distinct capsules.
* **Isolated Primary Actions:** Highlight critical triggers (e.g., blue "Done" button) with distinct tinted capsules.
* Buttons: Capsules in **horizontal rows**; rounded rectangles in **vertical stacks**.

---

## 3. Layout Guidelines (Apple HIG 2026)

* **Visual Hierarchy:** Critical commands placed top-left (reading order).
* **Progressive Disclosure:** Use disclosure triangles, menus, and nested views rather than crowding surfaces.
* **Differentiating Controls from Content:** Liquid Glass for navigation/controls; *scroll edge effect* softly dissolves content underneath.
* **Edge Safety (macOS):** Avoid placing primary triggers at the extreme bottom edge of windows (users frequently drag windows partly off-screen).
* **Concentric Radii:** All nested panels, cards, and buttons derive their radii from the parent container geometry.

---

## 4. Drag & Drop (HIG Standard)

* Drag preview appears after ~**3 pt** of movement.
* Drop targets provide visual drop highlights; invalid drop locations smoothly animate the item back to its origin.
* Multi-item selections display a circular count badge.
* *Spring loading*: Hovering over a directory or tab during a drag operation automatically opens it.

---

## 5. Linux Implementation Status (GTK3 + Hyprland)

| Apple HIG Paradigm | Linux / hyprmac Implementation | Status |
|---|---|---|
| Panel materialization from origin | Layer rule `popin 90%` + shell `emerge()` anchoring origin coordinates; `macPop` 320ms spring | Implemented (Control Center, Media Player, Tray Menus) |
| Dynamic animated resizing | `ScrolledWindow` animated height clip (`_animate_height`) | Implemented (Control Center Edit Mode) |
| Internal click glow | CSS `box-shadow: inset` on `:active` with instant 40ms attack and 260ms decay | Implemented in Control Center |
| Adjacent glow radiation | Propagate temporary highlight classes to neighbor widgets on click | Planned |
| Shared platter union | Group related controls on single glass platter (e.g., player transport controls) | Verified |
| Proximity fluid morphing | Distance-based metaball blending via NumPy SDF raymarching in Spotlight controls | Implemented in `SpotControls` |
| Inactive window recession | Hyprland `decoration.shadow.color_inactive` | Implemented |
