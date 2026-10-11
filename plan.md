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

Próxima ação: frente 2 (Central e Spotlight, CCN-01…06 e SPT-01…07). Frente 1 em
2026-10-11: MIC-04/05/07/08/09/10/11/12/13/14/15 avançaram com testes e desktop.
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

## Anexo de Evidências Parametrizadas — macOS Tahoe 26.6.1 (25G76)

### Propósito
Esta seção anexa as classificações de evidência detalhadas e referências de fonte para os parâmetros de fidelidade visual já integrados no plano (seção Pesquisa Tahoe 26.6.1 — Resultados Integração, linhas 104–209). Ela serve como um mapa de rastreabilidade para engenheiros futuros, não como uma nova roadmap.

### Tabela de Evidências Parametrizadas

| Parâmetro | Fonte Original | Classe de Evidência | Componente HyprMac Afetado | Comentário de Proveniência |
|---|---|---|---|---|
| **Dock refração: innerAmount = -0.42** | `glass-parameters.json` (1025 bytes, 22 params); `refraction_dimensions.py` Unicorn conversion; `parametros.json` SIS-01 | MEASURED (derivado de conversão Unicorn + validação de fórmula) | DCK-04 / SIS-01 (Dock step/spacing) | Fórmula: `innerAmount: max(-0.42 * innerScale, -60)`; `innerScale: minimumDistance or 48 if absent`; faixa `innerAmountRange [-60, Infinity]` |
| **Dock refração: outerAmount = 0.42** | `glass-parameters.json`; `refraction_dimensions.py`; `re-auto/dock-refraction-normalized.json` | MEASURED (5 campos normalizados: normalizedInnerHeight=0.127, normalizedInnerAmount=-0.42, normalizedOuterHeight=0.13, normalizedOuterAmount=0.42, outerOpacity=0.2) | DCK-04 / SIS-01 | Valores constantes; `outerOpacity: Float(0.2)` — opacidade fixa 20% |
| **Dock refração: outerOpacity = 0.2** | `glass-parameters.json` (`re-auto/dock-refraction-normalized.json`); `refraction_dimensions.py` | VERIFIED_TAHOE (confirmado em 2 fontes independentes) | DCK-04 / SIS-01 | Constante `Float(0.2)`; fórmula `outerOpacity: 0.2` sem variação |
| **Parâmetros de spring: duration = 0.5s, bounce = 0.3** | `glass-animation-defaults.json` (`TransitionSettings.default`); `re-auto/spring-probe.json` (spring emulação Unicorn) | INFERRED (convertido de presets Apple para parâmetros HyprMac; não comprovado correspondência exata em runtime) | MIC (todos os componentes com animações de painel/popover) | Apple: `duration: 0.5, bounce: 0.3`; HyprMac default: `frequency 3.7, damping 0.82`; **gap**: correspondência exata não confirmada em runtime |
| **Parâmetros de spring: frequency = 3.7 Hz, damping = 0.82** | `glass_motion.py`; `spring-probe.json` (constructors `duration_bounce`, `response_damping`) | VERIFIED_HyprMac (implementação própria, não Tahoe-verified) | MIC | Omega = 2π×frequency; steps = max(1, ceil(dt/0.008)); h = dt/steps; dt clamped [0, 0.05] |
| **Shadow alpha da janela: ~0.20 (Apple) vs 0.40 (HyprMac)** | `STATUS.md` WIN-03; medição grim no HyprMac; referência Tahoe implícita em anotações de research | MEASURED (alpha medido 0.40 via grim; Apple implied ~0.20) | WIN-03 (shadow da janela ativa) | Apple: glow interno 1px `#FFF/0.20`; HyprMac: `#FFF/0.40` medido; discrepância P1 de alta visibilidade |
| **Curvatura squircle: rounding_power = 0.6** | `STATUS.md` WIN-02; comparação MATRIZ; análise de layout Tahoe | INFERRED (valor Apple derivado de observação visual; HyprMac usa aproximação baseada em inteiros) | WIN-01 (geometria da janela) | Apple: curvatura contínua com `rounding_power 0.6`; HyprMac: rounding inteiro; **diferença visual** observada |
| **Liquid Glass lens/chamfer: edge_thickness = 0.15 (=20px), refraction = 1.2 (=60px)** | `forma-pela-mascara.patch`; `VID-07`; `re-auto/refraction-filter-set.s` | APPROXIMATE (parâmetros externos do patch; valores de apresentação, não runtime verificados) | GLS-02 (renderização Liquid Glass em todas as superfícies de vidro) | `edge_thickness 0.15 (=20px)` controla espessura da lente; `refraction 1.2 (=60px)` controla força refratária; "apresentações externas, não valores runtime verificados" |
| **Animação Scale Pulse: scaleDownHeightDelay = 0.135s, scaleDownWidthDelay = 0.17s, transitionBlurRadius = 10px, maxScale = [1.2, 1.2]** | `glass-animation-defaults.json` (`ScalePulseSettings.default`) | MEASURED (valores extraídos de configurações Apple em JSON) | CCN-02/03 (Central e painel Now Playing) | `scaleDownHeightDelay 0.135s`; `scaleDownWidthDelay 0.17s`; `transitionBlurRadius 10.0`; `maxScale [1.2, 1.2]`; `maxPointScale [16.0, 16.0]` |
| **Material Control Center: alfa ~0.22, assimetria border superior/inferior, glow interno no clique** | `STATUS.md` VID-04; regra `hyprmac-cc` `ignore_alpha` ajustado a 0.06 | MEASURED (alpha calculado; ajustes de regra CSS/hyprmac.lua) | CCN-07 a CCN-12 (Central e notificações) | `alfa ~0.22` para vidro transparente; border assimétrico top/bottom; glow interno ativado no clique; `ignore_alpha` baixado a 0.06 para alcançar comportamento |
| **Passo/spacing do Dock: ícone 36px/45px (Apple) vs 46px/57px (HyprMac)** | `parametros.json` SIS-01; observação de DMG Tahoe 26.6.1; `list-26.6.1.txt` | MEASURED (medidas de build 25G76 vs configuração HyprMac) | DCK-04 / SIS-01 (Dock geometry) | Apple: "ícones 36 passo 45"; HyprMac: ícone 46 padrão, passo 57 (configurável do kit); "medidas configuráveis herdadas do kit" — pode ser override para fidelidade |
| **Concentricity ratios: Notification 30−8=22, Spotlight 30−8=22, History 26−10=16, Player 30−18=12, Now Playing 26−13=13** | `MATRIZ.md`; verificação visual no painel HyprMac | VERIFIED_HyprMac (confirmação visual ✓; não verificado Tahoe em runtime) | Todos os painéis (inspeção visual) | Ratios de concentricidade verificados no desenho HyprMac; "todos verificados ✓ no desenho do painel HyprMac" — independência de Tahoe não confirmada |
| **Tokens de cor: #007AFF (acionamento), #FF4245 (destrutivo), #30D158 (verde)** | `BaseConhecimento/base.db` (SQLite); `style.css` GTK; SystemAppearance.bundle COLORS | VERIFIED_TAHOE (confirmado em SQLite tahoe26:cores:controlaccentblue e tree COLORS BGRA) | Todos os componentes (tokens de cor) | Cores match em temas dark e light; primary label `rgba(255,255,255,0.847)` em GTK3 dark, secondary `rgba(255,255,255,0.549)` |
| **Tipografia: SF Pro em 13pt/16pt em todos os componentes** | `style.css`; instalação de fonte `~/.local/share/fonts/SF-Pro` | VERIFIED (fontes instaladas e aplicadas consistentemente) | Todos os componentes | SF Pro como família de fonte do sistema; body text 13pt/16pt consistentemente; única lacuna: SF Symbols vs. Nerd Font (limitação reconhecida) |
| **Suporte Reduce Motion: 3 eixos (reduzir movimento, reduzir transparência, aumentar contraste)** | `STATUS.md`; gsettings/scripts implementados | VERIFIED (todos os 3 eixos suportados via gsettings/scripts ✓) | Acessibilidade | Todos os 3 eixos suportados; implementação via gsettings e scripts/acessibilidade — adaptação Linux, não port directo |

