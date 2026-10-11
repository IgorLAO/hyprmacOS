# Sources & Data Origins

**Origin:** User provided materials, `developer.apple.com` (HIG in JSON, WWDC25 videos), and official Apple Design Resources.  
**Processed on:** 2026-10-02.

---

## 📦 Ingested Sources

| Source | Description | Location in Knowledge Base | Ingestion Method |
|---|---|---|---|
| `Apple macOS 27 UI Kit/` (+ `.sketch`) | Official Apple Design Resources kit, Sketch 2026.2, v27.0.1 | `tokens/macos27/`, `referencias/kit/` | `extrair_kit.py`, `contorno_kit.py`; symbols and layers extracted |
| `VisionUIs/` | Official visionOS UI kit (Sketch 2025.2) | `tokens/visionos/`, `referencias/kit-visionos/` | Same parser |
| `* _ Apple Developer Documentation.html` (14) | Saved HIG pages | `hig/*.md` + `hig/imagens/` | `html_hig.py` (titles parsed from `<h1>`) |
| `developer.apple.com …/human-interface-guidelines/<page>.json` | Complete HIG JSON dumps | `hig/*.md` | 38 pages ingested via parser |
| WWDC25 sessions 219 and 356 | Transcripts for "Meet Liquid Glass", "Get to know the new design system" | `hig/wwdc/` | Video transcript parsing |
| `All_New_Features_macOS_Tahoe_Sept_2025.pdf` | Official Tahoe new features publication | `referencias/pdfs/novidades-macos-tahoe.txt` | `pdftotext -layout` |
| `Tahoe-Course-Companion-Book.pdf` | MacMost Tahoe course guide (72 pages) | `referencias/pdfs/tahoe-course-companion.txt` | `pdftotext` with ligature normalization |
| `macOS-pour-les-Utilisateurs-de-Windows.pdf` | Visual presentation slides | `referencias/pdfs/macos-pour-windows/p-*.jpg` | `pdftoppm -r 75` |
| `developer.apple.com …/tutorials/data/documentation/<path>.json` (DocC) | *Applying Liquid Glass to custom views*, *Adopting Liquid Glass*, `GlassEffectContainer`, `glassEffectUnion`, `glassEffectID`, `GlassEffectTransition`, `NSGlassEffectContainerView`, *Landmarks* | `dev/*.md` | `ferramentas/docc_md.py` |
| HIG `layout.json` and `drag-and-drop.json` | Updated Layout and Drag & Drop guidelines | `hig/layout.md`, `hig/drag-and-drop.md` | `ferramentas/docc_md.py` |
| `Apple_HIG_Quick_Index.md` | Third-party HIG summary | `referencias/pdfs/` | ⚠️ Metrics represent **iOS** (Body 17pt); macOS uses kit metrics |
| `Apple macOS 27 UI Kit/fonts/` | SF Pro (variable fonts, all weights) and SF Pro Rounded Medium | `referencias/kit/fontes/` | Ingested for local personal desktop use; family = "SF Pro" |
| [hyprglass](https://github.com/hyprnux/hyprglass) v0.9.0 + reverse engineering research | Hyprland glass shader plugin; optical model measured from iOS 27 | `padroes/liquid-glass-hyprland.md` | Shader analysis and custom mask patch |
| 18 UI Screenshots (jpg/webp/avif) | Official Tahoe UI screenshots | `referencias/telas/` + `INDICE.md` | Converted to `.jpg` / indexed |

---

## 🚫 Excluded Items (Non-UI Materials)
- Personal media, movies, and video games.
- High-res uncompressed 16-bit wallpaper TIFFs (converted to 93% quality JPGs).

---

## ⚠️ Known Gaps & Inferences
- The official Sketch kit **does not contain** Control Center, Spotlight, lock screen, or desktop widgets; those measurements are geometrically derived from 4K retina screenshots.
- Color tables in HIG documentation are rendered as images; authoritative hexadecimal and RGBA values are extracted directly from the Sketch kit styles.
