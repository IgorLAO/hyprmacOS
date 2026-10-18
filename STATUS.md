# Estado atual do HyprMac

## Migração Python → Rust — 2026-10-18

- Implementação do mapa de status: `scripts/status-map` agora chama `core/status-map/` em Rust; o hook de commit e o workflow usam o mesmo comando. O parser da lista de comportamentos, matriz e inventário de apps, o layout dos treemaps e a escrita idempotente foram transferidos.
- Validação do mapa de status: os sete SVGs gerados e o bloco do README coincidiram byte a byte com a saída Python anterior para o estado atual do repositório. O workflow remoto ainda não foi executado nesta branch.
- Implementação da miniatura: `scripts/captura-miniatura` foi substituído por `core/capture-thumbnail/` (`hyprmac-captura-miniatura`). `scripts/screenshot` e `scripts/gravacao` chamam o executável instalado em `~/.local/bin`; o instalador o compila e cria o link com backup idempotente. O desenho, clique para abrir, URI de arraste, pausa ao passar o ponteiro e descarte por botão direito seguem o contrato do script anterior. As medidas continuam uma extrapolação do kit macOS 27, sem evidência visual Tahoe 26.
- Validação da miniatura: teste Rust de limites e proporção passou, compilação release e verificações sintáticas dos chamadores passaram. No desktop Hyprland ativo, a camada `hyprmac-captura` apareceu e o processo saiu normalmente após cinco segundos. Clique, arraste, pausa com ponteiro e comparação visual Tahoe 26 ainda requerem conferência manual.
- Clipboard: `scripts/clipboard` foi substituído por `core/clipboard/`. O serviço `wl-paste --watch` está ativo apontando ao binário Rust. Testes isolados confirmaram texto, deduplicação, exclusão de conteúdo sensível, limpeza e geração de miniatura PNG. A transferência do clipboard real foi preservada durante a migração; o fluxo de cópia e colagem ao vivo ainda requer conferência manual.
- Acessibilidade e cor de destaque: `scripts/acessibilidade` e `scripts/accent` foram substituídos por `core/accessibility/` e `core/accent/`. A paleta compartilhada reside em `core/accent/palette.json` e segue acessível aos componentes Python restantes. O CSS de destaque Rust coincidiu byte a byte com o gerador Python antigo nas oito cores e nos dois modos. Acessibilidade foi testada com configuração isolada, CSS e escrita idempotente. Ambos os comandos foram executados no desktop, com Waybar ativa após a atualização. A comparação visual com Tahoe 26 permanece pendente.
- Validação do conjunto migrado: os 15 testes unitários Rust passaram; a suíte Python completa passou com 494 testes e 4 pulados. Os arquivos Python e Lua alterados compilaram, e o instalador e scripts shell passaram na verificação sintática.
- Implementação posterior: `input-source.sh` também foi substituído pelo comando Rust `hyprmac-waybar input-source`; ele lê a fonte de entrada do teclado principal e atualiza no evento `activelayout`.
- O Python embutido em `app-about.sh` saiu com a migração da ação About do menu de apps para o mesmo binário Rust.
- Implementação de aparência: `scripts/aparencia` foi substituído por `core/appearance/` (`hyprmac-aparencia`); o autostart Lua e o instalador apontam ao binário. O vigia C de inatividade continua responsável pelo disparo de 60 s.
- Validação posterior: teste controlado do socket mudou a fonte de entrada `US` → `BR` e encerrou ao fechar o socket; o comando About produziu a notificação esperada com classe, versão e pacote em ambiente de teste. A Waybar e o shell foram recarregados no desktop; duas barras, dois relógios Rust e duas fontes de entrada Rust ficaram ativos. O teste de aparência confirmou troca apenas com modo Auto e tema divergente; o vigia de 60 s foi reiniciado apontando para `hyprmac-aparencia check`. Os 6 testes unitários Rust passaram; a suíte Python completa passou com 496 testes e 4 pulados. O ciclo real de 60 s e a imagem de referência Tahoe 26 ainda precisam ser conferidos.
- Ações de janela: `scripts/janela` foi substituído por `core/window-actions/` (`hyprmac-janela`). Os atalhos em `hypr/hyprmac.lua` e o menu de apps do shell usam o novo binário. Testes Rust cobrem a ordem de abertura, o retorno da mesa e a filtragem das janelas visíveis; um `hyprctl` simulado confirmou os despachos de foco e Hide Others. Os 9 testes Rust e a suíte Python completa (494 testes, 4 pulados) passaram. O shell e o compositor foram recarregados (`hyprctl reload`: `ok`); o Dock permaneceu mapeado. Gestos reais de Hide/Quit/Show Desktop ainda precisam de conferência manual e comparação Tahoe 26.
- Implementação: a branch `migration/python-to-rust` substitui os seis scripts Python da Waybar (menus condicionais, relógio, Add Controls, gravação, fones e Sleep Focus) por `core/waybar-status/`. O instalador compila o binário Rust em release e cria o link local com backup idempotente. A configuração da barra, a busca de menus do Spotlight e os sinais dos Ajustes foram atualizados.
- Validação: `cargo test` passou (2 testes), compilação release passou, os 8 testes direcionados de relógio, eventos e menus passaram, e a suíte completa passou (499 testes, 4 pulados). O binário foi linkado em `~/.local/bin`; a Waybar foi reiniciada com dois processos de relógio Rust ativos para os dois monitores. O terminal tinha uma assinatura Hyprland antiga; após iniciar a barra com a assinatura da instância ativa, o log confirmou `Hyprland IPC starting` e duas barras configuradas. A imagem da barra ainda não foi confrontada com Tahoe 26.
- Limite: a migração integral solicitada continua pendente. O shell GTK, apps, scripts restantes, testes e ferramentas da BaseConhecimento ainda executam Python. Nenhuma fidelidade Tahoe 26 nova é inferida dessa troca de linguagem.

## Papel de parede automático — 2026-10-18

- Implementação SIS-08: o shell segue `org.gnome.desktop.background` por padrão,
  como Ajustes ▸ Wallpaper. Ao escolher uma foto em Ajustes, a origem `gnome` é
  gravada em `config.json` e o shell recarrega a imagem. Mudanças externas das
  chaves GNOME e da origem em `config.json` também atualizam as layers da mesa
  e o contraste da barra sem reiniciar o shell. Uma imagem explícita em
  `config.json` continua disponível; a foto local existente é o fallback.
- Validação SIS-08: troca em tempo real entre imagens brancas e pretas mudou
  `waybar/contrast.css` de 4556 para 0 bytes, tanto via GNOME quanto por troca
  do caminho em `config.json`; origem e wallpaper anteriores restaurados. A
  troca via `set_wallpaper()` de Ajustes gravou `"wallpaper": "gnome"` preservando
  os outros campos. O asset Tahoe padrão ainda não está neste checkout.

## Controle de gravação na Central — 2026-10-18

- Implementação CCN-01: `Screen Recording` entrou na categoria `Screenshot`,
  na galeria de edição e no layout padrão da Central. O controle usa
  `scripts/gravacao screen`: inicia a gravação, e durante a captura passa a
  `Stop Recording`. O aviso da barra continua automático e separado da lista
  de controles configuráveis da barra. Seu SVG agora reproduz o anel claro com
  quadrado arredondado da captura enviada pelo usuário (10.22.16).
- Validação CCN-01: shell recompilado e Central recarregada no desktop;
  21 testes dirigidos da Central passaram. Uma gravação real gerou MP4, exibiu
  o aviso na barra e o removeu após a parada. Captura local da Central em
  `BaseConhecimento/referencias/validacao/central-gravacao-2026-10-18.png`.
  O clique físico no novo botão ainda precisa de conferência manual.

## Barra, avisos de captura e OSD de volume — 2026-10-18

