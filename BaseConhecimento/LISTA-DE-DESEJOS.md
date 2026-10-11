# Catálogo de comportamentos e desejos — HyprMac / macOS Tahoe 26

Atualizado em 2026-10-10 por solicitação do usuário. Este é o catálogo canônico
para priorizar **próximas modificações**, com implementação e validação
independentes. São **113 requisitos únicos**, preservando os itens enviados
(mais de 60); Quick Look aparece uma única vez em FIL-01.

As descrições são **metas solicitadas**, não comprovação de comportamento Apple.
Os links de previews/favicons do texto enviado não são evidências verificadas.
Confirmar no Tahoe 26 as alegações, estados, medidas e mecanismos antes de
implementar. Não importar números, curvas ou fidelidade de fontes desconhecidas.

## Diretriz vigente

Priorizar sensação de uso, movimento, foco, materiais e continuidade. Consolidar
os componentes existentes do shell antes de criar Preview, Fotos, Notas, Diário,
Câmera ou outros aplicativos próprios. Recursos ausentes ficam no backlog até
uma etapa de expansão; integrações Linux são equivalentes funcionais, não
compatibilidade nativa com APIs ou serviços Apple.

| Área | Prioridade geral |
|---|---|
| Controles compartilhados e microinterações | Frente 1 — prioridade atual |
| Spotlight e Central de Controle | Frente 2 — prioridade atual |
| Janelas, Mission Control, animações e gestos | Frente 3 — preservar tiling |
| Barra, menus e notificações | Frente 4 — prioridade atual |
| Dock, refração e materiais | Investigação secundária; resultados preservados |
| Finder, arquivos e aplicativos próprios | P2 — expansão |

As prioridades de cada comportamento abaixo refinam a área: por exemplo,
SNI é P0 mesmo dentro da barra P1. INT usa P2 por ser expansão posterior;
é uma organização deste backlog, não prioridade atribuída pela Apple.
A fila atual de quatro frentes (2026-10-11) está no [TODO](../TODO.md),
referenciada por estes IDs; a fila anterior permanece como histórico.

## Estados e evidências por comportamento

- **Implementação:** `A_VERIFICAR`, `RELATADO_PARCIAL`, `RELATADO_AUSENTE`,
  `PARCIAL`, `IMPLEMENTADO` ou `AUSENTE`. Os estados RELATADO vêm dos checkpoints
  anteriores; não representam nova auditoria do código. `A_VERIFICAR` não
  significa que o recurso está ausente.
- **Validação:** `NAO_AVALIADO`, `TESTADO_LOCAL`, `COMPARADO_PARCIAL`,
  `VALIDADO_TAHOE` ou `BLOQUEADO_REFERENCIA`. Todos os requisitos começam
  `NAO_AVALIADO` contra seus critérios completos. Ensaios parciais anteriores
  permanecem nas evidências; não se perde nem se amplia sua conclusão.
- **Evidência:** `—` significa nenhuma evidência associada nesta inclusão.
  Acrescentar caminhos/IDs SQL e versão, captura ou gravação, condições,
  resultado e limitações quando a validação for executada. A solicitação do
  usuário é a origem da prioridade, não prova da implementação ou fidelidade.

Referências herdadas: **E1** = [STATUS — implementado e ciclos de 2026-10-10](../STATUS.md),
**E2** = [STATUS — incompleto ou sem evidência suficiente](../STATUS.md),
**E3** = `MacTahoe/base.db → descobertas:119` (reordenação parcial, execução
pausada; não retomar automaticamente essa execução). Para detalhes relacionados,
consultar FTS/SQL e os registros antes de ler o código ou `/mnt/macos/root`.

**E4** = registros `tahoe26:resource-auto:cocoa-navigation`,
`tahoe26:aplicacao:cocoa-shared-search`, `tahoe26:validacao:cocoa-shared-search`,
`tahoe26:aplicacao:cocoa-app-searches`, `tahoe26:validacao:cocoa-app-searches`,
`tahoe26:aplicacao:cocoa-navigation-completion` e
`tahoe26:validacao:cocoa-navigation-completion`
no SQLite. Mapeamentos estáticos AppKit 26.6.1/25G76 e testes GTK locais;
segmentação/bidi, overrides Apple e entrega dos atalhos pelo compositor não
certificados. Nenhuma validação global de MIC-04.

