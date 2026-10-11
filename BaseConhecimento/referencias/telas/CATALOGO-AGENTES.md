# Catálogo visual para agentes

Consulte este arquivo e os atlas antes de abrir originais. O JSON contém metadados estáveis; os atlas são miniaturas para triagem visual. Abra o original apenas para medir ou validar um detalhe.

## Protocolo multimodal

A descrição textual é um índice, não uma substituição da imagem. Use a sequência abaixo para reduzir custo sem perder informação visual:

```text
catálogo semântico → atlas → original → implementação → comparação
```

O atlas permite reconhecer a tela, o estado e a composição em uma única leitura visual. O original é necessário para texto pequeno, alinhamento, alpha, blur, raio, espessura, tipografia, ícones e comparação de pixels. Para uma animação, abra os frames pelo grupo e pela ordem `1/N`, `2/N`, `3/N`…; a relação entre os elementos ao longo dos frames faz parte da referência comportamental.

Prioridades: `golden` = referência principal; `canonical` = referência ampla; `secondary` = apoio.

`confianca=alta` indica classificação curada; `confianca=media` indica inferência pelo nome/estrutura e exige confirmação no atlas ou original antes de uma decisão visual crítica.

| Categoria | Prioridade | Arquivo | Estado | Uso recomendado | Dimensão |
|---|---|---|---|---|---|
| `desktop` | **secondary** | [`03gv9eretsydh3ic3etkffp-12_p5yz.1920.webp`](03gv9eretsydh3ic3etkffp-12_p5yz.1920.webp) | reference | desktop | 1280×720 |
| `control_center` | **secondary** | [`1_AWn03UdmtRaR6fupfQIMUQ.jpg`](1_AWn03UdmtRaR6fupfQIMUQ.jpg) | edit | control center | 1180×764 |
| `desktop` | **secondary** | [`1_UTWwDUD5PaEbW7XRmuWEoA.jpg`](1_UTWwDUD5PaEbW7XRmuWEoA.jpg) | reference | desktop | 1299×841 |
| `app_window` | **secondary** | [`Apple-WWDC25-macOS-Tahoe-26-Apple-Intelligence-Live-Translation-250609.webp`](Apple-WWDC25-macOS-Tahoe-26-Apple-Intelligence-Live-Translation-250609.webp) | reference | app window | 3840×2560 |
| `app_window` | **secondary** | [`Apple-WWDC25-macOS-Tahoe-26-Apple-Intelligence-Shortcuts-Notes-250609.jpg`](Apple-WWDC25-macOS-Tahoe-26-Apple-Intelligence-Shortcuts-Notes-250609.jpg) | reference | app window | 3840×2560 |
| `app_window` | **secondary** | [`Apple-WWDC25-macOS-Tahoe-26-Apple-Music-250609.jpg`](Apple-WWDC25-macOS-Tahoe-26-Apple-Music-250609.jpg) | reference | app window | 3840×2560 |
| `control_center` | **secondary** | [`Apple-WWDC25-macOS-Tahoe-26-Control-Center-250609.jpg`](Apple-WWDC25-macOS-Tahoe-26-Control-Center-250609.jpg) | light | control center | 3840×2560 |
| `control_center` | **secondary** | [`Apple-WWDC25-macOS-Tahoe-26-Control-Center-250609_big.jpg.large.jpg`](Apple-WWDC25-macOS-Tahoe-26-Control-Center-250609_big.jpg.large.jpg) | reference | control center | 980×653 |
| `lock_screen` | **canonical** | [`Apple-WWDC25-macOS-Tahoe-26-Lock-Screen-250609.jpg`](Apple-WWDC25-macOS-Tahoe-26-Lock-Screen-250609.jpg) | light, lock_screen | lock screen geometry, clock, avatar | 3840×2560 |
| `notification` | **secondary** | [`Apple-WWDC25-macOS-Tahoe-26-Phone-incoming-call-250609.jpg`](Apple-WWDC25-macOS-Tahoe-26-Phone-incoming-call-250609.jpg) | reference | notification | 3840×2560 |
| `control_center` | **secondary** | [`Edit-Controls-in-macOS-Control-Center.jpg`](Edit-Controls-in-macOS-Control-Center.jpg) | edit | control center | 948×1348 |
| `desktop` | **secondary** | [`WU6D54fr94LsaXw5qmN84N.jpg`](WU6D54fr94LsaXw5qmN84N.jpg) | reference | desktop | 1280×720 |
| `settings` | **secondary** | [`ajustes-aparencia-claro-cor-pastas.png`](ajustes-aparencia-claro-cor-pastas.png) | light | settings | 557×486 |
| `settings` | **secondary** | [`ajustes-general-escuro-aguas-vivas.png`](ajustes-general-escuro-aguas-vivas.png) | dark, settings | System Settings layout, sidebar, dark materials | 780×438 |
| `settings` | **secondary** | [`ajustes-wallpaper-clock-appearance-downlink.png`](ajustes-wallpaper-clock-appearance-downlink.png) | reference | settings | 1024×843 |
| `settings` | **canonical** | [`ajustes-wallpaper-clock-appearance-escuro.png`](ajustes-wallpaper-clock-appearance-escuro.png) | dark, popover, lock_screen | Clock Appearance popover, weight slider, lock screen settings | 1200×516 |
| `settings` | **secondary** | [`ajustes-wallpaper-clock-appearance-pequeno.png`](ajustes-wallpaper-clock-appearance-pequeno.png) | light, popover, lock_screen | Clock Appearance controls, popover proportions | 580×344 |
| `settings` | **secondary** | [`ajustes-wallpaper-landscape-claro.png`](ajustes-wallpaper-landscape-claro.png) | light | settings | 1670×1714 |
| `settings` | **secondary** | [`ajustes-wallpaper-landscape-escuro.png`](ajustes-wallpaper-landscape-escuro.png) | dark | settings | 1670×1556 |
| `settings` | **secondary** | [`ajustes-wallpaper-screen-saver-folha-claro.png`](ajustes-wallpaper-screen-saver-folha-claro.png) | light | settings | 1536×999 |
| `lock_screen` | **secondary** | [`bloqueio-26-final-relogio-estencil.png`](bloqueio-26-final-relogio-estencil.png) | reference | lock screen | 2000×1301 |
| `lock_screen` | **secondary** | [`bloqueio-beta-praia-abc-carregando.png`](bloqueio-beta-praia-abc-carregando.png) | beta | lock screen | 2000×1299 |
| `lock_screen` | **secondary** | [`bloqueio-relogio-data-por-extenso.png`](bloqueio-relogio-data-por-extenso.png) | light, clock_style | lock screen typography, date format, large clock | 852×546 |
| `lock_screen` | **secondary** | [`bloqueio-relogio-estencil-vidro-montanhas.png`](bloqueio-relogio-estencil-vidro-montanhas.png) | reference | lock screen | 1210×710 |
| `lock_screen` | **secondary** | [`bloqueio-varios-usuarios-relogio-serifa.png`](bloqueio-varios-usuarios-relogio-serifa.png) | reference | lock screen | 1920×1080 |
| `comparison` | **golden** | [`cc-comparacao-hyprmac-x-tahoe.png`](cc-comparacao-hyprmac-x-tahoe.png) | light, side_by_side | visual regression, side-by-side review | 735×678 |
| `control_center` | **canonical** | [`cc-edicao-galeria-sobre-azul.png`](cc-edicao-galeria-sobre-azul.png) | light, edit, gallery | Controls Gallery, edit mode, glass panel | 832×610 |
| `control_center` | **secondary** | [`cc-sobre-janela-clara.png`](cc-sobre-janela-clara.png) | light, overlay | Control Center over window, layer contrast | 575×627 |
| `control_center` | **golden** | [`cc-tahoe-alvo-usuario.png`](cc-tahoe-alvo-usuario.png) | light, target | Control Center layout, tile proportions, sliders | 496×491 |
| `desktop` | **secondary** | [`clear-dark-1.webp`](clear-dark-1.webp) | dark | desktop | 800×521 |
| `desktop` | **secondary** | [`dark-icons-widgets-macos-1.webp`](dark-icons-widgets-macos-1.webp) | dark | desktop | 800×521 |
| `menu_bar` | **secondary** | [`escuro-menu-contexto-sobre-rosa.png`](escuro-menu-contexto-sobre-rosa.png) | dark, overlay | menu bar | 640×733 |
| `spotlight` | **secondary** | [`escuro-spotlight-apps-sobre-claro.png`](escuro-spotlight-apps-sobre-claro.png) | dark, light, overlay | spotlight | 653×592 |
| `desktop` | **secondary** | [`images.jpeg`](images.jpeg) | reference | desktop | 353×566 |
| `control_center` | **canonical** | [`macos-tahoe-home-screen.jpg`](macos-tahoe-home-screen.jpg) | light, edit, widgets, dock | edit mode, ghost slots, widget layout | 1500×975 |
| `app_window` | **secondary** | [`macos-tahoe-looking-good-in-black.avif`](macos-tahoe-looking-good-in-black.avif) | reference | app window | 1600×900 |
| `app_window` | **secondary** | [`macos-tahoe-looking-good-in-black.jpg`](macos-tahoe-looking-good-in-black.jpg) | dark | app window | 1600×900 |
| `osd` | **secondary** | [`osd-volume-alto-falantes.png`](osd-volume-alto-falantes.png) | reference | osd | 655×239 |
| `osd` | **secondary** | [`osd-volume-arrastando.png`](osd-volume-arrastando.png) | reference | osd | 625×217 |
| `menu_bar` | **golden** | [`safari-escuro-barra-de-menus-abas.png`](safari-escuro-barra-de-menus-abas.png) | dark, safari, window, tabs | menu bar, window geometry, tabs | 1276×140 |
| `spotlight` | **secondary** | [`spotlight-abrir-1.png`](spotlight-abrir-1.png) | light, animation | spotlight | 621×173 |
| `spotlight` | **secondary** | [`spotlight-abrir-2.png`](spotlight-abrir-2.png) | light, animation | spotlight | 574×144 |
| `spotlight` | **secondary** | [`spotlight-clique-modo-1.png`](spotlight-clique-modo-1.png) | light, animation | spotlight | 777×165 |
| `spotlight` | **secondary** | [`spotlight-clique-modo-2.png`](spotlight-clique-modo-2.png) | light, animation | spotlight | 599×258 |
| `spotlight` | **secondary** | [`spotlight-clique-modo-3.png`](spotlight-clique-modo-3.png) | light, animation | spotlight | 489×296 |
| `spotlight` | **secondary** | [`spotlight-clique-modo-4.png`](spotlight-clique-modo-4.png) | light, animation | spotlight | 586×483 |
| `spotlight` | **secondary** | [`spotlight-clique-modo-5.png`](spotlight-clique-modo-5.png) | light, animation | spotlight | 611×506 |
| `spotlight` | **secondary** | [`spotlight-controles-1.png`](spotlight-controles-1.png) | light, animation | spotlight | 477×149 |
| `spotlight` | **secondary** | [`spotlight-controles-2.png`](spotlight-controles-2.png) | light, animation | spotlight | 576×150 |
| `spotlight` | **secondary** | [`spotlight-controles-3.png`](spotlight-controles-3.png) | light, animation | spotlight | 643×182 |
| `spotlight` | **secondary** | [`spotlight-controles-4.png`](spotlight-controles-4.png) | light, animation | spotlight | 700×88 |
| `spotlight` | **secondary** | [`spotlight-controles-5.png`](spotlight-controles-5.png) | light, animation | spotlight | 796×110 |
| `spotlight` | **secondary** | [`spotlight-controles-6.png`](spotlight-controles-6.png) | light, animation | spotlight | 743×99 |
| `spotlight` | **secondary** | [`spotlight-modo-apps-1.png`](spotlight-modo-apps-1.png) | light, animation | spotlight | 363×282 |
| `spotlight` | **secondary** | [`spotlight-modo-apps-2.png`](spotlight-modo-apps-2.png) | light, animation | spotlight | 340×264 |
| `spotlight` | **secondary** | [`spotlight-modo-apps-3.png`](spotlight-modo-apps-3.png) | light, animation | spotlight | 501×343 |
| `spotlight` | **secondary** | [`spotlight-modo-apps-4.png`](spotlight-modo-apps-4.png) | light, animation | spotlight | 439×357 |
| `spotlight` | **secondary** | [`spotlight-modo-apps-5.png`](spotlight-modo-apps-5.png) | light, animation | spotlight | 455×354 |
| `spotlight` | **secondary** | [`spotlight-modo-apps-6.png`](spotlight-modo-apps-6.png) | light, animation | spotlight | 480×376 |
| `spotlight` | **secondary** | [`spotlight-modo-apps-7.png`](spotlight-modo-apps-7.png) | light, animation | spotlight | 399×314 |
| `spotlight` | **secondary** | [`spotlight-modo-apps-8.png`](spotlight-modo-apps-8.png) | light, animation | spotlight | 376×375 |
| `spotlight` | **secondary** | [`spotlight-modo-apps-9.png`](spotlight-modo-apps-9.png) | light, animation | spotlight | 431×351 |
| `desktop` | **canonical** | [`tahoe-dark.jpeg`](tahoe-dark.jpeg) | dark, desktop, finder | dark theme, window decoration, Dock | 2560×1656 |
| `desktop` | **secondary** | [`tahoe-novidades-mosaico.png`](tahoe-novidades-mosaico.png) | reference | desktop | 2000×1125 |
| `desktop` | **secondary** | [`tahoe-photos-central-dock-claro.png`](tahoe-photos-central-dock-claro.png) | light | desktop | 1632×1074 |

## Como um agente usa o catálogo

1. Busque por categoria/estado/uso no `catalogo.json` ou com `consultar.py --imagem`.
2. Abra o atlas indicado em `triagem` para reconhecer rapidamente a tela.
3. Abra o arquivo original somente quando a tela for a referência escolhida.
4. Para sequências, leia `sequencia.grupo`, `ordem` e `total` na ordem numérica.
5. `golden` é referência principal; `canonical` é referência ampla; `secondary` é apoio.

## Categorias

`app_window` · `control_center` · `desktop` · `lock_screen` · `menu_bar` · `notification` · `osd` · `settings` · `spotlight` · `comparison`
