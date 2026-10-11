# Convergência visual — 2026-10-07

Continua os registros do SQLite `MacTahoe/base.db`; não repete extrações de
Assets.car/NIB nem altera as integrações dos controles. Comparação com Tahoe
**estimada**: as referências selecionadas são foto/recorte sem condições
equivalentes. As capturas antes/depois e os tempos abaixo são do Hyprmac real.

| Componente | Diferença inicial | Alteração | Resultado | Estado |
|---|---|---|---|---|
| Control Center | Chevron permanente comprimia “Bluetooth”; resize por timer independente da apresentação | Texto ocupa a cápsula; resize no frame clock, cancelado ao fechar e retomado da altura corrente | Título completo, mesma largura; edição gravada e teste de interrupção passou | MELHOROU |
| Dock | Rótulo cortado; ícones ampliados escapavam da base/área clicável | Altura do rótulo obtida do CSS; vidro e região de entrada seguem a ampliação; hit testing segue os ícones visíveis | Cápsula de hover inteira, ícones das pontas dentro do vidro; testes nas pontas e centro | MELHOROU |
| Popovers Wi-Fi/Bluetooth/Som | Toda reabertura aguardava outra leitura dos serviços e remontava o conteúdo | Apresentar conteúdo conhecido imediatamente; atualizar em thread, preservar widgets quando a estrutura não mudou | Bluetooth: mediana de 73,06 → 30,88 ms até mapear; slider Som preservado entre atualizações | MELHOROU |

## Evidências e medição

- Referências: `referencias/telas/cc-tahoe-alvo-usuario.png` (foto: títulos sem
  chevron permanente); `referencias/desejos/dock-rotulo-nome-app.png` (rótulo
  completo com ponteiro); `referencias/telas/cc-edicao-galeria-sobre-azul.png`
  (edição). SQLite: magnification/autohide, CompactView/ExpandedView e
  MenuExtraPopoversController já investigados; nenhum desses símbolos fornece
  duração, damping ou escala oficial.
- [Capturas, overlays, diferenças e metadados](MacTahoe/comparador/resultados/convergencia-20261007/).
  [Dock antes/depois](MacTahoe/comparador/resultados/convergencia-20261007/dock-antes-depois.png);
  [Central antes/depois](MacTahoe/comparador/resultados/convergencia-20261007/cc-antes-depois.png).
- [Runtime](MacTahoe/comparador/resultados/convergencia-20261007/runtime.json):
  cinco reaberturas Bluetooth por versão, mesmo estado. Redução de 57,7% na
  mediana até `hyprctl layers` listar a superfície; inclui D-Bus/polling.
  Primeira abertura: 94,52 → 102,34 ms, sem melhora demonstrada nesse caso.
- [Análise](MacTahoe/comparador/resultados/convergencia-20261007/analise.json):
  interior do popover Bluetooth, MAE antes/depois 0,090/255; aparência estável.
  `compare.edges` gerou contornos; `motion.trace`/`settle` analisaram as gravações
  do Dock usando timestamps reais. Amostragem efetiva 32,6/34,2 fps, não FPS do
  compositor. Estabilização da intensidade aparente 80/120 ms: a região visível
  mudou com o rótulo inteiro, portanto esses tempos não demonstram piora ou
  melhora da curva. A mola existente não foi recalibrada.
- Central em edição: sequência de 93 frames indicada em `capturas.json`.
  Os 250 ms do resize continuam uma estimativa local. Não há vídeo Tahoe
  equivalente para medir trajetória, spring, damping ou morphing.

## Checkpoint e continuidade

13 testes passaram (incluindo geometria/input, ações da cápsula, interrupção,
redução de movimento, atualização de serviços e matriz de aparência).
`py_compile` passou nos três scripts exigidos. `comparar.py --resumo` mantém
94%; `--pendentes` mantém 11 itens. Esse auditor não mede fidelidade perceptual.
Shell atualizado em execução; preferências, layout e serviços preservados.

Próximo alvo: expansão Wi-Fi/Bluetooth da Central, com captura/gravação Tahoe
equivalente. Na edição, os badges “−” ainda são recortados nos limites da grade;
medir a margem externa nativa antes de alterar a composição. Pendências já
existentes de magnificação Dock e duração de artwork continuam em
`MacTahoe/TODO.md`. Não calibrar vidro, curvas ou geometria fina pela foto.
Demais blocos conservam o progresso anterior; não receberam alterações nesta
rodada. Não há nova alegação de conformidade 1:1 ou SSIM Tahoe.

