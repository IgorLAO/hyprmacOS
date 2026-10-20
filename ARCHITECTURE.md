# Arquitetura atual do HyprMac

O HyprMac é uma camada de desktop para Hyprland/Wayland. O objetivo visual e
comportamental vigente é **macOS Tahoe 26**. A interface é composta por processos
e arquivos de configuração, não por um único aplicativo.

| Camada | Implementação | Responsabilidade |
|---|---|---|
| Compositor | `hypr/hyprmac.lua`, `hypr/vidro-presets.lua` | Gaps zero, curvatura, sombra, blur, regras de layer/window, atalhos e autostart. |
| Shell | `shell/hyprmac-shell`, `shell/style.css` | Dock, Central de Controle, Spotlight, notificações, widgets, menus e alternador de apps (Python/GTK3/LayerShell). |
| Módulos do shell | `shell/hypr_events.py`, `shell/app_index.py`, `shell/spotlight_search.py`, `shell/spotlight_controls.py`, `shell/cocoa_entry.py` | Uma conexão de eventos Hyprland; índice de apps compartilhado; busca/cálculo do Spotlight sem GTK; desenho e animação dos controles em GTK3; edição de texto compartilhada entre as buscas do Spotlight, Central, Clipboard e Ajustes. |
| Núcleo do Dock | `core/dock-model/`, `shell/dock_model.py`, `core/dock-geometry/`, `shell/dock_geometry.py`, `shell/dock_motion.py`, `shell/dock_drop.py` | Composição de seções, eventos e fixação e geometria lógica executam em Rust; os módulos Python preservam os contratos da view GTK e resolvem objetos Gio. Movimento e abertura de documentos seguem separados, sem processo nem socket próprios. |
| Views do shell | `shell/desktop_surface.py`, `shell/dock_widget.py`, `shell/session_overlays.py`, `shell/spotlight_view.py` | Papel de parede, widgets e ícones da mesa; desenho, gestos e menus do Dock; alternador de apps e Force Quit; view do Spotlight. Recebem serviços do processo principal por fábrica, sem conexão ou processo adicional. |
| Janelas auxiliares | `shell/hyprmac-ajustes`, `shell/hyprmac-overview`, `shell/hyprmac-lock` | Ajustes (GTK3), Mission Control (GTK3/LayerShell) e bloqueio (GTK4/PAM/ext-session-lock-v1). |
| Barra | `waybar/config.jsonc`, `waybar/style.css`, `waybar/scripts/` | Menus globais, extras e estado do aplicativo em foco. |
| Comandos da barra | `core/waybar-status/` | Binário Rust para menus condicionais, relógio, fonte de entrada, quatro indicadores, ação About e persistência das preferências SNI; instalado em `~/.local/bin/hyprmac-waybar`. |
| Aparência automática | `core/appearance/` | Binário Rust decide o tema em modo Auto após 60 s de inatividade, usando o vigia C existente. |
| Ações de janela | `core/window-actions/` | Binário Rust executa Hide, Quit, Show Desktop e ciclo de foco por snapshots do Hyprland. |
| Clipboard | `core/clipboard/` | Binário Rust vigia, guarda e limpa o histórico usado pelo painel GTK do shell. |
| Acessibilidade | `core/accessibility/` | Binário Rust persiste as opções de transparência e contraste e gera o CSS compartilhado. |
| Cor de destaque | `core/accent/` | Binário Rust gera CSS de destaque a partir da paleta Tahoe compartilhada em JSON. |
| Miniatura de captura | `core/capture-thumbnail/` | Binário Rust GTK3/LayerShell desenha a prévia flutuante, aceita clique e arraste de arquivo e fecha após cinco segundos sem interação. |
| Captura de tela | `core/screenshot/`, `scripts/screenshot` | Binário Rust seleciona área, janela ou monitor e coordena grim, clipboard, som e miniatura; o caminho do script é um invólucro Bash. |
| Barra de captura | `core/capture-bar/`, `scripts/captura` | Binário Rust GTK3/LayerShell mostra os seis modos, opções, atalhos e inicia captura ou gravação. O script é um invólucro Bash; os binds chamam o binário instalado. A layer `hyprmac-captura-barra` tem desfoque próprio e nos popups em `hypr/hyprmac.lua`. |
| Gravação de tela | `core/screen-recording/`, `scripts/gravacao` | Binário Rust: `main.rs` coordena `wf-recorder`, `hypr.rs` consulta monitor/janelas, `process_control.rs` cuida de PID e timer, `ui.rs` desenha o controle flutuante. O instalador cria o link em `~/.local/bin` e o script Bash mantém a entrada usada pela barra e pela Central. |
| Consultas de runtime | `core/runtime-helpers/`, `scripts/scratchpad`, `scripts/ocioso` | Binário Rust lê o estado do scratchpad, opções de inatividade e prontidão do bloqueio; os scripts Bash mantêm o fluxo de ações. |
| Movimento compartilhado | `core/motion/`, `shell/glass_motion.py` | Biblioteca Rust integra a mola usada por controles, Spotlight e Dock; o módulo Python mantém a interface para as views GTK existentes. |
| Cor das pastas | `core/folder-color/`, `shell/folder_appearance.py` | Biblioteca Rust resolve a cor global pela paleta compartilhada e recolore os pixels RGBA; a ponte GTK aplica o resultado à Mesa e ao Downloads do Dock. Pastas da Mesa podem guardar cor e símbolo/emoji próprios em atributos `user.hyprmac.*`, desenhados por `desktop_surface.py`. |
| Busca do Spotlight | `core/spotlight-search/`, `shell/spotlight_search.py` | Biblioteca Rust normaliza texto, pontua resultados, resolve categorias e seletores, separa filtros de arquivo e avalia contas comuns; o módulo Python mantém a interface da view e os escopos de app. |
| Teclas rápidas do Spotlight | `core/spotlight-quickkeys/`, `shell/spotlight_quickkeys.py` | Biblioteca Rust calcula sugestões, resolve conflitos e persiste as teclas rápidas; o módulo Python mantém a API da view GTK. |
| Histórico do Spotlight | `core/spotlight-history/`, `scripts/spotlight-itens` | Biblioteca Rust mantém a ordem das escolhas por modo, o cache drun e a persistência; o script preserva a API importada pela view GTK e seu comando. |
| Integração | `scripts/`, `gtk/`, `kde/`, `ghostty/`, `wofi/` | Tema, captura, ações de janela, vidro, acessibilidade e integração com apps. |
| Vidro | `scripts/vidro`, `shell/vidro.py`, plugin externo `hyprglass` | Instala/carrega a versão compatível do plugin e aplica presets às superfícies permitidas. |
| Instalação | `install.sh` | Cria links/configurações e backups de arquivos do usuário. Exige a localização `~/Projects/hyprmac`. |
| Mapa de status | `core/status-map/`, `scripts/status-map` | Gerador Rust dos SVGs e do bloco do README, chamado pelo hook e pelo workflow. |
| Matriz de comparação | `core/comparison/`, `BaseConhecimento/ferramentas/comparar.py` | Binário Rust mede parâmetros no código, gera `MATRIZ.md` e atualiza a tabela SQLite. O caminho `.py` é um invólucro Bash para compatibilidade com comandos existentes. |
| Auditoria da base | `core/audit/`, `BaseConhecimento/ferramentas/auditar_base.py` | Binário Rust confere SQLite, hashes de fontes e links operacionais; o caminho `.py` é um invólucro Bash. |
| Índice de código | `core/code-index/`, `BaseConhecimento/ferramentas/indexar_codigo.py` | Binário Rust percorre os componentes e gera `codigo.json` e `INDICE-CODIGO-AGENTES.md`; o caminho `.py` é um invólucro Bash. |
| Consulta da base | `core/query/`, `BaseConhecimento/ferramentas/consultar.py` | Binário Rust consulta o SQLite em modo somente leitura, com FTS, catálogos e proveniência; o caminho `.py` é um invólucro Bash. |
| Indexação da base | `core/knowledge-index/`, `BaseConhecimento/ferramentas/indexar.py` | Binário Rust atualiza fontes textuais, FTS, catálogos e hashes por SHA-256, preservando a curadoria e os snapshots ausentes; o caminho `.py` é um invólucro Bash. |

