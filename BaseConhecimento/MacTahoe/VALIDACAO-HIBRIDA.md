# Validação da busca híbrida — 2026-10-09 UTC

Backup: `backups/base-pre-hybrid-20261009T030956964017Z.db`.
Comparação linha a linha: todas as 10 tabelas relacionais originais idênticas.
`integrity_check=ok`; nenhuma violação de chave estrangeira.

64.457 arquivos e 118 descobertas preservados. 145 documentos de busca,
77 elegíveis, 58 vetores, 19 reaproveitamentos por duplicação. Nenhuma paráfrase
ultrapassou o limiar conservador de consolidação nesta base. Vetores: 87 KiB;
banco ~46 MiB (antes ~31 MiB), crescimento principalmente do catálogo FTS.
Nova execução: **0 documentos alterados e 0 embeddings gerados**.

Ensaio com modelo local, rede desativada: carga de 1081.49 ms; consultas híbridas
entre 4.89 e 6.57 ms com modelo já carregado. São amostras locais, não SLA nem
mediana de benchmark. Resultados e tempos completos em
[`validation-hybrid.json`](validation-hybrid.json).

| Consulta | Primeiro FTS | Primeiro vetor | Primeiro híbrido | Avaliação manual |
|---|---|---|---|---|
| control center wifi | WiFiContentView (#68) | WiFiNetworkStatusView (#70) | WiFiNetworkStatusView (#70) | Três resultados Wi-Fi pertinentes |
| dock hover neighboring icons | Hover de Notifications (#118) | Pressão do ícone Dock (#114) | Pressão Dock (#114), depois badge e magnification | Melhor foco no Dock; badge é ruído residual e faltam conclusões precisas sobre vizinhos |
| popover spring | SwiftUI Animation (#93) | SwiftUI Animation (#93) | SwiftUI Animation (#93) | Spring confirmado como símbolo; não comprova curva/duração do popover |
| window inactive material | Material de popup Dock (#115) | Traffic lights inativos (#117) | Traffic lights inativos (#117) | Apenas relação parcial; não existe conclusão suficiente sobre material de janela inativa |
| system settings sidebar | Sidebar (#76) | Sidebar (#76) | Sidebar (#76) | Híbrido também recupera NavigationSplitView e decisão de mapeamento |
| now playing transition | NowPlayingContentView (#100) | Mapeamento Now Playing (#9) | Mapeamento Now Playing (#9) | Recupera decisão existente; transição nativa ainda carece de evidência |

IDs sem indicação de tabela são de `descobertas`; mapeamentos pertencem a
`mapeamento_hyprmac`. Não calculamos recall/precisão: não existe conjunto rotulado
independente. A busca melhora recuperação, não cria conhecimento ausente.

Reprodução:

```bash
python -m unittest discover -s tests -p test_tahoe_hybrid.py -v
HF_HUB_OFFLINE=1 python BaseConhecimento/MacTahoe/tools/evaluate_search.py --output /tmp/tahoe-search.json
```

11 testes: backup/migração idempotente, preservação, atualização/remoção,
filtros nos três modos, duplicatas exatas/quase duplicatas, proteção contra
números/negação diferentes, metadata somente FTS, queries escapadas/vazias,
triggers de catálogo/componente, reaproveitamento por mudança de evidência e
versionamento do modelo e UPSERT inalterado do scanner. Sintaxe Python validada; auditor existente manteve 94%.
