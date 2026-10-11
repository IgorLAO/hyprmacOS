# Gap Analysis (P3): Screen Capture Toolbar ⇧⌘5 (SIS-06)

**Status:** ✅ CONFORMANT / REFINED  
**References:** Apple HIG, macOS Tahoe screen capture references, `scripts/captura`, `scripts/captura-miniatura`, `scripts/gravacao`

---

## 1. Apple Reference Specifications

### 1.1 Complete Capture Suite (⇧⌘5)
Invokes a floating segmented glass toolbar with interactive options:
* **Capture Entire Screen**: Captures active display.
* **Capture Selected Window**: Interactive window target selection.
* **Capture Selected Portion**: Marquee region selection.
* **Record Entire Screen / Selected Portion**: Video recording with status indicator.
* **Options Dropdown**: Destination folder (Desktop, Documents, Clipboard), timer (None, 5s, 10s), show mouse pointer, microphone toggle.

### 1.2 Floating Preview Thumbnail
* Appears immediately in the bottom-right corner upon capture.
* Persists for 5 seconds with fluid slide-in animation.
* **Click**: Opens default image editor / markup tool.
* **Drag-and-Drop**: Allows dragging directly onto applications, web browsers, or directories.
* Auto-dismisses smoothly after timeout.

### 1.3 Standard Keyboard Shortcuts
* `⇧⌘3`: Fullscreen capture.
* `⇧⌘4`: Interactive region selection (Space toggles window capture).
* `⇧⌘5`: Interactive capture and screen recording toolbar.
* Modifier `⌃`: Copies directly to clipboard rather than saving to disk.

---

## 2. hyprmac Implementation Status

**Source:** `scripts/captura`, `scripts/captura-miniatura`, `scripts/gravacao`

### Implemented:
* ✅ Fullscreen capture (`⇧⌘3`) and region capture (`⇧⌘4`).
* ✅ Floating thumbnail preview with timeout and click actions (`scripts/captura-miniatura`).
* ✅ Floating ⇧⌘5 capture bar matching native dimensions and glass aesthetics.
* ✅ Screen recording powered by `wf-recorder` (`scripts/gravacao`).
* ✅ Clipboard and file destination routing.
