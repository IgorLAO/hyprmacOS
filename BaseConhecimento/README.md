# Base de conhecimento do HyprMac

O objetivo vigente é **macOS Tahoe 26**. Esta árvore contém material de Tahoe 26, fontes rotuladas macOS 27, HIG sem versão confirmada, dados de visionOS, relatórios e arquivos históricos. A classificação em `base.db.documentos` informa estado, versão declarada, hash e proveniência. `experimental` significa hipótese ou fonte ainda não confirmada contra Tahoe 26; `verified` exige evidência concreta. A busca padrão omite `archived`, `superseded` e `invalid`.

```bash
B=./BaseConhecimento/ferramentas
$B/consultar.py --codigo "dock"                  # localizar implementação
$B/consultar.py "liquid glass" -n 5                # primeiras fontes relevantes
$B/consultar.py --documento componentes/dock.md    # verificar estado/proveniência
$B/consultar.py --registro "hyprglass"             # decisões e análises curadas
$B/consultar.py "dock" --historico                 # recuperar material antigo
$B/consultar.py --imagem "control center"          # catálogo e atlas visual
$B/comparar.py --resumo                             # matriz interna de parâmetros
$B/indexar.py                                      # atualizar FTS por SHA-256
$B/auditar_base.py                                 # integridade, hashes e links
```

`base.db` é o ponto de entrada versionado. `trechos` e `registros_fts` são índices; os Markdown longos e JSON de tokens preservam as fontes originais. `parametros.json` define as medições e `comparar.py` preenche a tabela `parametros`. O banco local `MacTahoe/base.db` guarda investigações especializadas do sistema Tahoe e oferece `MacTahoe/tools/query.py --mode fts`; ele não é versionado e pode não existir em outro clone.

Procure primeiro por componente e estado; abra o trecho ou imagem original somente quando a conclusão exigir. Para evidência sobre comportamento Apple, preserve caminho, versão, origem, data e ressalvas. Registre decisões curtas em `registros`, marque pesquisas antigas como `superseded` ou `archived` e mantenha uma relação com a evidência anterior. Antes de criar Markdown, confira `consultar.py` e os documentos de componentes/padrões existentes.

O guia extenso anterior está em [historico/legado-operacional-20261010/BaseConhecimento-README.md](historico/legado-operacional-20261010/BaseConhecimento-README.md). A arquitetura e o estado atuais estão em [ARCHITECTURE.md](../ARCHITECTURE.md) e [STATUS.md](../STATUS.md).