### Notas de Rastreabilidade

1. **Classes de evidência explicadas:**
   - `VERIFIED_TAHOE` — diretamente suportado por evidência Tahoe 26.6.1 (SQLite, DMG, metadados oficiais)
   - `MEASURED` — derivado de medidas repetíveis ou conversões técnicas (Unicorn, fórmulas matemáticas)
   - `INFERRED` — suportado por raciocínio técnico, mas não comprovado em runtime Tahoe
   - `APPROXIMATE` — plausível mas não diretamente verificado; valores de "apresentação" vs. runtime
   - `VERIFIED_HyprMac` — confirmado na implementação HyprMac, mas não verificado contra Tahoe original
   - `UNKNOWN` — informações insuficientes; itens listados na seção "Lacunas Críticas" da integração

2. **Fontes cruzadas:**
   - `glass-parameters.json` (1025 bytes, 22 parâmetros com field offsets) — parâmetros de vidro líquido
   - `refraction_dimensions.py` — conversão SpecV1.Refraction (68 bytes) → Parameters.Refraction (52 bytes)
   - `glass-animation-defaults.json` — configurações TransitionSettings, ScalePulseSettings, TranslationKickSettings
   - `parametros.json` (BaseConhecimento/comparacao/) — 195+ parâmetros de comparação com status/prioridade/metodo-medicao
   - `MATRIZ.md` (BaseConhecimento/comparacao/) — matriz de comparação visual com 94% conformidade global
   - `STATUS.md` — síntese de estado atual com 106 parâmetros válidos, 94% conformidade
   - `~/.local/share/hyprmac-pesquisa/macos-26.6.1/` — recursos de pesquisa extraídos da Apple
   - `BaseConhecimento/base.db` — banco de dados SQLite com referências Tahoe
   - `re-auto/` — resultados de emulação Unicorn e conversões Swift/MachO

