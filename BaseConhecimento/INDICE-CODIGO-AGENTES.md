# Índice de código para agentes

Metadados para localizar candidatos antes de ler arquivos completos.

| Caminho | Linguagem | Linhas | Tags | Resumo |
|---|---|---:|---|---|
| `ghostty/macos.css` | css | 78 | ghostty, menu, window | hyprmac — barra de título do Ghostty como a do Terminal no Mac: kit "Windows/Dark/Default + Title": barra de 33, padding 9, semáforo em |
| `gtk/a11y3.css` | css | 1 | gtk | gerado por scripts/acessibilidade */ |
| `gtk/a11y4.css` | css | 1 | gtk | gerado por scripts/acessibilidade */ |
| `gtk/accent3.css` | css | 7 | gtk, theme | gerado por scripts/accent — cor de destaque: blue (escuro) */ @define-color mac_accent      #007AFF; |
| `gtk/accent4.css` | css | 11 | gtk, theme | gerado por scripts/accent — cor de destaque: blue (escuro) */ @define-color mac_accent      #007AFF; |
| `gtk/gtk3.css` | css | 615 | gtk, menu, theme, window | hyprmac — GTK 3 no modo escuro do macOS Tahoe Aplicado por cima do Adwaita-dark (embutido no GTK, nada instalado). |
| `gtk/gtk4.css` | css | 377 | gtk, menu, theme, window | hyprmac — GTK 4 / libadwaita no modo escuro do macOS Tahoe Carregado por ~/.config/gtk-4.0/gtk.css. As cores vêm de palette4.css |
| `gtk/palette3-dark.css` | css | 59 | gtk, menu, theme, window | hyprmac — paleta GTK 3, modo escuro */ ───────────── paleta ───────────── */ |
| `gtk/palette3-light.css` | css | 59 | gtk, menu, theme, window | hyprmac — paleta GTK 3, modo claro */ ───────────── paleta ───────────── */ |
| `gtk/palette3.css` | css | 59 | gtk, menu, theme, window | hyprmac — paleta GTK 3, modo escuro */ ───────────── paleta ───────────── */ |
| `gtk/palette4-dark.css` | css | 81 | gtk, menu, theme, window | hyprmac — paleta GTK 4 / libadwaita, modo escuro */ ───────────── paleta (libadwaita ≥ 1.6 usa variáveis CSS) ───────────── */ |
| `gtk/palette4-light.css` | css | 81 | gtk, menu, theme, window | hyprmac — paleta GTK 4 / libadwaita, modo claro */ ───────────── paleta (libadwaita ≥ 1.6 usa variáveis CSS) ───────────── */ |
| `gtk/palette4.css` | css | 81 | gtk, menu, theme, window | hyprmac — paleta GTK 4 / libadwaita, modo escuro */ ───────────── paleta (libadwaita ≥ 1.6 usa variáveis CSS) ───────────── */ |
| `hypr/hyprmac.lua` | lua | 554 | hypr, dock, spotlight, notification, lock, menu | hyprmac — aparência macOS Tahoe (modo escuro) para Hyprland Carregado no fim do hyprland.lua; tudo aqui sobrescreve os padrões de lá. |
| `hypr/vidro-presets.lua` | lua | 219 | hypr, dock, spotlight, notification, menu, glass | hyprmac — presets de Liquid Glass para o plugin hyprglass Presets próprios e camadas só valem quando o Hyprland LÊ a config (o hyprglass os guarda |
| `scripts/accent` | python | 112 | scripts, menu, theme | """hyprmac — cor de destaque do sistema (Ajustes ▸ Aparência ▸ Cor de Destaque do macOS). accent                 reaplica a cor atual (usado por scripts/theme ao trocar claro/escuro) |
| `scripts/acessibilidade` | python | 91 | scripts, menu, glass, window | """hyprmac — Reduzir Transparência e Aumentar Contraste (Acessibilidade ▸ Tela no macOS). acessibilidade                         reaplica o estado salvo |
| `scripts/bar-style` | bash | 15 | scripts, menu | hyprmac — alterna a barra de menus entre transparente e clara fosca bar-style [toggle/light/transparent] |
| `scripts/build-waybar-extras` | bash | 57 | scripts, lock, menu | Build isolada do tray nativo 0.15.0; nunca instala sobre /usr/bin/waybar. set -euo pipefail |
| `scripts/captura` | python | 422 | scripts, dock, menu, glass, window | """hyprmac — barra de Captura de Tela (⇧⌘5 do macOS), sem gravação. Cápsula de vidro escuro no rodapé da tela, como no Tahoe: |
| `scripts/captura-miniatura` | python | 172 | scripts, window | """hyprmac — miniatura flutuante depois de uma captura de tela (como no macOS). captura-miniatura <imagem.png> [--abrir <arquivo>] |
| `scripts/clipboard` | python | 159 | scripts | """hyprmac — histórico da área de transferência (como o ⌘Espaço ⌘4 do Tahoe). clipboard watch    vigia a área de transferência (autostart do hyprmac.lua) |
| `scripts/gravacao` | python | 261 | scripts, menu, window | """hyprmac — gravação de tela da ferramenta ⇧⌘5 (como no macOS). gravacao screen   grava o monitor em foco |
| `scripts/janela` | python | 99 | scripts, menu, window | """hyprmac — comandos de app no estilo macOS (atalhos e menu do app). janela quit-app      fecha todas as janelas do app em foco        (⌘Q) |
| `scripts/menu-extras` | python | 191 | scripts, lock, menu | """Configuração e diagnóstico pontuais dos extras SNI. Não permanece residente.""" ROOT = Path(__file__).resolve().parent.parent |
| `scripts/ocioso` | bash | 65 | scripts, lock | hyprmac — inatividade como no Mac (Ajustes ▸ Tela de Bloqueio): ocioso start    inicia o vigia (shell/ocioso/hyprmac-ocioso), uma instância só |
| `scripts/scratchpad` | bash | 14 | scripts, window | hyprmac — mostra/esconde o scratchpad (área especial "magic"). Vazio, o Hyprland o fecha na hora (misc:close_special_on_empty) e parecia que |
| `scripts/screenshot` | bash | 89 | scripts, window | hyprmac — capturas de tela no estilo macOS (grim + slurp)  |
| `scripts/spotlight` | bash | 106 | scripts, spotlight, menu | hyprmac — Spotlight do shell GTK. Chamar de novo fecha. spotlight [apps/files/actions/clipboard] |
| `scripts/spotlight-itens` | python | 672 | scripts, control center, spotlight, notification, lock, menu | """hyprmac — itens dos modos Arquivos (⌘2) e Ações (⌘3) do Spotlight, e o histórico. Chamado por scripts/spotlight; não abre janelas (só o "Restart…/Shut Down…/Log Out…" |
| `scripts/theme` | bash | 70 | scripts, spotlight, menu, glass, theme | hyprmac — alterna o tema do sistema entre claro e escuro theme [toggle/light/dark] |
| `scripts/vidro` | bash | 144 | scripts, menu, glass | hyprmac — Liquid Glass via plugin hyprglass (refração, realce especular, chanfro) vidro instalar     compila o hyprglass na tag certa para o Hyprland em uso |
| `scripts/vpn` | bash | 46 | scripts | hyprmac — VPN do NetworkManager vpn status        JSON contínuo para a Waybar (atualiza a cada mudança de rede) |
| `shell/a11y-contraste.css` | css | 20 | shell, menu, control, center, control_center | hyprmac — Aumentar Contraste (Acessibilidade ▸ Tela no macOS) Bordas de 1 px bem visíveis em volta de vidros e controles, texto secundário |
| `shell/a11y-transparencia.css` | css | 29 | shell, menu, control, center, control_center | hyprmac — Reduzir Transparência (Acessibilidade ▸ Tela no macOS) Os vidros viram superfícies sólidas: mesmo tom do vidro, opaco. Carregado |
| `shell/accent_palette.py` | python | 22 | shell | """Destaques AppKit Tahoe 26; não confundir com system*Color do kit.""" nome → (escuro, claro): controlAccent*Color do macOS Tahoe 26.6.1 (25G76), lidos de |
| `shell/ajustes.css` | css | 454 | shell, lock, menu, glass, window | hyprmac — Ajustes do Sistema (System Settings do Tahoe). Kit macOS 27: janela #1E1E1E (escuro) / #FFFFFF (claro), raio 26; barra lateral |
| `shell/app_index.py` | python | 69 | shell, dock, spotlight, theme, window | """Índice compartilhado de aplicativos instalados para os componentes do shell.""" gi.require_version("Gtk", "3.0") |
| `shell/cocoa_entry.py` | python | 102 | shell | """Edição compartilhada dos campos GTK3 próprios do HyprMac. Mapeamentos: AppKit StandardKeyBinding.dict, Tahoe 26.6.1 (25G76). |
| `shell/desktop_surface.py` | python | 1275 | shell, lock, menu, theme, window | """Wallpaper, desktop widgets and desktop icons in the shared shell process.""" gi.require_version("Gtk", "3.0") |
| `shell/dock_drop.py` | python | 64 | shell, dock | """Abrir documentos no app de destino do Dock; sem GTK, cópia ou execução shell.""" def desktop_file_from_uris(uris, new_file): |
| `shell/dock_geometry.py` | python | 50 | shell, dock | """Medidas, layout de repouso e hit testing do Dock; unidades lógicas GTK.""" @dataclass(frozen=True) |
| `shell/dock_model.py` | python | 89 | shell, dock, window | """Conteúdo e política de atualização do Dock, sem GTK ou consultas ao compositor.""" REFRESH_EVENTS = frozenset(( |
| `shell/dock_motion.py` | python | 91 | shell, dock, lock | """Estado das molas, magnificação e quique do Dock; sem relógios ou timers próprios.""" class DockMotion: |
| `shell/dock_widget.py` | python | 1326 | shell, dock, spotlight, notification, lock, menu | """GTK view for the Dock. The shell supplies its shared UI and compositor services.""" gi.require_version("Gtk", "3.0") |
| `shell/glass_motion.py` | python | 27 | shell, glass | """Mola de transição baseada no GlassContainer do Tahoe 26.6.1 (25G76). TransitionSettings.default: duration=.5, bounce=.3 (SwiftUICore), recuperados |
| `shell/hypr_events.py` | python | 49 | shell | """Uma conexão com o socket de eventos do Hyprland para todo o shell GTK.""" class EventBus: |
| `shell/hyprmac-ajustes` | python | 3425 | shell, dock, spotlight, notification, lock, menu | """hyprmac — Ajustes do Sistema (System Settings do macOS Tahoe). hyprmac-ajustes [painel]     abre (ou traz para a frente) num painel: wifi, bluetooth, |
| `shell/hyprmac-lock` | python | 1409 | shell, lock, glass, window | """hyprmac-lock — tela de bloqueio no estilo do macOS Tahoe (GTK4 + ext-session-lock). Uso: |
| `shell/hyprmac-overview` | python | 1502 | shell, menu, theme, window | """hyprmac-overview — Mission Control do macOS para o Hyprland (GTK3 + gtk-layer-shell). Como a Apple fez (macOS Tahoe/27, ⌃↑): |
| `shell/hyprmac-preview` | python | 269 | shell, window | """Visualizador local: ações documentadas no Preview 26.6.1, layout experimental.""" gi.require_version("Gtk", "3.0") |
| `shell/hyprmac-shell` | python | 6278 | shell, dock, control center, spotlight, notification, lock | """hyprmac-shell — papel de parede, widgets da mesa e Central de Controle no estilo macOS Tahoe, para Hyprland (GTK3 + gtk-layer-shell). |
| `shell/lock.css` | css | 130 | shell, lock, window | hyprmac-lock — tela de bloqueio no estilo macOS Tahoe. Medidas em PONTOS da tela oficial da WWDC25 (MacBook Pro 14" = 1512×982 pt, 1,744 px/pt |
| `shell/session_overlays.py` | python | 346 | shell, dock, window | """Force Quit and app switcher overlays for the shell session.""" gi.require_version("Gtk", "3.0") |
| `shell/spotlight_controls.py` | python | 228 | shell, spotlight, lock, glass | """Controles de modo do Spotlight: desenho e animação GTK3. O painel permanece no processo do shell. Este módulo apenas desenha os |
| `shell/spotlight_search.py` | python | 134 | shell, spotlight | """Categorias, ordenação e cálculo do Spotlight; sem dependência de GTK. As categorias legadas derivadas de frames rotulados macOS 27 exigem validação Tahoe 26. |
| `shell/spotlight_view.py` | python | 1566 | shell, dock, spotlight, lock, menu, glass | """Spotlight GTK view and transitions, using the shared search/control modules.""" gi.require_version("Gtk", "3.0") |
| `shell/style-light.css` | css | 441 | shell, spotlight, menu, glass, control, center | keyboardFocusIndicatorColor, Aqua Tahoe 26.6.1 (25G76). */ @define-color shell_focus #3b99fc; |
| `shell/style.css` | css | 1720 | shell, dock, spotlight, notification, lock, menu | hyprmac-shell — widgets e Central de Controle no estilo Liquid Glass (macOS Tahoe). O desfoque de fundo vem do Hyprland (layer rules "hyprmac-widgets" e "hyprmac-cc"); |
| `shell/vidro-camadas-claro.css` | css | 25 | shell, spotlight, menu, glass, control, center | hyprmac — vidro real no tema CLARO: os painéis com texto (menus, notificações, Spotlight, Alt+Tab, histórico) levam mais branco por cima e texto escuro, como o menu "Folder color" e |
| `shell/vidro-camadas.css` | css | 89 | shell, spotlight, menu, glass, control, center | hyprmac — vidro de verdade nas camadas (plugin hyprglass carregado; os DOIS temas — o vidro é o mesmo; no claro, vidro-camadas-claro.css só clareia os painéis com texto) |
| `shell/vidro.py` | python | 75 | shell, glass, theme, window | """Liquid Glass do hyprmac (plugin hyprglass) para janelas GTK. O vidro é desenhado pelo compositor; a janela GTK só precisa ser transparente onde o |
| `tests/fixtures/status_notifier.py` | python | 120 | tests, menu | """SNI de teste: ícones ARGB, atenção/overlay, estado, eventos e menu D-Bus. Uso: status_notifier.py /tmp/events.jsonl |
| `tests/test_accent_palette.py` | python | 58 | tests, theme | """Integração do destaque entre gerador, Ajustes e Mission Control.""" ROOT = Path(__file__).resolve().parents[1] |
| `tests/test_cocoa_entry.py` | python | 192 | tests, spotlight, window | """Edição no Gtk.Entry real; não altera atalhos de aplicações externas.""" sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'shell')) |
| `tests/test_dock.py` | python | 655 | tests, dock, lock, menu, glass, window | """Regressão do núcleo do Dock e dos contratos entre núcleo, GTK e eventos.""" sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "shell")) |
| `tests/test_dock_recipe.py` | python | 58 | tests, dock | """Casos dimensionais conferidos com emulação ARM64 independente (25G76).""" PATH = Path(__file__).resolve().parents[1] / 'BaseConhecimento/ferramentas/receita_dock.py' |
| `tests/test_fidelity_qa.py` | python | 71 | tests, dock, window | """QA independente de gestos e atualização, executando métodos reais do Dock.""" class DockGestureLifecycleQA(unittest.TestCase): |
| `tests/test_glass_motion.py` | python | 41 | tests, glass | sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'shell')) class GlassTransitionTests(unittest.TestCase): |
| `tests/test_install_preflight.py` | python | 59 | tests, lock | """O instalador não substitui configurações por fontes ausentes.""" INSTALL = (Path(__file__).resolve().parents[1] / "install.sh").read_text() |
| `tests/test_keyboard_focus.py` | python | 207 | tests, dock, window | """MIC-04: foco global pelo teclado (HIG ▸ Keyboards). ⌃F4 / ⌃⇧F4 percorrem as janelas de qualquer app (scripts/janela next-any/prev-any); |
| `tests/test_menu_extras.py` | python | 53 | tests, menu | """Preferências dos extras: isolamento, persistência e identidades SNI.""" ROOT = Path(__file__).resolve().parents[1] |
| `tests/test_reduce_motion_shell.py` | python | 89 | tests, spotlight, glass | """MIC-14: com Reduce Motion, o shell não agenda animações elásticas nem de deslocamento. Evidência Apple (WWDC25 219, Meet Liquid Glass): "Reduced Motion decreases the |
| `tests/test_shell_events.py` | python | 83 | tests, dock, menu, window | """Regressões do assinante único do Hyprland e dos menus dinâmicos da barra.""" ROOT = Path(__file__).resolve().parents[1] |
| `tests/test_sni_watcher.py` | python | 143 | tests, window | """Teste opt-in da build real: execute dentro de dbus-run-session. HYPRMAC_TEST_SNI_WATCHER=1 dbus-run-session -- python -m unittest discover -s tests -p test_sni_watcher.py |
| `tests/test_spotlight_arg_actions.py` | python | 75 | tests, spotlight, menu | """SPT-03: ações que rodam pelo Spotlight sem abrir o app ("ar buy milk" → lembrete). Mac User Guide (Tahoe 26) ▸ Take actions and shortcuts in Spotlight: digitar a quick key |
| `tests/test_spotlight_launcher.py` | python | 60 | tests, spotlight | """O atalho não troca para o Wofi quando o shell está iniciando.""" SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/spotlight' |
| `tests/test_spotlight_mode_hover.py` | python | 120 | tests, spotlight, glass | """MIC-09: o hover nos botões de modo do Spotlight antecipa o nome e o atalho no campo. Referência Tahoe 26: referencias/telas/spotlight-controles-2…6 — ponteiro sobre |
| `tests/test_spotlight_quickkeys.py` | python | 66 | tests, spotlight, lock, window | """SPT-07: quick keys do Spotlight (Mac User Guide ▸ Take actions and shortcuts in Spotlight). "Click 'Add quick keys' next to an action, then enter the keyboard shortcut"; |
| `tests/test_spotlight_search.py` | python | 30 | tests, spotlight | """Comportamentos de busca preservados após extrair a lógica do Spotlight.""" sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "shell")) |
| `tests/test_spotlight_selector.py` | python | 188 | tests, spotlight, theme, window | """Seletor e busca em app, sem GTK nem display.""" ROOT = Path(__file__).resolve().parents[1] |
| `tests/test_system_fidelity.py` | python | 223 | tests, spotlight, lock, menu, theme | """Regressões funcionais dos subpainéis da Central, sem iniciar GTK.""" ROOT = Path(__file__).resolve().parents[1] |
| `tests/test_volume_feedback.py` | python | 103 | tests, dock, lock, theme | """MIC-12: "Play feedback when volume is changed" (Ajustes ▸ Som do macOS Tahoe 26). support.apple.com/guide/mac-help/mchlp2207/26: "when you press one of the volume |
| `waybar/a11y.css` | css | 1 | waybar | gerado por scripts/acessibilidade */ |
| `waybar/accent.css` | css | 3 | waybar, menu | gerado por scripts/accent — cor de destaque: blue (escuro) */ @define-color accent         #007AFF; |
| `waybar/barra-ocultos.css` | css | 0 | waybar | barra-ocultos.css |
| `waybar/config.jsonc` | jsonc | 565 | waybar, dock, spotlight, lock, menu, window | hyprmac — Waybar inspirada no macOS Tahoe "layer": "top", |
| `waybar/contrast-dark.css` | css | 115 | waybar, spotlight, lock, menu, window | hyprmac — barra TRANSPARENTE sobre papel de parede claro: texto e ícones escuros. No macOS Tahoe a barra transparente troca a cor do conteúdo conforme o fundo: preto sobre |
| `waybar/contrast.css` | css | 115 | waybar, spotlight, lock, menu, window | hyprmac — barra TRANSPARENTE sobre papel de parede claro: texto e ícones escuros. No macOS Tahoe a barra transparente troca a cor do conteúdo conforme o fundo: preto sobre |
| `waybar/mode.css` | css | 0 | waybar | mode.css |
| `waybar/modes/light.css` | css | 118 | waybar, spotlight, lock, menu, window | hyprmac — barra de menus clara e fosca (estilo macOS com vidro claro) Copiado para waybar/mode.css pelo script scripts/bar-style. |
| `waybar/scripts/app-about.sh` | bash | 30 | waybar, scripts, menu, window | "About <App>" do menu do app: mostra nome, versão e pacote do app em foco numa notificação (o Linux não tem uma janela "Sobre" padrão para todo app). |
| `waybar/scripts/app-menu.py` | python | 40 | waybar, scripts, menu, window | """Um resultado de menu por foco; o shell sinaliza a Waybar quando a classe muda. Uso: app-menu.py <rótulo> <regex de classe>. O snapshot atômico do shell evita |
| `waybar/scripts/camera.sh` | bash | 16 | waybar, scripts | Câmera em uso → cápsula verde com o ícone da câmera na barra (o indicador de privacidade do macOS; o módulo "privacy" do Waybar não conhece câmera). |
| `waybar/scripts/cc-state.sh` | bash | 7 | waybar, scripts, control, center, control_center | Estado do ícone da Central de Controle: "active" enquanto o painel está aberto. if [ -e "${XDG_RUNTIME_DIR:-/tmp}/hyprmac-cc-open" ]; then |
| `waybar/scripts/clock.sh` | bash | 15 | waybar, scripts, lock, menu | Relógio da barra de menus como na referência do Tahoe ("Sun 12:07"): dia da semana abreviado + hora, sem data; a data completa fica na dica. Em inglês, como os menus, |
| `waybar/scripts/input-source.sh` | bash | 36 | waybar, scripts | """Fonte de entrada na barra ("BR", como no Tahoe): sigla do layout ativo do teclado principal, em maiúsculas. Reescreve a cada troca de layout (evento activelayout do |
| `waybar/style.css` | css | 493 | waybar, spotlight, lock, menu, glass, theme | hyprmac — barra de menus inspirada no macOS Tahoe  |
| `waybar/theme.css` | css | 0 | waybar, theme | theme.css |
| `waybar/themes/light.css` | css | 44 | waybar, menu, theme | hyprmac — tema claro da barra: menus suspensos e dicas em vidro claro. Copiado para waybar/theme.css por scripts/theme. Os seletores com :not(.x) |
| `waybar/vidro.css` | css | 7 | waybar, menu, glass | gerado por scripts/vidro: menus com Liquid Glass do hyprglass */ menu:not(.x), |
| `wofi/accent.css` | css | 2 | wofi | gerado por scripts/accent — cor de destaque: blue (escuro) */ @define-color accent #007AFF; |
| `wofi/style.css` | css | 119 | wofi, spotlight, glass, theme, window | hyprmac — Spotlight (wofi) em Liquid Glass escuro. O desfoque vem da layer rule "hyprmac-spotlight" do Hyprland. */ |
| `wofi/theme.css` | css | 0 | wofi, theme | theme.css |
| `wofi/themes/light.css` | css | 31 | wofi, spotlight, theme, window | hyprmac — Spotlight (wofi) em vidro claro. Copiado para wofi/theme.css. #window:not(.x) só dá especificidade sobre o style.css. */ |

## Recuperação progressiva

1. filtre por caminho, linguagem ou tag;
2. leia `summary` e `symbols`;
3. recupere um trecho relevante;
4. carregue o arquivo completo somente quando necessário.