**E5** = registros `tahoe26:aplicacao:mic01-cc-pressed-light` e
`tahoe26:validacao:mic01-cc-pressed-light` no SQLite. CSS do tema claro da
Central e estados GTK reais; transcrição WWDC25 local classificada como
experimental/versão desconhecida. Sem quadro Tahoe 26 do botão pressionado,
medição do brilho ou clique físico nesta rodada.

**E6** = registros `tahoe26:aplicacao:mic02-menu-bar-passthrough` e
`tahoe26:validacao:mic02-menu-bar-passthrough` no SQLite. Diretriz Apple HIG
de popovers verificada na página oficial, sem versão Tahoe 26 declarada;
geometria de layers e troca local entre Central e extra Wi-Fi conferidas.
Entrega de clique físico e comportamento de todos os menus da Waybar pendentes.

## Como validar sem confundir aparência com fidelidade

Para cada componente, selecionar IDs e verificar separadamente aparência
estática, movimento, mouse/hover/pressed, drag-and-drop, teclado/foco,
integração com janelas/serviços e múltiplos monitores/HiDPI. Marcar explicitamente
os eixos que não se aplicam. No Dock, nenhum desses eixos substitui os demais.

Uma captura ou teste de CSS não certifica movimento, integração ou interação.
Só usar `VALIDADO_TAHOE` com evidência real equivalente para o comportamento e
seus estados relevantes. Resultado sem captura equivalente é estimado; registrar
a pendência e continuar nos itens com evidências suficientes. Não converter a
nota da matriz visual em porcentagem global de fidelidade do componente.

Executar comparar → implementar → capturar → medir → ajustar → validar.
Preservar callbacks, serviços, persistência e acessibilidade. Preferir até duas
rodadas por componente; terceira apenas para diferença importante com solução
clara. Animações devem ser responsivas, contínuas, interrompíveis e respeitar
movimento reduzido, sem subprocessos ou trabalho pesado por frame.

Pontos de atenção: magnificação desloca também os vizinhos, preservando
espaçamentos; menus abertos trocam com movimento horizontal sem exigir novo
clique; o vidro responde a conteúdo, geometria e interação; gestos conduzem o
progresso da animação e permitem reversão, em vez de só dispará-la ao terminar.
Para o Genie, investigar deformação da superfície real e sincronização com o
Dock; não certificar um simples fade/scale como equivalente.

## DCK — Dock

| ID | P | Comportamento / critério a confrontar | Implementação | Validação | Evidência |
|---|---|---|---|---|---|
| DCK-01 | P0 | Magnificação progressiva com influência e deslocamento suave dos ícones vizinhos | RELATADO_PARCIAL | NAO_AVALIADO | E2 |
| DCK-02 | P0 | Mola na reordenação e no retorno dos ícones, preservando espaçamentos | RELATADO_PARCIAL | NAO_AVALIADO | E3 |
| DCK-03 | P0 | Efeito Genie na minimização e restauração de janelas reais | PARCIAL | NAO_AVALIADO | E2 |
| DCK-04 | P0 | Vidro translúcido com geometria e máscaras corretas da base | RELATADO_PARCIAL | NAO_AVALIADO | E2 |
| DCK-05 | P0 | Indicadores discretos dos aplicativos abertos | A_VERIFICAR | NAO_AVALIADO | — |
| DCK-06 | P1 | Quique ao iniciar aplicativos | A_VERIFICAR | NAO_AVALIADO | — |
| DCK-07 | P1 | Arrastar aplicativos para adicionar, reordenar e remover fixação | RELATADO_PARCIAL | NAO_AVALIADO | E1 |
| DCK-08 | P1 | Arrastar arquivos sobre aplicativos para abri-los | RELATADO_PARCIAL | NAO_AVALIADO | E1 |
| DCK-09 | P1 | Stacks de pastas/Downloads em leque, grade ou lista | A_VERIFICAR | NAO_AVALIADO | — |
| DCK-10 | P1 | Menu contextual com opções específicas do aplicativo | RELATADO_PARCIAL | NAO_AVALIADO | E1 |
| DCK-11 | P1 | Indicadores de progresso e badges | A_VERIFICAR | NAO_AVALIADO | — |
| DCK-12 | P1 | Ocultação automática suave com ativação na borda | A_VERIFICAR | NAO_AVALIADO | — |

## BAR — Barra de menus