## Continuação — edição e continuidade das interações

Esta seção atualiza o checkpoint acima. Preserva as alterações que já existiam
no workspace. Não foram repetidas extrações do Tahoe.

| Componente | Diferença inicial | Alteração | Resultado | Estado |
|---|---|---|---|---|
| Central, edição | Círculos “−” cortados inclusive nos overlays internos | Excedente transparente de 4 px, compensado no passo e na âncora; margem negativa retirada do botão | 11 controles mantêm posição e tamanho; badges inteiros na captura real | MELHOROU |
| Central, arrasto | Handler desempacotava três valores de `translate_coordinates`, que retorna `(x, y)` | Corrigido o consumo das coordenadas na interação afetada | Reordenação passa no teste; gesto real após correção pendente | PENDENTE |
| Abertura de painéis/popovers | Timer de 8 ms atualizava margens repetidas entre apresentações | Frame clock, cancelamento explícito e movimento reduzido durante a transição | Testes de fechar/reabrir e restaurar âncora passam; captura nova pendente | PENDENTE |
| Dock, auto-ocultar | Repetir o gatilho reiniciava os 250 ms; movimento reduzido só consultado no início | Mesmo destino conserva o progresso; redução de movimento encerra a transição | Repetição, inversão e redução passam no teste; captura nova pendente | PENDENTE |

- [Antes/depois real da Central](MacTahoe/comparador/resultados/convergencia-20261007-continuacao/cc-antes-depois.png).
  Capturado com `grim`, HDMI-A-1, 1920×1080, escala 1, tema escuro, edição.
  O fundo mudou entre capturas: não usar o par para pontuar cores/materiais.
- [Medição GTK](MacTahoe/comparador/resultados/convergencia-20261007-continuacao/metricas.json):
  11/11 controles com delta de posição e tamanho **0 px**, após compensar a
  extensão transparente da janela. Alocação dos badges **18×18 → 22×22 px**.
  Há renders normalizados, overlay, diferença e bordas via `compare.edges`.
  Esses renders não contêm o blur do compositor e só validam geometria.
- Referência: `referencias/telas/cc-edicao-galeria-sobre-azul.png`, inspecionada:
  badges circulares completos, sobrepostos aos cantos. Os 4 px preservam o
  offset do CSS existente, não são uma medida oficial. Comparação Tahoe
  **ESTIMADA**; nenhuma nova nota SSIM/MAE ou curva nativa foi atribuída.
- Implementação: [real:shell/hyprmac-shell:1665],
  [real:shell/hyprmac-shell:2338], [real:shell/style.css:997],
  [real:shell/hyprmac-shell:2977], [real:shell/hyprmac-shell:256].
  Dock conserva o timer porque uma camada totalmente fora da tela pode ficar
  sem frames; os 250 ms e a curva atual continuam estimativas locais.
- Validação: 13 testes existentes passaram quando o display estava disponível.
  Após mudar as permissões, `Gtk.init_check()` retorna falso e `hyprctl` não
  consegue acessar o socket (que continua visível). Validação final: compilação
  dos três scripts passou; testes sem display passam e os GTK são explicitamente
  pulados. Auditor mantém **94% / 11 pendências**. `git diff --check` acusa
  espaços finais em documentação preexistente; não foi feita limpeza geral.
- `/mnt/macos/root` não está montado nesta sessão. Consultados os registros
  existentes do SQLite, a referência visual e a implementação. Descobertas e
  próximo passo registrados em `MacTahoe/base.db`, sem imagens no banco.

Próxima execução: recuperar acesso normal à sessão e capturar primeiro as
aberturas/interrupções alteradas e o arrasto da Central; depois retomar a
expansão Wi-Fi/Bluetooth com vídeo Tahoe equivalente. A Central foi recarregada
para as capturas dos badges; as alterações posteriores de animação e arrasto
ainda precisam de reload no desktop. Demais componentes mantêm o progresso
anterior: faltam evidências equivalentes para novos ajustes de material/curvas.

## Retomada — atualizações dos popovers e estado dos submenus

