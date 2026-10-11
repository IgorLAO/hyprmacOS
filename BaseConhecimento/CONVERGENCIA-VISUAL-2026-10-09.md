# Convergência visual — checkpoint pausado em 2026-10-09

**PAUSADO a pedido do usuário para troca de agente. Trabalho parcial.**
Este registro resume decisões e evidências; não certifica fidelidade Tahoe.
Não continuar automaticamente antes de nova instrução do usuário.

## Objetivo adicional solicitado após a pausa: apps internos

Incluir na próxima execução o trabalho nos apps internos da
[lista de desejos](LISTA-DE-DESEJOS.md), além dos componentes do shell:

- Preview de PDF, com miniaturas, navegação e ferramentas.
- Journal / Diário.
- Câmera / Photo Booth.
- Notas, com pastas, lista e editor.
- Visualizador de imagens / Markup.
- Biblioteca de Fotos.
- Ajustes do Sistema e fidelidade Finder/nautilus, também presentes na lista.

Consultar as referências de cada entrada em `referencias/desejos/` e verificar
o estado real da implementação antes de priorizar. O usuário acrescentou esses
apps como objetivo de continuidade; não foram implementados nem avaliados nesta
execução. A tarefa permanece pausada. Usar as entradas existentes da lista para
acompanhar o trabalho, sem duplicá-las ou marcá-las como concluídas.

## Escopo e estado inicial

- A missão visual substituiu a limpeza anterior. Nenhum arquivo foi removido
  na limpeza; seu inventário está em `/tmp/hyprmac-cleanup-before.json`.
- Workspace já continha muitas alterações locais, inclusive shell, CSS,
  documentação, SQLite e testes. Foram preservadas; **não restaurar pelo Git**.
- Lidos os checkpoints de 07/10 e 08/10, consultados SQLite híbrido e HIG local.
- Hyprland e shell acessíveis; `/mnt/macos/root/System` indisponível nesta sessão.
- Referência visual inspecionada: `referencias/telas/cc-sobre-janela-clara.png`.
  Não há vídeo Tahoe equivalente para os gestos trabalhados. Comparação
  Tahoe **ESTIMADA**, sem SSIM ou parâmetros nativos alegados.
- Auditor inicial: 94%, 11 pendências; isso não mede fidelidade perceptual.

## Decisões e alterações desta execução

| Componente | Diferença inicial | Alteração | Resultado observado | Estado |
|---|---|---|---|---|
| Dock, reordenação | Vizinhos saltavam uma vaga; cada troca chamava `refresh()` e consultava compositor/ícones | Posição/velocidade por identidade com a mola existente; item acompanha ponteiro; reordenação local; item arrastado desenhado por último | Ensaio GTK: salto máximo dos vizinhos Mail/Photos 45 → aproximadamente 7,7 px por amostra; mesma ordem salva; 4 → 0 chamadas de refresh durante o gesto | MELHOROU, validação final pendente |
| Popover Wi-Fi, também usado dentro da Central | “Other Networks” reconstruía switch, cabeçalho, redes e rodapé; altura saltava | Grupo com Gtk.Revealer interruptível, linhas persistentes e resize da superfície; chevron atualizado sem reconstrução | Ensaio GTK: 4 conjuntos de widgets → 1; altura passa por valores intermediários entre 151 e 235 px | MELHOROU, validação final pendente |

Fundamentação: HIG local `hig/drag-and-drop.md` pede feedback contínuo;
`hig/motion.md` pede movimentos breves e canceláveis. Foi reutilizada a mola
do Dock. Os 240 ms da expansão são uma estimativa local já usada pela Central,
não uma duração medida no macOS.

Segunda rodada no popover: `SLIDE_DOWN` revelava a última rede primeiro.
Após inspeção do render, mudou para `SLIDE_UP`, expondo a primeira rede a partir
do cabeçalho. Adicionado cancelamento do tick quando dados estruturais remontam
a lista. RSSI continua atualizando as linhas existentes.

## Arquivos e recuperação segura

Alterações desta execução:

- `shell/hyprmac-shell`: Dock e grupo expansível descritos acima.
- `tests/test_popover_updates.py`: fixture sem display ganhou `reveal_group`.
- `MacTahoe/comparador/resultados/convergencia-20261009/probe.py`: ensaio
  reproduzível GTK com dados/eventos controlados, sem alterar serviços ou preferências.