- Implementação CCN-03: o `+` aparece na barra durante Edit Controls e abre uma
  página de 620×600 na galeria da Central, com cartões de controles nativos
  configuráveis. Gravação e compartilhamento de tela ficaram fora da lista:
  são avisos automáticos. O primeiro mostra um anel com quadrado enquanto
  `wf-recorder` grava e para ao clicar; o segundo usa o módulo
  `privacy/screenshare` da Waybar.
  Fones e Sleep Focus começam fora da barra e têm indicadores próprios quando
  adicionados e ativos; apps externos permanecem no tray SNI já existente.
  Os botões Add/Remove reutilizam `menubar_items.py`.
- Validação CCN-03: galeria e `+` abertos no desktop e capturados em
  `BaseConhecimento/referencias/validacao/barra-galeria-2026-10-18.png`.
  Gravação real de 3 s gerou MP4; o aviso mudou de `on` para `off` após parar.
  O backend de compartilhamento não foi exercitado com uma sessão real;
  arrastar cartões para a barra ainda não está implementado.
- Implementação OSD: o controle de volume abre 20 px abaixo da barra; o glifo
  da Central passa ao de alto-falante por transição GTK3 de `background-image`
  em 180 ms, junto à aparição do painel. O tempo foi estimado dos quadros
  enviados pelo usuário, sem timestamps do vídeo.
- Validação OSD: Waybar e shell recarregados; sequência local de 60 fps mostrou
  glifo intermediário, cápsula e aparecimento gradual do painel. Captura em
  `BaseConhecimento/referencias/validacao/volume-osd-20px-2026-10-18.png`.
  A trajetória ainda precisa de comparação quadro a quadro com Tahoe 26.

## Arraste de apps e legibilidade dos menus — 2026-10-18

- Implementação DCK-07: tiles de Apps do Spotlight e lançadores `.desktop` da
  mesa fornecem `text/uri-list`; a Dock aceita um launcher local, insere na
  posição do drop, reordena se já fixado e persiste `dock.json`. Arquivos comuns
  continuam sendo entregues ao app de destino. Finder permanece na primeira vaga.
- Validação DCK-07: 36 testes direcionados do Dock e 499 testes totais passaram
  (4 pulados); compilação Python passou. Gesto real entre Spotlight e Dock ainda
  precisa ser conferido manualmente no desktop e comparado com Tahoe 26.
- Implementação visual GLS-08: menus GTK3/GTK4, menus da Waybar e menus do shell
  receberam fundo mais legível (alfa 0,94 em claro e escuro), com a captura
  fornecida pelo usuário como referência de legibilidade. A janela do popup
  continua transparente para manter cantos arredondados.
- Validação visual GLS-08: shell e Waybar recarregados no desktop; captura
  `BaseConhecimento/referencias/validacao/dock-arraste-menus-2026-10-18.png`
  confirma o Dock visível, mas não mostra um menu aberto. A comparação do
  material de menu com Tahoe 26 permanece pendente. O valor é um ajuste local
  de CSS, sem certificação Apple.

## Componentização do shell — 2026-10-18

- Removido o desenho temporário da borda vermelha do Dock e retirada a opção
  `dock_debug_bounds` da configuração local. O shell foi recarregado e a layer
  `hyprmac-dock` está mapeada no desktop.
- A view GTK do Dock foi movida para `shell/dock_widget.py`; Force Quit e o
  alternador de apps foram movidos para `shell/session_overlays.py`; papel de
  parede, widgets e ícones da mesa foram movidos para `shell/desktop_surface.py`.
  A view do Spotlight foi movida para `shell/spotlight_view.py`. As quatro
  fábricas recebem os serviços compartilhados do processo principal. O arquivo
  de entrada caiu de 10.587 para 6.278 linhas; Central, notificações e
  outros painéis ainda precisam de extração própria.
- Validação de implementação: compilação dos cinco arquivos Python e suíte
  de 496 testes passou (4 pulados); uma instância do shell após recarga, com layers do papel de
  parede nos dois monitores e a layer do Dock. Spotlight aberto e fechado pelo
  comando D-Bus, com layer mapeada. Validação visual: Dock
  mapeado e sem borda vermelha na captura local
  `BaseConhecimento/referencias/validacao/dock-sem-borda-2026-10-18.png`;
  a borda foi removida pelo código
  e pela configuração. Comparação
  visual com Tahoe 26 e exercício manual dos gestos permanecem pendentes.

Última revisão desta síntese: 2026-10-11. Objetivo: reprodução visual e
comportamental do **macOS Tahoe 26**. Barra e Spotlight foram abertos no desktop
após as mudanças; os demais estados refletem código, matriz e registros locais,
não uma certificação visual Tahoe 26.

## Instalação local — 2026-10-18

- `install.sh dark` executado; Waybar extras e vigia de inatividade compilados.
  Configuração anterior preservada em `backup/installation-20261018-092312/`.
- Criado `~/.config/hypr/hyprland.lua` a partir do exemplo distribuído pelo
  Hyprland 0.56.2, com teclado ABNT2, os dois monitores detectados e inclusão
  de `hypr/hyprmac.lua`. `Hyprland --verify-config` retornou `config ok`.
  A sessão existente usa o gerenciador hyprlang: sair/entrar ainda é necessário
  para ativar Lua, regras, atalhos e autostart completos.
- Corrigidos imports CSS ausentes no primeiro boot da barra; o shell agora
  tolera a ausência também do wallpaper padrão, usando fundo sólido.
  Barra e Dock mapeados no desktop. Isso não valida fidelidade Tahoe.
- Assets locais incompletos: wallpaper Tahoe ausente, instalador não encontrou
  fontes no kit e Nautilus não está instalado. O banco geral estava ausente;
  índice reconstruído das fontes presentes, sem recuperar registros curados
  históricos. Auditoria: integridade SQLite ok, sem hashes divergentes,
  com referências operacionais/visuais ausentes a recuperar.

## App Factory — expansão inicial

- O inventário Tahoe 26.6.1 continua com 70 entradas: 15 componentes parciais
  preservados e 55 manifestos novos. A fábrica gerou 55 lançadores XDG e 55
  ícones PNG; `Gio.AppInfo` e `AppIndex` resolveram todos. Os lançadores foram
  instalados no diretório XDG do usuário e o instalador foi atualizado.
- Clock e Music abriram como janelas flutuantes com classes próprias no
  Hyprland. A captura local de Music foi confrontada com a imagem WWDC25
  Tahoe 26: sidebar e identidade estão presentes, mas material, agrupamento,
  escala e conteúdo ainda divergem. Não há referência local confiável da
  janela Clock. Capturas em `validacao/2026-10-11/app-factory-*.png`.
- Pilotos Linux parciais: Clock (cronômetro, timer e alarmes só com a janela
  aberta), Activity Monitor (`/proc`), System Information, Console
  (`journalctl`), Calendar e Reminders locais, Voice Memos (`pw-record`),
  QuickTime Player (GStreamer), Terminal (Ghostty) e Disk Utility (UDisks2
  somente leitura, com fallback `lsblk`). O catálogo registra as limitações
  por app; nenhum piloto tem fidelidade Tahoe certificada.
- Testes de artefatos e stores locais passaram; aberturas controladas verificam
  inicialização e fechamento de amostras, temas GTK claro/escuro e ausência de
  processos das amostras após fechar. Áudio real, vídeo visual, eventos de
  calendário/reminders completos, menus globais Tahoe e responsividade ainda
  exigem validação. FreeLLM retornou HTTP 429; tarefas isoladas foram
  concluídas pelos agentes locais disponíveis.

## Implementado no código

- Shell GTK3 com Dock, Central de Controle, Spotlight, notificações, widgets,
  menus e alternador de apps; visão de janelas e Ajustes em processos próprios.
- Barra Waybar com menus e extras; temas claro/escuro e opções de acessibilidade.
- Tela de bloqueio GTK4/PAM, captura/gravação e ações de janela.
- Integração de Liquid Glass pelo plugin `hyprglass` e presets do compositor.
- Auditor de parâmetros, FTS5 para referências e catálogos de código/imagens.
- Uma assinatura compartilhada dos eventos Hyprland e um índice de apps usado
  por Dock, Spotlight e alternadores; busca/cálculo e controles visuais do
  Spotlight separados em módulos, ainda no mesmo processo GTK. Os menus da
  Waybar usam consultas pontuais sinalizadas pelo shell.
