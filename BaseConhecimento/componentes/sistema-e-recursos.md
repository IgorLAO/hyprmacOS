# System Features: Spotlight, Widgets, Lock Screen, Multitasking, Captures, and Cursors

> Sources: macOS Tahoe release notes, *Tahoe Course Companion*, Apple HIG [widgets](../hig/widgets.md), [searching](../hig/searching.md), [multitasking](../hig/multitasking.md), [going-full-screen](../hig/going-full-screen.md), [app-icons](../hig/app-icons.md).

---

## Spotlight (`⌘Space`)
* Invokes a floating glass capsule; queries across applications, files, settings, and web simultaneously.
* **Modes:**
  * `⌘1` **Apps** (Categorized application launcher replacing legacy Launchpad).
  * `⌘2` **Files** (Recent files and suggested documents).
  * `⌘3` **Actions** (System actions, menu bar items, Shortcuts).
  * `⌘4` **Clipboard** (Clipboard history of text, images, and links copied over the last ~8 hours).
  * `→` (right arrow) cycles through modes 1 to 4 sequentially.
* `↑` recalls search query history; supports instant inline mathematical evaluation (e.g. `5+5 = 10`), filter tokens, and quick action abbreviations (`em` for message, `al` for reminder).

---

## Desktop Widgets
* Footprints: Small, Medium, Large, Extra-Large.
* Rest behind windows and **fade to low contrast** when windows are focused over them.
* Edit Mode: Right-click desktop ▸ Edit Widgets (category gallery, search, add/remove controls).
* Widget Styles: Default, Dark, **Clear** (translucent frosted glass), Tinted.

---

## Lock Screen
* Small date banner at top, **large variable-weight glass clock** (`Lock Screen Time` style), selectable font styles (6 variations).
* Avatar + Username + "Touch ID or Enter Password" positioned at bottom; essential corner status indicators (keyboard layout, battery, Wi-Fi).

---

## Multitasking & Window Management
* **Mission Control (`⌃↑`):** Top desktop workspace strip with `+` trigger, spread window expose.
* **App Exposé (`⌃↓`)**, Split View, Fullscreen (`⌃⌘F`).
* Application hiding (`⌘H`) is preferred over minimizing (`⌘M`).
* Tiling: Dragging windows to screen edges; `Window ▸ Move & Resize`; `⌃⌥F` to fill screen.

---

## Screen Captures & Recording
* `⇧⌘3` Fullscreen capture.
* `⇧⌘4` Interactive region selection (Space toggles window capture).
* `⇧⌘5` Floating toolbar: Fullscreen, Window, Selection, Video Recording with audio, timer options, and show cursor toggle.
* Floating thumbnail preview in the lower-right corner enables quick drag-and-drop.
* Holding `⌃` copies directly to clipboard.

---

## System Appearance (Settings ▸ Appearance)
* Auto / Light / Dark modes · System accent colors (Multicolor + 8 palette colors) · Text highlight color.
* **Icon & Widget Styles:** Default / Dark / Clear / Tinted.
* **Folder Colors:** Continuous hue spectrum and tag markers.
* Wallpaper tinting toggle for window backgrounds.

---

## System Cursors & Wallpapers
* Official macOS SVG cursors available in `referencias/kit/ponteiros/` (pointer, hand pointing/open/closed, text I-beam, resize axes, beachball).
* Official macOS 27 wallpapers (Light and Dark) stored in `referencias/kit/papeis-de-parede/` (default Tahoe blue wave).
