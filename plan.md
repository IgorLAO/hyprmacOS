# Plano de execução — HyprMac / macOS Tahoe 26

Atualizado em 2026-10-11. Este plano governa a **ordem de trabalho**. O [TODO.md](TODO.md)
define a fila e os IDs; [LISTA-DE-DESEJOS.md](BaseConhecimento/LISTA-DE-DESEJOS.md)
guarda o estado de cada comportamento; [STATUS.md](STATUS.md) registra resultados e
limitações. Não criar outra lista paralela de requisitos.

## Objetivo e medida honesta

Reproduzir o Tahoe 26 no Hyprland em aparência **e** comportamento. Primeiro
fechar o shell existente; depois ampliar aplicativos. A nota de 94% da matriz
mede 106 parâmetros cadastrados, dos quais 84 têm status manual. Ela **não é**
porcentagem de fidelidade global. Testes locais comprovam regressões e contratos
do HyprMac, não equivalência ao Tahoe.

O marco **shell consolidado** exige que os comportamentos P0/P1 das quatro
frentes abaixo tenham implementação e validação registradas separadamente;
divergências, dependências do Linux e estados não comparáveis ficam explícitos.
O marco **sistema completo** inclui posteriormente os aplicativos e fluxos de
arquivos do catálogo. Nenhum dos dois marcos é alcançado por contagem de CSS,
capturas isoladas ou presença de um botão.

## Regras para evitar desvios

1. **Um comportamento ativo por vez.** Escolher um ID da frente atual e fechar
   implementação, ensaio e registro antes de iniciar outro. Bugs que impedem o
   desktop ou a validação podem interromper a fila; registrar motivo e retorno.
2. **Confronto antes de alteração.** Para o ID: consultar SQLite, abrir somente
   evidência relevante do Tahoe 26, localizar o código e capturar o estado atual.
   Fontes macOS 27, visionOS, kit sem versão e hipóteses não viram fatos Tahoe.
3. **Uma mudança com efeito observável.** Definir entrada, estado inicial, ação,
   saída esperada e diferença visível/comportamental. Evitar pesquisa ou refatoração
   sem consumidor e critério de aceitação identificados.
4. **Até duas rodadas de ajuste por estado.** Se faltar referência ou mecanismo,
   registrar `BLOQUEADO_REFERENCIA`/limitação e avançar na mesma frente. Terceira
   rodada só para diferença importante com solução concreta. Não elevar o estado
   do catálogo por aproximação visual.
5. **Sem expansão lateral durante a consolidação.** Novos apps, Rust, integrações
   externas, plugins e refração do Dock ficam no backlog. Exceção: dependência
   direta, demonstrada, de um comportamento ativo. Preservar pesquisas existentes.
6. **DMG sob demanda.** Antes de escavar código, formular pergunta ligada ao ID,
   saída esperada (string, token, curva, chamada, estado) e decisão que ela mudará.
   Consultar primeiro os dumps/registros já extraídos. Extração estática não
   demonstra layout, timing ou funcionamento em runtime. Encerrar a investigação
   quando a pergunta estiver respondida ou quando faltar referência executável.

## Fila fixa

