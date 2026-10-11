# Optimized Visual Index — Tahoe / hyprmac Knowledge Base

**Purpose:** Quick visual and architectural index for AI agents navigating macOS 27 / Tahoe design assets  
**Database:** `base.db` (SQLite FTS5, ~7,800 searchable snippets)  

> **Triagem de imagens:** use primeiro [`referencias/telas/CATALOGO-AGENTES.md`](referencias/telas/CATALOGO-AGENTES.md),
> `consultar.py --imagem` e os atlas em `referencias/telas/atlas/`. O catálogo
> informa categoria, estado, prioridade, dimensões, confiança e sequência;
> abra o original apenas para medir ou validar pixels.

---

## 🗂️ Document Map

### Level 1: Core Analysis
| Document | Purpose | Usage |
|---|---|---|
| **ANALISE-COMPLETA.md** | 360° overview: WWDC insights + components + gaps + invariants | Global architectural orientation |
| **VIDEO-INSIGHT-MACOS27.md** | Video analysis findings (1,000+ line transcript) | Feature verification and observed micro-behaviors |
| **EFEITOS-ANIMACOES-DETALHES.md** | Timing, inner glows, transitions, micro-interactions | Implementing precise visual feedback |

### Level 2: Target Gap Analyses
| Document | Area | Reference Frames |
|---|---|---|
| **GAPS-SIS01-DOCK.md** | Glass material, dimensions, P1 roadmap | `0020`, `0030` |
| **GAPS-SIS03-TELA-BLOQUEIO.md** | Lock screen, clock typography, PAM unlocking | Screenshots |
| **GAPS-SIS06-CAPTURAS.md** | Capture toolbar ⇧⌘5, screen recording | Tools |
| **GAPS-SIS07-APARENCIA.md** | Folder colors, window tinting, theme variants | `0100` |

### Level 3: Reference Documentation
| Directory | Content |
|---|---|
| **componentes/** | Menu bar, menus, Control Center, notifications, Dock, windows, controls, system features |
| **padroes/** | Liquid Glass, concentric geometry, colors, motion, shortcuts |
| **tokens/macos27/** | JSON & Markdown: 110 colors, 67 typography styles, 285 layer styles |
| **referencias/telas/** | 65 screenshots with agent catalog, JSON metadata, and triage atlases |
| **referencias/kit/** | UI kit layer outlines, 95 app icons, official wallpapers, SF Pro fonts |

---

## 🔍 How to Use This Index

### Scenario 1: "Implement Dock glass material"
```bash
1. Read: GAPS-SIS01-DOCK.md
2. Check: Frame 0020, 0030 (visual reference)
3. Query: ./ferramentas/consultar.py "dock material glass"
4. Metrics: referencias/kit/contornos/Menu_Bar_and_Dock.txt
```

### Scenario 2: "Check animation and glow timing"
```bash
1. Read: EFEITOS-ANIMACOES-DETALHES.md
2. Query: ./ferramentas/consultar.py "glow inset timing"
3. Verify: CSS transitions in shell/style.css
```

---

## 📐 Critical Reference Metrics

### Translucency & Glass Opacity (Liquid Glass)
| Element | Apple Reference | hyprmac Implementation | Code Reference |
|---|---|---|---|
| Dock | 0.05–0.15 | 0.22 (rest), 0.30 (hover) | `shell/style.css:98` |
| Control Center tiles | 0.05–0.15 | 0.22 (rest), 0.50 (active) | `shell/style.css:98` |
| Menus | 0.30–0.50 | 0.40–0.50 | `shell/style.css` |
| Menu Bar | 0.00 (translucent) | 0.00 | `waybar/style.css` |

### Radii (Concentric Geometry)
| Component | Radius (pt) | Notes |
|---|---|---|
| Windows | 16–22 pt | Continuous squircle (`rounding_power = 3.2`) |
| Notification Banners | 20 pt | Floating card |
| Popovers | 20 pt | Floating panel |
| Menus | 12 pt | Dropdown container |
| Menu hover highlight | 8 pt | Item capsule |
| Menu bar selection | 13 pt | Active item capsule |
| Dock | Continuous | Minimal blur backdrop |

### Typography (SF Pro)
| Element | Weight | Size | Usage |
|---|---|---|---|
| Menu bar items | Semibold 600 | 13 pt | Top bar menus |
| Active App name | Heavy 800–900 | 13 pt | Focused app in menu bar |
| Menu items | Medium 500 | 13 pt | Dropdown items |
| Apple logo | 20 pt font | 13×16 glyph | Apple menu trigger |

### Tahoe Color Palette
```
Blue:        #0088FF (Light), #0091FF (Dark) [Updated from #0A84FF]
Red:         #FF383C [Updated from #FF3B30]
Purple:      #AF52DE
Pink:        #FF2D55
Orange:      #FF9500
Yellow:      #FFD60A
Green:       #34C759
Gray/Labels: #A1A1A6
```

---

## 🎬 Key Video Frames

| Frame | Timestamp | Depicts | Key Observation |
|---|---|---|---|
| `0010` | ~00:01s | MacBook Pro + wallpaper | Scale, screen margins |
| `0020` | ~00:30s | Full Control Center | Glass tiles, sliders, sidebar layout |
| `0030` | ~00:45s | Multiple open windows | Squircle radii, Dock positioning |
| `0060` | ~01:15s | System Settings › General | Sidebar styling, form layout |
| `0100` | ~01:45s | Appearance Settings | Accent colors, icon styles (Default/Dark/Clear/Tinted) |

---

## 🔎 Query Commands

```bash
cd ~/Projects/hyprmac/BaseConhecimento

# Look up concept:
./ferramentas/consultar.py "liquid glass lensing"

# Look up metric:
./ferramentas/consultar.py "lock clock"

# Look up component specs:
./ferramentas/consultar.py "dock glass"

# Read gap analysis:
cat GAPS-SIS01-DOCK.md | less
```