| ID | P | Comportamento / critério a confrontar | Implementação | Validação | Evidência |
|---|---|---|---|---|---|
| BAR-01 | P0 | Barra transparente conforme o estado e a referência Tahoe | A_VERIFICAR | NAO_AVALIADO | — |
| BAR-02 | P0 | Menu do aplicativo ativo acompanhando as mudanças de foco | RELATADO_PARCIAL | NAO_AVALIADO | E1 |
| BAR-03 | P0 | Ícones de status dos aplicativos via D-Bus/SNI | A_VERIFICAR | NAO_AVALIADO | — |
| BAR-04 | P0 | Menus suspensos com geometria e materiais Tahoe | A_VERIFICAR | NAO_AVALIADO | — |
| BAR-05 | P1 | Trocar imediatamente entre menus abertos ao mover o ponteiro, sem novo clique | A_VERIFICAR | NAO_AVALIADO | — |
| BAR-06 | P1 | Menu Apple com ações de sistema | PARCIAL | TESTADO_LOCAL | 2026-10-11: About This Mac → Ajustes ▸ About, Force Quit → janela do shell; sem Recent Items (submenu derruba a Waybar) |
| BAR-07 | P1 | Indicadores de Wi-Fi, bateria, áudio e Bluetooth | A_VERIFICAR | NAO_AVALIADO | — |
| BAR-08 | P1 | Personalizar e reorganizar controles | A_VERIFICAR | NAO_AVALIADO | — |
| BAR-09 | P1 | Estados visuais ativo e pressionado dos itens | A_VERIFICAR | NAO_AVALIADO | — |
| BAR-10 | P1 | Volume e brilho com expansão contextual | A_VERIFICAR | NAO_AVALIADO | — |
| BAR-11 | P1 | Ocultação automática da barra em tela cheia | A_VERIFICAR | NAO_AVALIADO | — |
| BAR-12 | P1 | Indicação de microfone, câmera e captura em uso | A_VERIFICAR | NAO_AVALIADO | — |

## GLS — Liquid Glass

| ID | P | Comportamento / critério a confrontar | Implementação | Validação | Evidência |
|---|---|---|---|---|---|
| GLS-01 | P0 | Transparência com blur contextual | A_VERIFICAR | NAO_AVALIADO | — |
| GLS-02 | P0 | Refração do conteúdo atrás do componente | A_VERIFICAR | NAO_AVALIADO | — |
| GLS-03 | P0 | Máscaras alfa corretas, inclusive nos cantos arredondados | A_VERIFICAR | NAO_AVALIADO | — |
| GLS-04 | P0 | Contornos luminosos sutis | A_VERIFICAR | NAO_AVALIADO | — |
| GLS-05 | P0 | Contraste adaptado ao conteúdo de fundo | A_VERIFICAR | NAO_AVALIADO | — |
| GLS-06 | P1 | Transições suaves entre estados e materiais | A_VERIFICAR | NAO_AVALIADO | — |
| GLS-07 | P1 | Sombras e profundidade coerentes | A_VERIFICAR | NAO_AVALIADO | — |
| GLS-08 | P1 | Materiais distintos para menus, painéis e controles | A_VERIFICAR | NAO_AVALIADO | — |
| GLS-09 | P1 | Comportamento consistente em temas claro e escuro | A_VERIFICAR | NAO_AVALIADO | — |
| GLS-10 | P1 | Estados hover, pressed, focus e disabled | A_VERIFICAR | NAO_AVALIADO | — |

## WIN — Janelas e gerenciamento do desktop

| ID | P | Comportamento / critério a confrontar | Implementação | Validação | Evidência |
|---|---|---|---|---|---|
| WIN-01 | P0 | Semáforos vermelho, amarelo e verde com ações e estados corretos | A_VERIFICAR | NAO_AVALIADO | — |
| WIN-02 | P0 | Raios dos cantos compatíveis com Tahoe 26 | A_VERIFICAR | NAO_AVALIADO | — |
| WIN-03 | P0 | Sombras, bordas e estados ativo/inativo | A_VERIFICAR | NAO_AVALIADO | — |
| WIN-04 | P0 | Minimização e restauração sincronizadas com o Dock | PARCIAL | TESTADO_LOCAL | 2026-10-11: ⌘M, menu e botão amarelo dos apps (xdg minimize → hyprglass → Dock); restaurar pelo app e XWayland não cobertos |
| WIN-05 | P1 | Redimensionamento e snapping/tile | A_VERIFICAR | NAO_AVALIADO | — |
| WIN-06 | P1 | Duplo clique na barra de título com ação configurável | A_VERIFICAR | NAO_AVALIADO | — |
| WIN-07 | P1 | Alt/Option + clique em janela ao fundo e regras de foco | A_VERIFICAR | NAO_AVALIADO | — |
| WIN-08 | P1 | Tela cheia e Spaces próprios de aplicativos | A_VERIFICAR | NAO_AVALIADO | — |
| WIN-09 | P1 | Ciclo de janelas por aplicativo | A_VERIFICAR | NAO_AVALIADO | — |
| WIN-10 | P1 | Arrastar janelas e operar em múltiplos monitores | A_VERIFICAR | NAO_AVALIADO | — |
| WIN-11 | P2 | Persistir posições e estados quando aplicável | A_VERIFICAR | NAO_AVALIADO | — |
| WIN-12 | P0 | Decoração e comportamento consistentes em GTK, Qt, Electron e apps sem CSD | RELATADO_PARCIAL | NAO_AVALIADO | E2 |