| Etapa | Escopo | Critério de saída |
|---|---|---|
| 0. Base reproduzível | Inventariar a árvore de trabalho sem descartar alterações; separar arquivos ativos de fontes arquivadas; registrar ambiente, resolução, escala, tema e build Tahoe das referências. | Um checkpoint recuperável e um conjunto pequeno de cenas comparáveis. A limpeza geral de arquivos antigos não bloqueia a frente 1. |
| 1. Controles compartilhados | MIC-01 a MIC-04, MIC-08 a MIC-10, MIC-14. Começar fechando o alcance real de MIC-04: buscas próprias, foco e atalhos; depois pressionar, fechar popovers, estados de switches e movimento reduzido. | Para cada controle escolhido: repouso, hover, pressionado, foco/teclado e reversão de movimento, quando aplicáveis, medidos em componentes consumidores reais. |
| 2. Central e Spotlight | CCN-01 a CCN-06; SPT-01 a SPT-07. Completar ações, navegação, filtros, galeria e transições a partir do mesmo conjunto de controles. | Percursos completos de mouse e teclado, com abertura/fechamento, estados e resultado da ação; capturas e gravação equivalentes Tahoe/HyprMac. |
| 3. Movimento e janelas | WIN-01, WIN-04, WIN-12; MSC-01, MSC-02, MSC-05, MSC-10. Preservar tiling e regras de foco. | Minimizar/restaurar, Mission Control, Spaces e gesto interrompível verificados em janelas reais; diferenças por toolkit e monitor descritas. |
| 4. Barra e notificações | BAR-03; CCN-07 a CCN-12; MIC-02/MIC-03 onde usados na barra. | Extras, menus e notificações testados com apps reais, grupos/ações e estados abertos; sem processos residentes ou reinícios desnecessários. |
| 5. Expansão | Arquivos, Quick Look, apps próprios, integrações externas e investigação secundária do Dock/vidro, em ordem de impacto e evidência. | Abrir esta etapa só após o marco shell consolidado ou uma decisão explícita de repriorização registrada no TODO. |

## Ciclo obrigatório de cada ID

1. **Ficha curta:** ID, componente, referência Tahoe 26 com versão/proveniência,
   estado atual, hipótese, cenário reproduzível e risco visual. Buscar no SQLite
   antes de criar Markdown; usar registro curto no banco quando suficiente.
2. **Baseline:** captura ou vídeo Tahoe e HyprMac no mesmo estado, escala, tema,
   conteúdo e monitor quando possível. Se não forem equivalentes, declarar o que
   a comparação não permite concluir.
3. **Implementação:** editar a menor camada correta (`shell/style.css`, código do
   shell, `hypr/hyprmac.lua` etc.); preservar eventos compartilhados, AppIndex,
   backups/idempotência, gaps zero e regras de vidro.
4. **Validação local:** compilar arquivos afetados, executar testes pertinentes,
   recarregar o componente no desktop e deixá-lo visível. Conferir ação real,
   teclado/foco, temas, movimento reduzido e monitor/HiDPI conforme o ID.
5. **Comparação Tahoe:** medir geometria, tipografia, material, movimento e
   estados aplicáveis. Registrar resultado por eixo e a limitação restante.
6. **Fechamento:** atualizar implementação e validação **separadamente** no
   catálogo/SQLite; usar `indexar.py` após mudar fontes textuais/tokens e
   `auditar_base.py` após curadoria. Executar `comparar.py --resumo`,
   `comparar.py --pendentes`, `git diff --check` e `git status --short`.

`VALIDADO_TAHOE` só cabe com comparação equivalente nos estados relevantes.
Se um ID tiver apenas testes locais, registrar `TESTADO_LOCAL`; se a comparação
cobrir parte do escopo, `COMPARADO_PARCIAL`. Divergência visível não se esconde
sob uma nota agregada.

## Controle de progresso

Ao fim de cada ciclo, responder no STATUS ou no registro do ID: **o que mudou,
qual evidência Tahoe foi usada, o que foi testado, o que continua diferente e
qual é o próximo ID da fila**. Revisar a fila somente quando uma evidência nova
ou um bloqueio concreto mudar o impacto. Não trocar de frente por novidade.

