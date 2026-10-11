# Investigação do volume Tahoe e tradução para Hyprmac

Referência: `/mnt/macos/root`, somente leitura. `System/Library/CoreServices/SystemVersion.plist`
informa **macOS 26.7.1, build 25G241**. Não confundir esta evidência com os kits
denominados “macOS 27” presentes na BaseConhecimento.

Investigação e comparação precederam as mudanças. O repositório já tinha alterações
locais extensas; elas foram preservadas. Inventário reproduzível:

```sh
python3 BaseConhecimento/ferramentas/inventariar_tahoe.py \
  --output BaseConhecimento/referencias/tahoe-inventario.json
```

O JSON registra caminhos, tipos, tamanhos, proprietários, receitas e amostras de
identificadores. Não contém imagens, fontes ou cópias de catálogos proprietários.

## Proveniência

- **[TAHOE]**: dado lido no volume, identificado abaixo por caminho e chave.
- **[HYPRMAC]**: comportamento/código ou referência já presente no projeto.
- **[INFERÊNCIA]**: interpretação dos dados, sem alegação de medição direta.
- **[ESTIMATIVA]**: tradução visual para GTK/Cairo/Hyprland sem equivalência exata.

Os números da auditoria `comparar.py` são verificações por regex, não uma medida de
fidelidade perceptiva. Antes das alterações: 94% global. Há informação desatualizada:
o auditor descreve magnificação do Dock como ausente, mas o código já a implementa.

## Arquitetura e mapa visual [HYPRMAC]

Não há React, Tailwind, styled-components ou aplicação web. Python/PyGObject GTK3
e GtkLayerShell fornecem o shell; GTK4 fornece bloqueio; Cairo desenha ícones,
Dock, miniaturas e efeitos. Hyprland Lua fornece decoração, sombras, animações e
blur; o plugin hyprglass, com patch local, fornece refração/máscaras. Waybar compõe
a Menu Bar. CSS GTK3/4, esquemas KDE e terminais integram aplicações externas.

| Elemento | Componente/arquivo | Estilo, tokens e relação |
|---|---|---|
| Janelas | `hypr/hyprmac.lua`, `gtk/gtk3.css`, `gtk/gtk4.css` | rounding 22, power 3.2; sombras ativa/inativa; palette3/4 e accent3/4 |
| Ajustes/sidebar/folhas | `shell/hyprmac-ajustes`: Settings, Form, Choice, GlassKnob | `shell/ajustes.css`; formas explícitas enviadas ao hyprglass |
| Menu Bar | `waybar/config.jsonc`, `waybar/scripts/`, `waybar/menus/` | `waybar/style.css`, temas, accent, contrast e a11y gerados |
| Dock | `shell/hyprmac-shell`: Dock | Cairo; proporções locais; estilos de ícones e preferências persistentes |
| Central | ControlCenter, Circle, Tile, Toggle, Single, SliderTile, NowPlaying | `shell/style.css`, grade C/W2/W4; preset hyprmac-central |
| Menus/popovers | ShellMenu, BarPanel, WifiMenu, BluetoothMenu, SoundMenu | `.hyprmac-menu`, `.xmenu`; preset hyprmac-texto |
| HUD/player | LevelOSD, MediaPanel | `.osd`, `.media-panel`; presets pequeno/painel |
| Notificações | Banner, NotificationCenter, NotifPanel | `.notif`, `.nc`; componentes comuns de ícone/corpo/hora |
| Spotlight/clipboard | Spotlight, SpotControls, ClipboardPanel | `.spot-*`, `.clip-*`; conteúdo, busca e gotas Cairo |
| Widgets | WeatherWidget, ClockWidget, MonthWidget, BatteryWidget etc. | `.card`, `.weather`, `.shortcuts`; camada de conteúdo |
| Bloqueio | `shell/hyprmac-lock`: LockView, AuthPanel, VibrantLabel | `shell/lock.css`; somas Cairo, PAM, ext-session-lock |
| Overview | `shell/hyprmac-overview`: Screen, Overview | Cairo, miniaturas e curvas próprias |
| Tema/acessibilidade | `scripts/theme`, `scripts/accent`, `scripts/acessibilidade` | paletas e providers; preferências GNOME e arquivos JSON |
| Capturas/idle | `scripts/captura*`, `scripts/gravacao`, `shell/ocioso/` | GTK, D-Bus, protocolos Wayland; preservados |

Leitura orientada pelos índices `INDICE-AGENTES`, `INDICE-CODIGO-AGENTES`,
`GERENCIAMENTO-CONTEXTO` e catálogo de telas; componentes e padrões de materiais,
geometria, movimento, tipografia, menus, Dock, Central, janelas, notificações e
recursos do sistema. Fontes binárias, imagens e documentação não relacionada não
foram carregadas indiscriminadamente. IOGraphics é código de referência, não o
renderer usado pelo shell.

