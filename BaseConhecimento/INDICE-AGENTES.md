# Índice operacional para agentes — hyprmac

> Nota de versão (2026-10-10): o objetivo vigente é **macOS Tahoe 26**.
> As menções a “macOS 27” abaixo descrevem rótulos herdados das fontes e
> permanecem secundárias até validação específica. Estado e proveniência
> canônicos: `consultar.py --documento CAMINHO` e `STATUS.md` na raiz.

Este arquivo é o ponto de entrada rápido para qualquer agente que vá analisar,
implementar, revisar ou validar uma task no hyprmac. Ele também é indexado pelo
`BaseConhecimento/ferramentas/indexar.py`, portanto pode ser consultado pelo
`consultar.py`.

Para controlar custo e latência de contexto, use
[`GERENCIAMENTO-CONTEXTO.md`](GERENCIAMENTO-CONTEXTO.md). O índice de código em
[`codigo.json`](codigo.json) e o catálogo visual devem ser consultados antes de
carregar arquivos ou imagens completas.

Para escolher a próxima melhoria, consulte a fila em [TODO.md](../TODO.md) e
somente a seção do componente no [catálogo de comportamentos](LISTA-DE-DESEJOS.md).
Use os IDs para atualizar implementação, validação e evidência separadamente.
As metas do usuário não são evidência Apple; shell e interações têm precedência
sobre novos aplicativos próprios.

## Regra principal: fidelidade visual MÁXIMA

O objetivo do hyprmac é reproduzir o macOS Tahoe 26 com **MÁXIMA
FIDELIDADE visual e comportamental**. “Parecido”, “inspirado”, “bonito” ou
“uma aproximação plausível” não atende ao projeto.

Toda mudança de interface deve ser comparada com as referências disponíveis e
preservar, na medida permitida pelo Linux, a composição, escala, proporções,
alinhamento, espaçamento, tipografia, cor, opacidade, vibrancy, blur, sombras,
bordas, curvatura contínua, hierarquia, estados, transições, origem do
movimento e comportamento de teclado/mouse. Um detalhe pequeno também é parte
da fidelidade quando aparece na referência.

Antes de inventar um valor ou comportamento:

1. procure a referência visual em `BaseConhecimento/referencias/telas/`;
2. consulte a especificação em `BaseConhecimento/`;
3. confira a implementação real no código;
4. cite a evidência no comentário ou na documentação no formato
   `[real:arquivo:linha]` quando a decisão depender de uma medida.

Se a referência e o código divergirem, registre a divergência e corrija em
direção à referência. Não substitua uma medida verificada por preferência
pessoal ou por uma estética genérica de glassmorphism.

## Sequência de chegada

Leia somente o necessário para a task, nesta ordem:

```text
AGENTS.md
  → BaseConhecimento/INDICE-AGENTES.md
  → status/compliance atual
  → documento do componente ou parâmetro afetado
  → código real e referência visual
```

`CLAUDE.md`, `BaseConhecimento/README.md` e `ONBOARDING.md` são referências
complementares. Leia-os apenas quando a task exigir contexto geral da base ou
do projeto; não são leitura obrigatória para cada chegada.

Em seguida, execute:

```bash
./BaseConhecimento/ferramentas/comparar.py --resumo
./BaseConhecimento/ferramentas/comparar.py --pendentes
```

Não use a nota global para substituir a análise da tela afetada. Ela é um
sinal de regressão e prioridade; a decisão visual deve continuar baseada na
referência e no código.

## Mapa do sistema

