# Gerenciamento de contexto para agentes

Contexto é recurso computacional limitado. A janela máxima do modelo é um teto,
não uma meta. O agente deve carregar o menor conjunto que preserve a correção.

## Orçamento padrão

```text
MAX_WORKING_CONTEXT = 32k tokens
instruções do sistema  4k
task                   2k
working memory         3k
código recuperado     15k
resultados de tools    5k
saída reservada        3k

MAX_RETRIEVED_FILES = 6
MAX_FULL_FILES      = 2
MAX_SEARCH_RESULTS  = 10
MAX_TOOL_OUTPUT     = 4000 tokens
MAX_RETRIEVAL       = 12000 tokens
```

Quando o trabalho exigir mais informação, faça outra recuperação direcionada.
Não aumente o contexto apenas porque existe espaço disponível.

## Divulgação progressiva

```text
nível 0  path e nome
nível 1  resumo e papel
nível 2  símbolos, imports, estados e relações
nível 3  trechos relevantes
nível 4  arquivo completo
nível 5  binário ou imagem original
```

Para imagens, use `catalogo.json` e o atlas antes do original. Para código,
use `codigo.json`, `consultar.py --codigo` e busca por símbolos antes de ler o
arquivo completo.

## Working set

Mantenha somente:

- objetivo atual e critérios de aceite;
- perguntas ainda não resolvidas;
- decisões já tomadas;
- arquivos modificados;
- até seis arquivos diretamente relevantes;
- evidências que sustentam a próxima decisão.

Ao terminar uma investigação, converta o resultado em memória estruturada e
descarte a saída bruta de ferramentas. Não mantenha `find .`, dumps de logs,
arquivos inteiros ou imagens sem relação no contexto corrente.

Formato mínimo de memória:

```text
Goal:
Current question:
Relevant files:
Evidence:
Decisions:
Changes:
Validation:
Open risks:
Next action:
```

## Garbage collection do contexto

Quando o contexto se aproximar do limite:

1. preserve objetivo, perguntas, decisões, arquivos alterados e evidências;
2. resuma a investigação concluída em `WORKING MEMORY`;
3. remova resultados brutos repetidos e caminhos irrelevantes;
4. recupere somente o próximo trecho necessário.

Não recarregue o histórico completo para recuperar uma decisão que já foi
resumida.

## Regra de recuperação

```text
índice → metadados → resumo → trecho → arquivo completo → original visual
```

Avance somente quando o nível atual não responder à pergunta. Busca não é
leitura: um resultado de busca é uma lista de candidatos, não autorização para
carregar todos os arquivos encontrados.
