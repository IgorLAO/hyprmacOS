# Pesquisa: Mission Control / Spaces / App Exposé (macOS Tahoe 26.6.1)

Somente leitura. Nada foi editado no projeto. Legenda: [V] verificado na fonte primária; [S] fonte secundária do próprio projeto (não confrontada com o binário); [I] inferência.

## 1. Textos (fonte primária: material original 26.6.1, somente leitura)

- [V] `Dock.app/Contents/Resources/en.lproj/Localizable.strings`: `DesktopNum` = `Desktop %@` (formato do nome de Space numerado; "Desktop 1" é a instância com %@=1).
- [V] `Dock.app/Contents/Resources/en.lproj/DockMenus.strings`: `OTHER_DESKTOP` = `Desktop %@`; `OTHER_DESKTOP_ON` = `Desktop %@ on Display %@`; `DESKTOP_ON` = `Desktop on Display %@`; `THIS_DESKTOP` = `This Desktop`; `ALL_DESKTOPS` = `All Desktops`; `2_APP_TILED_SPACE` (Localizable) = `%@ & %@`.
- [V] Acessibilidade, `Dock.app/Contents/Resources/en_AU.lproj/Accessibility.strings`: `AXAddDesktop` = `add desktop`; `AXRemoveDesktop` = `remove desktop`; `AXMissionControlSpacesBarGroup` = `Spaces Bar`; `AXExposeWindowGroup` = `exposéd windows`; `AXExposeRecentsGroup` = `recent and minimised windows`; `AXShowExpose` = `show exposé`; `AXMissionControlGroup` = `Mission Control`.
- [V] Mesmos rótulos em `en.lproj/Accessibility.strings`: só `AXRemoveDesktop`, `AXMissionControlGroup`, `AXShowExpose`. `AXAddDesktop` e `AXMissionControlSpacesBarGroup` existem só em en_AU (não em en-US).
- [V] `Applications/Mission Control.app/Contents/Resources/en.lproj/Menu.loctable`: `Show Desktop`; `Show Application Windows`.
- [V] Não encontrado texto visível para o botão "+" (nem "Add Desktop" em en-US). O `+` provavelmente é imagem em `Assets.car` (não decodificado). [I] o rótulo visível do botão não está confirmado.
- [V] Não encontrado "Desktop 1" literal: só o formato `Desktop %@`.

## 2. Chaves de defaults (verificação por strings no executável)

Observação: correspondência lexical na string do binário. Não prova que é preferência real, nem o tipo ou o valor padrão.

| Chave pedida | Dock | WindowManager | Situação |
|---|---|---|---|
| mru-spaces | 0 | 0 | [V] ausente. Só existe `mru-spacH` truncado na lista candidata do codex, descartado. |
| expose-group-apps | 2 | 2 | [V] presente nos dois binários (lexical) |
| expose-group-by-app | 0 | 0 | [V] ausente |
| workspaces-auto-swoosh | 2 | 0 | [V] presente só no Dock (lexical) |
| mcx-expose-disabled | 2 | 2 | [V] presente nos dois (lexical) |
| showPlusSpace, showSpacesBarOnDemand | 4 cada | 0 | [V] presentes no Dock (lexical) |
| mru-spaces-changed, expose-animation-duration | 0 | 0 | [V] ausentes |

Símbolos do WindowManager (nomes Swift mangled, [V] existem no binário; semântica [I]):
- `ExposeMode`: `off`, `missionControl`, `appExpose`, `showDesktop`.
- `GroupingBehavior`: `singleApp`, `singleAppWithPromotion`, `allWindows`. Preferência `appGroupingBehavior`.
- `GroupReplacementOrder`: `leastRecentUsed`, `top`.
- Preferências: `enableMissionControl`, `enableAppExpose`, `enableShowDesktop`, `missionControlHotKey`, `enableMissionControlHotKey`, `enableStandardClickToShowDesktop`, `orderAllWindowsLimitFrontSpace`, `missionControlAppIconSize`, `inlineAppExposeIconSize`, `inlineAppExposeMaximumColumnCount`.
- `LayoutState.SpaceProperties`: `stageManagerEnabled`, `strip`. `assignWindows(_:toSpaces:removingFrom:fence:)`.
- Dock (lexical): `enable-spring-load-actions-on-all-items`, `showLaunchAnimations`, `showMissionControlGestureEnabled`, `showAppExposeGestureEnabled`, `wvous-*` (hot corners), `show-space-bindings`, `showAddUserSpaceTarget`, `showsAddUserSpaceTargetOnLeft`.

