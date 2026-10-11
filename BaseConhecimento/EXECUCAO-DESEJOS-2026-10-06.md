# Execução da lista de desejos — 2026-10-06

Escopo solicitado: concluir `LISTA-DE-DESEJOS.md` com máxima fidelidade e sem
interromper a sessão do usuário. **O escopo total ainda não está concluído.**
Nenhum checkbox novo foi marcado como concluído: implementação e testes técnicos
não substituem a comparação visual no compositor.

## Alterações implementadas

| Item | Implementação | Verificação e pendência |
|---|---|---|
| Busca dos Ajustes | Índice estático de 193 opções, painéis e subpáginas; busca sem diferenciar acentos; resultado abre a página correta e rola até a opção. O índice não constrói painéis nem executa comandos do sistema. | Índice/subpáginas testados. Layout, foco, rolagem e retorno por Escape precisam de teste GTK na sessão. |
| Baterias | Quatro posições de anéis; UPower e BlueZ Battery1; percentuais reais, bateria vazia, carregamento, dispositivos desconectados e deduplicação. Galeria oferece o widget médio. | Fontes testadas com D-Bus simulado. Render Cairo inspecionado. Material, temas e dados dos dispositivos reais ainda não conferidos. |
| Editor de widgets | Arrastar da galeria adiciona; arrastar um widget em edição reordena a lista persistida; índices independem da ordem dos filhos GTK. | Dados de drag/drop e modo somente leitura testados. Gesto GTK e gravação no config real não exercitados. Layout continua a grade existente de duas colunas. |
| Rótulo do Dock | Seta curva integrada ao contorno da cápsula, sem linha atravessando a base. | Referência e render Cairo inspecionados; material e posição no Dock real pendentes. |
| Bloqueio por inatividade | Publicação de prontidão somente após `ext-session-lock` confirmar o bloqueio; DPMS aguarda confirmação; retorno do usuário cancela desligamento pendente; marcador obsoleto não conta como bloqueio. | Ciclo e script exercitados em HOME/runtime temporários com compositor simulado. PAM real e sessão bloqueada não foram testados. |

## Arquivos e evidências reais

- Baterias e fonte de dados: [real:shell/hyprmac-shell:930].
- Recepção de drag/drop: [real:shell/hyprmac-shell:1249].
- Contorno do rótulo do Dock: [real:shell/hyprmac-shell:8473].
- Índice de opções dos Ajustes: [real:shell/hyprmac-ajustes:783].
- Navegação até a opção: [real:shell/hyprmac-ajustes:1305].
- Confirmação do protocolo de bloqueio: [real:shell/hyprmac-lock:1348].
- Espera e cancelamento por retorno do usuário: [real:scripts/ocioso:26].
- Cores de progresso reutilizam a paleta existente de `shell/style.css`.
- Testes: `tests/test_wishlist.py`, `tests/test_idle_lock.py`,
  `tests/test_lock_ready.py`.

## Referências e comparação

Referências inspecionadas em `referencias/desejos/`:
`widget-bateria-1.png`, `widget-bateria-2.png`, `widgets-editar.png`,
`ajustes-busca-1.png`, `ajustes-busca-2.png`, `dock-rotulo-nome-app.png`.
As referências de Preview, Journal, câmera, Notas, Fotos e integrações da barra
foram inspecionadas para delimitar o restante do escopo; esses aplicativos e
integrações **não foram implementados nesta execução**.

Medições da referência de bateria: cartão de aproximadamente 234×111 pixels,
anéis de 43 pixels, centros separados por 55 pixels. A implementação mantém
essas proporções dentro do footprint médio já estabelecido na grade.
O rótulo de referência tem corpo aproximadamente 126×35 pixels e seta curva de
12×7 pixels; a imagem é um recorte sem escala declarada, portanto não comprova
correspondência 1:1 em pontos com o runtime.

Artefatos temporários desta execução:

- `/tmp/hyprmac-audit/samsung-inicial.png`: captura real de `HDMI-A-2`, Samsung
  S22F350, 1920×1080 a escala 1, obtida antes da mudança de permissões.
  Mostra a sessão em uso; não serve como captura de aceite dos componentes novos.