| Área | Implementação principal | Fonte visual/documental |
|---|---|---|
| Shell e overlays | `shell/hyprmac-shell` | `BaseConhecimento/componentes/` |
| Estilo do shell | `shell/style.css`, `shell/style-light.css` | `BaseConhecimento/padroes/` |
| Ajustes do Sistema | `shell/hyprmac-ajustes`, `shell/ajustes.css` | `BaseConhecimento/componentes/sistema-e-recursos.md` |
| Tela de bloqueio | `shell/hyprmac-lock`, `shell/lock.css` | parâmetro `SIS-03`, referências de lock screen |
| Mission Control / App Exposé | `shell/hyprmac-overview`, `scripts/janela` | `BaseConhecimento/componentes/sistema-e-recursos.md` |
| Waybar/menu global | `waybar/config.jsonc`, `waybar/style.css`, `waybar/theme.css` | `BaseConhecimento/componentes/barra-de-menus.md` |
| Janelas e compositor | `hypr/hyprmac.lua` | `BaseConhecimento/padroes/forma-e-espacamento.md` |
| Liquid Glass | `hypr/vidro-presets.lua`, `shell/vidro.py`, `scripts/vidro`, `shell/vidro-camadas*.css` | `BaseConhecimento/padroes/liquid-glass*.md` |
| Tema claro/escuro | `scripts/theme`, `gtk/`, `kde/`, `kitty/`, `ghostty/` | `BaseConhecimento/padroes/cores-e-tipografia.md` |
| Ações de janela | `scripts/janela` | `BaseConhecimento/padroes/atalhos-de-teclado.md` |
| Captura e gravação | `scripts/captura`, `scripts/captura-miniatura`, `scripts/gravacao` | parâmetro `SIS-06` |
| Cursores e ícones | `cursores/`, `hyprmac/Kit/`, `BaseConhecimento/referencias/kit/` | referências indexadas e `hyprmac/Kit/` |
| Compliance | `BaseConhecimento/comparacao/parametros.json`, `BaseConhecimento/ferramentas/comparar.py` | `BaseConhecimento/comparacao/MATRIZ.md` |

## Fonte de verdade por tipo de decisão

| Decisão | Consultar primeiro | Regra |
|---|---|---|
| Cor, dimensão, padding, raio, transição ou sombra do shell | `shell/style.css` e `shell/style-light.css` | O CSS real vence notas antigas. |
| Borda, gap, rounding, sombra, blur e animação de janela | `hypr/hyprmac.lua` | Preserve `gaps_in = 0`, `gaps_out = 0` e `rounding_power = 3.2` salvo evidência contrária. |
| Estrutura e comportamento de um componente | implementação correspondente em `shell/` ou `waybar/` | Descreva o comportamento observado antes de refatorar. |
| Alvo mensurável | `BaseConhecimento/comparacao/parametros.json` | Rode `comparar.py`; não atualize a nota manualmente. |
| Token Apple | `consultar.py --cor`, `--tipografia`, `--estilo` | Use o token mais específico disponível. |
| Referência de tela | `consultar.py --imagem`, `referencias/telas/CATALOGO-AGENTES.md` e os atlas | Faça triagem pela categoria/estado; abra o original só para medir ou comparar. |
| Princípio de interação | `BaseConhecimento/padroes/` e `hig/` | Traduza o princípio para o componente e cite a fonte. |

## Consultas rápidas

```bash
B=./BaseConhecimento/ferramentas

# Encontrar uma regra ou receita
$B/consultar.py "menu hover radius" --completo
$B/consultar.py "liquid glass no glass on glass" -t padrao

# Encontrar valores estruturados
$B/consultar.py --cor blue
$B/consultar.py --tipografia body
$B/consultar.py --estilo "glass dark"

# Encontrar telas e frames
$B/consultar.py --imagem "control center"
$B/consultar.py --imagem "menu bar safari dark"

# Catálogo/atlas: regenerar somente quando imagens ou descrições mudarem
python3 $B/catalogar_imagens.py

# Consultar parâmetros e pendências
$B/consultar.py --sql "SELECT id, area, parametro, status, prioridade, onde FROM parametros ORDER BY prioridade, id"
$B/consultar.py --sql "SELECT caminho, tipo, titulo FROM trechos WHERE tipo IN ('componente','padrao') LIMIT 50"

# Procurar a implementação real
rg -n "termo|classe|seletor|namespace" shell hypr waybar scripts

# Encontrar candidatos sem ler arquivos completos
$B/consultar.py --codigo "dock"
$B/consultar.py --codigo "control center"

# Regenerar o índice leve de código após alterar arquivos estruturais
$B/indexar_codigo.py
```

Depois de alterar documentação, tokens ou referências textuais:

```bash
./BaseConhecimento/ferramentas/indexar.py
```

O indexador recria `BaseConhecimento/base.db` e chama a atualização da matriz.
Não edite `base.db` diretamente.

Para imagens, o fluxo multimodal é: catálogo semântico → atlas → original →
código → comparação. O catálogo reduz o custo de descoberta; a imagem original
continua sendo obrigatória para validar texto, posições, materiais, medidas,
pixels e transições entre estados.

## Roteamento por tipo de task

### Menu bar, menus e extras

Leia `BaseConhecimento/componentes/barra-de-menus.md`,
`BaseConhecimento/componentes/menus.md` e os parâmetros `BAR-*`. Inspecione
`waybar/config.jsonc`, `waybar/style.css`, `waybar/theme.css`,
`shell/style.css` e `shell/hyprmac-shell`. Valide ordem, foco, hover, teclado,
popovers e estados claro/escuro.