- Este checkpoint e registros de progresso no SQLite.

Snapshot **anterior a esta execução**, que conserva o trabalho de outros agentes:
`/tmp/hyprmac-convergencia-20261009/hyprmac-shell.before`.
Também há cópias de `style.css` e `style-light.css`; esses CSS não foram alterados.
Use diff contra esse snapshot para separar o trabalho desta sessão do restante.

## Evidências e validação executada

Diretório temporário: `/tmp/hyprmac-convergencia-20261009/`.

- `dock-before/`, `dock-after/`, `wifi-before/`, `wifi-after/`: frames PNG e
  `metrics.json` com timestamps, eventos, geometria, identidade dos widgets e ações.
- `dock-light/`, `wifi-light/`: renders do tema claro, ainda sem revisão final.
- `dock-contact.png`, `wifi-contact.png`: montagem de triagem. **Não usar para
  métricas**: o thumbnail redimensiona frames de alturas diferentes. A montagem
  Wi-Fi ainda mostra a primeira rodada; `wifi-partial.png` mostra a direção corrigida.
- `cc-before.png`: captura `grim` do shell real; nenhuma comparação óptica
  equivalente com Tahoe foi feita.
- Renders do probe são GTK OffscreenWindow: **não contêm o blur do compositor**.
  Cadência de amostragem não equivale a FPS do desktop.
- Compilação de `hyprmac-shell` passou após os dois blocos principais.
- 7 testes de `test_visual_convergence.py` passaram após o bloco Dock.
- 5 testes de `test_popover_updates.py` passaram após o bloco Wi-Fi.
- Shell recarregado após cada bloco; último reload inclui a segunda rodada.
  Dock real continua disponível no desktop. A prévia temporária da Central fechou.
- `hyprctl configerrors` estava vazio após o bloco Dock.

## Retomada: validações pendentes e limites

1. **Refazer Reduzir Movimento.** Os primeiros probes `*-reduced/` usavam
   equivocadamente `A11Y` em vez de `CFG` para o Cairo do Dock. O probe foi
   corrigido para `CFG['reduce_motion'] = True`, mas **não foi reexecutado**.
   Não usar os resultados antigos como validação de acessibilidade.
2. Conferir redução de movimento durante uma expansão em andamento, fechamento,
   reabertura e atualização estrutural da lista; verificar callbacks e foco.
3. Acrescentar teste específico do arrasto do Dock (inversão, encaixe, persistência,
   clique normal e ausência de refresh durante movimento). O gesto fora da camada
   e magnificação durante arrasto ainda precisam de validação real.
4. Capturar em Wayland os gestos alterados, com condições controladas, e inspecionar
   a geometria/input em movimento. Não tratar o render isolado como validação do vidro.
5. Produzir métricas/artefatos compactos a partir dos frames. Para igualdade final,
   comparar RGB/RGBA por NumPy: a checagem preliminar `ImageChops.getbbox()` em
   RGBA pode ignorar diferenças RGB quando alpha é igual; resultado não é conclusivo.
6. Executar compilação dos três scripts exigidos, validação geral básica, auditor
   resumo/pendentes e diff apenas das mudanças desta execução. Não houve validação
   geral final nem nova indexação após o pedido de pausa.
7. Consolidar evidências úteis no SQLite, atualizar o índice semântico apenas dos
   novos registros e indexar documentação quando o trabalho for retomado.
8. Deixar componentes alterados abertos para conferência. Não foi criada prévia
   persistente do Wi-Fi; o hardware local aparenta ter apenas Ethernet.

Demais prioridades não foram alteradas nesta sessão. Vidro da base do Dock,
curvas nativas e óptica fina continuam dependentes das referências já pendentes
em `TODO.md` / `MacTahoe/TODO.md`. Não duplicar essas entradas nem repetir extrações.

---

# Retomada — 2026-10-09, madrugada (00:00–01:20)

Retomado a pedido do usuário (nova missão de convergência). O usuário foi dormir
durante a execução; havia `shutdown` agendado para 01:24, por isso este checkpoint
foi gravado antes do fim. `/mnt/macos/root` continua indisponível.

## Validações pendentes da pausa — feitas