- Dock: conteúdo/eventos, geometria/reordenação e movimento extraídos em três
  módulos sem GTK. A classe principal passou de 1.005 para 896 linhas;
  materiais, menus, miniaturas e autohide continuam na camada gráfica.
  Ordenação de apps abertos permanece por foco (`focusHistoryID`).

## Validação da extração do Dock

- 18 testes passaram (11 novos para geometria, ordenação, estado/movimento,
  eventos agrupados e integração de refresh/drag/release com os métodos reais).
  Sintaxe dos quatro arquivos Python afetados validada.
- Shell recarregado e ocultar/restaurar acionado por D-Bus no desktop. Layer do
  Dock manteve 704×122 px em (608,958). Capturas de 720×130 px idênticas fora do
  selo de notificação de 16×16 px: o reload limpa notificações em memória.
- Uma instância do shell antes/depois, nenhum processo residente acrescentado.
  Snapshot RSS/PSS: 194.752/141.186 → 159.004/107.843 KiB após reload.
  O processo anterior tinha caches acumulados; estes snapshots não comprovam
  economia de memória causada pela extração nem redução de CPU.
- Drag e magnificação foram exercitados por testes determinísticos; o desktop
  validou repouso e autohide. Gesto físico completo, menus abertos, magnificação
  em desktop, temas alternativos e retina ainda requerem validação interativa.

## Ciclos de fidelidade paralelos — 2026-10-10

- Agentes: Dock Fidelity e Tahoe Fidelity — System implementaram em paralelo;
  Tahoe Research forneceu evidências; QA & Performance revisou/testou. O limite
  de quatro slots exigiu executar pesquisa e QA em sequência. Cópias privadas
  do shell isolaram edições; o principal aplicou os diffs sequencialmente.
- Dock: Ctrl+clique, Remove from Dock, arraste para remover com aviso Remove,
  cancelamento ao retornar e identidade estável durante refresh. Drop de
  documentos abre via Gio em apps compatíveis; nunca move/apaga a origem.
  O limiar de remoção de um ícone é uma tolerância local, não medida Tahoe.
- Central/extra Wi-Fi: perfis renomeados identificados pelo SSID e ativados por
  UUID. Cache de 20 s mantém quatro consultas no polling estável; a atualização
  custa quatro mais N perfis, verificado por mocks. Sem hardware Wi-Fi local,
  conexão real e reuso de credenciais não foram exercitados.
- Spotlight: `/tipo` + Return aplica tokens de Apps/Applications, Folders,
  Settings/System Settings e Actions. Consultas comuns, calculadora e histórico
  preservados; filtros desconhecidos/caminhos não são convertidos em tokens.
- 46 testes passaram (25 Dock, 6 Wi-Fi, 5 novos Spotlight, 3 QA independente e
  7 anteriores); Python compila e diff-check dos arquivos trabalhados passa.
  Diferenças de whitespace preexistentes continuam nos documentos legados.
- Runtime final: PID 144370, uma instância. Dock continua 704×122 em (608,958);
  pins preservados byte a byte. Central e Wi-Fi abriram por D-Bus. Previews sem
  teclado renderizaram tokens Spotlight Applications/Folders/Settings/Actions.
  Gio real entregou URI a um launcher efêmero `/usr/bin/true`; isso não é prova
  de gesto de drop Wayland nem de documento aberto por aplicativo final.
- Ctrl+clique/arraste automatizados no desktop foram inconclusivos devido ao
  movimento concorrente do cursor; input artificial foi interrompido e removido.
  Captura Dock final difere apenas no selo perdido no reload (209 pixels) e em
  16 pixels de indicador alterado pela interação do usuário.
- Snapshot antes/depois final: RSS 164.092 → 180.032 KiB, PSS 112.141 → 125.768
  KiB; CPU em janelas de 5 s: 3,60% → 1,60%. O depois inclui caches do Spotlight
  aquecido, e o desktop estava em uso: não prova melhora nem regressão de custo.
  Nenhum daemon ou dependência foi acrescentado.
- Fontes Apple explicitamente `/26/mac/26` registradas no SQLite como evidência
  textual; isto não certifica animação/material. Não alteramos CSS, parâmetros
  visuais, shaders ou curvas de movimento. Genie continua investigação, pois
  o shell não fornece deformação da superfície real até o ícone.

## Pesquisa open source e Genie — 2026-10-10 (noite)

- Cinco subagentes leram código (nothing-liquid/hyprglass fork, hyprglass v0.10.0,
  Better Blur DX, liquidGL, medfa12/liquid-glass-react, Cairo-Dock, Plank, KWin e
  Compiz Magic Lamp, hyprbars, Chromium/Electron) e documentação Apple. 24 registros
  no SQLite (`consultar.py --registro genie|hyprglass|spring|hyprbars`); só texto Apple
  lido ficou `verified`.
- Regressões da árvore corrigidas: `hypr/hyprglass/forma-pela-mascara.patch` e
  `gtk/gtk3.css` restaurados de HEAD; `scripts/vidro` volta a nomear o `.so` pelo hash
  do conteúdo dos patches. O hyprglass estava descarregado (não sobrevive a reinício do
  Hyprland); recarregado com `vidro carregar`.
- **Genie**: `hypr/hyprglass/genie.patch` (do fork nothing-liquid 55c00b0, BSD-3).
  ⌘M e o menu Janela chamam `Dock.minimize`, que passa ao plugin a vaga do item
  minimizado; clicar no item restaura pela vaga dele. Validado em Hyprland aninhado
  (minimizar/restaurar/3 ciclos) e no desktop com janela de laboratório; o clique físico
  de restauração não foi exercitado. Tempos 520/460 ms são do fork, não medidos no Tahoe.
- **Magnificação**: a curva acompanha o ponteiro no mesmo quadro e só a intensidade usa
  a mola (Cairo-Dock/Plank); antes cada ícone tinha mola própria (~0,2 s de atraso).
  Teste novo em `tests/test_dock.py`; sensação ao vivo pendente do usuário.
- Papel de parede padrão passou a `tahoe-light-1080p.jpg` (a faixa índigo da barra era
  o `indigo-referencia.png`).
- Não aplicado, aguardando evidência/decisão: refração ~3x mais forte que um chanfro
  Snell (testar 0,35–0,4 em A/B), Spotlight que encolhe de ~108% no Tahoe (hoje cresce
  de 94%), `macPop` mais seco que as molas Apple, raio 26/16 por tipo de janela, hyprbars
  para Qt/Electron, Brave em tema GTK e `window.controlsStyle` no VS Code.

## Incompleto ou sem evidência suficiente

- **Dock:** a matriz marca `SIS-01` como próximo; separar a máscara da base dos
  ícones/rótulos e confirmar magnificação/movimento com captura Tahoe 26.
  A magnificação já existe. As molas e o tempo de quique continuam aproximações
  locais. Remoção por arraste, Ctrl+clique e drop de documentos em apps compatíveis
  foram implementados; falta validar esses gestos no desktop. Drops em pastas,
  Open at Login/Show in Finder e efeito gênio continuam ausentes.
  As medidas 36/45/58 vêm de material rotulado macOS 27,
  classificado `experimental/unverified`; precisam de confirmação Tahoe 26.
- **Central de Controle:** pinagem direta da galeria na barra e estados de
  subpainéis Wi-Fi/Bluetooth carecem de paridade confirmada.
- **Spotlight:** animação de troca de modos tem duração ainda estimada. `/Apps`,
  `/Folders`, `/Settings`, `/Actions` + Return funcionam; seletor genérico `/`,
  MIME/PDF e nome de aplicativo + Tab continuam pendentes.
- **Janelas:** sombras compostas e semáforos em apps Qt/outros diferem do alvo
  registrado; verificar especificamente no Tahoe 26.
- **Bloqueio, Mission Control e Ajustes:** faltam medições completas de estados,
  transições e hierarquia contra runtime Tahoe 26.
- **Apps internos:** a lista de desejos inclui Preview, Diário, Câmera, Notas
  e Fotos; são escopo adicional, sem conclusão geral registrada.

