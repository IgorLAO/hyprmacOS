# Controls: Buttons, Toggles, Sliders, Fields, and Segmented Controls

> Sources: macOS 27 UI Kit layer outlines (*Buttons*, *Toggles*, *Sliders*, *Segmented Controls*, *Text Fields*, *Search Fields*, *Progress Indicators*), styles `Content Area/*` and `Over-Glass/*` ([estilos.md](../tokens/macos27/estilos.md)); Apple HIG [buttons](../hig/buttons.md), [toggles](../hig/toggles.md), [sliders](../hig/sliders.md), [segmented-controls](../hig/segmented-controls.md).

---

## macOS Control Sizing Standard
* Sizing scale: `mini` · `small` · **`regular`** · `large` · `x-large`.
* Small & Regular: Rounded rectangle.
* Large & Extra-Large: **Capsule geometry** (Extra-Large adopts Liquid Glass styling).

---

## Toggle Switches

| Size | Track Dimensions (pt) | Knob Capsule (pt) |
|---|---|---|
| Mini | 36×16 | 20×12 |
| Small | 44×20 | 26×16 |
| **Regular** | **54×24** | **32×20** (2 pt perimeter margin) |
| Large | 64×28 | 38×24 |
| X-Large | 80×36 | 48×32 |

* The knob in macOS 27 is **wider with glass styling**.
* Active / ON state: Track fills with system accent color; knob slides right with spring easing.

---

## Sliders
* Track height: **4 pt** capsule; filled portion reflects accent color; optional min/max flanking icons.
* Resting state: Clean, thin hairline.
* **Liquid Glass Interaction:** Dragging the slider dynamically transforms the knob into a magnified clear glass lens displaying the underlying track value.
* Center-biased variant: Fills outward symmetrically from the track center.

---

## Buttons & Interactive Platters
* Styles: **Bordered**, Bordered Tinted, Bordered Destructive, **Prominent** (solid system accent fill), Prominent Destructive.
* Over-Glass variants: Controls resting on glass surfaces adopt translucent fills rather than solid opacity.
* Standard push button height: **24 pt** (76×24 pt in modal dialogs).

---

## Search & Text Fields
* Background: Translucent subtle fill (`Fill 1/2`).
* Focus state: System accent focus ring.
* Search fields: Leading magnifying glass icon, trailing clear ("✕") trigger.

---

## Accessibility Invariant (Apple HIG)
System state must **never rely solely on color**: changes in state must always be accompanied by alterations in geometry, fill, position, or iconography.