### Central de Controle, notificações e Dock

Leia o componente correspondente e `padroes/liquid-glass.md`. Inspecione
`shell/hyprmac-shell`, CSS, regras de camada em `hypr/hyprmac.lua` e o estado
produzido pelos scripts. Valide origem da abertura, agrupamento, material,
concentricidade, foco e fechamento.

### Janelas, vidro e movimento

Leia `padroes/liquid-glass-hyprland.md`, `padroes/forma-e-espacamento.md`,
`padroes/movimento-escrita-e-principios.md` e `hypr/hyprmac.lua`. Verifique
se há vidro sobre vidro, se o tingimento tem alpha, se o blur está no layer
correto e se a superfície nasce da ação que a abriu.

### Tela de bloqueio, Spotlight, captura e widgets

Leia `componentes/sistema-e-recursos.md` e o parâmetro `SIS-*` correspondente.
Inspecione o script executável, o CSS dedicado e as referências de tela. Não
assuma que um componente listado em documentação ainda existe com o mesmo
nome: confirme a árvore atual.

### Tema, acessibilidade e integração

Inspecione `scripts/theme`, os arquivos `gtk/`, `kde/`, `kitty/`, `ghostty/`,
`shell/a11y-*.css` e `waybar/a11y.css`. Valide que a alteração atravessa as
camadas necessárias e mantém a aparência de alta fidelidade em claro, escuro,
transparência reduzida, contraste aumentado e movimento reduzido.

## Checklist de revisão visual

Revise nesta ordem, corrigindo o maior desvio primeiro:

1. composição e posição da superfície na tela;
2. proporções, largura, altura, margens e alinhamento;
3. hierarquia e densidade do conteúdo;
4. tipografia, peso, tamanho e baseline;
5. cor, contraste, opacidade e adaptação ao fundo;
6. material, blur, vibrancy, tint e separação de camadas;
7. raio, squircle, borda, sombra e concentricidade;
8. estados de hover, foco, ativo, desabilitado e erro;
9. abertura, fechamento, spring, duração e origem do movimento;
10. microdetalhes, ícones, cursores e feedback.

Não aceite “funciona” como evidência de fidelidade. Uma implementação pode
passar o teste técnico e ainda estar incorreta visualmente.

## Regras que evitam regressões

- Não adivinhe valores CSS: pesquise o código, o token ou a referência.
- Não use preenchimento opaco onde a referência exige tint translúcido.
- Não aplique blur em uma superfície de vidro que esteja sobre outra superfície
  de vidro; preserve a separação entre control layer e conteúdo.
- Não altere gaps, raios ou efeitos globais para resolver um único componente
  sem verificar a matriz e as referências afetadas.
- Não crie uma segunda implementação antes de procurar a existente com `rg`.
- Não faça refatoração não relacionada durante uma correção visual.
- Não substitua arquivos modificados por outro agente; examine `git status` e
  preserve mudanças locais.
- Não altere `install.sh` de modo a perder backups ou quebrar idempotência.

## Validação mínima antes do handoff

```bash
python3 -m py_compile shell/hyprmac-shell shell/hyprmac-ajustes shell/hyprmac-lock
./BaseConhecimento/ferramentas/comparar.py --resumo
./BaseConhecimento/ferramentas/comparar.py --pendentes
git diff --check
git status --short
```

Se a task alterou documentação, tokens ou referências, rode também
`./BaseConhecimento/ferramentas/indexar.py` e repita a consulta que motivou a
alteração. Se a task alterou UI, faça uma verificação visual no runtime quando
o ambiente estiver disponível e registre a tela/estado verificado.

Para verificar o runtime, use `hyprctl monitors -j` ou `hyprctl instances`. Se
`hyprctl` falhar, não conclua automaticamente que Hyprland não está rodando:
confira `HYPRLAND_INSTANCE_SIGNATURE`, `WAYLAND_DISPLAY`, `XDG_RUNTIME_DIR` e
os sockets em `$XDG_RUNTIME_DIR/hypr/`. Um socket visível com timeout indica
que a sessão existe, mas não está acessível ao processo do agente; registre
essa limitação separadamente da validação de código.

## Formato de handoff

Informe sempre:

```text
Task/escopo:
Arquivos alterados:
Referências consultadas:
Decisões visuais e evidências [real:arquivo:linha]:
Validação executada:
Nota ou pendência de compliance:
Risco visual restante:
```

Um handoff sem referência visual, sem validação ou sem indicar um desvio
conhecido não está completo.