## Sistema instalado [TAHOE]

Todos os caminhos desta seção são relativos a `/mnt/macos/root/System/Library`.

| Origem | Evidência e limite |
|---|---|
| `CoreServices/SystemAppearance.bundle/Contents/Resources/*.car` | 32 catálogos: Aqua/DarkAqua, Graphite, AX, Vibrant/FauxVibrant, VisibleBezels; variantes distintas, não um único tema |
| `Frameworks/AppKit.framework/Versions/C/Resources` | Assets.car, aparências Touch Bar, cores `.clr`, nibs e AquaGuideRules.plist |
| `PrivateFrameworks/CoreUI.framework/Versions/A/Resources` | DesignLibrary-macOS: Light/Dark Standard, Vibrant, IncreasedContrast; catálogos BOMStore |
| `PrivateFrameworks/CoreMaterial.framework/Versions/A/Resources` | `.materialrecipe` e `.visualstyleset` são plists legíveis por plistlib |
| `CoreServices/ControlCenter.app/Contents/Resources/Assets.car` | slider-fill, slider-fill-disabled, slider-knob, slider-knob-pressed, slider-track, outline-disabled, arquivos light/dark/ax e @2x |
| `CoreServices/ControlCenter.app/Contents/MacOS/ControlCenter` | símbolos SwiftUI Material._GlassVariant.controlCenter, notificationCenter, regular, adaptive, excludingShadow; accessibilityReduceTransparency |
| `CoreServices/Dock.app/Contents/Resources/default.plist` | grupos persistent-apps/persistent-others; Downloads separado; Apps e aplicativos do sistema |
| `CoreServices/Dock.app/Contents/Resources/DockMenus.plist` | seções, cabeçalhos, separadores e submenus explícitos para diretórios, documentos e aplicações |
| `CoreServices/Dock.app/Contents/MacOS/Dock` | DockGlassMaterialLayerController, DockGlassMaterialLayoutConfiguration; observadores de contraste/transparência/movimento |
| `CoreServices/SystemUIServer.app/Contents/Resources/Extras.plist` | extras com condições de carregamento; não descreve altura ou material da barra |
| `CoreServices/WindowManager.app` | Assets.car; binário referencia SpringBehavior, C2SpringIntegration e system corner radius, sem constantes recuperadas |
| `CoreServices/{NotificationCenter,Finder,Spotlight}.app` | Assets.car, nibs/loctables e recursos de cada app indexados; não fornecem CSS ou tokens diretamente legíveis |
| `Frameworks/Carbon.framework/Versions/A/Frameworks/HIToolbox.framework` | recursos de entrada, xibs, strings e rsrc; não é a especificação de Liquid Glass |
| `PrivateFrameworks/{Wallpaper,WallpaperAerialAssets,DesignLibrary,WindowManagement}.framework` | metadados, catálogos e entries.json de fundos; geometria visual não recuperada |
| `Fonts` | SFNS, SFNSItalic, SFNSRounded, SFNSMono, SFCompact e variantes de escrita; nenhuma fonte copiada |

### CoreUI / .car

526 `.car` localizados sob System/Library. `assetutil`, `cartool`, `carutil` e
`plutil` não estavam disponíveis; não foi encontrado parser equivalente no projeto.
`strings` e cabeçalhos BOMStore confirmam identificadores; **não** decodificam
renditions. `@2x`, DarkAqua, AX, Selected e Inactive são pistas de escala/estado,
não uma associação completa entre cada asset e todas as variantes.

Dimensões, cap insets, rendering modes e valores internos das cores CoreUI ficam
**não determinados**. Plists embutidos em alguns catálogos estão comprimidos;
encontrar `bplist00` em strings não autoriza tratá-los como plists íntegros.

### Receitas concretas, sem atribuição indevida de uso

Origem: `PrivateFrameworks/CoreMaterial.framework/Versions/A/Resources/`;
chaves `baseMaterial.materialFiltering` dos arquivos abaixo.

| Receita | blurRadius | saturation | Outros dados |
|---|---:|---:|---|
| toolbarButtonBackground.materialrecipe | 15 | 1.1 | backdropScale 0.25 |
| platformChromeDark.materialrecipe | 22.5 | 2.0 | brightness -0.1, luminanceAmount 0.75 |
| platformChromeLight.materialrecipe | 22.5 | 1.1 | brightness 0.1, luminanceAmount 0.75 |
| dockDark.materialrecipe | 30 | 1.6 | luminanceAmount 0.5 |
| dockLight.materialrecipe | 30 | 1.8 | brightness 0.08 |
| modulesBackground.materialrecipe | 25 | 1.6 | zoom 0.04 |
| platformContentThinDark.materialrecipe | 30 | 1.35 | luminanceAmount 0.6 |
| platformContentThickDark.materialrecipe | 45 | 1.5 | luminanceAmount 0.88 |
| platformChrome{Light,Dark}ReduceTransparency.materialrecipe | ausente | variável | averageColorEnabled true, receitas específicas |