## App Factory (expansão dos apps)

`shell/app_factory_registry.py` valida os manifestos em `shell/app-manifests/`.
`shell/hyprmac-app` abre a janela GTK3 compartilhada em `shell/app_factory_window.py`
ou executa um backend externo declarado. A janela reutiliza `gtk/gtk3.css`,
`shell/app_theme.py`, o índice XDG do shell e os semáforos GTK existentes.
`scripts/generate-app-factory` produz manifestos, ícones e lançadores apenas
para os 55 ausentes da matriz Tahoe 26.6.1; os 15 parciais existentes não são
substituídos. Os `.desktop` gerados são instalados por `install.sh`, e
`hypr/app-factory-classes.lua` aplica regras de janela apenas a esses IDs.
O catálogo `BaseConhecimento/referencias/hyprmac-apps-progress.json` guarda
estado e validação independentes da triagem original. Layouts sem referência
de janela Tahoe permanecem provisórios.

O fluxo de execução começa em `hypr/hyprmac.lua`, carregado pelo `hyprland.lua`
do usuário. O evento `hyprland.start` inicia Waybar, shell, clipboard, cache da
tela de bloqueio e serviço de inatividade. O shell conversa com Hyprland por
`hyprctl` e com serviços do usuário por subprocessos e D-Bus. Os temas claro e
escuro atravessam GTK, KDE, Waybar, Ghostty e o compositor via `scripts/theme`.
O patch local antigo está ausente. O hyprglass v0.9.0 cobre máscaras alfa de
layers no upstream, mas não o comando legado que declarava peças de janelas;
veja `STATUS.md`.
O shell publica a classe em foco em `hyprmac-active-class.json` no diretório de
runtime e sinaliza a Waybar com `SIGRTMIN+11` somente quando ela muda. Os 13
módulos de menu executam `hyprmac-waybar app-menu` uma vez por sinal; sem o shell, o comando
consulta a janela ativa diretamente. Não há um daemon adicional para os menus.

