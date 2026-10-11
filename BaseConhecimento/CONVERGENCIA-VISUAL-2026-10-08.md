# Convergência visual — 2026-10-08

Retomada do checkpoint de 07/10 e do SQLite `MacTahoe/base.db`.
Comparação Tahoe **ESTIMADA**: `/mnt/macos/root` indisponível; referências
existentes não formam pares equivalentes de tema, escala, fundo e interação.
As medidas abaixo são do **Hyprmac real**, com eventos controlados em GTK/Wayland.

| Componente | Diferença inicial | Alteração | Resultado | Estado |
|---|---|---|---|---|
| Dock, pressão e menu | Ícones recolhiam enquanto o botão estava pressionado; menu preso à posição de repouso | Conservar geometria durante pressão/menu; ancorar no ícone desenhado | Ícone 57,6 → 36 px durante pressão agora permanece 57,6; deslocamento do centro 9,489 → 0 px | MELHOROU |
| Menus do Dock | Véu quase transparente, sem o material dos outros menus | Habilitar preset existente `hyprmac-texto` em `hyprmac-dock:popups`; retirar blur sobreposto | Captura confirma fundo filtrado e borda do vidro, com ações e submenus preservados | MELHOROU |
| Dock, auto-ocultar | Inversão reiniciava easing com velocidade de sinal oposto | Reutilizar mola existente, preservar velocidade ao inverter; evitar margens repetidas | Primeiro deslocamento após inversão +16 → −3 px: continua brevemente na direção anterior antes de retornar; reabertura completa e movimento reduzido passaram | MELHOROU |
| Ajustes, semáforo | Glifo de expansão forçava cápsula 14×24 e desalinhava os centros | Desenhar símbolos numa caixa limitada, manter callbacks e nomes acessíveis; hover revela cores também na janela inativa | Três círculos 14×14; busca/lista deixam de ser empurradas 4 px; oito estados claro/escuro capturados | MELHOROU |

Evidências e resultados:

- [Métricas](MacTahoe/comparador/resultados/convergencia-20261008/metricas.json),
  [pressão antes/depois](MacTahoe/comparador/resultados/convergencia-20261008/dock-press-antes-depois.png),
  [menu antes/depois](MacTahoe/comparador/resultados/convergencia-20261008/dock-menu-antes-depois.png),
  [semáforo antes/depois](MacTahoe/comparador/resultados/convergencia-20261008/settings-lights-antes-depois.png).
- [Auto-ocultar antes](MacTahoe/comparador/resultados/convergencia-20261008/dock-auto-ocultar-antes.gif)
  e [depois](MacTahoe/comparador/resultados/convergencia-20261008/dock-auto-ocultar-depois.gif):
  78 capturas por sequência, após estabilizar o fundo procedural; timestamps
  reais, sem interpolação. Cadência de captura 29,90 → 29,92 Hz, **não FPS do
  compositor**. Última revelação estabilizou em 260,54 → 228,57 ms neste ensaio;
  duração menor não é, isoladamente, prova de melhora. Overshoot observado: zero.
- `analyze.py` reutiliza `compare.edges` e `motion.trace`; gera overlays,
  diferenças, bordas e CSVs de trajetória. Nenhum SSIM/MAE Tahoe foi atribuído.
- Referências inspecionadas: `referencias/telas/tahoe-dark.jpeg` (Dock em repouso),
  `ajustes-general-escuro-aguas-vivas.png`, `ajustes-aparencia-claro-cor-pastas.png`.
  Medida dos círculos: [real:BaseConhecimento/referencias/kit/contornos/Titlebars_and_Toolbars.txt:1144].
  Símbolos limitados como [real:gtk/gtk4.css:112]. O kit é macOS 27;
  as capturas Tahoe corroboram a forma circular, sem certificar medidas equivalentes.
- [Daemon final](MacTahoe/comparador/resultados/convergencia-20261008/runtime-final.json):
  shell recarregado, Dock e Central capturados. Ajustes também capturados ao vivo
  em `settings-runtime/`; estados controlados em ambos os temas, sem alterar preferências.

Validação: **29 testes passaram**, `py_compile` dos três executáveis,
`hyprctl configerrors` vazio e diff de código sem erros de whitespace.
Auditor: **94%, 11 pendências**, sem regressão; não é pontuação visual.
Alterações anteriores do workspace preservadas. Progresso e caminhos registrados
em `MacTahoe/base.db`, sem imagens no banco e sem reindexar o volume Tahoe.

Próximo: **vidro da base do Dock durante magnificação**. O protocolo de formas
explícitas atual atende janelas (`windowShapes`), enquanto a camada do Dock reúne
base, ícones e rótulo. Aplicar lente à máscara inteira também afetaria ícones fora
da base. Esse trabalho precisa de separação de máscara e referência visual em
movimento; permanece no TODO. Não repetir extrações NIB/CoreMaterial nem os ajustes
da Central e player já registrados. Continuam pendentes vídeo Tahoe equivalente,
gesto real de reordenação da Central e atualização real de sinal/bateria.

## Continuação leve — botão de fechar notificações

| Componente | Diferença inicial | Alteração | Resultado | Estado |
|---|---|---|---|---|
| Banners e Central de Notificações | `set_opacity` ignorava a transição CSS existente; × aparecia/desaparecia abruptamente | Estado `revealed` deixa o CSS interpolar a opacidade nos 120 ms já definidos | 0 → 25 amostras intermediárias em quatro mudanças de hover; cartão 344×93 preservado; callback de fechar preservado | MELHOROU |

[Métricas](MacTahoe/comparador/resultados/convergencia-20261008-notificacoes/metricas.json)
e [antes/depois](MacTahoe/comparador/resultados/convergencia-20261008-notificacoes/hover-antes-depois.png).
Ensaio GTK com eventos controlados, incluindo inversão durante a transição.
Reduzir Movimento produz zero amostras intermediárias, como esperado.
Os 120 ms pertencem ao CSS existente, **não** a uma medição nativa Tahoe.
Compilação, 29 testes e auditor 94%/11 pendências passaram; Hyprland sem erros.
Shell recarregado e notificação demonstrativa **deixada aberta** no HDMI-A-1,
sem expiração, para o usuário testar o hover e fechar quando quiser.