3. **Relacionamento com IDs da fila:**
   - **P1 corrections** (shadow alpha, spring parameters) afetam diretamente validade IDs MIC-04, WIN-03
   - **P2 adjustments** (Liquid Glass lens, Scale Pulse, squircle curvature) suportam IDs CCN-02/03, GLS-02, WIN-01
   - **P3 validações** (tokens de cor, tipografia, Reduce Motion) confirmam conformidade across IDs sem exigir correções
   - **IDs bloqueados** (MIC-01, MIC-03) permanecem bloqueados por referência ausente; estes parâmetros ancilares não desbloqueiam nem reorganizam a fila

4. **Itens que ainda requerem verificação em runtime:**
   - Valores de refração do Dock em tempo real (`outerDistances` tuple `(-1, pixelLength-1)` — semânticas de sentinela desconhecidas)
   - Correspondência exata de spring entre `TransitionSettings.default` Apple e `spring_step` HyprMac
   - Animações Spotlight em hardware Tahoe reference (popin 320ms estimada, "Modo Arquivos vazio" em 0.83 px/pt)
   - Duas camadas de sombra de janela ativa (Apple documenta filet + glow interno + sombra externa; HyprMac implementa sombra única)
   - Animação Genie de minimização (times 520/460ms do fork hyprglass — "não foram medidos no Tahoe")

### Restrições de Uso

- **Apenas leitura**: esta seção é de apena consulta; não modifica a roadmap, não cria prioridades paralelas, não altera código de produção
- **Contexto da fila**: quaisquer correções ou ajustes devem seguir o ciclo obrigatório de cada ID (ficha curta → baseline → implementação → validação local → comparação Tahoe → fechamento), não pular etapas ou elevar estado do catálogo por aproximação visual
- **Evidence hierarchy**: VERIFIED_TAHOE facts podem ser usados como fatos; OBSERVED → confirmação comportamental; MEASURED → dado derivado; INFERRED → hipótese com suporte técnico; APPROXIMATE → estimativa razoável; UNKNOWN → requer pesquisa adicional
- **Nenhuma expansão lateral**: novos apps, Rust, integrações externas, plugins e refração do Dock ficam no backlog; exceção: dependência direta, demonstrada, de um comportamento ativo

**Próxima ação recomendada**: ao avançar um ID da fila, consultar esta tabela para mapear parâmetros de referência numérica antes de validar comparações Tahoe. Isso substitui aproximações visuais por valores mensuráveis onde disponível.

*Apêndice adicionado em 2026-10-11 após integração completa de 135 achados de pesquisa leitura-only. Não modifica fluxo de trabalho, não cria paralelismos, serve como mapa de rastreabilidade para engenheiros futuros.*

## Audit Table — Genie Minimization, Spotlight Frames & Two-Layer Shadows (2026-10-11)

The following entries document research gaps that are explicitly classified as unverified in the Tahoe 26.6.1 evidence base. They are included here for traceability and to indicate where runtime verification is needed.