## Problemas conhecidos e bloqueios

- A matriz calcula **94% em 106 parâmetros válidos** após corrigir um registro
  órfão. Ela mistura fontes rotuladas Tahoe 26/27 e avaliações manuais; não é
  uma medida de fidelidade global ao Tahoe 26.
- A árvore local já continha 2.017 remoções e 57 modificações antes desta
  consolidação. Há fontes antigas ausentes do disco; 177 caminhos permanecem
  recuperáveis como snapshot FTS histórico. A intenção dessas remoções não foi
  presumida.
- `kitty/kitty.conf` e `gtk/gtk3.css` seguem ausentes neste checkout. O
  instalador agora preserva a configuração existente quando a origem falta;
  apenas os trechos afetados foram testados em diretório isolado.
- O patch próprio `hypr/hyprglass/forma-pela-mascara.patch` já estava ausente.
  O upstream hyprglass v0.9.0 já fornece máscara alfa para layers, mas não o
  antigo comando `hyprglass shape` usado por Ajustes para peças de janelas.
  `scripts/vidro` agora distingue builds upstream de builds com patches; Ajustes
  mantém a chamada como compatibilidade silenciosa. A separação dessas peças
  precisa migrar para o protocolo upstream ou ser validada sem ela.
- Evidência runtime Tahoe 26 ainda falta para abertura da Central, magnificação
  do Dock e troca de artwork. Veja os registros e a investigação especializada.
- Após recarregar shell e Waybar, 26 processos residentes de menu (198.465 KiB
  PSS somados) passaram a zero. A captura de 1000×40 px da barra foi idêntica
  antes/depois; 26 consultas pontuais paralelas levaram mediana de 117,8 ms.
  O shell principal ainda concentra Dock, Central, notificações e o painel do
  Spotlight; a modularização dessas classes permanece incremental.

## Próximas prioridades

Diretriz atualizada pelo usuário em 2026-10-10: consolidar o shell existente
antes de expandir aplicativos próprios. A fila de dez frentes está no
[TODO.md](TODO.md); os requisitos com implementação, validação e evidências
separadas estão no [catálogo de comportamentos](BaseConhecimento/LISTA-DE-DESEJOS.md).
Priorizar Dock/janelas/animações e Liquid Glass (P0), seguidos de barra,
Spotlight/Central e Mission Control/gestos (P1); arquivos e apps são expansão
P2, com exceções por comportamento descritas no catálogo.

Capturar estados Tahoe 26 e confrontar os parâmetros herdados faz parte da
validação de cada frente. Manter as limitações e entregas parciais acima;
incluir um requisito no catálogo não muda seu estado de implementação.
Problemas conhecidos de instalação continuam registrados, sem substituir a
fila de fidelidade por uma auditoria geral.

Comandos: `./BaseConhecimento/ferramentas/comparar.py --resumo`,
`./BaseConhecimento/ferramentas/comparar.py --pendentes` e
`./BaseConhecimento/ferramentas/consultar.py --registro "Tahoe 26"`.

## Menu Bar Extras — 2026-10-10

Tray nativo estendido na Waybar 0.15.0, com build local e fallback upstream.
Ícones originais, attention/overlay, menus D-Bus ancorados e cápsula persistente
para menus hospedados; filtros/ordem por Id/Title aplicados sem reload global.
NetworkManager Applet e VLC usados no desktop; fixture validou pixels, estados,
cliques, scroll e ação de menu. Três testes de preferências e dois testes reais de
watcher/ciclo de vida passaram; uma Waybar atende dois monitores. Ver
`BaseConhecimento/componentes/barra-de-menus.md` e suas capturas/limitações.
A equivalência visual Tahoe 26 não foi certificada: medidas são aproximações da
referência local; falta comparação independente nos mesmos estados.

## Retomada após interrupção do Claude — 2026-10-10

- Destaques: 16 valores `controlAccent*Color` conferidos no dump COLORS BGRA
  de Aqua/DarkAqua 26.6.1 (25G76). `shell/accent_palette.py` centraliza a tabela
  para gerador, Ajustes, menu do shell e Mission Control; este segue claro/escuro
  ao abrir. Tiling e presets de vidro preservados.
- COR-01/COR-02 agora comparam o token padrão com #007AFF e citam o asset Tahoe,
  em vez das cores semânticas do kit 27. A matriz não certifica fidelidade visual.
- Validação: dois testes de integração cobrem geração nos dois temas, aliases,
  fallback e idempotência. Python compilado; shell recarregado no desktop.
- Limites: hover e seleção derivados continuam aproximações locais; inspeção
  estática dos assets não prova a variante usada por cada controle Apple.
- RE do vidro: layouts/símbolos e builders foram preservados na pesquisa local,
  mas emulação e recuperação dos parâmetros finais não concluídas. Não aplicar
  números presumidos. Estado registrado em `tahoe26:glass:re-retomada`;
  GLS-01 a GLS-10/DCK-04 continuam pendentes.

## Análise da DMG/dyld retomada — 2026-10-10

- Pesquisa privada em `~/.local/share/hyprmac-pesquisa/macos-26.6.1/re-auto/`,
  volume somente leitura e build 25G76 confirmado por SystemVersion.plist.
- Implementação da pesquisa: leitura de metadata/VWT recupera 57 layouts de
  69 estruturas; 12 ficam desconhecidas. Parameters tem 1025 bytes, SpecV1 1152.
  Os 18 layouts anteriores de Parameters concordam com a recuperação automática.
- Dock (GLS-02/DCK-04): emulação de 16 instruções vincula cinco valores à
  SpecV1.Refraction: alturas normalizadas .127/.13, amplitudes -.42/.42,
  outerOpacity .20. Ranges e conversão por dimensão/estado ainda faltam; não
  transportar diretamente para refraction_strength/edge_thickness do hyprglass.
- Animações (MIC): sete funções numéricas Spring executadas com seis entradas
  sintéticas. São conversões, não presets das apps. Corrigido scanner privado
  LC_FUNCTION_STARTS que omitia __TEXT; listas antigas de constantes não provam
  timing de método. Backup preservado.
- Nove registros de recursos: edição Cocoa, atalhos/foco/tiling, textos de
  silenciamento/limpeza de notificações, Spotlight e temas AnnotationKit.
  Existência de recurso não prova disposição ou comportamento runtime; apps
  internos permanecem na expansão. Sete registros avaliam os cinco projetos RE.
- PoC isolada hyprglass: build0.56.2 e renderização em compositor aninhado,
  fundo sintético, hipótese de dois lóbulos do fit externo26.5.2. 37397 pixels
  mudaram só nas regiões de vidro. A referência Tahoe fotografada foi inspecionada,
  mas fundo/geometria diferentes impedem MAE de fidelidade. Perfil/direção e
  correspondência por tamanho continuam sem verificação. Sem integração no shell.
- Registros `tahoe26:re-auto:*`, `tahoe26:resource-auto:*` e `re-survey-*`
  distinguem implementação, evidência estática, emulação e limitações. Binários,
  catálogos brutos, clones externos e artefatos de laboratório continuam privados.

## Checkpoint curto — aplicação Tahoe 26 (2026-10-10)

57 layouts Swift e cinco entradas normalizadas de refração do Dock recuperados;
conversões Spring verificadas por emulação. Recursos Cocoa/notificações/Spotlight
e cinco projetos externos catalogados no SQLite. Pesquisa e PoC em
`~/.local/share/hyprmac-pesquisa/macos-26.6.1/re-auto/`. Próximo passo: aplicar
cores/edição verificadas nos componentes existentes; concluir ranges/conversão
do vidro antes de integrar. Tahoe 26 prevalece sobre kit 27; tiling preservado.