- `/tmp/hyprmac-audit/battery-render.png`: render diagnóstico Cairo com dados
  fictícios de teste, **não** uma captura do widget em execução.
- `/tmp/hyprmac-audit/dock-render.png`: render diagnóstico Cairo,
  **não** uma captura do compositor.

A renderização revelou conexões diagonais involuntárias entre os anéis e cor
incorreta na legenda do estojo; ambos foram corrigidos e o render foi reinspecionado.

## Validação

```bash
python3 -m unittest discover -s tests -v
python3 -m py_compile shell/hyprmac-shell shell/hyprmac-ajustes shell/hyprmac-lock
bash -n scripts/ocioso
./BaseConhecimento/ferramentas/comparar.py --resumo
./BaseConhecimento/ferramentas/comparar.py --pendentes
./BaseConhecimento/ferramentas/indexar.py
```

16 testes cobrem fontes de bateria, índice/subpáginas, reordenação, confirmação
atômica de bloqueio, segunda instância, falhas, marcadores obsoletos e cancelamento
por atividade. Nenhum teste autentica o usuário ou bloqueia a sessão real.
Compliance global continua em **94%**; não é uma certificação dos itens novos.
A checagem de whitespace dos arquivos de implementação alterados está limpa;
a checagem global encontra espaços finais em documentação já modificada antes
desta execução, preservada para não sobrescrever trabalho existente.

## Pendências e limitação de ambiente

Na continuação, o sandbox passou a impedir acesso aos sockets de Wayland,
Hyprland e X11. `Gtk.init_check()` falhou, `hyprctl monitors -j` não conseguiu
acessar o socket e Broadway não pôde abrir seu socket/porta. Assim, não foi
possível recapturar os estados novos no Samsung nem validar GTK interativo.
Não houve reinício do shell, troca de workspace, mudança de tema global,
bloqueio ou desligamento dos monitores do usuário.

Ainda faltam a calibração da Central escura sobre fundo claro; ícones e
integrações da barra (atividade, Studio/câmera e fila de mídia); ícones dos
menus; polimento visual/PAM real do bloqueio; Preview PDF e imagem/marcação;
Journal; câmera; Notas; Fotos; fidelidade Finder/nautilus; e as referências
pendentes especificadas em `REFERENCIAS-PENDENTES.md`.
O acesso gráfico impede o aceite visual das alterações acima, mas não explica
como concluídos os aplicativos e integrações que permanecem por implementar.

## Continuação com foco visual

A revisão lado a lado corrigiu a cápsula estreita do Dock: padding e altura
agora vêm do seletor `.dock-tooltip` em `shell/style.css`, e o texto é centralizado
pela área de tinta real de SF Pro. O contorno conserva uma única seta curva.

O widget de bateria agora tem material e tipografia próprios em `.battery-widget`.
Isso evita herdar o preenchimento branco dos cartões de atalhos no modo claro.
As legendas usam o tamanho CSS medido na comparação normalizada; os símbolos de
laptop, fones e estojo foram ajustados e a variante Clear mantém anéis brancos.
O indicador de energia do laptop foi posicionado no canto superior esquerdo do
anel, como em `widget-bateria-1.png`.

O diagnóstico reproduzível está em `tests/render_wishlist.py`, que lê o CSS real
e chama os métodos Cairo reais. Ele não substitui o motor de estilo GTK nem
simula blur/refração do compositor. Execute:

```bash
python3 tests/render_wishlist.py /tmp/hyprmac-visual
```

Comparações inspecionadas:
`/tmp/hyprmac-visual/dock-comparison.png`,
`/tmp/hyprmac-visual/battery-comparison.png` e
`/tmp/hyprmac-visual/battery-clear-comparison.png`.
A diferença de material/contraste com o wallpaper permanece sem aceite visual;
ela não pode ser resolvida comparando um fundo diagnóstico plano à referência.
Os dois estilos CSS passaram pelo parser GTK, que emitiu um aviso de ausência
de GDK screen por causa do ambiente sem conexão gráfica.