## SPT — Spotlight

| ID | P | Comportamento / critério a confrontar | Implementação | Validação | Evidência |
|---|---|---|---|---|---|
| SPT-01 | P0 | Pesquisa unificada de aplicativos e arquivos | A_VERIFICAR | NAO_AVALIADO | — |
| SPT-02 | P0 | Quatro modos: Aplicativos, Arquivos, Ações e Área de Transferência | A_VERIFICAR | NAO_AVALIADO | — |
| SPT-03 | P0 | Executar ações sem abrir o aplicativo | A_VERIFICAR | NAO_AVALIADO | — |
| SPT-04 | P1 | Histórico pesquisável da área de transferência | A_VERIFICAR | NAO_AVALIADO | — |
| SPT-05 | P1 | Filtros dinâmicos de resultados | RELATADO_PARCIAL | NAO_AVALIADO | E1 |
| SPT-06 | P1 | Buscar comandos dos menus do aplicativo ativo | A_VERIFICAR | NAO_AVALIADO | — |
| SPT-07 | P1 | Teclas rápidas personalizáveis para ações | A_VERIFICAR | NAO_AVALIADO | — |
| SPT-08 | P1 | Ranking por histórico e relevância | A_VERIFICAR | NAO_AVALIADO | — |
| SPT-09 | P1 | Pré-visualizar arquivos e resultados | A_VERIFICAR | NAO_AVALIADO | — |
| SPT-10 | P1 | Cálculos e conversões | A_VERIFICAR | NAO_AVALIADO | — |
| SPT-11 | P0 | Navegação completa por teclado | A_VERIFICAR | NAO_AVALIADO | — |
| SPT-12 | P0 | Transições e posicionamento fiéis | RELATADO_PARCIAL | NAO_AVALIADO | E2 |

## MSC — Mission Control, Spaces e gestos

| ID | P | Comportamento / critério a confrontar | Implementação | Validação | Evidência |
|---|---|---|---|---|---|
| MSC-01 | P0 | Exposição fluida das janelas com geometria coerente | RELATADO_PARCIAL | NAO_AVALIADO | E2 |
| MSC-02 | P0 | Animação contínua de entrada e saída do Mission Control | RELATADO_PARCIAL | NAO_AVALIADO | E2 |
| MSC-03 | P1 | Spaces com miniaturas e identificação | A_VERIFICAR | NAO_AVALIADO | — |
| MSC-04 | P1 | Arrastar janelas entre Spaces | A_VERIFICAR | NAO_AVALIADO | — |
| MSC-05 | P1 | Gestos de três/quatro dedos no touchpad | A_VERIFICAR | NAO_AVALIADO | — |
| MSC-06 | P2 | Papéis de parede independentes por desktop quando configurados | A_VERIFICAR | NAO_AVALIADO | — |
| MSC-07 | P1 | Hot Corners configuráveis | A_VERIFICAR | NAO_AVALIADO | — |
| MSC-08 | P1 | Exposé das janelas de um único aplicativo | A_VERIFICAR | NAO_AVALIADO | — |
| MSC-09 | P1 | Arrastar janelas para tela cheia ou outro espaço | A_VERIFICAR | NAO_AVALIADO | — |
| MSC-10 | P1 | Transições reversíveis que acompanham o progresso e a interrupção do gesto | A_VERIFICAR | NAO_AVALIADO | — |

## CCN — Central de Controle e notificações

