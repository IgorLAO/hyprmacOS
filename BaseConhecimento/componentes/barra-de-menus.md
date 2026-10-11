# Menu Bar

> Sources: macOS 27 UI Kit *Menu Bar and Dock* layer outline (`referencias/kit/contornos/Menu_Bar_and_Dock.txt`), Apple HIG [the-menu-bar](../hig/the-menu-bar.md), official WWDC25 and Tahoe UI screenshots.

---

## Anatomy (Left to Right)
**Apple Logo (``) · Active Application Name (Heavy Bold) · Application Menus** … **Status Extras** (System & third-party tray) · Control Center trigger (two toggles icon) · Siri · **Date and Time** ("Tue Apr 1  9:41 AM").

Extras observed in Tahoe: Battery status, Wi-Fi, Spotlight (magnifying glass), Control Center, Siri, User profile, Now Playing, Weather, Privacy indicators (green camera capsule).

---

## Dimensions & Layout (1× Scaling)
* **Useful Height:** **24 pt** (34 pt on Retina notch displays).
* **Menu Titles:** Start at $x = 10$, ~10 pt horizontal padding per side.
* **Apple Logo:** 33×24 pt bounding box, 16.3 pt glyph size.
* **Status Extras:** Bounding boxes ~30–31 pt wide, 16 pt icon footprint.

---

## Typography
* **Menus:** **SF Pro Semibold 13 pt**.
* **Active App Name:** **SF Pro Heavy 13 pt**.
* **Date & Clock:** Semibold 13.1 pt.

---

## Color & Material Fills

| Wallpaper Backdrop | Foreground Text | Active Selection Pill |
|---|---|---|
| Over Dark Wallpaper | `#FFFFFF` | Capsule `#FFFFFF33` (20%) *plus-lighter* + blur 30 |
| Over Light Wallpaper | `#000000D9` (85%) | Capsule `#00000014` (8%) *plus-darker* + blur 30 |

* The menu bar is **completely transparent** in macOS Tahoe, softly tinted by ambient desktop luminance.
* **Active Capsule Pill:** **62×25 pt, continuous 13 pt radius**, extending 4 pt beyond the item horizontally.
* **Open Control Center Trigger:** Enclosed in a persistent glass capsule while the panel is active.

---

## Behavioral Specifications (Apple HIG)
* Menus maintain standard hierarchy (Apple ▸ App ▸ File ▸ Edit ▸ View ▸ Window ▸ Help).
* Menu titles consist of single words; unavailable actions are dimmed rather than hidden.
* Status extras open **menus** rather than standalone popups.
* **Level OSD Feedback:** Volume and brightness adjustments invoke a floating glass OSD in the top-right corner under the bar (344×74 pt, continuous ~26 pt radius, positioned 7 pt below menu bar). Displays active output name ("MacBook Air Speakers", Semibold 13 pt), interactive slider line, and discrete dot calibration marks.

## Menu Bar Extras — investigação de 2026-10-10 (Tahoe 26)