Aplicado após o checkpoint: tokens AppKit exatos em GTK3/4/libadwaita, foco
claro/escuro também no shell e fallback Qt #007AFF. Campo Spotlight: Ctrl+A/E/K/T/Y,
Option+Backspace e Command+Backspace/A, com transposição de clusters Unicode.
Testes locais e parsing GTK3/4 passaram; comparação visual Apple ainda pendente.
Estado por descoberta: `tahoe26:aplicacao:*` no SQLite. Valores de vidro sem
conversão, receitas externas, defaults de animação não identificados e contexto
de recursos permanecem pendentes; não são fidelidade concluída.
Shell recarregado, Dock ativo e Spotlight deixado aberto em HDMI-A-2; captura
local `/tmp/hyprmac-tahoe-spotlight.png`. 19 testes pertinentes passaram; parsing
GTK3/4 e auditoria SQLite limpos. Diff dos arquivos desta aplicação sem whitespace;
diff global mantém 54 linhas de avisos em trabalho anterior, preservado.

## Checkpoint DMG — ranges e molas (2026-10-10)

- DCK-04/GLS-02: ranges da refração recuperados (altura0..20, amplitude−60..∞)
  e conversão emulada por dimensão: `.127/−.42` internas; `.13/.42` externas;
  fallback48. Campo externo pode usar a dimensão da maior área. Ambiente real,
  perfil e unidades finais do filtro ainda pendentes; sem integrar no shader.
- MIC/Spotlight: defaults nomeados GlassContainer recuperados (transition .5/.3,
  scalePulse e translationKick). Controle Spotlight agora usa mola analítica
  baseada no default, com reversão contínua e Reduzir Movimento imediato.
  Correspondência específica Spotlight experimental; geometria/material não certificados.
- Dois agentes de baixo custo: 6 novos registros sobre QuickLook, AppIntents,
  migração Dock e affordances Finder. 12 registros apps corrigidos para inspeção
  estática, sem declarar execução. JSONs privados `re-auto/*followup-records.json`.
- Retomar em `re-auto/refraction_dimensions.py` e `glass_animation_probe.py`;
  falta obter dimensões runtime do Dock e relacionar presets por componente.
Validação deste lote: 20 testes passaram (mola, edição Cocoa e verificações
do shell), mais exercício GTK de reversão/Reduzir Movimento. Shell recarregado
e prévia +ctl renderizada; capturas `/tmp/hyprmac-glass-motion-{start,mid,end}.png`.
Auditoria íntegra/sem links ou hashes divergentes. Diff dos arquivos tocados limpo;
avisos globais anteriores preservados. Não há certificação visual Tahoe por captura.

## Aplicação no desktop — Spotlight (2026-10-10)

Super+Espaço aponta ao shell pelo lançador. Removido fallback automático Wofi
em caso de D-Bus lento: inicia/aguarda shell até5s, legado só por variável explícita.
Reset da mola ao fechar evita estado residual.3 testes integração passaram;
Bash/Python/Lua válidos, shell/Hyprland recarregados sem configerrors.
Atalho físico ainda depende de conferência; lançador acionado no desktop.
Registro `hyprmac:spotlight:launcher-native`.

## Checkpoint — ligação com o filtro (2026-10-10)

SetInput enum e CFStrings resolvidos automaticamente com fixups dyld; sete
entradas de refração confirmadas e55 casos de switch examinados. Filtro criado:
`glassBackground`. Emulação instrumentada confirma passagem escalar sem inversão
ou escala nesse trecho. Metadata confirmou BackgroundFilter.refraction (offset224), do tipo
Parameters.Refraction. Faltam construção a partir do campo opcional da raiz,
ajustes por estado, dimensões runtime do Dock e perfil/unidades do renderizador. Sem alteração
do shader principal. Evidências privadas: `re-auto/filter-{enum,values}.json`.
Calculador próprio: `BaseConhecimento/ferramentas/receita_dock.py --minimum 80
--largest 200 --pixel-length .5`; não presume dimensões Apple.4 testes e12 casos
independentes de emulação validados. Registros `tahoe26:re-auto:filter-*` e
`tahoe26:aplicacao:recipe-calculator`; schema antigo corrigido para metadata estática.

## Apps coletados no DMG — Pré-Visualização (2026-10-10)

Prioridade redirecionada pelo usuário para os apps da Apple. Primeira versão
local em `shell/hyprmac-preview`: PDF via Poppler, imagens via GdkPixbuf,
páginas/miniaturas, zoom, ajuste à janela, rotação de visualização e inspector.
Registro desktop e instalador incluem o aplicativo sem alterar associações MIME.
Base: registros `tahoe26:apps:preview-menus-ferramentas` e
`tahoe26:apps-followup:preview-appintents-catalog`, extraídos do build25G76.
Rótulos/ações têm evidência estática; layout e controles GTK são experimentais.
Validação: PDF sintético de3 páginas, limites de navegação/zoom, miniaturas,
geometria rotacionada e substituição por PNG passaram; Python/Bash e desktop-file
validator passaram. Aplicativo abriu no desktop. Ainda faltam TOC, busca no PDF,
anotação, edição/salvamento, senha e comparação visual Tahoe. Rotação não altera
o arquivo. Primeiro arquivo por abertura; não há interface multidocumento.

## PoC Swift/ARM64 — refração Dock 25G76 (2026-10-10)

O parser Linux foi reproduzido com o dump Swift existente: 57 layouts fixos entre
69 tipos; 12 acessores continuam desconhecidos. O `ipsw` do ambiente lê os
campos no cache dyld. MachOSwiftSection 0.22.0 tem suporte documentado para
layouts estáticos, mas não foi executado no Linux (sem Swift 6.3 neste host).
Relatório privado: `re-auto/machoswiftsection-linux-feasibility.json`.

Estrutura: `SpecV1.Refraction` tem 68 bytes em `SpecV1+0x1b0`; converte para
`Parameters.Refraction` de 52 bytes e entra em `BackgroundFilter+0xe0`.
ARM64/Unicorn confirmaram os valores normalizados do Dock e o ramo bruto
`w27.bit5=1 && w24.bit9=0`, que zera só a altura interna. O significado dos
bits em estados de interface é desconhecido. O calculador
`BaseConhecimento/ferramentas/receita_dock.py` expõe esses bits explicitamente;
5 testes passaram. Relatório privado: `re-auto/refraction-origin-audit.json`.
O mesmo método identificou a receita regular (.25/-.8/.125/.2, opacidade .3)
e outro ramo bruto que pode zerar a altura interna; registrados separadamente
no SQLite, sem aplicação visual.

Implementação: somente no laboratório privado `hyprglass-lab`, com parâmetros
calculados para dimensões ausentes e perfil espacial hipotético. Validação:
compilou e renderizou em Hyprland aninhado (800×600); 37.524 pixels dentro das
duas superfícies diferiram do baseline. A foto Tahoe disponível tem outro
fundo, escala e composição, então não certifica ganho de fidelidade.
`hypr/vidro-presets.lua` e o shader principal não foram alterados. Antes de
integrar, faltam dimensão/pixelLength reais do Dock, perfil/unidades do filtro
e captura Tahoe equivalente. Relatório privado: `re-auto/dock25g76-poc-report.json`.
O dispatcher passa o mesmo `Environment` ao builder Dock e ao regular;
`pixelLength` é lido em `Environment+0` e `Dimensions` por offset de metadados,
mas a origem dos valores de runtime permanece desconhecida
(`re-auto/environment-refraction-flow.json`). A curva de lóbulo usada no lab é
equivalente à transcrição de terceiros para macOS 26; o vínculo ao shader
QuartzCore 25G76 e a mistura das amostras seguem sem confirmação
(`re-auto/ca-glassBackground-profile.json`).


## Controles compartilhados — ciclo fora do Dock (2026-10-11)

MIC-02, clique fora e troca de menus pela barra (2026-10-11): os capturadores
invisíveis da Central e dos menus de extras, mídia e notificações cobriam
`y=0…1080`, sobre a Waybar em `y=0…34`. Agora começam abaixo da barra, em
`y=34`, nos dois monitores [real:shell/hyprmac-shell:2419]
[real:shell/hyprmac-shell:6155]. A altura vem do valor compartilhado 34 e
da configuração da Waybar [real:shell/hyprmac-shell:455]
[real:waybar/config.jsonc:5]. O restante da tela continua capturando cliques
fora; os comandos de abertura já fecham outros painéis registrados
[real:shell/hyprmac-shell:427]. Entrada: Central aberta; ação: abrir menu
Wi-Fi pela barra; saída esperada: um clique alcança a Waybar e troca o painel.
Referência: Apple HIG oficial de popovers recomenda fechar ao clicar fora e,
quando possível, trocar popovers da barra com um clique. A página não identifica
build Tahoe 26 nem demonstra o runtime da Central.