| ID | P | Comportamento / critério a confrontar | Implementação | Validação | Evidência |
|---|---|---|---|---|---|
| CCN-01 | P0 | Controles reais de Wi-Fi, Bluetooth, áudio, brilho e foco | RELATADO_PARCIAL | NAO_AVALIADO | E1 |
| CCN-02 | P1 | Layout personalizável por arrastar e soltar | A_VERIFICAR | NAO_AVALIADO | — |
| CCN-03 | P1 | Arrastar/adicionar controles à barra de menus | PARCIAL | TESTADO_LOCAL | E2; 2026-10-11: Add/Remove from Menu Bar no clique direito da galeria (shell/menubar_items.py, tests/test_menubar_items.py); arrastar ausente |
| CCN-04 | P1 | Subpainéis animados com navegação consistente | RELATADO_PARCIAL | NAO_AVALIADO | E2 |
| CCN-05 | P1 | Sliders com resposta imediata | A_VERIFICAR | NAO_AVALIADO | — |
| CCN-06 | P1 | Controles de reprodução multimídia via MPRIS | A_VERIFICAR | NAO_AVALIADO | — |
| CCN-07 | P1 | Notificações agrupadas por aplicativo | A_VERIFICAR | NAO_AVALIADO | — |
| CCN-08 | P1 | Ações diretas nas notificações | A_VERIFICAR | NAO_AVALIADO | — |
| CCN-09 | P1 | Pré-visualização e expansão de notificações | A_VERIFICAR | NAO_AVALIADO | — |
| CCN-10 | P1 | Dismiss e transições suaves | A_VERIFICAR | NAO_AVALIADO | — |
| CCN-11 | P1 | Não Perturbe integrado a D-Bus | A_VERIFICAR | NAO_AVALIADO | — |
| CCN-12 | P2 | Indicadores de atividades em andamento | A_VERIFICAR | NAO_AVALIADO | — |

## FIL — Finder e experiência de arquivos

| ID | P | Comportamento / critério a confrontar | Implementação | Validação | Evidência |
|---|---|---|---|---|---|
| FIL-01 | P1 | Quick Look com barra de espaço, desacoplado do gerenciador de arquivos | A_VERIFICAR | NAO_AVALIADO | — |
| FIL-02 | P2 | Visualizações em ícones, lista, colunas e galeria | A_VERIFICAR | NAO_AVALIADO | — |
| FIL-03 | P1 | Pré-visualização imediata de imagens, PDFs e vídeos | A_VERIFICAR | NAO_AVALIADO | — |
| FIL-04 | P1 | Renomear arquivos com Enter | A_VERIFICAR | NAO_AVALIADO | — |
| FIL-05 | P2 | Tags coloridas | A_VERIFICAR | NAO_AVALIADO | — |
| FIL-06 | P2 | Barra lateral Tahoe com Liquid Glass | A_VERIFICAR | NAO_AVALIADO | — |
| FIL-07 | P1 | Drag-and-drop consistente com Dock e aplicativos | A_VERIFICAR | NAO_AVALIADO | — |
| FIL-08 | P2 | Informações do arquivo e ações rápidas | A_VERIFICAR | NAO_AVALIADO | — |
| FIL-09 | P2 | Cores, símbolos e emojis para pastas | A_VERIFICAR | NAO_AVALIADO | — |

## MIC — Microinterações e consistência