Próxima ação: MIC-11 (tema claro/escuro sincronizado entre apps), depois MIC-13 e
MIC-15 (HiDPI e monitores). Feitos em 2026-10-11 nesta frente: MIC-10 emerge sem
salto; MIC-08 GtkSwitch medido; MIC-04 ⌃F3/⌃F4; MIC-09 hover de modo do Spotlight;
MIC-12 sons (volume e interface); MIC-07 mouse persistente; MIC-05 ⌘Tab e capturas.
Bloqueados por referência: MIC-01, MIC-03; MIC-04 ⌃F2 depende da Waybar.
Ciclos de 2026-10-11: MIC-03 BLOQUEADO_REFERENCIA (curva vinha de registro
`invalid`; sem vídeo Tahoe 26 de popover). MIC-01 BLOQUEADO_REFERENCIA quanto ao
instante pressionado: as sequências `spotlight-clique-modo-*` e
`spotlight-controles-*` mostram hover e transição de modo, não o quadro do
clique. MIC-14 avançou: Spotlight e Mídia respeitam Reduce Motion
(`tahoe26:validacao:mic14-reduce-motion-shell`). MIC-02 segue sem entrega
física do clique; MIC-04 segue parcial quanto ao foco global.

## Pesquisa Tahoe 26.6.1 — Resultados Integração (2026-10-11)

Esta seção integra os resultados da pesquisa completa de campo leitura-only sobre
macOS Tahoe 26.6.1 (25G76) no plano de execução. Todos os 135 achados classificados
pelo nível de evidência (VERIFIED: 58, OBSERVED: 34, MEASURED: 18, INFERRED: 12,
APPROXIMATE: 5, UNKNOWN: 8) com 94% de conformidade global.

### Mapeamento de Prioridades P1/P2/P3 para IDs da Fila

**P1 — Impacto Crítico (evidence-supportado):**
- **Dock refração** (SIS-01/DCK-04): `innerAmount: -0.42`, `outerAmount: 0.42`,
  `outerOpacity: 0.20` — mapear para etapa 3 (movimento e janelas) e etapa 4
  (barra e notificações). Parâmetros diretamente verificados através de
  `glass-parameters.json` e `refraction_dimensions.py`.
- **Shadow alpha da janela** (WIN-03): alpha implícita ~0.20 da Apple vs. 0.40
  medido no HyprMac — mapear para WIN-03. Afeta o elemento visual mais visível
  (borda da janela).
- **Passo/spacing do Dock** (SIS-01/DCK-04): ícone 36px/45px da Apple vs. 46px/57px
  do HyprMac — mapear para etapa 4. Tamanho configurável do kit, pode ser
 override para fidelidade Tahoe.
- **Parâmetros de spring padrão** (MIC): `duration 0.5s, bounce 0.3` de
  `TransitionSettings.default` vs. HyprMac `frequency 3.7, damping 0.82` —
  mapear para todas as etapas com animações de painel/popover. Afeta timing de
  abertura/fechamento de todos os componentes.

**P2 — Impacto Notável (baixo impacto):**
- **Lente/chamfer do Liquid Glass** (VID-07/GLS-02): `edge_thickness 0.15 (=20px)`,
  `refraction 1.2 (=60px)` de `forma-pela-mascara.patch` — mapear para etapa 4.
  Controla efeito refratário na borda de todas as superfícies de vidro.
- **Animação Scale Pulse** (VID-03): `scaleDownHeightDelay 0.135s`,
  `scaleDownWidthDelay 0.17s`, `transitionBlurRadius 10px`, `maxScale 1.2` —
  mapear para etapa 2 (Central e Spotlight). Afeta animações do Control Center
  e painel Now Playing.
- **Curvatura squircle da janela** (WIN-02): `rounding_power 0.6` para curvatura
  contínua vs. aproximação baseada em inteiros do HyprMac — mapear para WIN-01.
- **Material do Control Center** (VID-04): `alfa ~0.22` para vidro transparente,
  assimetria de border superior/inferior, glow interno no clique — mapear para
  etapa 4. O `ignore_alpha` da regra `hyprmac-cc` foi reduzido a 0.06 para
  alcançar esse comportamento.

**P3 — Detalhe/Secundário:**
- **Ratios de concentricidade** (todos os painéis): Notification `30−8=22`,
  Spotlight `30−8=22`, History `26−10=16`, Player `30−18=12`, Now Playing
  `26−13=13` — todos verificados ✓ no desenho do painel HyprMac. Mapear para
  inspeção visual.