- **Reduzir Movimento** (item 1): probe reexecutado com `CFG['reduce_motion']`.
  Dock: Mail só assume 173/218 px (salto único de 45 px, sem quadros intermediários).
  Wi‑Fi: altura só 151/235 px. Comportamento correto.
- **Teste do arrasto do Dock** (item 3): `test_dock_drag_reorders_live_without_refresh_and_click_still_activates`
  cobre limiar de 8 px, duas inversões, encaixe, salvar só ao soltar, nenhum `refresh`,
  Finder fixo e clique normal.
- Ainda pendente: gesto real Wayland do arrasto (não há ydotool/wtype; não reordenar
  o Dock do usuário sem ele).

## Tabela desta retomada

| Componente | Diferença inicial | Alteração | Resultado | Estado |
|---|---|---|---|---|
| Menus (barra, Dock, widgets) | ✓ como prefixo de texto ("✓ "/"    "); rótulo marcado desalinhado | Coluna da marca do kit (`menu_check_column`): em menu com item de estado, todos os itens recebem a coluna; 􀆅 SF Pro Bold 13 | Medido ao vivo: texto 15 → 29 px da borda (kit 28); tinta da marca 10–23 px (kit 10–22); todos os rótulos alinhados | MELHOROU |
| Menus — submenu | Triângulo `pan-end-symbolic` do tema | Chevron 􀆊 Bold 13 do kit, cor dos atalhos, cinza no estado aberto | Captura: chevrons alinhados à direita com ⌘M | MELHOROU |
| Menu do widget / fundo | Sem cabeçalho; Change Wallpaper… no widget; ordem diferente | Cabeçalho "Size" (kit Header Bold 13 #8A8A8A/#737373), tamanhos com ✓, Remove Widget, Edit Widgets…; fundo: Change Wallpaper… + Edit Widgets… | Igual à estrutura de ui_0073 / ui_0183 | MELHOROU |
| Menu do Dock | Sem "Show All Windows" | Item novo → foca janela do app + `hyprmac-overview app` | Exposé do app conferido em captura | MELHOROU (sem referência visual do menu do Dock; ordem do macOS) |

Referências reais usadas: `video/frames-ui/ui_0073.png` (menu do widget, claro),
`ui_0183.png` (menu do fundo com ✓ Use Stacks), `escuro-menu-contexto-sobre-rosa.png`,
`referencias/kit/contornos/Menus.txt` (Menu with Selection, Header, chevron).
Escala do vídeo: semáforo com passo 50,25 px = 23 pt → 2,185 px/pt.

Evidências: `MacTahoe/comparador/resultados/convergencia-20261009-noite/`
(menu-window-marca, menu-window-chevron, menu-view-coluna, menu-widget-tahoe-x-hyprmac,
menu-desktop-depois, menu-app-antes). SQLite: descobertas `convergencia-20261009-noite:*`.

Conferidos e **sem diferença relevante** (não repetir): barra de menus (safari-escuro),
menu do app (padding/raio/altura), barra lateral dos Ajustes contra ui_0177
(passo 32 pt, ícone 20, seleção 32 alta e raio ~8 — já iguais), Dock em repouso
(tamanho 32 é escolha do usuário em config.json).

Validação: 42 testes, `py_compile` dos 4 scripts Python, `bash -n install.sh`,
`hyprctl configerrors` vazio, auditor 94%. Shell recarregado.

## Pendências / próxima execução

1. `scripts/captura` (opções do ⇧⌘5) ainda usa prefixo "✓ " e cabeçalhos como itens
   desabilitados; tem CSS próprio — migrar para coluna + Header do kit.
2. ~~Tema claro dos menus novos~~ — conferido num processo-probe com style-light.css,
   sem trocar o tema do desktop: `menu-escuro-claro-probe.png` (sem blur do compositor).
3. Menu do Dock: Options ▸ "Open at Login"/"Show in Finder"/"Assign To" — sem referência.
4. Quadros não indexados úteis: ui_0061 (menu de extensão do Safari), ui_0045/46
   (menus do Safari), ui_0066–0076 (widgets/calendário), ui_0173–0175 (tiling/janela).
5. Próximo componente prioritário: **Popovers da barra** (Wi‑Fi/Bluetooth/Som), depois
   Notificações (ui_0009). Continuam pendentes as do checkpoint anterior (vídeo Tahoe,
   lente da base do Dock).