| ID | P | Comportamento / critério a confrontar | Implementação | Validação | Evidência |
|---|---|---|---|---|---|
| MIC-01 | P0 | Feedback visual imediato ao pressionar botões | IMPLEMENTADO | TESTADO_LOCAL | E5 — Central: tema claro distingue hover e pressionado; spring_step anima scale de 1.0 → 0.97 ao pressionar e retorna com spring(3.7, 0.82); hover/pressed states visíveis em botões GTK; reduced_motion snap a 1.0 immediately (shell/hyprmac-shell:1830-1836) |
| MIC-02 | P0 | Menus fecham naturalmente ao clicar fora | PARCIAL | TESTADO_LOCAL | E6 — capturadores deixam a faixa da Waybar livre e preservam fechamento no resto da tela; clique físico e menus da barra não cobertos integralmente |
| MIC-03 | P0 | Popovers aparecem e desaparecem com animações coerentes | PARCIAL | TESTADO_LOCAL | BLOQUEADO_REFERENCIA (2026-10-11) — a curva spring(0.3, 0.7) 150 ms veio de `tahoe26:apps:DesignLibrary.framework:animations`, registro **invalid**; não serve de evidência. Painéis do shell (CC, NC, Media) animam com emerge()/spring, só com testes locais. Falta captura em vídeo de popover Tahoe 26 (abrir/fechar/interromper) para medir duração, curva e origem |
| MIC-04 | P0 | Foco de teclado consistente entre aplicativos e controles | RELATADO_PARCIAL | TESTADO_LOCAL | E4 — edição em sete buscas próprias, incluindo Option+↑/↓ e Option+Control+B/F; atalhos Command mapeados em shell/hyprmac-shell (⌘H, ⌘Q, ⌘Option-Escape); focus tracking via hyprctl; paridade runtime Tahoe pendente |
| MIC-05 | P1 | Atalhos Command adaptados ao teclado Linux | A_VERIFICAR | NAO_AVALIADO | — |
| MIC-06 | P1 | Ponteiros contextuais adequados, preservando a preferência vigente por cursores Linux | A_VERIFICAR | NAO_AVALIADO | — |
| MIC-07 | P1 | Rolagem suave e comportamento natural do touchpad | A_VERIFICAR | NAO_AVALIADO | — |
| MIC-08 | P1 | Feedback visual na alternância de interruptores | PARCIAL | TESTADO_LOCAL | 2026-10-11: o puxador é animado pelo próprio GtkSwitch (~70 ms, só em toggle do usuário); a transição CSS margin-left anterior era inócua e foi removida; trilho troca de cor em 70 ms (`tahoe26:validacao:mic08-switch-gtk`). BLOQUEADO_REFERENCIA: sem vídeo Tahoe 26 de NSSwitch para duração, curva e estado pressionado |
| MIC-09 | P1 | Tooltips com delay e posicionamento coerentes | RELATADO_PARCIAL | TESTADO_LOCAL | E6 captura hover tracking em spotlight_controls.py:55 (self.hover = -1/128-133); delay de tooltip não implementado; posicionamento baseado em centers() calculation; necessidade de delay de 300ms e anchorage to screen edges |
| MIC-10 | P0 | Transições interrompíveis sem saltos abruptos | PARCIAL | TESTADO_LOCAL | 2026-10-11: emerge dos painéis voltou à curva macPop/320 ms do popin (antes saltava 84% do trajeto num quadro, por usar a curva do registro invalid); fechar no meio congela as margens, reabrir recomeça; altura da Central e layout da Mídia partem do valor atual. tests/test_panel_emerge.py + 14 quadros no desktop (`tahoe26:validacao:mic10-emerge-continuo`). Critério: HIG Motion "Let people cancel motion". Pendentes: vídeo Tahoe de popover; troca de capa e Wi-Fi Other não auditados quanto a reversão |
| MIC-11 | P1 | Temas claro/escuro sincronizados entre aplicativos | PARCIAL | TESTADO_LOCAL | `shell/app_theme.py` liga Notes, Journal e Photos a GSettings durante a janela; teste com sinal simulado. Sem troca real no desktop nem validação Tahoe de todos os apps. |
| MIC-12 | P2 | Sons de sistema e feedback de operações | A_VERIFICAR | NAO_AVALIADO | — |
| MIC-13 | P0 | Layout correto em monitores HiDPI | A_VERIFICAR | NAO_AVALIADO | — |
| MIC-14 | P1 | Respeitar a preferência de movimento reduzido | PARCIAL | TESTADO_LOCAL | E6 — Ajustes recarrega o Hyprland (Spaces slide↔fade validado); slider de vidro; tests/test_reduce_motion.py. 2026-10-11: entrada esticada e grade do Spotlight e troca de layout da Mídia passaram a respeitar Reduce Motion (critério WWDC25 219: sem propriedades elásticas); tests/test_reduce_motion_shell.py + medição no desktop (`tahoe26:validacao:mic14-reduce-motion-shell`). Pendentes: tremida do bloqueio sem evidência; comparação com Tahoe em Reduce Motion |
| MIC-15 | P1 | Consistência ao conectar e desconectar monitores | A_VERIFICAR | NAO_AVALIADO | — |

## INT — Integrações avançadas — expansão posterior