Validação: `py_compile` do shell e 11 testes `test_system_fidelity` passaram.
Após reload, `hyprctl layers` mediu Waybar `0,0,1920×34`, capturadores da
Central e extras `0,34,1920×1046` em HDMI-A-1 e HDMI-A-2; Central `y=44`,
menu Wi-Fi `y=38`, sem sobreposição com a faixa da Waybar. Troca por comando
D-Bus fechou a Central e mostrou o menu Wi-Fi. Capturas locais
`/tmp/hyprmac-mic02-before.png` e `/tmp/hyprmac-mic02-extras-after.png`;
Wi-Fi deixado visível. Sem injeção de clique físico, confirmação de consumo
do primeiro clique ou cena Tahoe equivalente. Geometria da barra foi medida
no HyprMac; tipografia, material e movimento do menu não foram comparados.
Menus nativos da Waybar e cliques em áreas da barra sem ação do shell podem
permanecer abertos junto ao painel; conferir em ensaio físico. Implementação
PARCIAL; validação TESTADO_LOCAL. Registros separados:
`tahoe26:aplicacao:mic02-menu-bar-passthrough` e
`tahoe26:validacao:mic02-menu-bar-passthrough`. Próximo ID: MIC-03.

MIC-01, feedback pressionado da Central no tema claro (2026-10-11):
`style-light.css` tinha prioridade sobre `style.css`; hover e pressionado
resolviam para o mesmo fundo `rgba(132,132,150,0.48)` nos blocos largos,
círculos e botão Edit Controls [real:shell/style-light.css:211]. O tema claro
agora repete o brilho interno e fundo pressionado já existentes no tema
escuro [real:shell/style-light.css:214] [real:shell/style.css:178], incluindo
o brilho azul do círculo ligado [real:shell/style-light.css:232]. O mecanismo
de compressão do `GlassButton` já existia [real:shell/hyprmac-shell:1747].
Referência: transcrição local da sessão WWDC25 219 descreve reação luminosa
à interação, mas está classificada experimental/versão desconhecida no banco;
não estabelece valores, timing ou aparência final Tahoe 26.

Validação: em `Gtk.Button` reais sob `.cc`, o fundo calculado no tema claro
é 0,42 em repouso, 0,48 em hover e 0,50 pressionado (alfas; as cores também
mudam); antes hover e pressionado eram ambos 0,48. Renderização GTK do bloco
144×66 teve 8.669 pixels diferentes entre hover e pressionado. Central
recarregada e inspecionada no desktop em claro e escuro (HDMI-A-1,
1920×1080 escala 1); tema escuro original restaurado e Central deixada
visível. Capturas locais `/tmp/hyprmac-mic01-cc-light.png` e
`/tmp/hyprmac-mic01-cc-dark.png`; renderizações em
`/tmp/hyprmac-mic01-render-{hover,pressed}.png`. Não houve clique físico nem
captura Tahoe equivalente; geometria, tipografia e material foram observados
em repouso, mas não comparados em cena equivalente. O brilho e 40 ms seguem
estimativas locais. Implementação PARCIAL; validação TESTADO_LOCAL. Registros
separados: `tahoe26:aplicacao:mic01-cc-pressed-light` e
`tahoe26:validacao:mic01-cc-pressed-light`. Próximo ID: MIC-02.

MIC-04, complemento da navegação (2026-10-11): o `StandardKeyBinding.dict`
original do AppKit 26.6.1/25G76 (SHA-256
`500c1d3a0afb3f9bcca83a9ec20f128b5b802c699bd336634d20bebfecad0390`)
declara Option+Up/Down para parágrafo e Option+Control+B/F para palavra,
com variantes Shift que estendem a seleção. `shell/cocoa_entry.py` agora
encaminha esses movimentos nos sete campos de busca próprios que já usam
`CocoaEntryKeys`. Oito testes `test_cocoa_entry` passaram, incluindo Entry e
SearchEntry reais; `py_compile` passou. Shell recarregado, Spotlight aberto com
campo focado no HDMI-A-1; há dois monitores 1920×1080, escala 1. Captura local em
`/tmp/hyprmac-mic04-spotlight.png`. Não houve entrada física de teclas nem
captura Tahoe equivalente. Aparência do campo não mudou; geometria,
tipografia, material e movimento não foram comparados nesta rodada. O
mapeamento é estático, e GTK/Pango pode escolher outros limites de palavra;
foco global entre apps, IME e atalhos capturados pelo Hyprland seguem sem
validação. Implementação PARCIAL; validação TESTADO_LOCAL. Registros separados:
`tahoe26:aplicacao:cocoa-navigation-completion` e
`tahoe26:validacao:cocoa-navigation-completion`. Próximo ID: MIC-01.
Auditoria: integridade SQLite e links operacionais íntegros; 11 hashes
divergentes de registros de apps alheios a MIC-04 permaneceram pendentes.
`comparar.py --resumo` marcou 94% na matriz interna existente, sem medir
este incremento; `--pendentes` foi conferido. `git diff --check` global
continua acusando whitespace em documentos anteriores fora deste ciclo.

Fila redirecionada em TODO/AGENTS/catálogo: controles, Central/Spotlight,
movimento/janelas e barra/notificações. Dock/refração permanece secundário,
com os resultados anteriores preservados. MIC-04 é parcial e testado localmente
somente no escopo abaixo; não há certificação de foco global.

Evidência: AppKit StandardKeyBinding.dict do Tahoe 26.6.1/25G76, conferido no
original e por SHA-256. Option+setas horizontais move por palavra;
Ctrl/Command+setas horizontais move às extremidades da linha; Command+setas
verticais move no documento. Shift estende seleção; Ctrl+Shift+A/E também.
Metadata recuperado mostra SearchField:NSSearchField e editor NSTextView no
Spotlight. São evidências estáticas, sem comprovar overrides ou execução Apple.

Implementação: `shell/cocoa_entry.py` compartilha a edição já existente e os
novos movimentos entre Spotlight, galeria da Central, Clipboard e Ajustes.
Handlers dos resultados preservam setas modificadas para edição; setas simples
continuam navegando. Campos somente leitura não recebem mutações. Desenho do
Spotlight continua em spotlight_controls; GTK, tiling e arquitetura preservados.

Validação: 23 testes passaram (7 Cocoa, 11 integração system_fidelity, 2 busca,
3 lançador), incluindo propagação por Gtk.Window e seleção com âncora.
py_compile passou; Ajustes renderizados, shell recarregado em uma instância,
Central/galeria visível e inspecionada; hyprctl configerrors vazio. Capturas e
log locais em `/tmp/hyprmac-cocoa-cycle/`. Comparar resumo/pendentes executados:
94% é nota interna da matriz existente, sem medir o incremento de teclado.

Limites: segmentação e bidi usam GTK/Pango; sem confronto runtime Tahoe,
IME ou entrega física dos modificadores pelo compositor. Super+setas pode
ser consumido pelo tiling; os atalhos globais não foram alterados. Kill buffer
continua por campo. Option+Up/Down e Option+Ctrl+B/F fora deste subconjunto.
Risco visual baixo sem CSS; seleção/foco precisam confronto equivalente Tahoe.
O ambiente emitiu warnings de acessibilidade indisponível e deprecações GTK.

Registros: `tahoe26:resource-auto:cocoa-navigation`,
`tahoe26:aplicacao:cocoa-shared-search`, `tahoe26:validacao:cocoa-shared-search`
e `tahoe26:pesquisa:shared-controls-opportunities`. Ciclo inicial do Spotlight
preservado como superseded. Corrigidas proveniência de ControlCenterSettings
para Localizable.loctable e classificação de galeria/opções da barra para
inspeção estática. Próximos incrementos: taxonomia da galeria e opções reais
do relógio; depois investigar estados e geometria compartilhados em
DesignLibrary/SwiftUICore por perguntas específicas, sem recuperar todos os tipos.