`platformStroke{Light,Dark}.visualstyleset` distingue primary, secondary, tertiary,
quaternary; primary é preto/branco a 0.96, e outros papéis usam vibrantColorMatrix.
`moduleFill.visualstyleset` separa moduleItemOff, moduleHighlight e regras sobre
fundos claros/escuros; há composição `plusD`. Isso evidencia que alpha sobre uma
cor uniforme não reproduz sozinho vibrancy.

**[INFERÊNCIA]** A separação por papel/tema/estado é uma boa tradução arquitetural.
**Não comprovado:** que dockLight.materialrecipe seja a receita efetivamente
selecionada pelo DockGlassMaterialLayerController atual. Portanto não se alterou
o blur do Dock para 30 nem se converteram esses valores diretamente para Hyprland.

## Inventário visual e comparação

Medidas abaixo vêm do código e das referências locais, **não da decodificação
dos catálogos**. Capturas consultadas: `referencias/telas/tahoe-dark.jpeg`,
`osd-volume-arrastando.png`, `cc-tahoe-alvo-usuario.png` e catálogo associado.

| Área | Referência / Hyprmac atual | Diferença e prioridade |
|---|---|---|
| Windows | [HYPRMAC] 22 px / power 3.2, filete 1, fundo branco/#1E1E1E, sombra ativa mais forte; toolbar unificada/sidebar inset | Sombra Hyprland não equivale às duas sombras do kit; precisão óptica ainda estimada, P2 |
| Menu Bar | [HYPRMAC] transparente, 34 px, SF 13 semibold, pill ativo; configuração de extras existente | 34 é escolha da referência com notch, não constante de todo monitor. Sem evidência para trocar, P2 |
| Dock | [HYPRMAC] escala ícone/36; padrão ícone46, altura58×escala, passo45×escala, raio15×escala, indicador4×escala, separador41×escala | Alto contraste não chegava ao desenho Cairo: corrigido. Magnificação já existe; curva e suavização permanecem estimativas, P2 |
| Control Center | [HYPRMAC] grade 4 colunas; peças 1×1/2×1/2×2/4×1, capa 29%, títulos13/sub11, tiles separados | Cor ativa do provider de vidro ignorava accent escolhido, P1 corrigido |
| Popovers/menus | [HYPRMAC] menu12/item8, popover20 conforme kit; ancoragem/emerge e um painel por vez existentes | Menus e Spotlight faltavam em seletores AX; material errado no claro, P0 corrigido |
| Buttons | [HYPRMAC] push, default, destructive, secondary, icon, selected em CSS GTK; shell remove outline geral | Foco de teclado invisível; seleção perdia fill no hover AX, P1/P2 corrigido |
| Inputs | [HYPRMAC] entradas/search com seleção accent; switches cápsula; segmentos/dropdowns GTK | Manter estilos existentes; estados de dispositivo não estavam ligados à aparência, P1 corrigido |
| Sliders | [TAHOE] assets disabled/pressed; [HYPRMAC] trilha4, knob20×16 sob hover, fill#F8F8F8 | Ausência de DDC/áudio parecia nível0 operacional; foco sem knob, P1 corrigido |
| Typography | [HYPRMAC] famílias SF/Inter fallback, papéis body13/sub11/legenda10; campos e notificações hierarquizados | Light+AX impunha branco a texto secundário; P0 corrigido. Não copiar fontes |
| Materiais | [TAHOE] recipes/strokes/fills/variantes; [HYPRMAC] presets painel/central/texto/pequeno/lateral e Dock próprio | Preservar filtros separados; corrigir véus/foreground por papel, P0/P1 |
| HUD | [HYPRMAC] OSD claro usa material Clear compartilhado | Provider claro deixava glifos pretos sobre véu quase transparente; P1 corrigido |
| Sheet/overlay | [HYPRMAC] Ajustes tem folhas/popovers; clipboard pinta dim separado | Spotlight não ficava sólido com transparência reduzida; corrigido sem tornar o overlay inteiro opaco |
| Movimento | [TAHOE] spring e observadores AX; [HYPRMAC] pop320ms/out160ms e curvas locais | CSS continuava transitando com reduce_motion no config; corrigido. Timings exatos Apple não recuperados |

## Implementação e tokens