| ID | P | Comportamento / critério a confrontar | Implementação | Validação | Evidência |
|---|---|---|---|---|---|
| INT-01 | P2 | Transferência local equivalente ao AirDrop; avaliar LocalSend | A_VERIFICAR | NAO_AVALIADO | — |
| INT-02 | P2 | Continuidade de tarefas equivalente a Handoff por integração própria | A_VERIFICAR | NAO_AVALIADO | — |
| INT-03 | P2 | Área de transferência entre dispositivos; avaliar KDE Connect ou equivalente | A_VERIFICAR | NAO_AVALIADO | — |
| INT-04 | P2 | Atividades ao Vivo por eventos e notificações persistentes | A_VERIFICAR | NAO_AVALIADO | — |
| INT-05 | P2 | Automações equivalentes a Shortcuts por motor local de ações | A_VERIFICAR | NAO_AVALIADO | — |
| INT-06 | P2 | Continuidade com celular; avaliar KDE Connect ou equivalente | A_VERIFICAR | NAO_AVALIADO | — |
| INT-07 | P2 | Screen Time por monitoramento e relatórios locais de uso | A_VERIFICAR | NAO_AVALIADO | — |
| INT-08 | P2 | Preview integrado ou aplicativo próprio somente após consolidar o shell | A_VERIFICAR | NAO_AVALIADO | — |
| INT-09 | P2 | Senhas por integração Secret Service/libsecret | A_VERIFICAR | NAO_AVALIADO | — |

A preferência de cursores Linux está no registro `decision:linux-cursors`;
MIC-06 trata dos contextos do ponteiro e não revoga essa decisão.
App Intents/Spotlight podem ser traduzidos por adaptadores, comandos e D-Bus;
não é necessário replicar a API Apple. Quick Look de INT referencia FIL-01;
INT-04 (integração de atividades) e CCN-12 (apresentação na Central) são camadas
diferentes, não dois pedidos da mesma implementação.

## Pedidos e checkpoints anteriores — histórico de escopo

Preservados abaixo para referência e links. A fila vigente é a deste catálogo
e do TODO. Os `[x]` históricos registram entregas locais e **não equivalem a
VALIDADO_TAHOE**; reenquadrar o estado por comportamento antes de continuar.
Itens já contemplados no catálogo devem usar seus IDs, sem abrir tarefas
paralelas (menus: BAR; animações Spotlight: SPT-12; Dock: DCK; Finder: FIL;
Hot Corners: MSC-07). Pedidos adicionais de Ajustes, bloqueio e widgets seguem
preservados, subordinados à prioridade do shell.

# Histórico — solicitações anteriores

User requests backed by visual reference screenshots stored in `referencias/desejos/`.
Before implementing any item, measure its dimensions and geometry against the reference image, and check `[x]` upon completion.

Updated: 2026-10-06.

---

## 🎯 Fila anterior — consultar prioridades vigentes acima
- [ ] **Control Center in Dark Mode over Light Wallpaper:** Request user screenshot of Dark Control Center over light background to calibrate contrast curve.
- [x] **Spotlight Mode Switch Animations:** (Completed 2026-10-04: panel expands smoothly from the search capsule before revealing mode content for Files and Apps).
- [ ] **Menu Icons:** Context menus have reference (`referencias/telas/escuro-menu-contexto-sobre-rosa.png`). Pending menu bar dropdown reference.
- [ ] **Lock Screen Polish:** Clock glass styling, PAM authentication testing, and idle lock integration.
- [ ] **Missing References:** See `REFERENCIAS-PENDENTES.md`.

---

## 🧭 Menu Bar
- [ ] **Icon Sharpness:** Replace low-resolution/thin glyphs with clean SF-weighted SVGs at 16 pt.
- [ ] **Additional Status Integrations:**
  - *Live Activity Capsule* (`barra-atividade-ao-vivo.png`): Capsule showing icon + countdown with segmented progress card.
  - *Camera & Studio Indicator* (`barra-camera-screen-studio.png`): Purple status capsule with tabs for camera preview, Center Stage, Studio Light, and Mic Mode.
  - *Media Player Queue* (`barra-player-musica-lista.png`): Album art, track info, progress bar, shuffle/repeat, and "Continue Playing" queue list.

---

## 🔍 Spotlight
- [x] **Enhanced Search & Filters** (`spotlight-busca-filtro-folders.png`, `spotlight-busca-filtros-tab.png` — Completed 2026-10-04): Filter capsules (Folders, Applications, Settings, Actions), tokenized field search, date/path sublabels, and `tab` auto-completion.

---

## ⚙️ System Settings (`shell/hyprmac-ajustes`)
- [x] **Navigational Separator between ‹ and ›** (Completed 2026-10-04: 1px subtle divider inside capsule).
- [x] **Sticky Header with Soft Shadow** (Completed 2026-10-04: 22px gradient + subtle title shadow on scroll).
- [ ] **Functional Settings Search** (`ajustes-busca-1.png`, `ajustes-busca-2.png`): Search field in sidebar above user account card that filters settings panels and options.
- [x] **Liquid Glass Sliders with GlassKnob** (Completed 2026-10-04: white capsule knob expands into enlarged transparent glass knob with magnified blue refraction when dragged).

