# Colors, Vibrancy, and Typography

> Sources: macOS 27 UI Kit → [tokens/macos27/cores.md](../tokens/macos27/cores.md), [tipografia.md](../tokens/macos27/tipografia.md); Apple HIG [color](../hig/color.md), [dark-mode](../hig/dark-mode.md), [typography](../hig/typography.md).

---

## Destaques AppKit verificados no Tahoe 26.6.1

`controlAccent*Color` de `SystemAppearance.bundle/{Aqua,DarkAqua}.car`, build
25G76, árvore BOM COLORS em ordem BGRA. Valores conferidos com o dump local:

| Destaque | Claro | Escuro |
|---|---|---|
| Blue | `#007AFF` | `#007AFF` |
| Purple | `#953D96` | `#A550A7` |
| Pink | `#F74F9E` | `#F74F9E` |
| Red | `#E0383E` | `#FF5257` |
| Orange | `#F7821B` | `#F7821B` |
| Yellow | `#FFC726` | `#FFC600` |
| Green | `#62BA46` | `#62BA46` |
| Graphite (`controlAccentNoColor`) | `#989898` | `#8C8C8C` |

Implementação compartilhada: `shell/accent_palette.py`. GTK, Ajustes, menu do
shell e Mission Control usam essa tabela. Hover e seleção derivados continuam
aproximações locais. A inspeção estática dos assets não comprova qual variante
cada controle usa em runtime. Proveniência no SQLite: `tahoe26:cores:controlaccentblue`.

## Tokens semânticos AppKit Tahoe 26.6.1

| Token | Claro (Aqua) | Escuro (DarkAqua) |
|---|---|---|
| windowBackgroundColor | #ECECEC | #323232 |
| labelColor | preto / 216÷255 | branco / 216÷255 |
| secondaryLabelColor | preto / 127÷255 | branco / 140÷255 |
| tertiaryLabelColor | preto / 66÷255 | branco / 63÷255 |
| keyboardFocusIndicatorColor | #3B99FC | #25ADFF / 127÷255 |

Origem: mesma árvore COLORS/BGRA do build 25G76. Aplicados às paletas GTK3/4,
variáveis libadwaita e anel de foco; a largura do anel permanece uma escolha local.
Texto vibrante sobre vidro tem outra composição e não é certificado por esses tokens.

## System Colors (kit macOS 27; referência secundária)

| Color Name | Light | Dark | Dark Vibrant (*plus-lighter*) | Light Vibrant (*plus-darker*) |
|---|---|---|---|---|
| Red | `#FF383C` | `#FF4245` | `#FF4747` | `#F52F32` |
| Orange | `#FF8D28` | `#FF9230` | `#FF9E33` | `#F58625` |
| Yellow | `#FFCC00` | `#FFD600` | `#FFE014` | `#F5C200` |
| Green | `#34C759` | `#30D158` | `#3BDB63` | `#26BF4D` |
| Mint | `#00C8B3` | `#00DAC3` | `#2DE0CD` | `#00BDA9` |
| Teal | `#00C3D0` | `#00D2E0` | `#2DD7E0` | `#00B3BF` |
| Cyan | `#00C0E8` | `#3CD3FE` | `#47D8FC` | `#00ABCF` |
| **Blue** | **`#0088FF`** | **`#0091FF`** | `#0A99FF` | `#0078F0` |
| Indigo | `#6155F5` | `#6D7CFF` | `#7163FF` | `#5C50E6` |
| Purple | `#CB30E0` | `#DB34F2` | `#E647FC` | `#B72BC9` |
| Pink | `#FF2D55` | `#FF375F` | `#FF4169` | `#F5234B` |
| Brown | `#AC7F5E` | `#B78A66` | `#C29672` | `#9E7354` |
| Gray | `#8E8E93` | `#98989D` | `#A2A2A7` | `#848489` |

### Specific Component Colors:
* **Menu item selection pill:** **`#0069F9`** (deeper accent blue), white text.
* **Window Stoplight:** Close `#FF5C60`, Minimize `#FAC800`, Zoom `#35C759` (0.5px border `#00000073`); Inactive `#00000026`.
* **Destructive Alert Button:** Red fill at 25% (*plus-lighter*), text `#FF4747` (Dark) / `#F52F32` (Light).
* **Privacy Indicators:** Camera = **green** capsule; Microphone = orange capsule; Screen = purple capsule.
* **Calendar "Today" dot & month title:** Red.

> Não confundir cores semânticas `system*Color` deste kit com os destaques
> `controlAccent*Color` do Tahoe 26. `#007AFF` permanece nos assets AppKit verificados.

---

## Labels, Fills, and Separators (kit 27; secundário)

| Design Token | Light Mode | Dark Mode |
|---|---|---|
| Label 1 (Primary) | `#000000D9` (85%) | `#FFFFFF` (Vibrant `#FFFFFFFA` 96%) |
| Label 2 (Secondary) | `#00000080` (50%) | `#FFFFFF8C` (55%) |
| Label 3 (Tertiary) | `#00000040` (25%) | `#FFFFFF40` (25%) |
| Label 4 (Quaternary) | `#0000001A` (10%) | `#FFFFFF1A` (10%) |
| Separator | `#3C3C434A` (29%) | Vibrant `#FFFFFF14` (8% in menus) |
| Window Background | `#FFFFFF` | `#1E1E1E` |

**Vibrancy:** Foreground text and glyphs over glass materials use *plus-lighter* (Dark) / *plus-darker* (Light) blend modes, drawing ambient luminance from the backdrop. In GTK3, approximate via white/black alpha transparency.

---

## Typography (SF Pro, macOS — 1 pt = 1 px at 1× scaling)

| Style | Normal Weight / Emphasis | Font Size / Line Height (pt) |
|---|---|---|
| Large Title | Regular / Bold | 26 / 32 |
| Title 1 | Regular / Bold | 22 / 26 |
| Title 2 | Regular / Bold | 17 / 22 |
| Title 3 | Regular / Semibold | 15 / 20 |
| Headline | Bold / Heavy | 13 / 16 |
| **Body** | Regular / Semibold | **13 / 16** |
| Callout | Regular / Semibold | 12 / 15 |
| Subheadline | Regular / Semibold | 11 / 14 |
| Footnote, Caption | Regular / Semibold | 10 / 13 |

### Measured Component Applications:
* **Menu Bar:** Items **Semibold 13 pt**, active app name **Heavy 13 pt**, clock **Semibold 13 pt**.
* **Menus:** Items **Medium 13 pt**, headers Bold 13 pt gray, shortcuts Medium 13 pt gray (`#4C4C4C`), checkmarks Bold 13 pt.
* **Notifications:** Title Bold 13 pt, body text Regular 13 pt, timestamp Regular 11 pt.
* **Alerts:** Title Bold 13 pt, description Regular 13 pt, buttons Medium 13 pt.
* **Tooltips:** Medium 11 pt.
* **Letter Spacing (Tracking):** Positive tracking on small font sizes (10pt: +0.12, 9pt: +0.17, 8pt: +0.21).

**System Font:** **SF Pro** (variable weights).