## 3. Atalhos

- [S] `BaseConhecimento/padroes/atalhos-de-teclado.md` e `componentes/sistema-e-recursos.md`: `⌃↑` Mission Control; `⌃↓` App Exposé; `⌃←`/`⌃→` trocar de Space; `⌃⌘F` tela cheia. Não confrontado no binário. Não há hotkey padrão confirmado no executável (só o nome da preferência `missionControlHotKey`).

## 4. Durações e curvas

- [V] `minerar/codex-2026-10-11/animacoes.json` está vazio (`[]`). Nenhum número extraído.
- [V] `WindowManager` contém `SpringParameters(dampingRatio:response:)` ligado a `DesktopPeekMonitor` (revelar widgets/desktop), não a Spaces/Mission Control. Valores não extraídos.
- Lacuna: nenhuma duração/curva de Mission Control ou troca de Space confirmada.

## 5. Agrupamento de janelas por app

- [V] Símbolos `GroupingBehavior` (singleApp / singleAppWithPromotion / allWindows) e `AppExposeTarget` (bundle/process) no WindowManager.
- [V] Rótulo `Show Application Windows` (Mission Control.app).
- [I] Padrão provável: App Exposé mostra só janelas do app; o modo `allWindows` é o Mission Control. Não confirmado em runtime.

## 6. Arrastar janela para a faixa de Spaces

- [V] Não há texto de runtime descrevendo isso.
- [V] Símbolo `assignWindows(... toSpaces ... removingFrom ...)` no WindowManager sugere API de atribuição de janelas a Spaces.
- [I] Arrastar para a faixa provavelmente cria/atribui Space; não confirmado.
- Lacuna: nenhuma evidência de comportamento de arraste (MSC-04 em `LISTA-DE-DESEJOS.md` está A_VERIFICAR).

## 7. Faixa de Spaces: recolhida/expandida

- [V] Só os rótulos de acessibilidade existem. Não há estados nomeados "recolhida"/"expandida" nas strings.
- [I] Nenhum dado de estado de altura da faixa.

## 8. Frames e transcrição

- [V] `BaseConhecimento/video/frames-meta.json` (206 entradas): zero ocorrências de mission/spaces/expos/desktop/workspace nos metadados.
- [V] `BaseConhecimento/video/transcripr.txt`: nenhuma ocorrência de Mission Control ou Spaces (só "desktop" genérico).
- Lacuna: nenhum frame com Mission Control catalogado.

## 9. Fontes secundárias e registros

- [S] `BaseConhecimento/referencias/pdfs/tahoe-course-companion.txt` linhas ~301–360: "Open Mission Control with Control-Up Arrow to see all visible windows"; "Mission Control does not show hidden or minimized windows"; "Add multiple desktops in Mission Control with the plus button at the top". Fonte secundária, sem número de versão.
- [S] `BaseConhecimento/LISTA-DE-DESEJOS.md` MSC-01..10: todos NAO_AVALIADO. MSC-02 (animação contínua) e MSC-03/04 (miniaturas, arraste entre Spaces) são requisitos, não evidência.
- [S] `BaseConhecimento/ferramentas/consultar.py` "mission control" retornou registro `tahoe26:cores:paleta-compartilhada` (cores de destaque compartilhadas com Mission Control), status experimental; não usado como fato de Spaces.
- Registros `tahoe26:apps:*` não foram usados, conforme alerta.

## Lacunas (resumo)

1. Rótulo visível exato do botão "+" e da faixa de Spaces (possível imagem em Assets.car, não decodificada).
2. Estados de faixa recolhida/expandida.
3. Valores padrão e tipos das chaves de defaults (mru-spaces ausente; expose-group-apps, mcx-expose-disabled, workspaces-auto-swoosh, showPlusSpace presentes só lexicalmente).
4. Durações e curvas (animacoes.json vazio; sem SpringParameters de Spaces).
5. Comportamento de arraste para a faixa.
6. Nenhum frame de Mission Control no vídeo catalogado.
7. Atalhos padrão só têm fonte secundária do próprio projeto.

## Caminhos de origem

- /home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/mnt/root/System/Library/CoreServices/Dock.app/
- /home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/mnt/root/System/Library/CoreServices/WindowManager.app/
- /home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/mnt/root/System/Applications/Mission Control.app/
- /home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/minerar/codex-2026-10-11/ (defaults/com.apple.dock.json, defaults/com.apple.WindowManager.json, animacoes.json, progresso.json)
- /home/igor/Projects/hyprmac/BaseConhecimento/video/frames-meta.json, video/transcripr.txt