---

## 🖥️ Desktop & Widgets
- [ ] **Battery Status Widget** (`widget-bateria-1.png`, `widget-bateria-2.png`): Multi-device concentric battery rings (Mac, AirPods, Case) reading BlueZ / upower states.
- [ ] **Widget Customization & Layout Editor** (`widgets-editar.png`): Drag-and-drop addition, removal, and reordering.

---

## 📱 Tahoe Styled Utility Apps
- [ ] **PDF Preview Viewer** (`preview-pdf-claro.png`, `preview-pdf-escuro-com-central.png`):
  - Glass sidebar with page thumbnails and blue selection outline.
  - Header: "filename.pdf / Page 12 of 17".
  - Segmented capsule toolbar (Zoom, Markup, Rotate, Sign, Share) and search.
  - Parcial 2026-10-11 (`shell/hyprmac-preview`): título + "Page N of M", lateral flutuante com seleção em cápsula, sem rodapé, ajuste automático; abre PDF/imagens por padrão. Faltam marcação, assinatura, busca e rolagem contínua (`tahoe26:aplicacao:preview-layout`).
- [ ] **Journal App** (`journal-app.png`):
  - Sidebar with "Insights" and "Places" cards, journal timeline, and empty state with butterfly glyph.
  - Parcial 2026-10-11 (`shell/hyprmac-diario`): cartões, All Entries, estado vazio, lista e editor simples; medidas aproximadas (`tahoe26:aplicacao:journal-app`).
- [ ] **Camera / Photo Booth App** (`camera-app.png`): Live preview sidebar, circular blue capture trigger, and glass zoom slider.
  - Provisório 2026-10-11: GNOME Snapshot renomeado "Photo Booth" (`shell/apps`); visual ainda libadwaita.

---

## 🗃️ From Notes & Obsidian Backlog
- [ ] **Dock App Hover Label** (`dock-rotulo-nome-app.png`): Floating frosted glass tooltip with app name and pointer arrow on cursor hover.
- [ ] **Notes App** (`notes-app-claro-tela.png`, `notes-app-escuro.png`): Three-pane layout (Folders, Notes List, Editor), yellow text cursor, circular checklist toggles.
  - Parcial 2026-10-11 (`shell/hyprmac-notas`): lista + editor, cursor amarelo, círculos de checklist clicáveis, menu Format na barra; sem painel de pastas (`tahoe26:aplicacao:notes-app`).
- [x] **Screen Capture Bar Options** (`captura-barra-opcoes.png` — Completed 2026-10-04: ⇧⌘5 toolbar with capture modes, timer, and recording options).
- [ ] **Image Viewer / Markup** (`preview-imagem-janela.png`): Header with file name and dropdown; bottom annotation bar (crop, shapes, text, signature).
- [ ] **Photos Library** (`fotos-biblioteca.png`): Sidebar collections, pinned items, video duration overlays, and selection outlines.
  - Parcial 2026-10-11 (`shell/hyprmac-fotos`): Library/Pinned/Albums, grade quadrada, contorno de seleção; duração de vídeo ainda 0:00 (`tahoe26:aplicacao:photos-app`).
- [x] **Appearance Preferences Parity** (`ajustes-aparencia-escuro.png` — Completed 2026-10-04: Folder color picker, Dark/Clear/Tinted icon modes).
- [x] **Hot Corners Modal** (`ajustes-mesa-dock-cantos-ativos.png`, `cantos-ativos-folha.png` — Completed 2026-10-04: 4 corner dropdowns around desktop thumbnail with live layer-shell hot corners).
- [ ] **Finder Fidelity & nautilus Theming**:
  - Replicate macOS Finder look & feel: floating glass sidebar, capsule toolbars, alternating striped row colors in dark mode, column view, and metadata tags.

---

## Implementation checkpoint — 2026-10-06

Search now indexes 193 settings options and subpages. Battery device rings,
widget gallery drag/drop and reordering, a curved Dock label pointer, and a
confirmed idle/session-lock handshake have been implemented. Sixteen regression
tests cover the data and lifecycle behavior.

These items remain unchecked until their interactive behavior and maximum visual
fidelity are verified in the compositor. The continuation sandbox currently
cannot access the desktop sockets. Utility apps, Finder parity, menu icons and
additional status integrations remain unimplemented.

See [execution evidence and remaining scope](EXECUCAO-DESEJOS-2026-10-06.md).