| Componente | Diferença inicial | Alteração | Resultado | Estado |
|---|---|---|---|---|
| Wi-Fi, barra e Central | Oscilação de sinal reconstruía/reordenava as linhas | Atualizar ícone na linha existente; reconstruir quando muda a lista, conexão ou segurança | Em 3 snapshots controlados, reconstruções 3 → 1; identidade das linhas preservada | MELHOROU |
| Bluetooth, barra e Central | Variação de bateria destruía os botões | Atualizar percentual e visibilidade no mesmo widget | Em 6 snapshots controlados, reconstruções 6 → 1; conexão/desconexão continuam trocando a ação | MELHOROU |
| Menus da barra e Dock | Submenu aberto conservava seleção colorida; tema claro não cobria foco/atalhos/setas integralmente | Estado `submenu-open` acompanha map/unmap; tint neutro do kit e regras de foco completas | Lógica e sintaxe CSS verificadas; aparência em runtime pendente | PENDENTE |

- [Métricas controladas](MacTahoe/comparador/resultados/convergencia-20261007-popovers/metricas-controladas.json)
  executam a lógica anterior e atual com snapshots sintéticos e widgets de
  teste. São contagens de reconstrução, **não** FPS, latência ou comparação
  perceptual. Captura/gestos reais de todas estas mudanças continuam pendentes.
- Referências: SQLite (`WiFiNetworkStatusView`, `BluetoothDeviceDetailsView`:
  símbolos, sem duração nativa); kit em
  [real:BaseConhecimento/referencias/kit/contornos/Menus.txt:50] e
  [real:BaseConhecimento/referencias/kit/contornos/Menus.txt:325]: submenu aberto
  usa branco 8% / preto 7%. A imagem `escuro-menu-contexto-sobre-rosa.png` mostra
  hover colorido antes de abrir; esse estado foi preservado. Nenhum ajuste de
  geometria, blur ou duração foi inferido dessas fontes.
- Código: [real:shell/hyprmac-shell:7311],
  [real:shell/hyprmac-shell:7409], [real:shell/hyprmac-shell:7933],
  [real:shell/style.css:494], [real:shell/style-light.css:83].
- Validação: 10 testes passaram; 14 GTK pulados sem display. Compilação dos
  três scripts passou; CSS carregou no parser GTK (sem tela para resolver os
  ícones); diff dos arquivos de código sem erros de whitespace. Auditor segue
  94%, 11 pendências. Callbacks e serviços mantidos; nada foi escrito nas
  preferências do usuário. Nenhum reload foi possível nesta retomada.

Próximo: no desktop acessível, recarregar o shell e capturar popovers durante
atualizações e menus com submenus abertos em claro/escuro, além das transições
do checkpoint anterior. Só depois calibrar expansão Wi-Fi/Bluetooth contra
vídeo Tahoe equivalente. Comparação Tahoe desta retomada: **ESTIMADA**.

## Checkpoint final — expansão, menus e Liquid Glass

Correções abaixo **feitas** conforme os critérios verificados. `MELHOROU` não
significa fidelidade nativa certificada. `/mnt/macos/root` continua indisponível;
nenhum par Tahoe equivalente foi obtido. Comparação Tahoe **ESTIMADA**.

| Componente | Diferença inicial | Alteração | Resultado | Estado |
|---|---|---|---|---|
| Central, primeira expansão | Destino vazio enquanto Bluetooth respondia; salto de altura | Preservar grade até haver dados; reabrir usando conteúdo conhecido; cancelar navegação ao voltar/editar | 3 → 0 frames com destino selecionado sem conteúdo; cancelamento/reabertura passaram | MELHOROU — feita |
| Now Playing, arrasto | Puxador em 2:15 com rótulos retornando a 0:12 após polling atrasado | Rótulos e posição local acompanham o gesto; retomar sincronização ao soltar | 3 respostas controladas: erro de 123 s → 0 s; comando preservado | MELHOROU — feita |
| Menus claros/escuros | Hover do pai tornava brancos os textos de todas as opções do submenu | Seletores de estado limitados aos filhos diretos do item | 7 opções inativas claras: branco → preto/86%; seleção continua branca; tint neutro 8%/7% confirmado em runtime | MELHOROU — feita |
| Vidro da Central e painéis | Blur forte e pouco contraste davam aspecto fosco; reflexos discretos | Central: blur 1 → 0,8, contraste 0,61 → 0,87, specular 0,08 → 0,4, Fresnel 0,05 → 0,35; material de texto: blur 1,1 → 0,8 | Alvo colorido: desvio de luminância transmitida 15,02 → 17,42 (+16%); alvo branco: 185 → 181/255 | MELHOROU — feita |
| Movimento do vidro | Materialização acabava antes da escala; navegação lateral recortava cápsulas; pressed rígido | Lente/escala sincronizadas em 320 ms; crossfade interno em 240 ms; flexão com mola existente no Dock | Pressão 1 → 0,97068 → 1; alocação 144×66 constante; interrupção e Reduzir Movimento passaram | MELHOROU — feita |