O Dock recebe snapshots pelo shell e resolve aplicativos pelo `AppIndex` existente.
`hyprmac-shell` cria a classe GTK em `dock_widget.create_dock_class` depois de
inicializar os serviços compartilhados. A fábrica vincula callbacks explícitos
para eventos, menus, aparência e compositor; a view não abre outro socket.
`session_overlays.create_session_overlays` usa o mesmo padrão para o alternador
de apps e Force Quit. `desktop_surface.create_desktop_classes` vincula os
serviços compartilhados às views de papel de parede, widgets e ícones da mesa.
`spotlight_view.create_spotlight_class` usa a busca de `spotlight_search.py` (normalização e ranking em `core/spotlight-search/`) e
os controles de `spotlight_controls.py` no mesmo processo.
`core/dock-model/` compõe as seções sem consultar o compositor; `core/dock-geometry/` resolve
layout e alvos de clique; `dock_motion` recebe tempo e o integrador `spring_step`
compartilhado de `core/motion/` pela interface de `glass_motion.py`. A classe GTK coordena esses módulos e mantém desenho/material,
miniaturas, menus, persistência e timers. Magnificação e drag usam as mesmas
constantes visuais anteriores; o primeiro frame após repouso continua com passo zero.
O widget é destino GTK de `text/uri-list`. Spotlight Apps e lançadores `.desktop`
da mesa são origens de arraste; arquivos `.desktop` externos também podem ser
soltos na seção fixa do Dock. O drop fixa o AppInfo de destino antes de receber
dados e sempre finaliza com `delete=False`; o helper entrega documentos ao
launcher sem shell nem operações de cópia/movimento. `dock_model` calcula a
posição de inserção e impede duplicatas dos apps fixados.
Ctrl+clique e remoção de fixação por arraste usam o gesto de ponteiro existente.

O Wi-Fi usa o mesmo `WifiMenu` no subpainel da Central e no extra da barra.
Redes salvas são relacionadas por SSID real e ativadas por UUID. O cache dos
SSIDs dura 20 s e invalida ao mudar o conjunto de UUIDs; a consulta de perfis
permanece na thread de fetch existente. Spotlight `/tipo` + Return reutiliza os
tokens existentes para Apps, Folders, Settings e Actions.

## Conhecimento e busca

- `BaseConhecimento/base.db` é o ponto de entrada versionado. `documentos`
  guarda estado, versão declarada, proveniência e hash; `trechos` é o índice FTS5
  derivado. `registros` guarda decisões e análises curadas, com seu próprio FTS5.
  `imagens_catalogo` e `codigo_catalogo` localizam evidência visual e código.
  `auditar_base.py` detecta desvios de hash, links quebrados e erros de integridade.
- `BaseConhecimento/ferramentas/consultar.py` chama `core/query/` e consulta essas tabelas sem escrita.
  A busca normal omite `archived`, `superseded` e `invalid`; `--historico`
  recupera esse material. `indexar.py` chama `core/knowledge-index/`, atualiza fontes textuais por SHA-256 e
  mantém snapshots legados quando o arquivo de origem já não existe.
- `BaseConhecimento/comparacao/parametros.json` define as medições; `comparar.py`
  calcula status a partir do código e atualiza `parametros` no banco e a matriz
  gerada. A nota mede apenas os itens cadastrados nessa matriz.
- `BaseConhecimento/MacTahoe/base.db` é um banco especializado, local e não
  versionado, com investigações do sistema Tahoe, catálogo de arquivos e busca
  híbrida opcional. `classificacao_registros` guarda estado e versão sem alterar
  os fatos nem os vetores. Seu conteúdo não está garantido em outros clones.
- Markdown de componentes, padrões, HIG e guias de módulo preserva textos longos
  e proveniência. Tokens estruturados dos kits continuam em JSON de origem; as
  tabelas de consulta são derivadas. Imagens e outros binários ficam fora dos
  bancos, referenciados por caminhos e hashes.

Para valores efetivamente implementados, consulte primeiro `shell/style.css`
e `hypr/hyprmac.lua`. Para alegações sobre Apple, confira a classificação da
fonte e a evidência Tahoe 26. Material rotulado `macos27`, visionOS ou de
versão desconhecida é secundário até ser confrontado com Tahoe 26.

O tray nativo da Waybar recebe uma extensão fixada em 0.15.0 por
`waybar/patches/tahoe-sni.patch`, compilada isoladamente por
`scripts/build-waybar-extras`. `scripts/menu-extras` inicia uma instância e faz
consultas pontuais; a escrita de preferências usa `core/waybar-status/src/menu_extras.rs`,
com reserva Python antes do build. Um FileMonitor no próprio tray aplica filtros
e ordem de `~/.config/hyprmac/menu-extras.json` sem reiniciar a barra; nenhum
daemon SNI adicional é criado. Os Ajustes listam registros SNI para visibilidade.
Detalhes e limites estão em `BaseConhecimento/componentes/barra-de-menus.md`.