Curadoria e índices atualizados; auditoria dos dois bancos íntegra, sem links
quebrados nem hashes divergentes. Diff dos arquivos deste ciclo limpo;
`git diff --check` global mantém avisos de whitespace em documentos anteriores
não alterados neste ciclo. `git status --short` conferido; trabalho local preservado.

## Orquestração FreeLLM e Clock Options — 2026-10-11

- `BaseConhecimento/ferramentas/agentes.py`: auxiliares sem estado pelo gateway FreeLLM
  (localhost:3001, só inferência OpenAI; sem runtime de agentes). Chave lida da config
  local do gateway, nunca impressa; histórico/cache em `.agentes/` (ignorado pelo git).
  Primeiro lote: FMT-01 (formatador, corrigido: dependia do locale e de `show_date`
  inválido) e TST-01 (testes às cegas, aprovado; detectou o defeito real).
- Relógio da barra: Clock Options reais do Tahoe 26.6.1 (`shell/clock_format.py`,
  `waybar/scripts/clock.py` no lugar de `clock.sh`, folha em Ajustes ▸ Menu Bar).
  Hora agora `H:mm` sem zero (template `EEE H:mm` do ControlCenter). 25 testes; validado
  na barra real. Limites: "When Space Allows" não mede a sobra da barra (data oculta);
  Analog/Announce ausentes; ordem/largura da folha sem captura Tahoe.
- Alerta: os 90 registros `tahoe26:apps:*` marcados `verified` vêm do
  `scripts/mineração-agents.sh`, cujo `agent-runner.js` não existe; valores como
  `spring(0.4, 0.8)` não constam do material minerado. Ver
  `tahoe26:auditoria:apps-registros-suspeitos`; não usar sem verificação.
- Genie pelo botão amarelo dos apps: o Hyprland 0.56.2 descartava `xdg_toplevel.set_minimized`
  (sem evento). `genie.patch` publica `minimized>>ADDR,1|0`; o Dock faz o Genie como ⌘M. Validado
  com janela GTK de laboratório (evento, estacionamento e quadros da animação). X11/XWayland e
  restauração pedida pelo app não cobertos. `scripts/vidro instalar` agora roda `git clean`.
- Regressão anterior corrigida: `shell/style.css` local tinha `@define-color dl_* Npx` (4 tokens
  sem uso, mesma origem dos registros suspeitos) que impedia o shell de iniciar; comentados.
- Finder: Nautilus 51 é o padrão de `inode/directory` (antes `kitty-open`); `install.sh` repete
  isso. `gtk/gtk4.css` ganhou regras só para `window.nautilus-window`, medidas em
  `tahoe-dark.jpeg`: linhas de 32, cápsula de seleção cinza (tinta 6 %) com texto/ícone em
  destaque, sem título na lateral. Faltam: cabeçalhos Favorites/Locations (o Nautilus usa
  separadores), lateral flutuante de vidro, barra de status e toolbar em cápsulas.

## Orquestração N agentes FreeLLM — 2026-10-11 (madrugada)

- `BaseConhecimento/ferramentas/orquestra.py`: fila SQLite persistente (`.agentes/fila.db`),
  agentes autônomos por tool calling (`auto` do FreeLLM), isolamento por tarefa em
  `.agentes/iso/<ID>`, comandos em `bwrap` (sistema somente leitura, sem rede, 8 GB, 120 s),
  backoff de limite de taxa, compactação de histórico, bloqueio de chamadas repetidas e
  integração só após aprovação (sha256 da base). Escrito por agentes FreeLLM (ORQ-01..05);
  defeitos de laço, raiz, permissões e histórico de tool_calls corrigidos pelo orquestrador.
- Resultado prático: tarefas curtas funcionam (NOT-TST: 86 testes integrados; fumaça em 4
  passos). Tarefas longas esbarram em ~8 rotas com tool calling, em cooldown de 5–10 min, e
  em laços; APP-ID, MIC-14 e AUD-APPS foram concluídas pelo orquestrador.
- Apps: Photo Booth/Calculator/TextEdit renomeados (`shell/apps`), Papers/Loupe ocultos;
  PDF e imagens → `shell/hyprmac-preview` (testado com PNG e PDF); nomes na barra.
- Reduzir Movimento: alternar nos Ajustes recarrega o Hyprland (validado ida e volta);
  slider de vidro vai direto ao estado final. Tremida da senha mantida (sem evidência).
- Auditoria: dos 90 registros `tahoe26:apps:*`, 11 → `invalid`, 79 → `experimental`
  (`registros_reclassificados` guarda o estado anterior).
- Problema conhecido: cada recarga da Waybar deixa processos zumbis (0 KB) dos módulos.
- Notes: `shell/hyprmac-notas` + `shell/notas.css` (rascunho FreeLLM completado pelo orquestrador),
  `.desktop` e passo no `install.sh`; snapshot e janela real conferidos; ver
  `tahoe26:aplicacao:notes-app` para limites (sem pastas, sem menu Format, claro não conferido).
- Preview (`shell/hyprmac-preview`): título à esquerda com página, lateral flutuante com seleção
  em cápsula, sem rodapé Previous/Next, ajuste automático e página centralizada; comparado com
  `preview-pdf-escuro-com-central.png`. Faltam marcação, busca, rolagem contínua e tema claro.
- Journal (`shell/hyprmac-diario` + `diario.css`): lateral com Insights/Places, All Entries, estado
  vazio com borboleta, lista e editor simples; claro/escuro e janela real conferidos. Medidas
  aproximadas (referência reduzida). Notes: corrigidos clique no círculo, perda de marcadores
  ao salvar e laço salvar/selecionar — achados pelos testes do agente TST-NOTAS.
- Photos (`shell/hyprmac-fotos`): biblioteca de ~/Pictures, lateral Library/Pinned/Albums, grade
  quadrada com ajuste, colunas, busca, favoritos, lixeira; janela real conferida (CPU ociosa 0).
  Vídeos com quadro e duração (ffmpeg em segundo plano, cache); miniaturas escaladas à célula. Falta Collections.
- Notes: menu **Format** na barra (Notes File Edit Format View Window Help), itens do MainMenu
  real (Checklist, Mark as Checked, Check All, Uncheck All, Move Checked to Bottom, Delete
  Checked) via org.gtk.Actions do app; validado por D-Bus. Os itens de More ficam planos:
  submenu no menu da Waybar 0.15 dá segfault (isolado numa Waybar temporária). Os testes
  `tests/test_notes_app.py` cobrem clique no círculo, salvamento e troca de nota.
- Base: `auditar_base.py` aponta 11 `documentos` com caminho fictício `tahoe26:apps:*` marcados
  presentes (mesmo pipeline falso); não removidos — decidir com o usuário. Catálogo atualizado
  (MIC-14 PARCIAL; Preview/Journal/Notes/Photos parciais, Photo Booth provisório).
- **Problema encontrado 2026-10-11 07:31**: após horas ocioso (DPMS do hyprmac-ocioso), o
  hyprmac-shell seguia vivo mas sem as camadas no HDMI-A-1 (sem Dock, widgets, ícones e wallpaper);
  só a Waybar restava. Reiniciar o shell restaurou. Investigar recriação das layer surfaces
  quando a saída volta do DPMS (provável `monitor-removed/added` no GDK).
  **Corrigido 2026-10-11 09:0x:** causa confirmada no journal (05:46: amdgpu reconfigura a saída e
  uma Waybar aborta no destrutor do IPC = saída removida no sono profundo do HDMI). O shell agora
  ouve `monitoradded` e faz `hyprmac-shell reload` 3 s depois do último evento. Validado
  desativando/reativando o HDMI-A-2: monitorremoved → monitoradded → PID novo, camadas completas.
- Central/galeria: categorias do Tahoe 26.6.1 (BentoGallery) em ordem alfabética como na referência;
  rótulos da Central em inglês com strings do ControlCenter (antes "Rede", "Tela", "Som"…).
