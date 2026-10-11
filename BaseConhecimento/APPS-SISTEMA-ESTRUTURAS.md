# System Apps and Structural Layouts: macOS Tahoe / 27

**Focus:** System Settings, Finder, Mail, Notes, and structural navigation layouts.  
**Sources:** Video frames 0060, 0100, 0110, Apple HIG, `shell/hyprmac-ajustes`.  
**Updated:** 2026-10-03  

---

## 🏗️ Structural Pattern #1: Modern System Settings Layout

### Sidebar Navigation Architecture
* Permanent **left sidebar** organizing all settings domains.
* Sidebar items feature rounded colored iconography + text labels.
* Active selection: High-contrast pill highlight (`#0088FF` background or active gray pill with white text).
* Main content panel updates fluidly based on active selection without window-level flashing.

### Sidebar Categories
```
📱 Wi-Fi
🔵 Bluetooth
🌐 Network
🔋 Battery
⚙️ General
♿ Accessibility
🎨 Appearance
📋 Menu Bar
🧠 Apple Intelligence & Siri
🖥️ Desktop & Dock
🖥️ Displays
🔍 Spotlight
🖼️ Wallpaper
🔔 Notifications
🔊 Sound
🌙 Focus
⏱️ Screen Time
```

---

## 🎨 Structural Pattern #2: Appearance Preferences Panel

### Appearance Sections
1. **Theme Mode:** Visual miniatures representing Auto / Light / Dark modes.
2. **Accent Color:** Multicolor, Blue, Purple, Pink, Red, Orange, Yellow, Green, Graphite.
3. **Highlight Color:** Accent-aligned selection highlight.
4. **Icon and Widget Style:** Default, Dark, Clear, Tinted.
5. **Folder Color:** Automatic or custom tint selector.
6. **Window Tinting:** "Tint window background with wallpaper color" toggle.
7. **Scroll Bars:** Automatically based on mouse/trackpad, When scrolling, Always.

---

## 🗃️ Structural Pattern #3: Finder & File Management

### Core Visual Invariants
* **Unified Header:** Seamless title bar merging window controls, segmented navigation capsules (`‹ ›`), and search.
* **Floating Sidebar:** Translucent material with clear section headers (*Favorites, iCloud, Locations, Tags*).
* **View Modes:** Icons, List, Columns, and Gallery.
* **Alternating Row Fills:** List view uses subtle alternating row shades in dark mode.
* **Metadata Tags:** Circular color dots identifying file tags.
