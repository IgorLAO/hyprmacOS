# Tahoe → convergência por blocos

Continuação de `INVESTIGACAO-TAHOE-2026-10-06.md`. Referência montada somente
leitura; sem nova indexação geral. [TAHOE] identifica arquivos do volume;
[HYPRMAC] código/referências locais; [INFERÊNCIA] tradução funcional para Linux.
Não foram criados componentes grandes ausentes.

| Bloco | Existe? | Diferente? | Decisão | Resultado |
|---|---|---|---|---|
| 1 Control Center | Sim | Navegação/teclado e reabertura | MELHORAR | MELHORADO: retorno por mouse, Escape por nível, alvo de teclado independente do clique, reanexação segura |

## Evidências e validação por bloco

1. **Central:** [HYPRMAC] ControlCenter, Tile, BarPanel, menus hosted e grade
   persistente em `shell/hyprmac-shell`. [TAHOE] ControlCenter.app/Resources/
   Bluetooth.loctable e WiFi.loctable distinguem ligado, conectado, redes conhecidas,
   outras redes e acesso explícito a Ajustes. [INFERÊNCIA] o detalhe no Gtk.Stack
   precisa de retorno acionável sem fechar toda a Central; seta direita abre o
   detalhe e Escape retorna um nível. Dimensões, backends e grid preservados.
