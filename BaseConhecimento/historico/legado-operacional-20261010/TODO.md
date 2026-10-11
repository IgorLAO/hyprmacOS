> Arquivo histórico anterior à consolidação de 2026-10-10. Consulte STATUS.md e o SQLite para o estado atual.

# hyprmac — Project Roadmap & Backlog

> Current status: **94% compliance** against official Apple macOS Tahoe / macOS 27 specifications.  
> Complete matrix: `BaseConhecimento/comparacao/MATRIZ.md`  
> Live check command: `./BaseConhecimento/ferramentas/comparar.py --pendentes`  
> Checked items `[x]` are implemented (some partially verified; refer to MATRIZ.md).

---

## 🎯 Direct User Priorities & Focus Areas (High Impact)

- [ ] **Apps internos — objetivo adicional solicitado em 09/10:** trabalhar nos
  apps da [lista de desejos](../../../BaseConhecimento/LISTA-DE-DESEJOS.md), incluindo
  Preview, Diário, Câmera, Notas e Fotos. Escopo e continuidade no
  [checkpoint pausado](../../../BaseConhecimento/CONVERGENCIA-VISUAL-2026-10-09.md).

Checkpoint visual 2026-10-08: [medidas e capturas](../../../BaseConhecimento/CONVERGENCIA-VISUAL-2026-10-08.md).
- [x] Notificações: × usa a transição CSS existente no hover, com inversão suave
  e Reduzir Movimento respeitado. Compilado, recarregado e demonstrado no desktop.
- [x] Dock: pressão mantém ampliação e alvo; menu acompanha o ícone visível e
  recebe o material de vidro existente. Auto-ocultar preserva velocidade ao inverter.
  Capturas GTK/Wayland, trajetórias e reabertura após ocultação completa validadas.
- [x] Ajustes: semáforo 14×14 sem expansão pelo glifo; hover e estado inativo
  conferidos nos dois temas, com callbacks preservados.
- [ ] Dock: separar a máscara da base dos ícones/rótulo antes de aplicar refração
  à camada. O protocolo atual de formas explícitas atende janelas; refinar contra
  gravação Tahoe equivalente, já pendente em `MacTahoe/TODO.md`.

Checkpoint visual 2026-10-07: [resultados e próxima execução](../../../BaseConhecimento/CONVERGENCIA-VISUAL-2026-10-07.md).
Central (títulos/resize), Dock (hover/geometria/input) e popovers (reabertura)
melhorados e capturados; comparações Tahoe ainda estimadas.
- [x] Primeira expansão Wi-Fi/Bluetooth/Som: manter a grade até a resposta real,
  sem animar uma vista vazia; cancelamento e reabertura verificados.
  Bluetooth em GTK/Wayland: 3 → 0 frames com vista detalhada sem conteúdo.
  Curva e material nativos continuam dependentes de gravação Tahoe equivalente.
- [x] Now Playing: tempos decorrido/restante acompanham o puxador durante o
  arrasto, mesmo com respostas atrasadas do player; atualização normal retorna
  ao soltar. Teste GTK e capturas antes/depois com estado controlado passaram.
- [x] Menus claros/escuros: seleção do pai não colore os textos do submenu;
  estados hover, submenu aberto e fechamento capturados em GTK/Wayland.
- [x] Liquid Glass: calibrar Central e material dos painéis para menos blur e
  maior definição; validar fundo colorido e branco. Parâmetros locais estimados,
  sem alegação de igualdade óptica com Tahoe.
- [x] Resposta líquida: flexão discreta de cápsulas/círculos, mola interrompível,
  lente sincronizada com a abertura e transição interna sem corte lateral.
  Layout preservado e Reduzir Movimento verificado.
- [x] Corrigir recorte dos badges “−” na edição da Central sem deslocar os
  controles: captura real e medição GTK de 11 controles no checkpoint.
  O excedente de 4 px conserva o CSS anterior; medida exata nativa ainda estimada.
- [ ] Capturar atualização real de sinal/bateria nos popovers. Auto-ocultar do
  Dock capturado em 08/10; abertura, expansão da Central e submenus nos dois temas
  já foram capturados no checkpoint anterior.
Capturas Tahoe pendentes para expansão Wi-Fi/Bluetooth, magnificação Dock e
troca de artwork continuam acompanhadas em `BaseConhecimento/MacTahoe/TODO.md`.

1. **Lock Screen Parity (`shell/hyprmac-lock`)**:
   - Refine clock typography weight/vibrancy, password capsule animations, and screen wake behavior.
2. **Task & Workspace Visualization (`shell/hyprmac-overview` & App Switcher)**:
   - Polish Mission Control (`⌃↑`) and `⌘+Tab` App Switcher to match Tahoe transitions, desktop space thumbnails, and fluid window animations.
3. **File Management / Finder Experience**:
   - Standard file managers (nautilus/Nautilus) do not yet visually resemble macOS Finder.
   - Deeply research and implement Finder details: unified toolbar, path bar, sidebar categorization (Favorites, iCloud, Locations, Tags), column view styling, and colored folder tags.