- CCN-03 (parcial): clique direito num controle da galeria → "Add to Menu Bar"/"Remove from Menu
  Bar" (strings do BentoGallery) para Wi‑Fi, VPN, Focus e Now Playing; lógica compartilhada com
  Ajustes em `shell/menubar_items.py` (4 testes). Ocultar/mostrar validado na barra real; o clique
  no menu da galeria não foi exercitado fisicamente. Arrastar para a barra continua ausente.
- Central de Notificações (CCN-07 parcial): grupos do mesmo app empilhados com "N more
  notifications" e bordas dos cartões de trás; clique expande com cabeçalho "Show less" + ✕;
  textos do NotificationCenter.app 26.6.1 (Clear All, now, %dm ago, Yesterday, %d days ago,
  No notifications available); calendário em inglês. Ajuste de altura refeito após a alocação.
  Gancho de teste `nc-preview-expanded`. Ações nos cartões do histórico (CCN-08) ainda ausentes.
- Notificações (CCN-08 parcial): ações da notificação (ex.: Reply, Mark as Read) aparecem ao
  passar o ponteiro no cartão do histórico; gancho `nc-preview-actions`. Validado com
  notify-send -A; o clique na ação não foi exercitado (usa o mesmo invoke dos banners).
- Preview: barra de marcação para imagens (Codex gpt-6.1-sol, CDX-PRV): desenho livre, retângulo,
  oval, seta, texto, 6 cores, 3 espessuras, desfazer, salvar cópia "(marcado).png" sem tocar o
  original; 20 testes. Estilo plano e botão circular ajustados pelo orquestrador contra
  preview-imagem-marcacao.png. Faltam seleção, Instant Alpha, assinatura, forma de borda/preenchimento.
- Notes: painel de pastas (Codex gpt-6.1-sol, CDX-NOT): "On My Mac", pastas = subdiretórios com
  contagem, New Folder com renomeação inline, Recently Deleted, nova nota na pasta selecionada,
  `--snapshot-folders`; 101 testes de Notes. Snapshot conferido: layout de três colunas do Notes.
- Menu Apple (BAR-06 parcial): "About This Mac" abre Ajustes ▸ General ▸ About (`hyprmac-ajustes
  about`); Force Quit… abre a janela Force Quit do shell (antes `hyprctl kill`, modo matar-com-
  clique); removido "Menu Bar Settings…", que não existe no Mac. Recent Items fica de fora
  (submenu derruba a Waybar 0.15).
- Codex rodada 2 (gpt-6.1-sol, validado e integrado pelo orquestrador; 315 testes):
  - Spotlight (CDX-SPT): seletor "/" com filtros (Applications, Folders, Settings, Actions) e
    nome de app + Tab entra em "buscar em <App>" (Finder → arquivos, System Settings → ajustes,
    demais → janelas e ações); Backspace vazio remove o token. Prévia "/" conferida.
    Faltam Files/Clipboard no seletor e MIME/PDF; ícone de Actions igual ao de Settings.
  - Photos (CDX-FOT): visualizador interno (‹ + data, coração, informação; ←/→, Esc volta),
    coração nas favoritas; `--snapshot-viewer` conferido.
  - Journal (CDX-JRN): editar entrada existente, Delete Entry com confirmação (lixeira),
    busca, streak no Insights, lista agrupada por mês; snapshot conferido.
- Mineração do DMG: Codex dedicado em ~/.local/share/hyprmac-pesquisa/.../minerar/codex-2026-10-11
  (textos en, menus, defaults, inventário de animações); terminal "Codex — mineração do DMG".
- Ajustes: 9 textos corrigidos pelas strings reais do Tahoe (auditoria do subagente contra
  minerar/codex-2026-10-11/textos: Battery, Print-Scan, Wi‑Fi, Family, Dock, Siri…). Em aberto
  com evidência parcial: "Widget style"/"Full-color" (no Tahoe só há "Dim widgets on desktop"),
  descrições de hero e textos de Wallet sem equivalente. Relatório: /tmp/claude-1000/auditoria-ajustes.md.
- Codex rodada 3 (validada por Haiku; 383 testes):
  - Spotlight (SPT3): "/" com Applications, Files, Folders, Settings, Actions, Clipboard; Actions
    com ícone próprio; filtros kind:pdf/image/folder. Ordem final ainda sem captura do Tahoe.
  - Mission Control (MSC): barra de Spaces com "Desktop N" (formato "Desktop %@" do Dock 26.6.1),
    "+", arrastar janela para mesa (follow=false), Exposé de app mantém a fileira de minimizadas
    (comportamento do App Exposé; o validador rejeitou por engano, revertido). Captura conferida.
  - Calculator (CALC): app próprio dev.hyprmac.Calculator (botões circulares, laranja, lógica
    Decimal, = repetido, %, ±, Error), 30 testes; GNOME Calculator oculto. Falta conferir o
    operador ativo invertido ao vivo.
- Dock (Codex rodada 4, validado por Haiku): magnificação contínua sem saltos, mola na reordenação com espaçamento constante, indicador de 4 px a 4 px do ícone.

## Reconstrução dos 70 apps e piloto Rust — 2026-10-11

- Mineração conferida por JSON e amostra na origem montada: 70 apps examinados,
  38 menus estruturados, 2 incertos (Finder/Freeform), 30 sem MainMenu estático.
  Contagens atuais: 309 pacotes com textos, 2.370 tabelas, 110.437 entradas,
  1.581 candidatas de defaults e 53 registros de animação. A extração anterior
  308/2.369/110.433/1.268 estava desatualizada; não há hashes originais para
  certificar toda a origem. `catalogar_apps_tahoe.py` gera a matriz JSON e 70
  registros SQLite conservadores: 15 PARCIAL, 55 AUSENTE. Menu NIB não prova UI
  nem comportamento em execução.
- MIC-04: as buscas de Notes, Journal e Photos passaram a usar `CocoaEntryKeys`.
  MIC-11: `app_theme.py` acompanha `color-scheme` nos três apps abertos, sem
  unificar geometrias CSS. Implementação e validação registradas separadamente
  no SQLite. 66 testes locais passaram, inclusive os widgets GTK reais e um
  sinal de mudança de tema simulado; sintaxe dos arquivos afetados conferida.
  Notes foi aberto e deixado visível no desktop. Não houve ensaio Tahoe em
  runtime nem troca real de tema do desktop nesta rodada.
- Calculadora: `Exec` do `.desktop` agora aponta ao script existente. Cópia
  instalada atualizada; `desktop-file-validate`, Gio e janela mapeada no
  Hyprland confirmados. Os seis lançadores próprios (Calculator, Notes,
  Photos, Preview, Journal e Settings) apontam a PNGs 256×256 extraídos dos
  respectivos ICNS do volume Tahoe 26.6.1 build 25G76. Resolução de ícone e
  executável validada por Gio/GdkPixbuf e teste local; comparação visual de
  todos os tamanhos/estados no Tahoe ainda pendente.
- Rust: `core/activity-probe/` é um piloto isolado, sem dependências externas
  nem ligação ao shell. Lê PID, nome, estado, CPU ticks e RSS de `/proc` em JSON
  Lines. Três testes, build release e formatação passaram. Em 101 coletas locais
  de cerca de 451 processos: Rust p50/p95 11,882/12,151 ms, pico 2.504 KiB;
  Python stdlib com os mesmos campos 18,032/19,151 ms, pico 10.244 KiB. A
  comparação sequencial não controla carga nem custo de iniciar o processo;
  ganho preliminar, insuficiente para integrar o piloto ao app. Binário release
  538.200 bytes. Nenhum aplicativo mudou de linguagem neste ciclo.
- Atalho local: `SUPER + F5` executa `shell/hyprmac-shell reload`, preservando
  `SUPER + F8` para recuperação do renderizador/configuração. Lua compilou,
  `hyprctl reload` aplicou a configuração e o bind `SUPER/F5` apareceu ativo.
  Acionamento físico das teclas ainda não foi testado.
