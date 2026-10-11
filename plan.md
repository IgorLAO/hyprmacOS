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

Próxima ação: MIC-04 ⌃F2 (foco na barra de menus), depois MIC-09. Em 2026-10-11: MIC-10
emerge sem salto (`tahoe26:validacao:mic10-emerge-continuo`); MIC-08 transição inócua
removida, puxador do GtkSwitch medido em ~70 ms (`tahoe26:validacao:mic08-switch-gtk`);
MIC-04 ⌃F3 Dock e ⌃F4 janelas (`tahoe26:validacao:mic04-foco-global`).
Ciclos de 2026-10-11: MIC-03 BLOQUEADO_REFERENCIA (curva vinha de registro
`invalid`; sem vídeo Tahoe 26 de popover). MIC-01 BLOQUEADO_REFERENCIA quanto ao
instante pressionado: as sequências `spotlight-clique-modo-*` e
`spotlight-controles-*` mostram hover e transição de modo, não o quadro do
clique. MIC-14 avançou: Spotlight e Mídia respeitam Reduce Motion
(`tahoe26:validacao:mic14-reduce-motion-shell`). MIC-02 segue sem entrega
física do clique; MIC-04 segue parcial quanto ao foco global.
