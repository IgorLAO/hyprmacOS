# Memória técnica do macOS Tahoe

> Curadoria (2026-10-10): `classificacao_registros` guarda estado e versão por
> descoberta, investigação ou mapeamento. A migração 003 inicia os registros
> antigos como `experimental`/`unknown`; confiança `DIRETO` descreve a origem,
> sem certificar automaticamente comportamento Apple. A busca padrão omite
> `superseded`, `archived` e `invalid`; `query.py --historico` recupera o
> histórico. Este banco é local e não versionado.
> Snapshots anteriores às migrações 002 e 003 foram comprimidos como `.db.gz`
> após verificação SHA-256; descomprima uma cópia antes de abri-la com SQLite.

`base.db` é um índice local e curado da instalação somente leitura em
`/mnt/macos/root`. A fonte original sempre prevalece sobre o banco. O índice
guarda localização e metadados globais; conteúdo, símbolos e configurações só
são examinados quando uma pergunta concreta exigir.

O schema contém `componentes`, `bundles`, `arquivos`, `descobertas`, `relacoes`,
`mapeamento_hyprmac`, `investigacoes` e `analises`. `conhecimento_fts` fornece
busca FTS5 sobre descobertas curadas.

```bash
python3 BaseConhecimento/MacTahoe/tools/query.py "control center wifi"
python3 BaseConhecimento/MacTahoe/tools/scan.py
python3 BaseConhecimento/MacTahoe/tools/seed_initial.py
python3 BaseConhecimento/MacTahoe/tools/inspect_tahoe.py /mnt/macos/root/caminho/Info.plist --component "Control Center"
python3 BaseConhecimento/MacTahoe/tools/inspect_tahoe.py /mnt/macos/root/caminho/binario --component Dock --keywords 'magnif|tile|badge'
```

Antes de inspecionar um arquivo, consulte o banco. `inspect_tahoe.py` também recusa
repetir o mesmo nível de análise sem `--refresh`. O scanner é idempotente e lê
somente metadados de arquivos priorizados e `Info.plist` pequenos de pacotes;
ele não executa `strings`, não calcula hashes e não decodifica `Assets.car`.

## Busca híbrida local

**SQL para fatos. FTS para palavras. Vetores para significado. `/mnt/macos` para
as evidências originais.** A migração é aditiva: preserva todas as tabelas e IDs
anteriores e faz backup consistente via SQLite em `backups/` antes do schema.

```bash
# Uso normal — também funciona com o Python do sistema, usando a .venv local:
python BaseConhecimento/MacTahoe/tools/query.py "dock magnification spring"
python BaseConhecimento/MacTahoe/tools/query.py "expansão do control center" --component "Control Center"
python BaseConhecimento/MacTahoe/tools/query.py "spring" --type animation --confidence direct
python BaseConhecimento/MacTahoe/tools/query.py "NowPlayingContentView" --mode fts
python BaseConhecimento/MacTahoe/tools/query.py "ícones ampliados" --mode vector --component Dock
python BaseConhecimento/MacTahoe/tools/query.py "Assets.car" --catalog --component Dock
# Após registrar/editar conhecimento: somente embeddings novos ou alterados.
python BaseConhecimento/MacTahoe/tools/index_knowledge.py
```

Padrão: 5 resultados; `--limit 1..20`, `--json`, `--db` alternativo. A consulta
abre o banco **somente para leitura**. FTS/catalog funcionam sem modelo.
`--type animation` equivale a `animacao`; `--confidence direct` a `DIRETO`.
Os nomes originais dos tipos e graus de confiança também são aceitos. Filtros
são aplicados em SQL antes do ranking; não alteram os registros originais.
`DIRETO` pode ser uma observação do **Hyprmac**: leia origem e ressalvas, não
interprete automaticamente como confirmação do Tahoe.

### Regra para agentes

Antes de investigar `/mnt/macos/root`:

1. Faça busca semântica/híbrida com `query.py`.
2. Consulte FTS/SQL para nomes exatos, detalhes e relações.
3. Verifique as evidências e os níveis de análise já registrados.
4. Abra o arquivo Tahoe **somente se faltar informação**.
5. Registre a nova descoberta em `descobertas` (ou atualize a existente), com
   componente, tipo, conclusão, confiança e evidência; preserve as ressalvas.
6. Execute `index_knowledge.py`: gere embedding **somente dessa descoberta nova
   ou alterada**. Não rode `seed_initial.py` como rotina de atualização.

Cada resultado contém `source:source_id` para recuperar o registro original:

```sql
SELECT * FROM descobertas WHERE id = 93;
SELECT * FROM analises WHERE arquivo_id = (SELECT arquivo_id FROM descobertas WHERE id = 93);
SELECT * FROM relacoes WHERE origem_tipo = 'componente' AND origem_id = 1;
SELECT * FROM mapeamento_hyprmac WHERE componente_id = 1;
```

### Modelo e armazenamento

Modelo: `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`, ONNX
quantizado do repositório `qdrant/paraphrase-multilingual-MiniLM-L12-v2-onnx-Q`,
384 dimensões, mean pooling e normalização L2. Revisão exata fixada em
[`embedding-model.json`](embedding-model.json). Execução CPU local via
[FastEmbed](https://qdrant.github.io/fastembed/examples/Supported_Models/), sem
servidor ou chamadas de embedding externas. Modelo ~225 MiB, fora do Git e do
banco. Não há extensão vetorial SQLite instalada: usamos BLOB float32 little
endian e cosseno em lotes de até 64 vetores filtrados, com heap dos 60 melhores.
Não carregamos a matriz inteira. Limite de 512 tokens por unidade: textos
maiores são recusados para curadoria, não divididos nem truncados silenciosamente.

Instalação reproduzível (somente o download inicial precisa de rede):

```bash
python -m venv BaseConhecimento/MacTahoe/.venv
BaseConhecimento/MacTahoe/.venv/bin/pip install -r BaseConhecimento/MacTahoe/requirements-semantic.txt
python BaseConhecimento/MacTahoe/tools/index_knowledge.py --download-model
```

- `conhecimento_fts`: índice original preservado, inclusive seus triggers.
- `catalog_fts`: nomes, tipos, identificadores e descrições de arquivos/bundles/
  componentes; paths são metadata não vetorizada.
- `knowledge_documents` + `hybrid_fts`: descobertas, resultados de investigações
  e decisões de mapeamento, com origem/ID, componente, tipo, confiança e paths.
- `knowledge_vectors`: somente conhecimento interpretado, uma unidade semântica
  por vetor; sem PNGs, binários, plists crus ou dumps de strings.

Hashes/versionamento evitam recalcular conteúdo inalterado. Uma edição apenas
na confiança ou evidência reaproveita o vetor. Renomear componente ou editar/
remover a fonte invalida o documento derivado por trigger; execute o indexador
para repor as alterações. O indexador verifica os poucos registros de
conhecimento, não lê os 64 mil arquivos do inventário nem `/mnt/macos`.

Conclusões idênticas compartilham vetor; resumos de investigação que repetem a
conclusão conservam as ressalvas como metadata. Paráfrases com cosseno >0,97,
mesmo componente, números e marcadores de negação podem compartilhar vetor;
nenhuma evidência ou linha original é apagada. A regra é conservadora e não
substitui curadoria humana de contradições. Duplicatas não ocupam vários lugares
nos resultados; seus IDs relacionados continuam acessíveis.

Ranking híbrido: fusão recíproca de ranks (k=60, semântica 3:FTS 1), preferência
pelo componente explicitamente citado e menor peso para metadata crua. Candidatos
vetoriais precisam de cosseno ≥0,30 e ≥85% do melhor cosseno. O FTS também admite
prefixos para classes/selectors. Scores dos três modos têm escalas diferentes;
score não representa confiança factual nem comprova que a base responde a toda
a pergunta. Consulte a [validação e limitações](VALIDACAO-HIBRIDA.md).