4. **Control Center Internal Sub-Popovers**:
   - Currently, clicking secondary settings (e.g., Bluetooth, Wi-Fi, Sound) can open external dialogs.
   - **Requirement:** Simple settings must open as **inline sub-popovers / expandable cards inside the Control Center itself**; external system apps should only open via an explicit "Advanced Settings…" button.
   - Refine Control Center opening animation and Liquid Glass optics.
5. **System Settings App (`shell/hyprmac-ajustes`)**:
   - Ensure visual and structural parity with macOS 27 System Settings, including mocked Apple Account / iCloud profile card and Tahoe sidebar layouts.

---

## ⌨️ Keyboard Shortcuts (Completed)

- [x] **Super+M behavior:** `Super+M` maps to Minimize (scratchpad) rather than quitting Hyprland.
- [x] **macOS Standard Shortcuts:**
  - `⌘H` Hide App · `⌥⌘H` Hide Others · `⌃⌘F` Fullscreen · `⌥⌘Esc` Force Quit · `⌘\`` Cycle windows of same app · `⇧⌘3` / `⇧⌘4` / `⇧⌘5` Capture tools · `⌥⌘D` Toggle Dock · `⌘Q` Quit App.

---

## 🧭 Menu Bar (`waybar/`)

- [x] **Height:** Fixed at **34 pt** matching Retina reference screens.
- [x] **Typography:** Menu text Body 13 pt (Semibold 13 / Heavy 13 for app name).
- [x] **App Menu:** Focused app name opens the application menu (About, Settings ⌘,, Hide ⌘H, Hide Others ⌥⌘H, Show All, Quit ⌘Q).
- [x] **Menu Bar Extras:** System status icons open menus rather than arbitrary popovers.
- [x] **Right Status Order:** Third-party tray items on the left, Input Source ("BR"), Focus moon (Do Not Disturb), Wi-Fi, Spotlight, Control Center, Notification dot, Clock ("Fri 22:52").
- [ ] **Menu Bar Controls (BAR-17):** Parity for "Allow in the Menu Bar" app tray control toggles.

---

## 📋 Menus & Popovers

- [x] **Visible Shortcuts:** Display shortcut glyphs (⌘Z, ⇧⌘Z, ⌘X, ⌘C, ⌘V, ⌘A) aligned right; unavailable items are dimmed rather than hidden.
- [x] **Edit Menu:** Complete items: Undo, Redo | Cut, Copy, Paste, Paste and Match Style, Delete, Select All | Find… | Show Clipboard | Emoji & Symbols.
- [x] **Window Menu:** Zoom, Bring All to Front, and active window list; close window is in File.
- [x] **View Menu:** State-toggling labels ("Show/Hide Scratchpad", "Enter/Exit Full Screen", or checkmarks).
- [x] **Single Popover Rule:** Opening Control Center closes Notification Center / media player, and vice versa.
- [ ] **Panel Resize Animations:** Animate panel dimension transitions seamlessly (e.g., Control Center edit mode toggle).
- [X] **Menu Icons:** Add standard macOS iconography to specific menu items where applicable.

---

## 💎 Liquid Glass & Form (Tahoe / 27 Design System)

- [x] **Concentricity:** $\text{inner radius} = \text{outer radius} - \text{margin}$.
- [x] **No Glass on Glass:** Elements placed on top of glass use transparency/vibrancy fills, never nested blur.
- [x] **Color as Tint:** Color applied to glass is a translucent tint rather than a solid opaque fill.
- [x] **Materialize from Origin:** Menus, Control Center, and media player expand outward from their trigger source.
- [x] **Selective Dimming:** 35% background dimming reserved for modal interrupting tasks; parallel non-modal tasks (like Spotlight) do not dim.
- [x] **Accessibility Toggles:** "Reduce Transparency" and "Increase Contrast" fully supported via `scripts/acessibilidade`.
- [x] **True Optical Liquid Glass:** Hyprland shader mask patch (`hyprglass`) rendering lens curvature and specular highlights.
- [ ] **True Liquid Effect:** Revisar refracao de liquida

---

## 🚀 System Components Backlog

### Dock
- [x] Basic Dock implementation with active indicators and Tahoe icon styling.
- [X] **P1:** Icon magnification on hover (spring magnification physics).
- [ ] **P2:** Minimized window genie / scale animation effect.#NAO NECESSARIO
- [ ] **P2:** App notification badges on Dock icons. #NAO NECESSARIO

### Spotlight (`shell/hyprmac-shell`)
- [x] General search, math calculation, app launcher, and recent files.
- [x] Modes: Files (`⌘2`), Apps (`⌘3`).
- [x] Dynamic filter pills and tokenized search.

### Control Center & Widgets
- [x] Core concentric grid with circles and sliders.
- [x] Widget Gallery and Desktop Widgets (Clock, Weather, Shortcuts, Calendar, Photos).
- [ ] Direct menu bar pinning for individual controls.
- [ ] Inline expandable sub-popovers for Wi-Fi and Bluetooth devices.

### Screenshots & Recording
- [x] `⇧⌘3` Fullscreen capture.
- [x] `⇧⌘4` Interactive region selection.
- [x] `⇧⌘5` Control bar with screen recording (`wf-recorder`) and floating preview thumbnail.
