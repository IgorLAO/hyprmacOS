# Matriz de comparação — hyprmac × Apple (macOS Tahoe/27)

Gerada por `ferramentas/comparar.py` a partir de `comparacao/parametros.json`. Valores marcados com 📏 foram **lidos do código agora**; os outros foram avaliados à mão.

Legenda: ✅ conforme · 🟡 próximo · 🔴 diverge · ⬜ ausente · ➖ limitação do Linux (não conta). Prioridade: **P1** visível/perigoso · **P2** notável · **P3** detalhe.

## Nota geral: **94%**

| Área | Nota | ✅ | 🟡 | 🔴 | ⬜ |
|---|---|---|---|---|---|
| Barra de menus | 98% | 16 | 1 | 0 | 0 |
| Menus | 100% | 12 | 0 | 0 | 0 |
| Central de Controle | 94% | 9 | 1 | 0 | 0 |
| Notificações | 100% | 9 | 0 | 0 | 0 |
| Janelas | 90% | 10 | 2 | 0 | 0 |
| Cores | 100% | 7 | 0 | 0 | 0 |
| Tipografia | 100% | 2 | 0 | 0 | 0 |
| Vidro e materiais | 100% | 9 | 0 | 0 | 0 |
| Movimento e popovers | 88% | 2 | 1 | 0 | 0 |
| Spotlight | 83% | 3 | 2 | 0 | 0 |
| Atalhos | 100% | 8 | 0 | 0 | 0 |
| Recursos do sistema | 73% | 5 | 5 | 0 | 0 |

## Pendências P1

- 🟡 **SIS-01 Dock** — Apple: vidro quase transparente, ícones 36 passo 45, pontos e separador; hyprmac: Dock no hyprmac-shell, no mesmo processo GTK; dock_model/geometry/motion separados, app_index e eventos compartilhados. Medidas configuráveis herdadas do kit (padrão ícone 46, passo 57, raio ~19), materiais e animações preservados. Indicadores, separadores, Downloads, Lixo, miniaturas, selos, Apps/Spotlight e autohide. Magnificação opcional já implementada; drag reordena fixos, protege Finder e remove fixação ao soltar fora com aviso Remove; app aberto permanece na seção de abertos. Ctrl+clique/botão direito abre menu com Keep in Dock/Remove from Dock, Hide e Quit. Drop text/uri-list abre documentos por Gio em apps compatíveis, sem copiar/mover/apagar. Comportamento textual confirmado em support.apple.com/en-gb/guide/mac-help/mh35859/26/mac/26; gesto real completo, múltiplos monitores/temas e materiais ainda não certificados contra Tahoe. Genie e drops em pastas permanecem ausentes

## Barra de menus — 98%

