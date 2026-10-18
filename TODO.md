# Prioridades

## Migração integral Python → Rust — solicitação de 2026-10-18

A branch `migration/python-to-rust` iniciou a substituição do Python por Rust por contrato executável. A Waybar e a ação About usam `core/waybar-status/`; aparência, janelas, clipboard, acessibilidade, destaque, miniatura de captura, mapa de status e comparação usam `core/appearance/`, `core/window-actions/`, `core/clipboard/`, `core/accessibility/`, `core/accent/`, `core/capture-thumbnail/`, `core/status-map/` e `core/comparison/`. Restam o shell GTK e suas views, os apps, outros scripts de integração, as ferramentas de conhecimento e os testes. Preservar funcionamento e validação por componente durante a troca; a solicitação atual do usuário substitui a recomendação histórica de Rust optativo abaixo.

## Expansão de aplicativos — direção do usuário em 2026-10-11

A App Factory cobre os 55 ausentes com identidade XDG, ícone e janela ou
adapter Linux; 10 pilotos prioritários têm funcionalidade parcial. O estado
individual está em `BaseConhecimento/referencias/hyprmac-apps-progress.json`.
Próximos ciclos: comparar janelas com capturas Tahoe 26 específicas, completar
menus/toolbar/sidebar de cada app com evidência, validar hardware para áudio e
vídeo, e avançar funcionalidades mantendo COMING SOON quando a referência ou
o backend faltar. Os controles compartilhados e o shell continuam importantes
para fidelidade dos apps; a fila anterior abaixo permanece como contexto.

Execução e critérios de saída: [plan.md](plan.md). Este arquivo mantém a fila
canônica e os IDs; o plano define como fechar cada comportamento sem desvio.

Fila redirecionada pelo usuário em 2026-10-11: reproduzir o Tahoe 26 como
sistema completo. Priorizar impacto perceptível, alcance entre componentes,
evidência Tahoe disponível, viabilidade, complexidade e risco de regressão.

| Fila atual | Frente | IDs do catálogo |
|---|---|---|
| 1 | Controles compartilhados: edição, foco, estados, geometria e microinterações | MIC-01 a MIC-04, MIC-08 a MIC-10, MIC-14 |
| 2 | Central de Controle e Spotlight: organização, ações, busca e transições | CCN-01 a CCN-06, SPT-01 a SPT-07 |
| 3 | Movimento e janelas: springs, Mission Control, Spaces e gestos; preservar tiling | WIN-01, WIN-04, WIN-12, MSC-01, MSC-02, MSC-05, MSC-10 |
| 4 | Barra, menus e notificações: extras, popovers, agrupamento e feedback | BAR-03, CCN-07 a CCN-12, MIC-02, MIC-03 |

Dock e refração permanecem como investigação secundária, com todos os
resultados preservados. Não usar Liquid Glass como medida da fidelidade geral.
Ciclo atual: clique fora e troca de menus pela barra (MIC-02), registrado em
`tahoe26:aplicacao:mic02-menu-bar-passthrough` e
`tahoe26:validacao:mic02-menu-bar-passthrough`. Próximo ID: MIC-03. MIC-01 e
MIC-04 permanecem parciais e testados localmente.
Próximas oportunidades: taxonomia da galeria e opções reais do relógio da barra;
consultar `tahoe26:pesquisa:shared-controls-opportunities` antes de analisar novamente.

## Reconstrução dos 70 apps e adoção gradual de Rust

A matriz reproduzível dos pacotes Tahoe 26.6.1 está em
`BaseConhecimento/referencias/tahoe-apps-70.json` e nos registros SQLite
`tahoe26:matriz70:*`. A triagem inicial é 15 parciais e 55 ausentes; nenhuma
classificação representa fidelidade certificada. Consolidar os 15 e a biblioteca
visual compartilhada antes de expandir os grupos B/C/D. Estados COMING SOON
só entram quando houver janela, identidade e limite funcional explícitos.

Rust é optativo por componente. O primeiro piloto isolado,
`core/activity-probe/`, coleta `/proc` para um futuro Activity Monitor; não está
integrado ao runtime. Comparar o mesmo esquema e carga, medir p50/p95, pico de
memória, custo de build/manutenção e risco visual antes de integrar. Se o ganho
não justificar o custo, preservar o app Python/GTK e o piloto como experimento.
Não migrar Spotlight, molas do Dock ou apps existentes sem gargalo comprovado.

## Fila anterior — 2026-10-10 (histórico)

Ordem anterior preservada para rastreabilidade; a fila atual acima prevalece.
Consolidar comportamento, materiais, movimento e integração do shell antes
de expandir Preview, Fotos, Notas ou outros aplicativos próprios.

Os requisitos e seus estados independentes de implementação/validação estão
no [catálogo de comportamentos](BaseConhecimento/LISTA-DE-DESEJOS.md).
Esta fila referencia os mesmos IDs; não cria cópias dos requisitos.
Um item só é concluído após validar o escopo com evidências equivalentes,
não apenas por existir código ou uma captura estática.

| Fila | P | Frente | IDs do catálogo |
|---|---|---|---|
| 1 | P0 | Genie e integração Dock/janelas | DCK-03, WIN-04 |
| 2 | P0 | Liquid Glass e máscaras | GLS-01 a GLS-10, DCK-04 |
| 3 | P0 | Ícones de aplicativos na barra via SNI | BAR-03 |
| 4 | P0 | Semáforos e decoração entre toolkits | WIN-01, WIN-12 |
| 5 | P1 | Animações e gestos reais do Mission Control | MSC-01, MSC-02, MSC-05, MSC-10 |
| 6 | P1 | Ações e busca de menus no Spotlight | SPT-03, SPT-06 |
| 7 | P1 | Arrastar controles da Central para a barra | CCN-03 |
| 8 | P1 | Quick Look com barra de espaço | FIL-01 |
| 9 | P1 | Drag-and-drop completo no Dock | DCK-07, DCK-08, FIL-07 |
| 10 | P1 | Microinterações, continuidade e timing | MIC-01 a MIC-04, MIC-08 a MIC-10, MIC-14 |

Os P0 individuais abaixo indicam importância do requisito, não precedência
sobre o redirecionamento atual. Avançar quando faltar evidência, houver bloqueio técnico
ou retorno baixo, registrando a pendência. Ausentes como Genie/Quick Look ficam
registrados para investigação/expansão; sua prioridade não autoriza criar agora
novos componentes nem substituir o compositor. Consultar o estado existente
antes de refazer drag-and-drop, filtros ou outras entregas parciais.

Veja [STATUS.md](STATUS.md) para implementação e bloqueios vigentes. O backlog
anterior, incluindo decisões e checkpoints datados, está preservado em
[legado-operacional-20261010/TODO.md](BaseConhecimento/historico/legado-operacional-20261010/TODO.md)
e pesquisável com `consultar.py --historico`.