Ampliou-se a abstração existente de providers. `shell_stylesheet()` resolve a
mesma paleta de accent em CSS normal/claro/vidro; a substituição é simultânea,
sem substituir novamente a cor resultante. GTK continua resolvendo tokens de
cor; não há gerador de CSS, outro framework ou segundo sistema de temas.

`style.css` define `shell_accent`, `shell_selection`, `shell_surface_opaque`,
`shell_content_opaque`, `shell_peek*`, `shell_contrast_{label,border,separator}`,
`shell_glass_{text,spotlight,border,control}`, `shell_control_{opaque,hover,ink}`
e `shell_slider_{fill,knob,track}`. O provider claro redefine os papéis de leitura;
Central/player mantêm sua hierarquia Clear. Os providers AX referenciam esses
papéis e mantêm selecionados/hover opacos quando a transparência está reduzida.

Não se inventou `blur.global`. Os presets existentes continuam responsáveis por
blur/refração/saturação, o CSS por tint/borda/conteúdo, e Cairo pelo Dock. Raios e
espaçamentos continuam em seus seletores/constantes existentes: GTK CSS não tem
variáveis dimensionais equivalentes às custom properties da web.

### Estimativas preservadas ou explícitas

- Véus 0.04/0.05 e leitura clara 0.42/Spotlight0.60: calibração local existente;
  não são alphas oficiais extraídos do Tahoe.
- Cores opacas e alto contraste: paleta local, incluindo fill claro 246/246/248
  e borda clara preto0.60; aproximações sem medir runtime Apple em AX.
- Disabled0.38: reaproveita a hierarquia local de transporte indisponível.
- Focus2px/offset−3: aproximação GTK coerente com o focus ring já existente.
- Raios, sombras, timings, easing, proporções do Dock e passes de blur: estimativas
  documentadas no código/referências; não valores oficiais inferidos de nomes.
- Filtragem CoreMaterial, refração hyprglass e mistura alpha não são equivalentes.

## Validação e limites

A validação cobre parser GTK, renderização real de componentes e precedência dos
providers, estados claro/escuro × vidro × transparência reduzida × alto contraste,
mudança de accent, disabled e foco, além das verificações do projeto. Capturas
offscreen validam GTK; somente a sessão Hyprland pode validar o shader no fundo.

Os resultados executados são registrados ao final desta investigação. Não há
typecheck de TypeScript nem build web neste projeto; Python compila para bytecode,
GTK valida CSS, e os Makefiles existentes compilam os componentes C.

Para fidelidade adicional ainda é necessário renderizar o Tahoe de referência
nos mesmos estados/fundos/escalas, decodificar renditions com ferramenta CoreUI
adequada e medir animações por frames temporizados. O volume estático sozinho
não permite certificar equivalência visual 1:1.

### Resultado executado

- Formatter Ruff nos arquivos novos e apenas nos trechos Python alterados do shell.
- Lint Ruff dos arquivos novos: aprovado; shell: E9/F821/F822/F823 aprovado.
- `py_compile` do shell, Ajustes e bloqueio: aprovado.
- `python3 -m unittest discover -s tests -v`: três testes de integração aprovados,
  incluindo 16 combinações de providers, duas cores de accent, estados de
  seleção/hover/foco/disabled e atualização de slider sem disparar comandos.
- Os dois Makefiles (`shell/ocioso` e `waybar/cffi`) concluíram: alvos atualizados.
- Pyright executado nos três Python envolvidos: 72 erros e três avisos no shell;
  comparação com a cópia anterior produz exatamente os mesmos diagnósticos.
  Há imports dinâmicos GI sem tipagem e problemas prévios. Não é um typecheck limpo;
  os dois arquivos novos não têm diagnósticos.
- Auditoria `comparar.py --resumo/--pendentes`: permanece em 94%, sem regressão.
- `indexar.py`: documentação incorporada ao índice local.
- `git diff --check` global acusa whitespace preexistente em documentação;
  os arquivos desta implementação são verificados separadamente.
- GTK offscreen: capturas das 16 combinações em `/tmp/hyprmac-tahoe-audit/render`;
  inspecionados claro opaco/alto contraste e escuro com véu. Fundo neutro de teste
  não simula refração: a verificação do shader é separada.
- Hyprland real: shell reiniciado, Central aberta por D-Bus e captura em
  `/tmp/hyprmac-tahoe-audit/runtime-after.png`; plugin hyprglass 1.0.0 carregado.
  Log sem exceções/erros GTK CSS, com depreciações prévias de PyGObject/GTK.

Nenhum arquivo do volume macOS foi alterado. Nenhuma preferência visual do usuário
foi persistida pela suíte de testes. A Central aberta para inspeção é fechada ao
final da validação.
