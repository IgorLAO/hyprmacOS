# AGENTS.md — HyprMac

**Objetivo absoluto: reproduzir visualmente e em comportamento o macOS Tahoe 26 no Hyprland.** Fidelidade máxima exige confrontar composição, medidas, tipografia, material, movimento e estados com evidências Tahoe 26. A base antiga também contém itens rotulados macOS 27, visionOS e versões desconhecidas; trate-os como secundários até verificar a correspondência. Nunca apresente fonte não verificada como comportamento oficial Apple.

Leia [ARCHITECTURE.md](ARCHITECTURE.md) para o fluxo atual e [STATUS.md](STATUS.md) para pendências. Mantenha o contexto inicial curto. Para cada tarefa: identifique o componente → busque no SQLite → abra somente evidências relevantes → confira o código e a referência visual → implemente. Ponto de partida: até 3.000 tokens permanentes, 2.000 tokens na primeira busca; expanda sob demanda.

Nas próximas modificações, siga a fila de [TODO.md](TODO.md) e os IDs do [catálogo de comportamentos](BaseConhecimento/LISTA-DE-DESEJOS.md). Priorize controles compartilhados, Central/Spotlight, movimento/janelas e barra/notificações, conforme o redirecionamento de 2026-10-11. Dock/refração são investigação secundária preservada; consolide o shell antes de novos apps. Registre implementação e validação separadamente por comportamento, com evidência e limitações; coincidência de CSS ou nota da matriz não certifica fidelidade. Requisitos do catálogo são metas do usuário, não fatos Apple já verificados. Componentes ausentes permanecem no backlog até a etapa de expansão.

```bash
B=./BaseConhecimento/ferramentas
$B/consultar.py --codigo "dock"            # candidatos no código
$B/consultar.py "liquid glass" -n 5          # FTS de fontes atuais
$B/consultar.py --documento componentes/dock.md  # estado e proveniência
$B/consultar.py --registro "hyprglass"       # decisões e projetos externos
$B/consultar.py "dock" --historico           # fontes arquivadas, substituídas ou inválidas
$B/consultar.py --imagem "control center"    # catálogo antes do original
$B/comparar.py --resumo                       # nota interna da matriz, não fidelidade global
```

Fonte de verdade por decisão: `shell/style.css` para propriedades visuais do shell; `hypr/hyprmac.lua` para compositor e janelas; código executável para comportamento; `comparacao/parametros.json` para definições das medições; `BaseConhecimento/base.db` para estado/proveniência dos documentos e registros curados. `BaseConhecimento/MacTahoe/base.db` contém investigação especializada local e não versionada. Consulte o original quando um número ou conclusão importar. Cite `[real:arquivo:linha]` para medidas tiradas do código.

No shell, assine eventos por `shell/hypr_events.py`; não abra outro socket Hyprland por componente. O índice compartilhado de apps fica em `shell/app_index.py`. O núcleo do Dock fica em `shell/dock_model.py` (conteúdo/eventos), `shell/dock_geometry.py` (layout/hit testing) e `shell/dock_motion.py` (molas/magnificação), sem GTK ou timers próprios. Busca/cálculo do Spotlight ficam em `shell/spotlight_search.py`; desenho/animação dos seus controles ficam em `shell/spotlight_controls.py`. Menus da Waybar recebem sinal 11 quando a classe em foco muda.

Não introduza vidro sobre vidro, tintas opacas em superfícies de vidro nem gaps de janela diferentes de zero sem evidência Tahoe 26. Preserve backups e idempotência do instalador. Antes de criar Markdown, procure documento ou registro equivalente; atualize o SQLite para decisões e pesquisas curtas. Use `indexar.py` após alterar fontes textuais ou tokens: ele indexa incrementalmente e preserva o histórico. Classifique registros como `verified`, `experimental`, `superseded`, `archived` ou `invalid`, com fonte, versão e evidência; só use `verified` quando houver verificação concreta. Não limpe trabalho local de outros agentes.

Para alterações de código, compile os arquivos afetados e execute verificações pertinentes. Para mudanças visuais, recarregue o componente no desktop e deixe-o visível para conferência. Antes do handoff: `comparar.py --resumo`, `comparar.py --pendentes`, `git diff --check` e `git status --short`. Relate arquivos alterados, evidências, validação, limitações e risco visual restante.

Após curadoria/indexação, rode `BaseConhecimento/ferramentas/auditar_base.py` para detectar hashes divergentes, links operacionais quebrados e problemas de integridade SQLite.