### Evidências e limites

- [Expansão, menus e player: capturas, overlays, bordas e métricas](MacTahoe/comparador/resultados/convergencia-20261007-expansao/metricas.json).
  Bluetooth usa leitor real em GTK/Wayland; a grade do harness conserva controles
  inicializados para estabilizar a cena. Player usa snapshots MPRIS **sintéticos**
  em GTK real; nenhum seek foi enviado ao player do usuário. Menus usam ViewMenu
  real, sem ativar ações. Referência dos estados: kit `Menus.txt:50,325`.
- [Vidro antes/depois sobre alvo colorido](MacTahoe/comparador/resultados/convergencia-20261007-liquid/colorido-antes-depois.png),
  [sobre branco](MacTahoe/comparador/resultados/convergencia-20261007-liquid/branco-antes-depois.png),
  [pressão capturada](MacTahoe/comparador/resultados/convergencia-20261007-liquid/pressao-real.gif)
  e [métricas](MacTahoe/comparador/resultados/convergencia-20261007-liquid/metricas.json).
  Alvo óptico procedural, mesma resolução/escala/tema/tint, captura via `grim`.
  ROI [306,62,370,82] evita texto e artwork. O ganho de 16% mede variação de
  luminância transmitida no alvo; **não** mede fidelidade Tahoe, nitidez universal
  ou transparência percentual. Usar `fundo/central.png` e
  `fundo-branco/central.png` como fundos limpos, capturados sem a Central.
- A rodada com `adaptive_dim=0,32` foi revista: protegia branco, mas comprimia
  demais os tons médios. Valor final **0,16** preserva aproximadamente a leitura
  anterior sobre branco e recupera variação no alvo colorido. Tint do usuário
  permanece **14**; Reduzir Transparência/Contraste continuam prioritários.
- Referências visuais inspecionadas: `cc-sobre-janela-clara.png`,
  `cc-tahoe-alvo-usuario.png`, atlas Control Center e edição. O HIG local
  `hig/motion.md:19` orienta resposta ao gesto; `hig/sliders.md:22` orienta feedback
  vivo. SQLite registra `CrossfadeEffectProgress` e CompactView/ExpandedView,
  **sem** provar duração/curva. Os 3%, 240/320 ms, blur e reflexos continuam
  calibrações locais; não são parâmetros oficiais extraídos do Tahoe.
- Frame clock GTK durante a pressão: mediana **16,162 → 16,152 ms**;
  p95 **21,620 → 21,637 ms**. Sem regressão detectável nesse ensaio curto;
  **não é FPS do compositor**. Captura sequencial com timestamps reais, sem
  interpolação de frames. `wf-recorder` não está instalado.
- [Capturas do daemon final com serviços reais](MacTahoe/comparador/resultados/convergencia-20261007-liquid/capturas-runtime.json):
  Central e menu Som, HDMI-A-1, escala 1, tema escuro. Shell recarregado e presets
  ativos. Não foi necessário alterar/recompilar o shader ou criar sistema gráfico.

Implementação: [real:shell/hyprmac-shell:1670],
[real:shell/hyprmac-shell:2595], [real:shell/hyprmac-shell:3654],
`hypr/vidro-presets.lua`, `hypr/hyprmac.lua`, `shell/style.css`,
`shell/style-light.css`. Fixtures GTK passaram a usar a mesma prioridade CSS do
shell; o teste de menus sem display recebeu o callback opcional novo.

Validação: **27 testes passaram**, compilação dos três scripts passou,
`hyprctl configerrors` vazio, diff dos arquivos de código sem erros de whitespace.
Auditor mantém **94% / 11 pendências**; não usar essa nota como avaliação óptica.
Alterações anteriores do workspace preservadas.

Próximo alvo: **vidro do Dock durante magnificação/auto-ocultar**. Medir refração e
continuidade contra gravação Tahoe equivalente antes de recalibrar curvas finas.
Ainda pendentes: gestos reais de reordenação da Central, mudanças reais de
sinal/bateria e vídeo Tahoe de expansão/materialização. Não repetir extrações
CoreMaterial/NIB ou a investigação dos estados de submenu já concluída.