- **Tokens de cor** (#007AFF acionamento, #FF4245 destrutivo, #30D158 verde) —
  todos ✓. Mapear para verificação de tokens no SQLite.
- **Consistência tipográfica** — SF Pro em 13pt/16pt em todos os componentes ✓;
  única lacuna é SF Symbols vs. Nerd Font (limitação reconhecida).
- **Suporte Reduce Motion** — Todos os três eixos (reduzir movimento, reduzir
  transparência, aumentar contraste) suportados via gsettings/scripts ✓. Mapear
  para validação de acessibilidade.

### Lacunas Criticas (Não ainda Certificadas)

Itens da matriz de evidência "UNKNOWN" que requerem atenção na fila:
1. **Valores de refração do Dock em tempo de execução** — `outerDistances`
   tuple `(-1, pixelLength-1)` de `dock-refraction-dimensional.json` tem "semânticas
   de sentinela desconhecidas". Requer verificação em runtime.
2. **Correspondência exata de spring** — `spring_step` do HyprMac com
   `frequency=3.7, damping=0.82` não foi confirmado para corresponder a
   `TransitionSettings.default` da Apple com `duration 0.5, bounce 0.3`.
3. **Animações do Spotlight** — "popin 320ms estimada" e "Modo Arquivos vazio"
   medido em 0.83 px/pt não capturados em hardware Tahoe 26 reference.
4. **Camadas de sombra de janela duas** — Documentação da Apple menciona "duas
   sombras" para janelas ativas (filet + glow interno + sombra externa), mas o
   HyprMac implementa "sombra única" per STATUS.md. O exact layering da sombra
   da Apple não foi observado em runtime.
5. **Animação Genie de minimização** — Times 520/460ms do fork `hyprglass`,
   "não foram medidos no Tahoe". Requer integração com o compositor.

### Integração com a Fila Atual

Estes mapeamentos suportam os IDs já na fila sem criar prioridades paralelas:

- **MIC-02 (click-through da barra)**: Os achados de geometria e comportamento de
  passthrough parcialmente verificados agora têm parâmetros de referência
  (delayFactor 0.4, minDelay 0.1, maxDelay 0.2 de `TransitionSettings.default`)
  para validar implementações futuras.
- **MIC-04 (foco global ⌃F3/Dock e ⌃F4/janelas)**: As discrepâncias de shadow
  alpha (P1) e parâmetros de spring (P1) afetam diretamente a validade desta
  verificação. As correções propostas aqui devem ser tentadas antes de fechar
  este ID.
- **MIC-03 (animações de popover)**: Os parâmetros de `macPop 320ms` e a
  curva de surgimento-from-origin agora têm valores de referência numérica
  (durations 0.35-0.5s, bounces 0.3-0.6 de `glass-animation-defaults.json`) para
  testar contra.
- **WIN-01/WIN-03 (geometria e shadow da janela)**: Os valores de shadow alpha
  e rounding power agora têm alvos numéricos específicos para comparar contra
  captures Tahoe no mesmo estado/escala/tema.

### Próximos Passos no Plano

1. **Priorizar correções P1** antes de avançar IDs bloqueados — as correções de
   shadow alpha e parâmetros de spring têm alto impacto visual e evidence
   suportado.
2. **Usar parâmetros numéricos** da pesquisa para substituir aproximações
   visuais na validação de cada ID.
3. **Documentar quais parâmetros são "configuráveis herdados do kit"** (SIS-01
   Dock step/spacing) vs. ones que exigem mudança de implementação.
4. **Agendar validação** usando os achados de evidence classification como
   referência: VERIFIED → pode ser usado como fato; OBSERVED → confirmação
   comportamental; MEASURED → dado derivado de medida repetível.

*Esta seção é de apenas leitura — não modifica o fluxo de trabalho, mas fornece
contexto de evidence para decisões na fila existente.*