Referências verificadas: [guia Apple selecionado em Tahoe 26](https://support.apple.com/guide/mac-help/whats-in-the-menu-bar-mchlp1446/26/mac/26)
(status menus, clique, reordenação com Command) e
[personalização](https://support.apple.com/guide/mac-help/customize-the-menu-bar-mchl4af84660/26/mac/26).
Essas fontes confirmam comportamento, não dimensões, alfa ou duração de hover.
A captura local `referencias/telas/safari-escuro-barra-de-menus-abas.png` foi
inspecionada: extras de terceiros precedem os controles do sistema; seleção
individual em cápsula. O catálogo a classifica manualmente como Tahoe, sem
proveniência independente da versão. Medidas 16 pt, passo 38–39 pt, cápsula
36×20 pt e barra 34 pt são aproximações da captura, não métricas oficiais Apple.
Os números anteriores deste documento oriundos do kit rotulado macOS 27 não
são evidência verificada do Tahoe 26.

Implementação encontrada: Waybar 0.15.0, um processo, duas barras (um host por
monitor), watcher `org.kde.StatusNotifierWatcher` da própria Waybar e nenhum
item registrado inicialmente. `tray` já constava de modules-right, com ícones
15 px e spacing 12 px. Menus de aplicativos à esquerda são XML/ações locais;
os controles Wi-Fi/Som/Central chamam `dev.hyprmac.Shell.Command`. São contratos
diferentes dos menus `com.canonical.dbusmenu` dos aplicativos SNI.

Limitações concretas do tray upstream 0.15.0, confirmadas no
[código Item](https://github.com/Alexays/Waybar/blob/0.15.0/src/modules/sni/item.cpp),
[Tray](https://github.com/Alexays/Waybar/blob/0.15.0/src/modules/sni/tray.cpp) e
[Watcher](https://github.com/Alexays/Waybar/blob/0.15.0/src/modules/sni/watcher.cpp):

- `AttentionIconPixmap` e `OverlayIconPixmap` têm TODO; `getIconPixbuf` só
  seleciona o ícone normal e ignora attention/overlay, mesmo em NeedsAttention.
  `NewAttentionIcon` e `NewOverlayIcon` não são assinados. CSS não corrige isso.
- Só há ordem de chegada ou reverse-direction; nenhum filtro/ordem por Id.
  As classes CSS só expõem Status, não identidade. Usar nth-child seria instável.
- `makeMenu` remove prelight e não expõe estado de menu aberto; não há cápsula
  persistente enquanto o menu D-Bus está aberto.
- O watcher solicita REPLACE/ALLOW_REPLACEMENT, podendo substituir outro watcher.
- Activate, SecondaryActivate, ContextMenu, Scroll e libdbusmenu já existem.
  O host deduplica por serviço/caminho; Id não é chave única (Electron compartilha Id).

Decisão: estender pontualmente o **tray nativo**, com patch fixado em 0.15.0,
compilação local e fallback para Waybar do sistema. Não criar outro daemon nem
reimplementar SNI no shell. Preservar os módulos e ações existentes. O custo é
manter um patch C++ e uma build local, explicitamente isolados do pacote do sistema.

### Implementação entregue

`waybar/patches/tahoe-sni.patch` estende somente SNI na Waybar 0.15.0.
`build-waybar-extras` baixa fontes oficiais com SHA-256 fixado, aplica o patch e
compila em `~/.cache/hyprmac/waybar-tahoe`; nunca substitui `/usr/bin/waybar`.
Mantém módulos MPRIS, network, pulseaudio, privacy/PipeWire, rfkill e CFFI.
O autostart chama `scripts/menu-extras start`, que evita outra instância e usa
fallback upstream com limitações explícitas se a build não estiver disponível.
O lock é CLOEXEC; o PID inclui starttime para não confundir PID reciclado.
O launcher sincroniza `vidro.css` com o plugin realmente carregado: nesta sessão
havia CSS de vidro ativo sem plugin, deixando menus quase transparentes. A ação
`vidro sync-css` restaura o material de fallback existente sem carregar plugin.

`IconName`/`IconPixmap`, aspect ratio, ícones de atenção, overlays e seus sinais
são preservados. `PropertiesChanged` e propriedades invalidadas também são
tratados. Menus D-Bus ficam ancorados abaixo da barra e expõem `menu-open` até
fechar. A alteração do caminho Menu recria o cliente libdbusmenu e libera o anterior.
O watcher não pede substituição; hosts externos continuam com suas barras.
A deduplicação permanece por serviço/caminho, sem eliminar apps que compartilham Id.
Uma instância por monitor é esperada; não é duplicação dentro da mesma barra.

Geometria local: ícone 16 px, padding horizontal 10 px em GtkImage, margem GTK
vertical 7 px em EventBox, spacing 2 px: cápsula 36×20 e passo 38 px na barra
34 px. EventBox ignora padding/margem CSS no cálculo; isso foi constatado no
runtime e corrigido com `item-margin`. Ícones não quadrados mantêm proporção e
largura variável. Hover/destaque usam os tokens e variantes de contraste da
barra, com transição existente de 120 ms (aproximação, não tempo Apple medido).
Os menus reutilizam tema, acessibilidade e material da barra.

Preferências em `~/.config/hyprmac/menu-extras.json`, incluídas no config:

```json
{"tray": {"hidden-items": ["nm-applet"], "order-items": ["vlc", "nm-applet"]}}
```

`policy-file` observa o diretório com Gio::FileMonitor **no processo da Waybar**.
Renames atômicos atualizam visibilidade/ordem sem SIGUSR2, sem perder menus,
watcher ou estado dos outros controles. Arquivos inválidos são rejeitados.
Nos Ajustes ▸ Menu Bar, a seção `Allow in the Menu Bar` lista apenas SNI
registrados (incluindo os ocultos) e permite ativar/desativar cada app. Abra o
painel novamente para atualizar a lista de registros; não há polling residente.
Comandos pontuais, a partir da raiz do projeto:

```sh
scripts/menu-extras list
scripts/menu-extras hide nm-applet
scripts/menu-extras show nm-applet
scripts/menu-extras order vlc nm-applet
scripts/menu-extras order   # restaurar ordem de chegada
scripts/menu-extras diagnose
scripts/build-waybar-extras
```

A ordem lista identidades da esquerda para a direita; apps restantes seguem a
ordem de chegada. `title:Título exato` diferencia Id compartilhado, sobretudo
`chrome_status_icon_1` do Electron. Title pode mudar: prefira Id estável quando
for único. Ocultar o item não encerra o aplicativo. `show-passive-items: false`
continua respeitando Passive; não é um indicador de todos os processos abertos.
Para mover o bloco inteiro em relação aos controles, edite modules-right.

### Validação e limites

- NetworkManager Applet (`nm-applet --indicator`) e VLC Qt (`--qt-system-tray`)
  registraram ícones originais automaticamente. Seus menus nativos foram abertos
  no desktop. Nenhuma conexão de rede foi alterada para o teste.
- Fixture `tests/fixtures/status_notifier.py`: 256 pixels originais em 16×16;
  NeedsAttention e NewAttentionIcon preservados; overlay verde com 36 pixels e
  220 pixels remanescentes do ícone original; Passive oculta e Active restaura.
- Activate, SecondaryActivate, Scroll vertical/horizontal e ações DBusMenu foram
  recebidos e registrados. Clique esquerdo em ItemIsMenu abriu o menu.
  A cápsula permaneceu acesa após mover o ponteiro para fora, até fechar.
- Ocultar/mostrar por Id e ordenar foram exercitados no desktop. Reordenação
  deslocou o ícone exatamente 38 px. Preferências mantiveram o mesmo PID da
  Waybar e os dois hosts dos monitores. Um segundo `start` não abriu outra barra.
- Três testes de preferências passaram. Dois testes opt-in `test_sni_watcher.py`, com
  D-Bus privado e build real, confirmou host registrado sem substituir watcher
  externo mesmo quando este permitia replacement, e encerramento do item após três recargas. Build C++ e sintaxe Python,
  Bash e reload Hyprland validados. Capturas e relatório em
  `comparacao/resultados/menu-extras-sni-20261010/`.

Não há reordenação por Command+drag, galeria de extras terceiros nem política
por monitor; a ordenação configurada substitui o gesto. `AttentionMovieName`
não anima vídeos; attention pixmap/name e mudanças de status são suportados.
Menus abertos pelo próprio aplicativo via ContextMenu/Activate não expõem
visibilidade em SNI: nesse caso não há cápsula persistente, apenas hover.
Não há ponte XEmbed nem detecção de apps que não publicam SNI. Outros hosts
visíveis podem exibir os mesmos itens em seus próprios painéis; o HyprMac não
encerra nem modifica esses painéis. A fidelidade visual ao Tahoe permanece
**experimental**: falta captura independente do Tahoe 26 nos mesmos estados,
escala e fundo. A conformidade SNI no Linux foi verificada separadamente.

Regressão de ciclo de vida encontrada no encerramento dos testes: o watcher
upstream remove GfWatch da lista em nameVanished sem cancelar/liberar a
assinatura. Após registrar antes de obter o nome D-Bus e recarregar a barra,
o encerramento do app pode chamar um Watcher destruído. Confirmado por core
SIGSEGV em g_slist_remove/Watcher::nameVanished. O patch agora libera a watch
removida, desconecta handlers e libera o skeleton na destruição. O teste com
fixture `late-name` falhou na build anterior e passou com a correção, depois
de três recargas. NetworkManager Applet e VLC também foram registrados, a
barra recarregada e ambos encerrados mantendo a Waybar viva.

Referência visual oficial adicional: [imagem da barra no guia Apple /26](https://help.apple.com/assets/69DD569682238CF8EC0621E2/69DD569982238CF8EC0621E9/en_US/62a24ce3b2745abaa8344ab3ce1d050f.png),
verificada no link de imagem de “What’s in the menu bar” na página versionada
Tahoe 26. Cópia em `comparacao/resultados/menu-extras-sni-20261010/apple-menu-bar-support26.png`
(1146×310). Confirma separação entre menus do app e status menus/controles à
direita e composição transparente; não declara escala, dimensões em pt nem
estados de hover de apps terceiros. Não substitui a validação métrica pendente.
