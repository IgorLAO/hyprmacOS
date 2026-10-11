# Design Principles, Motion, Copywriting, and Menu Hierarchy

> Sources: Apple HIG [design-principles](../hig/design-principles.md), [motion](../hig/motion.md), [writing](../hig/writing.md), [menus](../hig/menus.md), [the-menu-bar](../hig/the-menu-bar.md), [popovers](../hig/popovers.md), [modality](../hig/modality.md), [panels](../hig/panels.md); WWDC25.

---

## Core HIG Design Principles

Purpose · User Agency (allow personalization, undo errors) · Responsibility (privacy) · **Familiarity** (standard mental models, visual consistency, unambiguous feedback) · Flexibility · **Simplicity** ("every element must earn its place") · **Craftsmanship** (pixel-level precision) · Delight (meaningful, non-gratuitous refinement).

---

## Motion & Animation Physics

* **Purposeful & Brief:** Animations must be cancelable; never block user input while waiting for transitions.
* **Realistic Trajectories:** Follow physical gestures (panels dropping from the top retreat back to the top).
* **Liquid Glass Dynamics:**
  * Surfaces **materialize from their origin element** by modulating lens refraction rather than simple alpha cross-fades.
  * Click interactions illuminate the internal glass volume from the point of contact.
  * Transitions between modes morph continuously on the same floating plane.
  * Modals and popovers animate height/width changes smoothly.
* **Selection Flash:** In native macOS menus, selecting an item triggers a quick double-flash (~60ms off, ~60ms on) before the menu dismisses.

### Measured Curves & Timings in hyprmac
| Motion | Curve & Duration |
|---|---|
| Panel Reveal (Control Center, Media Player, Banners) | Cubic bezier `macPop` `(0.2, 1.08, 0.32, 1)` with subtle end flex — **320 ms**; expands from **90%** scale anchored to origin coordinates |
| Panel Dismissal | Cubic bezier `macOut` `(0.4, 0, 1, 1)` — **160 ms** (snappy, zero lag) |
| Panel Dimension Resize | Cubic ease-out — **250 ms** |
| Workspace Slide | `macSlide` `(0.25, 1, 0.5, 1)` — 420 ms |
| Interactive Click Glow | 40 ms attack, 260 ms release |
| Reduce Motion Override | `enable-animations = false` forces linear cross-fade with zero spring bounce |

---

## Copywriting & Interface Text

* **Clarity:** Direct, concise language; action-oriented verbs on buttons; eliminate conversational filler and redundant possessives ("my/your").
* **Title Case:** All menu items and buttons follow English Title Case without articles. Append "…" exclusively when an action requires further user input before taking effect.
* **Inline Error States:** Display error guidance directly adjacent to the relevant control with actionable resolution steps.
* **Meaningful Empty States:** Provide context and the next logical action.

---

## Menu Bar Architecture (macOS Standard)

### Menu Bar Hierarchy
1. **Apple Menu (``)**: System-wide global commands.
2. **App Menu (Bold Application Name)**: About, Settings… (`⌘,`), Services, Hide (`⌘H`), Hide Others (`⌥⌘H`), Show All, Quit (`⌘Q`).
3. **Standard Menus**: `File` · `Edit` · `Format` · `View` · `[App-Specific Menus]` · `Window` · `Help`.
4. **Edit Menu Items**: Undo · Redo | Cut · Copy · Paste · Paste and Match Style · Delete · Select All | Find | Spelling & Grammar · Substitutions · Transformations · Speech · Emoji & Symbols.
5. **View Menu Items**: Show/Hide Tab Bar, Toolbar, Sidebar · Enter/Exit Full Screen (labels toggle based on current state).
6. **Window Menu**: Minimize (`⌘M`) · Zoom | tabs | **Bring All to Front** | Alphabetical open window list.
   *(Note: Close Window belongs in File; fullscreen belongs in View).*

### Menu Interaction Invariants
* Visible shortcut glyphs aligned to the right edge.
* Unavailable actions remain visible but dimmed (subdued gray).
* Checkmarks (`✓`) denote active mutually exclusive or toggled states.
* Top bar extras (tray items) open **menus**, not arbitrary dialogs or popovers.
* Right-click context menus: Unavailable items are omitted entirely rather than dimmed; shortcuts are hidden.

---

## Popovers, Panels, and Modals

* **Single Popover Rule:** Only one popover or menu may be open at any time. Clicking outside or selecting an option dismisses the active popover immediately.
* **Origin Anchoring:** The popover arrow points directly to its source element without obscuring it.
* **Modality:** Reserve modal sheets for short, focused interrupting tasks. Provide clear cancel buttons and apply a 35% background dimming veil.