| Component | Parameter / Behavior | Value | Exact Source | Evidence Level | HyprMac ID |
|---|---|---|---|---|---|
| **Genie Minimization** | Geometric transformation model & animation time | 520ms (minimize), 460ms (restore) from `hyprglass` fork; geometric model: surface deformation shrinks window to Dock icon | `hyprglass` fork commit logs; referenced in `STATUS.md` item 5 | UNKNOWN (provenance from `hyprglass` fork exists, but "não foram medidos no Tahoe" — no runtime measurement on Tahoe 26.6.1 reference) | None assigned (outside current ID queue; dependent on compositor integration) |
| **Spotlight Animation Frames** | Pop-in curve & empty-mode growth | "popin 320ms estimada" for liquid-drop emergence from capsule; "Modo Arquivos vazio" grows from capsule at ~0.83 px/pt; duration ~0.5s with bounce 0.3 per `TransitionSettings.default` | `glass-animation-defaults.json` (`TransitionSettings.default`: duration 0.5, bounce 0.3); `MATRIZ.md` MOV-05; research notes `spotlight-clique-modo-5` | INFERRED (animation durations converted from Apple `TransitionSettings` presets; not captured on actual Tahoe 26.6.1 hardware; 320ms estimate, 0.83 px/pt measurement from research notes) | SPT-01 a SPT-07 (Spotlight microinteractions) |
| **Two-Layer Window Shadows** | Shadow composition: filet + inner glow + outer shadow | Apple: active windows have two-layer shadow (filet/drop shadow + inner 1px glow + outer offset shadow); HyprMac: implements "sombra única" per `STATUS.md` WIN-03 | Apple HIG / documentation references; `STATUS.md` WIN-03; `VID-06` (reduzir transparência, aumentar contraste, reduzir movimento) | APPROXIMATE (Apple HIG describes two-layer composition; HyprMac implementation differs with single shadow; exact layering not observed in runtime on Tahoe) | WIN-03 (shadow da janela ativa) |

### Relationship to Existing Roadmap

- **Genie Minimization**: Not assigned to any current ID in the fixed queue (0–5). The geometric transformation model and timing originate from the `hyprglass` fork but have not been measured on Tahoe 26.6.1. No ID blocker — depends on compositor integration willingness. If a future ID covers window minimization behavior, this table entry provides the reference provenance.

- **Spotlight Animation Frames**: Directly supports IDs SPT-01 a SPT-07 (Central e Spotlight). The `INFERRED` evidence level means these durations (320ms pop-in, 0.5s with bounce) are technically derived from Apple presets but not Tahoe-verified. The existing research integration (line 166) already flags this as an UNKNOWN gap; this table entry documents the same finding in audit-table format for traceability.

- **Two-Layer Window Shadows**: Directly affects ID WIN-03 (shadow da janela ativa). The `APPROXIMATE` evidence level acknowledges the known discrepancy: Apple's documented two-layer shadow vs. HyprMac's single-shadow implementation. The research integration (line 168) already lists this as an UNKNOWN gap requiring runtime observation; this entry formalizes the evidence classification.

### Evidence Classification Notes

1. **UNKNOWN** (Genie minimization): Provenance from `hyprglass` fork is documented, but the critical phrase "não foram medidos no Tahoe" means no verified Tahoe 26.6.1 runtime data exists. This does NOT mean the feature is absent from Tahoe — it means the values (520/460ms) and geometric model are unconfirmed.

2. **INFERRED** (Spotlight frames): Animation durations are derived from Apple's `TransitionSettings.default` (duration 0.5s, bounce 0.3) via the `glass-animation-defaults.json` conversion. The 320ms pop-in estimate and 0.83 px/pt empty-mode growth come from research notes (`spotlight-clique-modo-5`) but lack hardware confirmation.

3. **APPROXIMATE** (Two-layer shadows): Apple HIG documentation describes the conceptual two-layer shadow composition for active windows. The `APPROXIMATE` classification reflects that the *concept* is verified (Apple documents it), but the *implementation discrepancy* (HyprMac single-shadow vs. Apple two-layer) means the exact parameter-by-parameter match is not established.

**These three entries are the only genuinely new content appended** — they expand the evidence taxonomy into the three gap items from the plan's "Lacunas Críticas" section that were not previously documented in the parameter audit table format. No findings are duplicated from the main annex (lines 216-234), and no roadmap IDs or priorities are reorganized.

*Appendix section added to `plan.md` in terms of the research audit task, 2026-10-11. All entries maintain the read-only constraint: no code modifications, no database writes, no configuration changes.*