| ID | Parâmetro | Apple | hyprmac | | Prio | Onde | Fonte |
|---|---|---|---|---|---|---|---|
| BAR-01 | Altura da barra | ~34 pt na referência principal (24 pt em telas sem entalhe) | 34 📏 | ✅ | P1 | `waybar/config.jsonc` | referencias/telas/safari-escuro-barra-de-menus-abas.png (medido, MacBook Pro 16" a 2056 pt) · componentes/barra-de-menus.md |
| BAR-02 | Tamanho do texto dos menus | 13 pt (SF Pro Semibold) | 13 📏 | ✅ | P1 | `waybar/style.css` | padroes/cores-e-tipografia.md |
| BAR-03 | Peso do texto dos menus | Semibold (600) | 600 📏 | ✅ | P2 | `waybar/style.css` | componentes/barra-de-menus.md |
| BAR-04 | Nome do app | Heavy 13 (800–900) | 800 📏 | ✅ | P3 | `waybar/style.css (#window)` | componentes/barra-de-menus.md |
| BAR-05 | Logo Apple | glifo de 13×16 a 23 da borda (medido na referência; kit: 16,3 em caixa 33×24) | 20 📏 | ✅ | P3 | `waybar/style.css (#custom-apple)` | referencias/telas/safari-escuro-barra-de-menus-abas.png · referencias/kit/contornos/Menu_Bar_and_Dock.txt |
| BAR-06 | Seleção (menu aberto/hover) | cápsula 25 de altura, raio 13, branco 20% (escuro) / preto 8% (claro), 4px além do item | cápsula de 24, branco 20% (escuro) / preto 8% (claro) | ✅ | P3 | `waybar/style.css, waybar/mode.css` | componentes/barra-de-menus.md |
| BAR-07 | Transparência e cor do texto | barra totalmente transparente; texto branco ou preto 85% conforme o papel de parede | transparente com sombra no texto (modo escuro) ou clara fosca (opcional) | ✅ | P3 | `waybar/style.css, waybar/modes/light.css` | componentes/barra-de-menus.md |
| BAR-08 | Ordem dos menus | Apple · App (negrito, é um menu) · File · Edit · Format · View · Window · Help | Apple · App (menu com o nome real) · File · Edit · View · Window · Help + menus de cada app como no Mac: navegador = History · Bookmarks · Develop (Safari da referência); mesa/nautilus = Finder com Go; VS Code = Selection · Go · Run · Terminal; Spotify = Playback. Barra de todas as telas mostra o app ativo; sem janela = "Finder"<br>_waybar/scripts/app-menu.py + waybar/menus/*.xml_ | ✅ | P2 | `waybar/config.jsonc` | padroes/movimento-escrita-e-principios.md |
| BAR-09 | Data e hora | "Sun 12:07" (dia abreviado + hora; a data é opcional em Ajustes ▸ Relógio), Semibold 13 | "Fri 22:52" (dia abreviado + hora, em inglês como os menus); data completa na dica | ✅ | P3 | `waybar/scripts/clock.sh` | componentes/barra-de-menus.md · referencias/telas/safari-escuro-barra-de-menus-abas.png |
| BAR-10 | Extras abrem menu (não app/popover) | clique em Wi‑Fi/Bluetooth/Som abre um MENU com opções e slider | Wi‑Fi/Bluetooth/Som abrem menus do shell (vidro de menu raio 12, itens 24, cabeçalhos Bold 13, interruptor, rede/dispositivo atual em azul, slider, saídas, "… Settings…"); botão direito abre o app | ✅ | P2 | `shell/hyprmac-shell · waybar/config.jsonc` | hig/the-menu-bar.md (Menu bar extras) |
| BAR-11 | OSD de volume/brilho | painel de vidro 344×74 (largura das notificações), canto contínuo ~26, a ~7 da barra e da borda direita; título = nome da saída (Semibold 13, a 19 da esquerda); speaker · trilha · speaker.wave.3 (ícones a ~17/18 das bordas, 8 até a trilha); linha de 4,5 a 47,6 do topo, preenchida branca, resto branco fraco, fileira de pontos 7 abaixo a cada 15,7; interativo: com o ponteiro em cima aparece o puxador (cápsula branca ~28×18) e arrasta | LevelOSD no hyprmac-shell com essas medidas (conferidas por pixel: altura 74, maiúscula do título a 16, linha a 47,5, borda a 7); arrastável, não some com o ponteiro em cima; ícones desenhados (draw_sf) | ✅ | P2 | `shell/hyprmac-shell (LevelOSD) · shell/style.css (.osd)` | referencias/telas/osd-volume-alto-falantes.png · osd-volume-arrastando.png (1,125 px/pt) |
| BAR-12 | Indicadores de privacidade | microfone laranja, tela roxa, câmera VERDE | microfone laranja e tela roxa (módulo privacy) + câmera em cápsula VERDE (waybar/scripts/camera.sh: fuser em /dev/video*) | ✅ | P3 | `waybar/config.jsonc (privacy)` | padroes/cores-e-tipografia.md |
| BAR-13 | Ordem dos extras à direita | terceiros à esquerda · sistema · fonte de entrada · Foco · Wi‑Fi · Spotlight · (Siri) · Central de Controle · relógio | privacidade · bandeja · mesas · ▶ · bateria · Bluetooth · som · VPN · BR · Foco · rede · Spotlight · Central · relógio; título da música fora da barra (só ▶) | ✅ | P2 | `waybar/config.jsonc (modules-right)` | referencias/telas/safari-escuro-barra-de-menus-abas.png |
| BAR-14 | Fonte de entrada | sigla do layout ("BR") num quadrado contornado de cantos arredondados | custom/input: sigla do layout ativo em maiúsculas, borda 1.5 raio 4, atualiza no evento activelayout; clique troca de layout | ✅ | P3 | `waybar/scripts/input-source.sh · waybar/style.css` | referencias/telas/safari-escuro-barra-de-menus-abas.png |
| BAR-15 | Foco na barra | lua (Não Perturbe/Foco) aparece na barra enquanto o Foco está ativo | custom/focus: lua aparece com Não Perturbe ligado na Central (estado em $XDG_RUNTIME_DIR/hyprmac-dnd, sinal 10) | ✅ | P3 | `shell/hyprmac-shell · waybar/config.jsonc` | referencias/telas/safari-escuro-barra-de-menus-abas.png |
| BAR-16 | Cor do conteúdo da barra transparente | texto e ícones PRETOS sobre papel de parede claro, BRANCOS sobre escuro; o preto puxa o tom do fundo (kit Labels/Light Vibrant Primary #363636 plus-darker = fundo − 201: Finder (3,33,56) sobre (136,206,250)). Calibrado em telas reais: branco até L 0,204, preto a partir de 0,516 | hyprmac-shell (Wallpaper._bar_contrast) mede a luminância linear da faixa de 34 da barra no papel de parede (como desenhado, por monitor) e acima de 0,33 grava waybar/contrast.css (de contrast-dark.css) com a cor fundo − 201; recarrega o Waybar; refeito quando o papel de parede ou o tema mudam. Também cobre os menus próprios de cada app (VS Code, mesa, navegador, Spotify), que faltavam no modo de barra clara<br>_limiar 0,33 = ponto médio perceptual entre as amostras (nenhuma tela de referência entre 0,204 e 0,516); a barra é uma só cor para todos os monitores (média), o Mac decide por tela_ | ✅ | P1 | `shell/hyprmac-shell · waybar/contrast-dark.css · waybar/style.css` | referencias/telas: macos-tahoe-home-screen, 1_AWn…, 1_UTW…, ajustes-wallpaper-screen-saver-folha-claro (branco) · 03gv…, Edit-Controls…, tahoe-photos-central-dock-claro (preto) |
| BAR-17 | Ajustes ▸ Menu Bar ▸ Menu Bar Controls | cartão "System and app controls can be configured…" + Add Controls… + a Central desenhada; lista com caixa à esquerda + ícone colorido; Clock sem caixa com Clock Options…; Battery Options…; "Show When Active" nos que só aparecem ativos; depois "Allow in the Menu Bar" com os apps; ícone do painel = dois interruptores | 2026-10-20: a caixa tira/põe o item da barra (waybar/barra-ocultos.css + SIGUSR2; ~/.config/hyprmac/barra.json). Fones e Sleep Focus aparecem quando ativos; gravação e compartilhamento são avisos automáticos. Add Controls… abre a Central em edição; Clock Options… abre folha com data, dia, segundos e separador ligados ao relógio Rust; Allow in the Menu Bar lista apps SNI registrados com opção de ocultar. O ajuste 5/10/15 limita as três seções de Recent Items. Analog e Announce continuam indisponíveis; When Space Allows não mede o espaço da barra. Snapshots locais conferidos, sem comparação visual Tahoe 26 equivalente; limites 5/10/15 e resolução do ID de System Settings conferidos em ensaio isolado com 20 itens por seção | 🟡 | P3 | `shell/hyprmac-ajustes (_menubar_controls), waybar/style.css` | video/frames-ui/ui_0002–0005 |

## Menus — 100%

| ID | Parâmetro | Apple | hyprmac | | Prio | Onde | Fonte |
|---|---|---|---|---|---|---|---|
| MENU-01 | Raio do menu | 12 (contínuo) | 12 📏 | ✅ | P3 | `waybar/style.css · gtk/gtk3.css · shell/style.css` | componentes/menus.md |
| MENU-02 | Altura do item | 24 (regular) | 24 📏 | ✅ | P2 | `waybar/style.css` | componentes/menus.md |
| MENU-03 | Texto do item | SF Pro Medium 13 | 13 📏 | ✅ | P2 | `waybar/style.css` | componentes/menus.md |
| MENU-04 | Raio do destaque (hover) | 8 | 8 📏 | ✅ | P3 | `waybar/style.css` | componentes/menus.md |
| MENU-05 | Cor do destaque (hover) | #0069F9 | #0069F9 (barra e apps GTK) | ✅ | P3 | `waybar/style.css · gtk/palette3-dark.css` | componentes/menus.md |
| MENU-06 | Padding do contêiner | 6 topo / 16 lados / 5 base (destaque ultrapassa o texto 11px) | contêiner 6/5/5/5 + item 11px de cada lado (texto a 16 da borda, destaque 11 além do texto) | ✅ | P3 | `waybar/style.css · gtk/gtk3.css` | componentes/menus.md |
| MENU-07 | Material do menu | Liquid Glass: #5A5A5A/0.50 luminosity, desfoque 20, saturação 1.2, filete + aros + sombra 0 4 24 /0.30 | Liquid Glass de verdade (plugin hyprglass + patch hypr/hyprglass/forma-pela-mascara.patch): o passe de popups da barra e do shell ('waybar:popups', 'hyprmac-menu:popups') vira vidro com lente de 20 pt, aro e especular por peça; o CSS só tinge (rgba(30,30,34,0.42), waybar/vidro.css e shell/vidro-camadas.css). Sem o plugin: vidro translúcido 0.74 + desfoque do Hyprland | ✅ | P2 | `hypr/vidro-presets.lua · waybar/vidro.css (scripts/vidro) · shell/vidro-camadas.css` | padroes/liquid-glass.md |
| MENU-08 | Atalhos visíveis nos itens | ⌃⌥⇧⌘+tecla à direita, Medium 13 cinza | atalhos à direita em cinza (Ctrl para edição, ⌘ onde há atalho Super real) | ✅ | P2 | `waybar/menus/*.xml` | componentes/menus.md |
| MENU-09 | Itens indisponíveis | esmaecidos (não somem) | menu Window esmaece (sensitive); File e Edit têm versão da mesa (Finder sem janela) com Close Window, Undo, Redo, Cut, Copy, Delete, Select All e Find esmaecidos (waybar/menus/*-mesa.xml, trocados por app-menu.py) | ✅ | P3 | `shell/hyprmac-shell (WindowMenu) · waybar/menus` | padroes/movimento-escrita-e-principios.md |
| MENU-10 | Conteúdo do menu Window | Minimize · Zoom | Bring All to Front | lista de janelas; sem Close; sem Full Screen | Minimize ⌘M · Zoom · Center | Move & Resize ▸ (Float/Tile, Keep on All Desktops, Move to Desktop) · Desktops · New Desktop | Bring All to Front | janelas do app em ordem alfabética com ✓; sem Close | ✅ | P3 | `shell/hyprmac-shell (WindowMenu._build)` | padroes/movimento-escrita-e-principios.md |
| MENU-11 | Itens alternáveis com rótulo de estado | Show/Hide …, Enter/Exit Full Screen | View montado na hora: Enter/Exit Full Screen, Show/Hide Scratchpad, Use Light/Dark Appearance, Use Light/Transparent Menu Bar | ✅ | P3 | `shell/hyprmac-shell (view-menu)` | hig/the-menu-bar.md |
| MENU-12 | Edit completo | Undo, Redo | Cut, Copy, Paste, Paste and Match Style, Delete, Select All | Find | … Emoji & Symbols | Undo, Redo | Cut, Copy, Paste, Paste and Match Style, Delete, Select All | Find… (⌃F) | Show Clipboard | Emoji & Symbols | ✅ | P3 | `waybar/menus/editar.xml` | hig/the-menu-bar.md |

## Central de Controle — 94%

| ID | Parâmetro | Apple | hyprmac | | Prio | Onde | Fonte |
|---|---|---|---|---|---|---|---|
| CC-01 | Proporção vão/diâmetro da grade | ≈0.20 | 12 ÷ 66 = 0.182 📏 | ✅ | P3 | `shell/hyprmac-shell (C, GAP)` | componentes/central-de-controle.md |
| CC-02 | Material dos blocos | vidro CLARO quase transparente, tingido pelo papel de parede, aro de luz branco | vidro CLARO e transparente (alfa ~0.22): o ignore_alpha da layer rule hyprmac-cc foi baixado para 0.06, então o bloco desfoca mesmo com alfa baixo e fica tingido pelo papel de parede, com aro de luz branco forte no topo e fraco embaixo + brilho interno; o fundo da janela (alfa 0) não desfoca, só os blocos; acende por dentro ao clicar (WWDC25); com o plugin hyprglass + patch hypr/hyprglass/forma-pela-mascara.patch: cada bloco é um vidro próprio (lente de quarto de círculo 20 pt, aro, especular pelo lado de cada peça), preenchimento 0.06<br>_ | 2026-10-04 (2ª rodada): curva medida em 5 referências dos dois temas = bloco ≈ 0,53·fundo + 58; preset hyprmac-central brilho 1,0, contraste 0,61, sat 1,7 (medido 20→68, 100→110, 180→152, 250→188; o antigo 0,82/0,87 escurecia tudo), lente 1,0 nas bordas (o usuário sentiu falta da distorção com 0,3), desfoque 1,0, chanfro 0,14 a 45°; filete branco 22 % (medido topo +46, base +37, lados +28 contra Apple +40/+36…50/+8…70); glifos dos círculos 31 px (0,35 do círculo), disco 24, mídia 27/32, capa 0,29 do bloco com canto 7, título 14 Semibold, Editar Controles 13 a 18 da grade; grade 66/12 = 300 pt (Apple 295–299); estado #FFF/0.80; sem sombra no texto; só o Foco tinge de azul_ | ✅ | P1 | `shell/style.css (.cc .tile) · hypr/hyprmac.lua (ignore_alpha)` | componentes/central-de-controle.md · referencias/telas |
| CC-03 | Controle ligado | círculo branco sólido + glifo azul (claro e escuro) | disco branco + glifo azul nos dois temas | ✅ | P2 | `shell/style.css · shell/style-light.css (.circle.on)` | componentes/central-de-controle.md |
| CC-04 | Tamanhos de controle | pequeno (círculo), médio (2×1), grande (2×2), largo (sliders) | small, medium, large, wide | ✅ | P3 | `shell/hyprmac-shell (SPANS)` | componentes/central-de-controle.md |
| CC-05 | Modo de edição: "−" e espaços fantasmas | "−" no canto de cada controle + círculos fantasmas onde está vazio | "−" + círculos fantasmas até completar a grade e mais uma linha | ✅ | P3 | `shell/hyprmac-shell (_wrapper/_build_grid)` | referencias/telas/macos-tahoe-home-screen.jpg |
| CC-06 | Galeria de controles | painel ao lado com busca, categorias, sugestões nos 3 tamanhos, Done azul; arrastar para a Central OU para a barra de menus | painel à esquerda da Central com busca, categorias, controles em todos os tamanhos, rodapé + Done azul; clique adiciona/troca tamanho. O + da barra durante edição mostra, na mesma bandeja, cartões Add/Remove de controles nativos. Arrastar cartões para a barra ainda falta. A galeria usa um painel de vidro com texto (preset hyprmac-texto); "Search Controls" visível com o campo focado. A página nova foi validada localmente em barra-galeria-2026-10-18.png, sem medição Tahoe 26 | 🟡 | P2 | `shell/hyprmac-shell (_build_gallery, _build_bar_gallery)` | referencias/telas/1_AWn03UdmtRaR6fupfQIMUQ.jpg |
| CC-07 | Sliders | Tahoe final (tahoe-dark.jpeg, 2 px/pt): linha de 4 pt sem puxador, centrada a 42 pt do topo do bloco de 63,5; preenchimento #F8F8F8, trilha ~10 % de preto; ícones SF fora da linha (sun.min com pontos / sun.max com raios; speaker / speaker.wave.3), esquerdo a 14,5 da borda e 5 da linha, direito a 6,5 da linha e 15 da borda; Som com AirPlay de ÁUDIO em círculo branco de 25,5 a 10 do ícone; puxador do kit (20×16 #DEDEDE) só com o ponteiro em cima | igual, escalado ×1,055 (bloco 67): SliderTile com ícones desenhados em cairo (draw_sf: sun.min/max, speaker, speaker.wave.3, airplayaudio), linha de 4, título a 17/16, canto 21 (aproxima o contínuo) | ✅ | P2 | `shell/hyprmac-shell (SliderTile, draw_sf) · shell/style.css (.cc scale, .slider-tile)` | referencias/telas/tahoe-dark.jpeg · osd-volume-arrastando.png · kit Sliders/Dark/Content Area/Knob |
| CC-08 | Tocando Agora na Central | capa GRANDE no topo, título, artista, ◀◀ ▶ ▶▶; vazio = quadrado cinza + "Not Playing" | capa 53px (36% do bloco de 147, raio concêntrico 27 − 15 = 12); título 15 Bold, artista 13, controles 21; vazio = quadrado cinza + "Nada Tocando" | ✅ | P2 | `shell/hyprmac-shell (NowPlaying)` | componentes/central-de-controle.md |
| CC-09 | Bloco médio com estado | título Semibold + estado (Home, Off, On) | largura fixa 2 círculos + vão (147); ícone 37 recuado 15 (concêntrico), texto 7 depois; título Semibold 13 (12/11,5 se não couber) + subtítulo 11 | ✅ | P3 | `shell/hyprmac-shell (Toggle)` | componentes/central-de-controle.md |
| CC-10 | Entrada da Central | brota do ícone da barra (que fica em cápsula de vidro) | brota do ícone da barra (ponto do clique fixo enquanto o vidro cresce de 90% com mola); ícone ganha cápsula | ✅ | P3 | `hypr/hyprmac.lua (hyprmac-cc animation)` | padroes/liquid-glass.md (regra 6) |

## Notificações — 100%

| ID | Parâmetro | Apple | hyprmac | | Prio | Onde | Fonte |
|---|---|---|---|---|---|---|---|
| NOT-01 | Largura do banner | 344 | 344 📏 | ✅ | P3 | `shell/hyprmac-shell (BANNER_W)` | componentes/notificacoes.md |
| NOT-02 | Raio do banner | 20 | 20 📏 | ✅ | P2 | `shell/style.css (.notif)` | componentes/notificacoes.md |
| NOT-03 | Ícone do app | 32×32 | 32 📏 | ✅ | P3 | `shell/hyprmac-shell (ICON)` | componentes/notificacoes.md |
| NOT-04 | Texto do corpo | Regular 13 | 13 📏 | ✅ | P3 | `shell/style.css (.notif .body)` | componentes/notificacoes.md |
| NOT-05 | Hora | Regular 11 | 11 📏 | ✅ | P3 | `shell/style.css (.notif .time)` | componentes/notificacoes.md |
| NOT-06 | Padding do banner | 12 / 14 / 12 / 10 | 12 / 14 / 12 / 10 | ✅ | P3 | `shell/style.css (.notif)` | componentes/notificacoes.md |
| NOT-07 | Posição | 16 da direita, 15 abaixo da barra, 16 entre grupos | 16 da direita, 15 abaixo da barra, 16 entre banners/grupos | ✅ | P3 | `shell/hyprmac-shell (NotificationCenter margins) · .notif margin-bottom` | componentes/notificacoes.md |
| NOT-08 | Pilha (empilhamento por app) | cartão de trás aparece 6–8px, recuado 16px | banners do mesmo app empilham: o novo entra na frente e os anteriores viram cartões de trás (7 px recuado 16, 6 px recuado 32); continuam todos na central | ✅ | P3 | `shell/hyprmac-shell (NotificationCenter.notify, Banner.set_stack) · shell/style.css` | componentes/notificacoes.md |
| NOT-09 | Material | Liquid Glass Notification (#666/0.10 lighten, desfoque 10, aros) | Liquid Glass (plugin hyprglass + patch hypr/hyprglass/forma-pela-mascara.patch): cada banner é uma peça de vidro com lente/chanfro de 20 pt, aro claro, tinta adaptativa (adaptive_dim); preenchimento rgba(34,34,38,0.42) | ✅ | P3 | `hypr/vidro-presets.lua (hyprmac-pequeno) · shell/vidro-camadas.css` | padroes/liquid-glass.md |

## Janelas — 90%

| ID | Parâmetro | Apple | hyprmac | | Prio | Onde | Fonte |
|---|---|---|---|---|---|---|---|
| WIN-01 | Raio das janelas | ~22 (janela com barra de ferramentas, medido); 16 sem barra | 22 📏 | ✅ | P1 | `hypr/hyprmac.lua` | referencias/telas/safari-escuro-barra-de-menus-abas.png (medido, MacBook Pro 16" a 2056 pt) · padroes/forma-e-espacamento.md |
| WIN-02 | Curvatura contínua | squircle (suavização 0.6) | 3.2 📏 | ✅ | P3 | `hypr/hyprmac.lua` | padroes/forma-e-espacamento.md |
| WIN-10 | Margem da janela às bordas do monitor e à barra | 0 — a janela encosta na barra e nas laterais | 0 📏 | ✅ | P1 | `hypr/hyprmac.lua` | referencias/telas/safari-escuro-barra-de-menus-abas.png (medido, MacBook Pro 16" a 2056 pt) |
| WIN-11 | Barra de abas | faixa de 34 um tom acima da janela (#333 sobre #202020), abas em cápsula de 31, ativa #565656 | tabbar do GTK4/libadwaita (Ghostty, Nautilus): faixa de 34 com tinta 8,5 %, cápsulas de 30, ativa com tinta 24 % (= #565656 no escuro), sem sublinhado | ✅ | P2 | `gtk/gtk4.css (tabbar)` | referencias/telas/safari-escuro-barra-de-menus-abas.png (medido) |
| WIN-03 | Sombra da janela ativa | 0 36 100 preto/40% + filete 0 0 1 preto/80% (todas as janelas); aro interno 1px #FFF/0.20 só na escura ativa (kit Windows/*; medido em tahoe-dark.jpeg: 0,5 pt preto + 1 pt a 20 %) | filete = borda de 1 px preto/0.50 (o 0,5 pt da referência a 1×) em todas as janelas e nos dois modos; aro = glow interno de 1 px #FFF/0.40 → 20 % medido com grim (0.200), só na escura ativa; sombra: uma só, range 50, offset 0 18, preto/40% (o Hyprland não faz duas sombras) | 🟡 | P2 | `hypr/hyprmac.lua (border, shadow, glow) · scripts/theme` | tokens/macos27 (estilos Windows/*) · referencias/telas/tahoe-dark.jpeg (borda do Finder, medida) · padroes/liquid-glass.md (Janelas) |
| WIN-04 | Sombra da janela inativa | 0 16 32 preto/20% (menor e mais fraca que a ativa) | mesmo alcance, preto/20%; filete preto/0.50 e SEM aro interno (como no kit: a inativa não tem a borda branca)<br>_o Hyprland 0.56 tem uma sombra só para todas as janelas (só a cor muda na inativa) e as regras de janela não casam por foco; dá para escurecer menos (color_inactive), não encolher_ | ➖ | P3 | `hypr/hyprmac.lua (color_inactive)` | padroes/liquid-glass.md |
| WIN-05 | Borda | escuro: 1px interna branca 20%; claro: sem borda | escuro: 1px branca 20% (ativa) / 8% (inativa); claro: sem borda (scripts/theme troca na hora) | ✅ | P3 | `hypr/hyprmac.lua (col)` | padroes/liquid-glass.md |
| WIN-06 | Semáforo (fechar/minimizar/zoom) | círculos 14, vão 9, #FF5C60 #FAC800 #35C759; cinza na inativa | semáforo do kit (14, vão 9, cores e anel 0,5; #FFF/0.17 na inativa; símbolos só ao passar o ponteiro) à esquerda em GTK 3/4 e libadwaita (barra unificada de 52, semáforo a 18), no Ghostty (barra simples de 33, semáforo em 9,9) e no Brave com o tema GTK; apps Qt, VS Code e GTK sem barra própria continuam sem<br>_vermelho fecha (testado com clique); amarelo: o Hyprland ignora o pedido de minimizar do cliente (use ⌘M); verde: o hyprland.lua do usuário tem a regra padrão suppress-maximize-events (desligá-la faria apps que abrem maximizados cobrirem o tiling); título do Ghostty fica centrado (no Tahoe o título vem à esquerda, logo após o semáforo — kit: Title em x=93); o AdwHeaderBar não deixa alinhar pelo CSS_ | 🟡 | P2 | `gtk/gtk3.css · gtk/gtk4.css · ghostty/macos.css · button-layout` | componentes/janelas-popovers-alertas.md |
| WIN-07 | Fundo da janela GTK | #1E1E1E / #FFFFFF | #1e1e1e | ✅ | P3 | `gtk/palette3-dark.css (mac_window)` | padroes/cores-e-tipografia.md |
| WIN-08 | Scratchpad / minimizar | ⌘M minimiza para o Dock; ⌘H oculta o app | Super+M e Window ▸ Minimize mandam a janela para o Dock (área especial "minimized"): miniatura real (grim -T) entre o separador e Downloads com o ícone do app no canto; clique (ou Show no menu) traz de volta à mesa atual; Super+H oculta o app (scratchpad) | ✅ | P3 | `hypr/hyprmac.lua · shell/hyprmac-shell (Dock, WindowMenu)` | padroes/atalhos-de-teclado.md |
| WIN-12 | Seleção da barra lateral | retângulo raio 8, 32 de altura, na cor de destaque escurecida (medido no Tahoe com o azul: 0,84,196 — referencias/telas/ajustes-general-escuro-aguas-vivas.png), texto branco | #0054C4 com o azul (outras cores: destaque escurecido por canal), texto branco; igual com e sem foco (pedido do usuário), barra lateral também sem mudar de cor no :backdrop | ✅ | P2 | `shell/ajustes.css` | referencias/telas/ajustes-general-escuro-aguas-vivas.png · referencias/kit/contornos/Sidebars.txt |
| WIN-13 | Pop-up nos formulários | valor + Arrow Button 24 (círculo #FFF/0.07, ⌃⌄ Semibold), vão 6; valor tão claro quanto o título | igual (popup_button) | ✅ | P3 | `shell/hyprmac-ajustes · shell/ajustes.css` | referencias/kit/contornos/Forms.txt · Buttons.txt |
| WIN-14 | Barra lateral de vidro (Ajustes) | Sidebar/Background/Dark/Active #0C0C0C/0.85 sobre desfoque 80, saturação 2, distorção 0,5 (inativa #2E2E2E/0.85; claro #FAFAFA/0.80 e #F4F4F4); flutuante recuada 8, raio 18 | janela com alfa só na barra lateral (moldura opaca pintada em cairo, _draw_side_frame); preenchimento do kit por CSS; vidro do hyprglass (preset hyprmac-lateral) ou desfoque do Hyprland sem o plugin · 2026-10-04: conferido com video/frames-ui/ui_0099/0192 (macOS 27): interruptor Mini do kit (36×16, botão 21×13) e linha de 40; botões comuns raio 6 (não cápsula); Desktop & Dock com Windows, encaixe, Mission Control completo, navegador padrão em pop-up com ícone (muda de verdade), "?"; Menu Bar com Menu Bar Controls do 27 | ✅ | P2 | `shell/hyprmac-ajustes · shell/ajustes.css · hypr/vidro-presets.lua` | referencias/kit/contornos/Windows.txt · consultar.py --estilo Sidebar/Background · referencias/telas/dark-icons-widgets-macos-1.webp |

## Cores — 100%

| ID | Parâmetro | Apple | hyprmac | | Prio | Onde | Fonte |
|---|---|---|---|---|---|---|---|
| COR-01 | Azul de destaque (escuro) | #007AFF (controlAccentBlueColor, Tahoe 26.6.1 25G76) | #007aff 📏 | ✅ | P2 | `gtk/palette3-dark.css` | SQLite tahoe26:cores:controlaccentblue; SystemAppearance.bundle/{Aqua,DarkAqua}.car, árvore COLORS BGRA; Tahoe 26.6.1 25G76 |
| COR-02 | Azul de destaque (claro) | #007AFF (controlAccentBlueColor, Tahoe 26.6.1 25G76) | #007aff 📏 | ✅ | P2 | `gtk/palette3-light.css` | SQLite tahoe26:cores:controlaccentblue; SystemAppearance.bundle/{Aqua,DarkAqua}.car, árvore COLORS BGRA; Tahoe 26.6.1 25G76 |
| COR-03 | Vermelho destrutivo (escuro) | #FF4245 | #ff4245 📏 | ✅ | P3 | `gtk/palette3-dark.css` | padroes/cores-e-tipografia.md |
| COR-04 | Verde (escuro) | #30D158 | #30D158 📏 | ✅ | P3 | `waybar/style.css (@green)` | padroes/cores-e-tipografia.md |
| COR-05 | Rótulo primário (escuro) | #FFF/216÷255 (labelColor) | GTK3/GTK4: rgba(255,255,255,0.847058824) | ✅ | P3 | `gtk/palette3-dark.css · gtk/palette4-dark.css` | padroes/cores-e-tipografia.md |
| COR-06 | Rótulo secundário (escuro) | #FFF/140÷255 (secondaryLabelColor) | GTK3/GTK4: rgba(255,255,255,0.549019608) | ✅ | P3 | `gtk/palette3-dark.css · gtk/palette4-dark.css` | padroes/cores-e-tipografia.md |
| COR-07 | Cor de destaque escolhível | multicolor + 8 cores em Ajustes ▸ Aparência | View ▸ Accent Color: Blue, Purple, Pink, Red, Orange, Yellow, Green, Graphite (cores do kit, tons de claro/escuro; seleção 16 % mais escura como o #0069F9); scripts/accent gera gtk/accent3|4.css, waybar/accent.css, wofi/accent.css, grava no GNOME/KDE; o hyprmac-shell troca o azul do CSS e recarrega ao vivo | ✅ | P3 | `scripts/accent · shell/hyprmac-shell (load_css, ViewMenu)` | componentes/sistema-e-recursos.md |

## Tipografia — 100%

| ID | Parâmetro | Apple | hyprmac | | Prio | Onde | Fonte |
|---|---|---|---|---|---|---|---|
| TIP-01 | Fonte do sistema | SF Pro (família "SF Pro", arquivo variável com todos os pesos) | SF Pro instalada (~/.local/share/fonts/SF-Pro) e primeira em todos os CSS; GTK settings.ini e gsettings = "SF Pro 10"<br>_fonte disponível em BaseConhecimento/referencias/kit/fontes (uso pessoal); instalar em ~/.local/share/fonts e incluir "SF Pro" no font-family_ | ✅ | P1 | `waybar/style.css · shell/style.css · gtk` | referencias/kit/fontes/SF-Pro.ttf · padroes/cores-e-tipografia.md |
| TIP-02 | Corpo de texto padrão (Body) | 13 / 16 | barra 13, menus 13, notificações 13, Central 13 Semibold / 11 | ✅ | P2 | `vários CSS` | padroes/cores-e-tipografia.md |
| TIP-03 | Símbolos | SF Symbols (traço que acompanha o peso do texto) | Symbols Nerd Font (Material Design Icons) | ➖ | P3 | `CSS (font-family Symbols Nerd Font)` | hig/sf-symbols.md |

## Vidro e materiais — 100%

| ID | Parâmetro | Apple | hyprmac | | Prio | Onde | Fonte |
|---|---|---|---|---|---|---|---|
| VID-01 | Desfoque do material | raio 60, saturação 1.45–2.0 (Regular) | Hyprland size 12 × 3 passes, vibrancy 0.4 (≈ desfoque 60 / saturação 1.9 do kit) | ✅ | P2 | `hypr/hyprmac.lua (blur)` | padroes/liquid-glass.md |
| VID-02 | Sem vidro sobre vidro | por cima do vidro só preenchimento/transparência | respeitado (pílulas e campos usam preenchimento) | ✅ | P3 | `shell/style.css` | padroes/liquid-glass.md (regra 2) |
| VID-03 | Cor como tingimento | ação principal tingida; nada de preenchimento sólido opaco em vidro | galeria de controles da Central sem "+" (clique na prévia adiciona; a Apple arrasta — "Drag a control to place it in Control Center or Menu Bar…", cc-edicao-galeria-sobre-azul.png); controle ligado = branco + glifo azul e hover de menu #0069F9 sólido, como no kit; cores sólidas só nos ícones de categoria (como os da Apple)<br>_conferido em 2026-10-04; o "+" azul da galeria de widgets da mesa não tem referência_ | ✅ | P3 | `shell/style.css` | padroes/liquid-glass.md (regra 4) |
| VID-04 | Concentricidade dos painéis | raio interno = externo − margem | notificação ✓, Spotlight 30−8 = 22 ✓, histórico 26−10 = 16 ✓, player 30−18 = 12 ✓, Tocando Agora 26−13 = 13 ✓ | ✅ | P3 | `shell/style.css · wofi/style.css` | padroes/forma-e-espacamento.md |
| VID-05 | Escurecimento em painel modal | 35% (Clear sobre fundo claro); tarefa que interrompe = escurece | histórico 35% (ignore_alpha 0.36 na camada); scratchpad dim_special 0.25 | ✅ | P3 | `shell/style.css (.clip-backdrop) · hypr/hyprmac.lua` | padroes/liquid-glass.md |
| VID-06 | Acessibilidade do vidro | Reduzir Transparência, Aumentar Contraste, Reduzir Movimento | Reduzir Movimento (gsettings enable-animations / reduce_motion); View ▸ Reduce Transparency (vidros opacos no shell, barra e Dock sólidos, menus GTK opacos) e View ▸ Increase Contrast (bordas fortes, texto secundário mais claro) via scripts/acessibilidade (~/.config/hyprmac/acessibilidade.json, ao vivo) | ✅ | P3 | `scripts/acessibilidade · shell/a11y-*.css · waybar/a11y.css · gtk/a11y3|4.css` | padroes/liquid-glass.md (regra 9) |
| VID-07 | Lente (refração) e chanfro | lente na borda, perfil de quarto de círculo, faixa 20 pt / deslocamento 60 pt, sem aberração cromática; cada peça é um vidro | plugin hyprglass + patch hypr/hyprglass/forma-pela-mascara.patch: edge_thickness 0.15 (= 20 px), refraction 1.2 (= 60 px), aberração 0, forma pela máscara de alfa (cada bloco/banner/menu) | ✅ | P1 | `hypr/vidro-presets.lua · hypr/hyprglass/` | padroes/liquid-glass-hyprland.md (modelo óptico do iOS 27) |
| VID-08 | Liquid Glass Clear ↔ Tinted | Ajustes ▸ Aparência: de ultra transparente a totalmente tingido (macOS 27) | slider em Ajustes ▸ Aparência (glass_tint 0–100 em aparencia.json) → tinta e adaptive_dim do preset; Reduzir Transparência = fosco sem lente | ✅ | P2 | `shell/hyprmac-ajustes · hypr/vidro-presets.lua · scripts/vidro recarregar` | apple-support-scraped/pages/What’s new in macOS 27.md |
| VID-09 | Materializar | aparece/some modulando a lente, não só com fade | uniform appear no patch: refração e especular crescem com smoothstep do alfa da animação da camada | ✅ | P3 | `hypr/hyprglass/forma-pela-mascara.patch` | hig/wwdc/219-meet-liquid-glass.txt |

## Movimento e popovers — 88%

| ID | Parâmetro | Apple | hyprmac | | Prio | Onde | Fonte |
|---|---|---|---|---|---|---|---|
| MOV-01 | Um popover por vez | abrir um fecha o outro | um painel por vez (CC, Notificações, player, histórico) | ✅ | P2 | `shell/hyprmac-shell` | padroes/movimento-escrita-e-principios.md |
| MOV-02 | Superfícies brotam da origem | menu/painel cresce a partir do botão clicado | Central, player e menus dos extras brotam do ícone clicado (popin 90% + margens compensadas pelo shell para o ponto de origem ficar parado; mola macPop 320 ms); galeria materializa (popin 96%); banners e Central de Notificações deslizam da direita (como no macOS); Spotlight popin 94%; menus GTK (barra/Janela) sem animação própria; o vidro MATERIALIZA (lente e especular crescem com o alfa da animação — patch do hyprglass) | 🟡 | P3 | `hypr/hyprmac.lua (layer rules)` | hig/wwdc/219-meet-liquid-glass.txt |
| MOV-03 | Mudanças de tamanho animadas | animar redimensionamento de popover | altura da Central animada (250 ms, desaceleração) ao entrar/sair da edição e ao adicionar/remover controles; galeria materializa | ✅ | P3 | `shell/hyprmac-shell` | hig/popovers.md |

## Spotlight — 83%

| ID | Parâmetro | Apple | hyprmac | | Prio | Onde | Fonte |
|---|---|---|---|---|---|---|---|
| SPT-01 | Modos ⌘1–⌘4 | Apps, Arquivos, Ações, Área de Transferência | Apps (drun), Arquivos (recentes + pastas do usuário, ícone/miniatura, Ctrl+R mostra na pasta), Ações (teclas rápidas + itens dos menus) e Área de Transferência; Super+1…4 | ✅ | P2 | `scripts/spotlight · scripts/spotlight-itens` | componentes/sistema-e-recursos.md |
| SPT-02 | Histórico, teclas rápidas, itens de menu | ↑ histórico; "em"/"al" teclas rápidas; busca nos itens da barra de menus | histórico das últimas 20 escolhas por modo no topo; ↑ com o campo vazio volta às buscas digitadas antes (2026-10-04, 30 últimas); teclas rápidas fixas (nt, dm, sc…); itens da barra de menus pesquisáveis · 2026-10-04: ao digitar, fileira de cápsulas de filtro com os tipos/apps dos resultados (spotlight-busca-filtros-tab); o filtro vira token no campo com ícone (spotlight-busca-filtro-folders), ⌫ com campo vazio ou Esc tiram; arquivos com "data · pasta"; numa pasta selecionada "Buscar em … tab" e o tab busca dentro dela; buscas de várias palavras casam em qualquer ordem ("base conhecimento" → BaseConhecimento); conta digitada vira o cartão do Tahoe (video/frames-ui/ui_0156: "5+5 =" / "10", botão copiar, "= 10" no campo e o ícone da Calculadora; ↩ copia); /Apps (/Applications), /Folders, /Settings (/System Settings) e /Actions + Return aplicam os tokens existentes (comportamento textual Tahoe 26: support.apple.com/guide/mac-help/narrow-search-results-in-spotlight-mchl4d69efd3/26/mac/26). Falta seletor genérico de /, filtro MIME/PDF e app+Tab | 🟡 | P3 | `scripts/spotlight-itens` | referencias/pdfs/novidades-macos-tahoe.txt |
| SPT-03 | Histórico da área de transferência | ~8 h; texto, imagens, links, arquivos; cola texto puro; limpar | 8 h, 100 itens, texto/imagens/arquivos, cola texto puro, Limpar, busca | ✅ | P3 | `scripts/clipboard · shell (ClipboardPanel)` | componentes/sistema-e-recursos.md |
| SPT-04 | Painel e busca única | cápsula 587×52 a 97 do topo, texto 25; com resultados vira painel (raio 26) com separador recuado 18, linhas 51/passo 53, ícone 28, título 16 + subtítulo 13, seleção cinza raio 12; conclusão em linha ("final cut Pro — Open") e ícone do melhor resultado à direita; busca única em apps, ajustes, ações, arquivos e contas | painel nativo do hyprmac-shell (Spotlight): mesmas medidas (588 px centrado, conferido com grim), vidro Regular-Large escuro/claro, busca única com ranking (apps > Ajustes > ações > arquivos; sem acento/caixa), 27 painéis de Ajustes, calculadora, conclusão em linha + ícone à direita, Tab completa, Esc limpa/fecha, ⌘R/Ctrl+R mostra na pasta, Super+1…4 = modos; wofi só como reserva<br>_falta: fichas de fontes (Photos, Mail…) sob o campo e resultados da web/Siri_ | ✅ | P1 | `shell/hyprmac-shell (Spotlight) · shell/style.css · scripts/spotlight · hypr/hyprmac.lua` | video/frames-ui/ui_0147.png · ui_0151.png · ui_0153.png (medido a ~2,4 px/pt pelo "Help" da barra) |
| SPT-05 | Botões de modo de vidro (animação) | 4 círculos do diâmetro da cápsula brotam da ponta dela como gota líquida (incha, estica, solta, divide-se com pescoços); clique funde de volta; modo mostra placeholder = nome e ⌘N | SpotControls em shell/spotlight_controls.py (painel em shell/hyprmac-shell): união suave (smooth-min de SDFs) calculada por pixel em numpy; o hyprglass (forma pela máscara) dá lente e aro a cada gota; aparece com o ponteiro na metade direita da cápsula; clique troca o modo e reabsorve; lupa vira o ícone do modo; teclas ⌘N. Modo Arquivos vazio como no Tahoe (medido em spotlight-clique-modo-5 a 0,83 px/pt): painel de 500 que cresce vazio a partir da cápsula e depois mostra o conteúdo (tempo 320 ms estimado — os quadros não têm tempo), "⋯" no campo, cápsulas de filtro pelos apps que abrem os recentes (clique filtra), "Suggestions" (histórico do Spotlight) e "Recents" em grade de 5 colunas de 112 com miniatura de 65 e nome em 2 linhas, setas navegam na grade. Modo Apps (2026-10-04, spotlight-modo-apps-9): mesmo crescimento vazio e depois o conteúdo; "A" da App Store no campo e placeholder "Applications"; cápsulas de categoria do tamanho do texto (categorias do freedesktop mapeadas para as do Tahoe; clique filtra; rolam de lado), linha dos usados por último, filete a 201, todos os apps em ordem alfabética (ícone 58, nome Medium 12 cortado em ~92, passo 103); trocar de modo com a grade aberta esmaece o conteúdo novo. Falta: menu do "⋯" e modo Ações (sem referência); variante com seções por categoria e "Show More" (escuro-spotlight-apps-sobre-claro) | 🟡 | P2 | `shell/hyprmac-shell (SpotControls, Spotlight) · shell/style.css (.spot-key)` | referencias/telas/spotlight-controles-*.png · spotlight-clique-modo-*.png |

## Atalhos — 100%

| ID | Parâmetro | Apple | hyprmac | | Prio | Onde | Fonte |
|---|---|---|---|---|---|---|---|
| ATL-01 | Super+M | ⌘M = minimizar | Super+M minimiza (scratchpad, sem abrir); sair da sessão só pelo menu Apple<br>_risco de perder a sessão por reflexo_ | ✅ | P1 | `hypr/hyprmac.lua` | padroes/atalhos-de-teclado.md |
| ATL-02 | Super+Q | ⌘Q = sair do app | Super+Q fecha todas as janelas do app (scripts/janela quit-app); terminal foi para Super+Return | ✅ | P2 | `hypr/hyprmac.lua · scripts/janela` | padroes/atalhos-de-teclado.md |
| ATL-03 | Fechar janela | ⌘W | Super+W fecha a janela (Super+C continua) | ✅ | P2 | `hypr/hyprmac.lua` | padroes/atalhos-de-teclado.md |
| ATL-04 | Tela cheia | ⌃⌘F | Super+Ctrl+F (e Super+F) | ✅ | P3 | `hypr/hyprmac.lua` | padroes/atalhos-de-teclado.md |
| ATL-05 | Ocultar app / ocultar outros | ⌘H / ⌥⌘H | Super+H oculta o app, Super+Alt+H oculta os outros; o app oculto volta ao escolhê-lo no Alt+Tab (testado) ou no Dock, nas mesas atuais, como no Mac | ✅ | P3 | `scripts/janela` | padroes/atalhos-de-teclado.md |
| ATL-06 | Capturas | ⇧⌘3 / ⇧⌘4 / ⇧⌘5 (⌃ = área de transferência) | Print / Shift+Print / Ctrl+Print (⌃ = área de transferência); ferramenta ⇧⌘5 em Super+Shift+5 (e Super+Print) abrindo a barra de captura e gravação | ✅ | P3 | `hypr/hyprmac.lua` | padroes/atalhos-de-teclado.md |
| ATL-07 | Seletor de apps | ⌘Tab; Q encerra e H oculta o selecionado; ⌘` janelas do app | Alt+Tab com Q (encerra) e H (oculta) no app selecionado; Super+` / Super+Shift+` passam pelas janelas do app em foco (scripts/janela next-window) | ✅ | P3 | `hypr/hyprmac.lua · shell (AppSwitcher)` | padroes/atalhos-de-teclado.md |
| ATL-08 | Forçar Encerrar | ⌥⌘Esc | Super+Alt+Esc abre "Forçar Encerrar Aplicativos" (hyprmac-shell ForceQuit): texto de instrução, lista de apps com ícone e nome, dica do atalho, botão azul e confirmação "Deseja forçar o encerramento de…" | ✅ | P3 | `shell/hyprmac-shell (ForceQuit) · hypr/hyprmac.lua` | padroes/atalhos-de-teclado.md |

## Recursos do sistema — 73%

| ID | Parâmetro | Apple | hyprmac | | Prio | Onde | Fonte |
|---|---|---|---|---|---|---|---|
| SIS-01 | Dock | vidro quase transparente, ícones 36 passo 45, pontos e separador | Dock no hyprmac-shell, no mesmo processo GTK; dock_model/geometry/motion separados, app_index e eventos compartilhados. Medidas configuráveis herdadas do kit (padrão ícone 46, passo 57, raio ~19), materiais e animações preservados. Indicadores, separadores, Downloads, Lixo, miniaturas, selos, Apps/Spotlight e autohide. Magnificação opcional já implementada; drag reordena fixos, protege Finder e remove fixação ao soltar fora com aviso Remove; app aberto permanece na seção de abertos. Ctrl+clique/botão direito abre menu com Keep in Dock/Remove from Dock, Hide e Quit. Drop text/uri-list abre documentos por Gio em apps compatíveis, sem copiar/mover/apagar. Comportamento textual confirmado em support.apple.com/en-gb/guide/mac-help/mh35859/26/mac/26; gesto real completo, múltiplos monitores/temas e materiais ainda não certificados contra Tahoe. Genie e drops em pastas permanecem ausentes | 🟡 | P1 | `shell/hyprmac-shell (Dock)` | componentes/dock.md |
| SIS-02 | Mission Control / App Exposé | ⌃↑ visão geral com faixa de mesas e + | Ctrl+↑ abre o Mission Control (shell/hyprmac-overview): faixa de mesas com miniaturas reais (grim -T) e "+", janelas espalhadas sem sobreposição com voo de 260 ms, destaque com ícone e título, arrastar para outra mesa; Ctrl+↓ abre o App Exposé: só as janelas do app em foco (em cada tela), sem a faixa das mesas, e as ocultas do app numa fileira menor embaixo após uma linha (clicar traz de volta) | ✅ | P2 | `shell/hyprmac-overview · hypr/hyprmac.lua` | componentes/sistema-e-recursos.md |
| SIS-03 | Tela de bloqueio | medido na foto oficial (MacBook Pro 14" = 1512×982 pt, 1,744 px/pt): data 27 pt wght≈560 (topo 95,3), relógio de vidro 138 pt wght≈647 tracking −5,9 (topo 132,2), avatar 49, nome 15 pt wght≈560 branco sem sombra (base a 88,9 do pé), dica "Touch ID or Enter Password" 12 pt vibrante plus-lighter #999999 sem caixa (base a 59,0), canto: "U.S." 13 Regular + teclado 16×10, bateria 22,5×11,6, Wi‑Fi 14,6×10,4, a 22,4 da borda; data em plus-lighter #646464 (soma ≈100 ao fundo, 3 telas); relógio configurável em Ajustes ▸ Wallpaper ▸ Clock Appearance… (6 estilos + Weight 100–900, mostrar/nunca) | shell/hyprmac-lock (GTK4 + ext-session-lock + PAM): medidas locais aplicadas em pt; dica vibrante, cápsula de senha sob digitação, ícones do canto, um bloqueio por monitor; Super+Ctrl+Q e inatividade. Ajustes ▸ Wallpaper oferece Clock Appearance, peso e prévia; o bloqueio lê estilo/peso/mostrar. Em 2026-10-20, snapshots de repouso e digitação a 1512×982 foram inspecionados; --test-auth rejeitou senha errada via PAM. A foto original citada na fonte não está neste checkout, e o desbloqueio real com senha correta não foi testado; Movimento Reduzido mostra erro textual sem tremida e desativa transições do campo, validado em GTK isolado<br>_estilos estêncil, pesado e linha dupla são fontes internas da Apple (amostra da referência, desativados); New York não instalada; SF Pro Rounded só Medium (sem efeito do Weight); sem referência: cápsula ao digitar, ícone de cabo, popover/folha no modo claro/escuro oposto ao print; falta testar destravar com a senha certa; falta conferir o erro com Movimento Reduzido na sessão real_ | 🟡 | P2 | `shell/hyprmac-lock · shell/lock.css` | referencias/telas/Apple-WWDC25-macOS-Tahoe-26-Lock-Screen-250609.jpg |
| SIS-04 | Widgets da mesa | galeria editável, vários tamanhos, esmaecem com janela na frente, estilos Clear/Tinted | grade de 2 colunas com tamanhos pequeno/médio/grande (Tempo P/M, Calendário, Relógio analógico, Fotos P/M/G, Atalhos); botão direito na mesa ou no widget: tamanhos, Remove Widget, Edit Widgets…, Change Wallpaper…; galeria Edit Widgets (categorias, prévias com +, Done) e "−" em cada widget; esmaecem com janela ativa na tela; arranjo salvo em ~/.config/hyprmac/widgets.json; estilos Default/Dark/Clear/Tinted (View ▸ Icon & Widget Style), Tinted na cor de destaque; no escuro, Tempo em vidro neutro com ícones brancos e Relógio com mostrador de vidro, 60 tracinhos e números brancos (tahoe-dark.jpeg) | ✅ | P3 | `shell/hyprmac-shell (DesktopWidgets, WidgetGallery) · shell/style.css` | componentes/sistema-e-recursos.md |
| SIS-05 | Central de Notificações | abre no relógio, agrupa por app, widgets | abre no relógio, agrupa por app, calendário | ✅ | P3 | `shell/hyprmac-shell (NotifPanel)` | componentes/notificacoes.md |
| SIS-06 | Ferramenta de captura ⇧⌘5 e miniatura flutuante | barra de captura + gravação + miniatura no canto → editor | barra ⇧⌘5 (Super+Shift+5) em cápsula de vidro no rodapé: captura de tela inteira / janela / área + GRAVAÇÃO de tela inteira / área (scripts/gravacao via wf-recorder, com controle ⏹ e cronômetro na barra de menus); Opções com destino, temporizador, Mostrar Miniatura Flutuante e Gravar Microfone; captura para arquivo + área de transferência; miniatura flutuante no canto (clique = editar no Spectacle / abrir o vídeo, arrastar = soltar o arquivo); ⌃ só para a área de transferência. Sem 'mostrar cliques do mouse'; gravação exige o wf-recorder instalado · 2026-10-04 (referencias/desejos/captura-barra-opcoes, 2,39 px/pt): barra refeita nas medidas do Tahoe — 53 de altura, canto 13, ✕ em círculo de 17, 3 capturas (passo 50,6, seleção em quadrado 46×37 canto 6) e 3 gravações (tela, janela — nova, gravacao pick —, área) com ícones em contorno e o ponto de gravação no canto, filetes, "Opções" com chevron.down desenhado, "Capturar" azul 82×38 canto 9; vidro do compositor (camada hyprmac-captura-barra, preset hyprmac-texto) e tema claro/escuro | ✅ | P3 | `scripts/captura · scripts/gravacao · scripts/screenshot · core/capture-thumbnail · hypr/hyprmac.lua` | componentes/sistema-e-recursos.md |
| SIS-07 | Aparência personalizável | ícones Default/Dark/Clear/Tinted, cor de pastas, tingir janelas com o papel de parede | claro/escuro, barra clara/transparente, cor de destaque e estilo de ícones/widgets Default/Dark/Clear/Tinted. Ajustes ▸ Aparência oferece Folder color (Automatic, 8 cores, Choose Color…) e os rádios Dark/Clear; painel antigo foi conferido com video/frames-ui/ui_0099 rotulado macOS 27, sem certificação Tahoe 26. Em 2026-10-20, a cor das pastas passou a colorir os ícones da Mesa e Downloads do Dock por núcleo Rust; ícone vermelho local e tela de Ajustes foram inspecionados. O gerenciador de arquivos externo, símbolos/emojis e o tingimento das janelas pelo papel de parede seguem pendentes; seleção das oito cores e da cor personalizada agora resolvida em Rust pela paleta compartilhada; Graphite corrigido na reserva Python | 🟡 | P3 | `scripts/accent · shell/hyprmac-shell (styled_icon, ViewMenu) · shell/style.css` | componentes/sistema-e-recursos.md |
| SIS-08 | Papel de parede | referências locais de wallpapers declarados macOS 27, secundárias até conferência Tahoe 26 | 2026-10-18: shell segue por padrão org.gnome.desktop.background, mesma origem alterada por Ajustes ▸ Wallpaper; alterações GNOME e de config.json recarregam a imagem e o contraste da barra sem reiniciar. Caminho explícito em config.json continua possível. Fallback local photo-fallback.jpg; asset Tahoe padrão tahoe-light-1080p.jpg ausente neste checkout. Troca branco/preto exercitada localmente, sem certificação visual Tahoe 26 | 🟡 | P3 | `wallpapers/ · shell (Wallpaper)` | referencias/kit/papeis-de-parede |
| SIS-10 | Ícones da Mesa (~/Desktop) | arquivos da Mesa em colunas a partir do canto superior direito; ícone 64, nome 12 branco com sombra; seleção = fundo cinza + nome em cápsula azul; duplo clique abre | shell/hyprmac-shell DesktopIcons: colunas do canto superior direito, ícone 64 (.desktop com ícone do app, demais com miniatura/ícone do tipo), nome 12 com sombra até 2 linhas, seleção cinza + cápsula na cor de seleção, duplo clique abre, botão direito Open / Move to Trash, atualiza ao vivo | ✅ | P2 | `shell/hyprmac-shell (DesktopIcons) · shell/style.css` | comportamento padrão do Finder (sem tela na base) |
| SIS-11 | Cantos ativos (Hot Corners) | Ajustes ▸ Desktop & Dock ▸ Hot Corners…: folha com 4 menus em volta da miniatura do papel de parede (cantos marcados) e Done; levar o ponteiro ao canto dispara a ação (Mission Control, Application Windows, Desktop, Notification Center, Quick Note, Put Display to Sleep, Lock Screen…) | 2026-10-04: folha nas medidas da referência (547 de largura, menus 198×21 passo 40, miniatura 87×61 com triângulos nos cantos, Done); hyprmac-shell HotCorners põe uma camada de 1×1 px em cada canto configurado de cada monitor (dispara uma vez por chegada); ações: Mission Control, Application Windows, Desktop (scripts/janela show-desktop, novo), Notification Center, Put Display to Sleep (mexer/teclar acorda: mouse_move_enables_dpms), Lock Screen. Sem Quick Note e protetor de tela (não há Notas nem protetor) nem as teclas modificadoras do menu | 🟡 | P3 | `shell/hyprmac-ajustes (_hot_corners_sheet), shell/hyprmac-shell (HotCorners), scripts/janela` | referencias/desejos/cantos-ativos-folha.png, ajustes-mesa-dock-cantos-ativos.png |

## Como medir cada um

- **BAR-01** — valor de height; medido na referência: 21 px ÷ 0,617
- **BAR-02** — font-size de window#waybar
- **BAR-03** — font-weight de window#waybar
- **BAR-04** — font-weight de #window
- **BAR-05** — font-size de #custom-apple (o glifo da Nerd Font de 20 mede 13×16, como na referência)
- **BAR-06** — print com grim ampliado; comparar altura e alfa
- **BAR-07** — visual
- **BAR-08** — modules-left
- **BAR-09** — visual
- **BAR-10** — on-click de network/bluetooth/pulseaudio
- **BAR-11** — apertar tecla de volume
- **BAR-12** — abrir a câmera
- **BAR-13** — modules-right × captura de referência
- **BAR-14** — visual
- **BAR-15** — ligar Não Perturbe na Central
- **BAR-16** — trocar o papel de parede e conferir a barra com grim
- **BAR-17** — hyprmac-ajustes --snapshot menubar x.png; marcar/desmarcar e olhar a barra
- **MENU-01** — border-radius de menu
- **MENU-02** — min-height de menuitem
- **MENU-03** — font-size do label
- **MENU-04** — border-radius de menuitem
- **MENU-05** — background de menuitem:hover
- **MENU-06** — padding de menu e menuitem
- **MENU-07** — visual sobre papel de parede colorido
- **MENU-08** — abrir File/Edit
- **MENU-09** — abrir menus sem janela em foco
- **MENU-10** — abrir Window
- **MENU-11** — abrir View
- **MENU-12** — abrir Edit
- **CC-01** — GAP ÷ C
- **CC-02** — print lado a lado com Apple-WWDC25-…-Control-Center
- **CC-03** — ligar Bluetooth nos dois temas
- **CC-04** — Editar Controles
- **CC-05** — Editar Controles
- **CC-06** — Editar Controles
- **CC-07** — abrir a Central nos dois temas
- **CC-08** — abrir a Central com/sem música
- **CC-09** — visual
- **CC-10** — abrir/fechar
- **NOT-01** — BANNER_W
- **NOT-02** — border-radius de .notif
- **NOT-03** — ICON
- **NOT-04** — font-size
- **NOT-05** — font-size
- **NOT-06** — padding
- **NOT-07** — print
- **NOT-08** — mandar 3 notificações do mesmo app
- **NOT-09** — visual
- **WIN-01** — decoration.rounding
- **WIN-02** — rounding_power (> 2 = contínuo)
- **WIN-10** — general.gaps_out
- **WIN-11** — Ghostty com 2 abas
- **WIN-03** — grim + pixel na borda: 30→75 na ativa (0.200), papel de parede escurecido à metade fora
- **WIN-04** — duas janelas
- **WIN-05** — print ampliado
- **WIN-06** — print: círculo vermelho em (9,9) no Ghostty, (18,19) na barra unificada
- **WIN-07** — valor
- **WIN-08** — uso
- **WIN-12** — pixel da seleção × fundo da barra
- **WIN-13** — visual
- **WIN-14** — barra lateral mais escura que o conteúdo e tingida pelo papel de parede
- **COR-01** — @mac_accent padrão; igualdade do token não valida material ou interação
- **COR-02** — @mac_accent claro
- **COR-03** — @mac_destructive
- **COR-04** — @green
- **COR-05** — valor
- **COR-06** — valor
- **COR-07** — —
- **TIP-01** — fc-list | grep -i 'SF Pro'; a família do kit é "SF Pro"
- **TIP-02** — grep font-size
- **TIP-03** — visual
- **VID-01** — comparar print de painel sobre o mesmo papel de parede
- **VID-02** — revisão de CSS
- **VID-03** — visual
- **VID-04** — raio externo − padding vs raio interno
- **VID-05** — valor
- **VID-06** — —
- **VID-07** — fundo de listras atrás do painel (scratchpad fundo.py)
- **VID-08** — slider nos dois extremos
- **VID-09** — quadros da abertura da Central
- **MOV-01** — abrir CC e depois o relógio
- **MOV-02** — abrir cada painel
- **MOV-03** — Editar Controles
- **SPT-01** — Super+Espaço, Super+1/4
- **SPT-02** — —
- **SPT-03** — Super+Shift+V
- **SPT-04** — gdbus … Command "spotlight preview <texto>" (não pega o teclado) + grim
- **SPT-05** — spotlight preview +ctl (sem teclado) e quadros com grim
- **ATL-01** — hyprctl binds
- **ATL-02** — hyprctl binds
- **ATL-03** — hyprctl binds
- **ATL-04** — hyprctl binds
- **ATL-05** — —
- **ATL-06** — hyprctl binds
- **ATL-07** — Alt+Tab
- **ATL-08** — —
- **SIS-01** — print da base da tela
- **SIS-02** — —
- **SIS-03** — hyprmac-lock --snapshot ARQ --demo --size 1512x982 (GDK_BACKEND=broadway) e comparar com a foto
- **SIS-04** — —
- **SIS-05** — clicar no relógio
- **SIS-06** — —
- **SIS-07** — —
- **SIS-08** — —
- **SIS-10** — mesa vazia
- **SIS-11** — HYPRMAC_AJUSTES_OPEN=hotcorners hyprmac-ajustes --snapshot desktop x.png; cursor no canto (hl.dsp.cursor.move)
