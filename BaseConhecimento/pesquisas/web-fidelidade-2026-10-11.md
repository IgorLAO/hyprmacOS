# Pesquisa web: referências para fidelidade ao macOS Tahoe 26

Data: 2026-10-11. Somente leitura. Nenhum arquivo do projeto foi alterado.
Legenda de utilidade: **alta** / **média** / **baixa**. Atividade: o que foi possível confirmar na página do repositório; quando a página não mostra data de commit, está indicado.

---

## Frente 1: Liquid Glass / refração em compositores e shaders

### hyprglass (hyprnux)
- URL: https://github.com/hyprnux/hyprglass
- O que oferece: plugin de Hyprland que já faz o que o nosso plugin faz. Desfoque gaussiano em duas passadas (1 a 5 iterações, `blur_strength` × 12 px). Máscara por campo de altura SDF nas janelas (interior 1.0, cai a 0.0 na borda, largura `edge_thickness`). Refração pelo gradiente do campo de altura, com escalas diferentes por canal RGB (aberração cromática), lente central, Fresnel (Schlick) e brilho especular. Em layers, a máscara segue o alfa do conteúdo ou a região do protocolo `ext-background-effect-v1`.
- Licença: BSD-3-Clause (confirmado na página).
- Atividade: 213 commits na main; data do último commit não apareceu na página. Ver também o nosso próprio plugin hyprglass, que deve ser comparado com este.
- Utilidade: **alta**. É a referência direta de arquitetura do que o nosso compositor precisa (máscara por SDF e aberração cromática). Vale comparar parâmetros com a curva medida da Central (memória `vidro-central-curva`).

### LiquidGlass (OverShifted)
- URL: https://github.com/OverShifted/LiquidGlass
- O que oferece: squircle com shader que aproxima SDF para emular refração, somado a desfoque, ruído e brilho. Parâmetros não detalhados na página.
- Licença: MIT.
- Atividade: 10 commits no total. Projeto pequeno.
- Utilidade: **média**. Bom para estudar a forma do squircle em GLSL, sem substituir o hyprglass.

### liquid-glass-studio (iyinchao)
- URL: https://github.com/iyinchao/liquid-glass-studio
- O que oferece: engine WebGL2/WebGPU com formas superelípticas e fusão suave de formas por SDF. Útil para validar matemática de squircle e união de formas.
- Licença e atividade: não verificadas.
- Utilidade: **média**. Referência matemática de SDF, não de compositor.

### archisvaze/liquid-glass e naughtyduk/liquidGL
- URLs: https://github.com/archisvaze/liquid-glass , https://github.com/naughtyduk/liquidGL
- O que oferecem: demos de refração por GLSL em WebGL (Three.js e biblioteca leve para DOM). Sem SDF de squircle.
- Utilidade: **baixa**. Úteis apenas como demo rápida de `refract()`.

### liquid-glass-js (npm)
- URL: https://cdn.jsdelivr.net/npm/liquid-glass-js@0.1.0/README.md
- O que oferece: abordagem por `feDisplacementMap` (SVG), não por shader.
- Utilidade: **baixa**. Não serve ao compositor. Pode servir como comparação visual de deslocamento.

### Nota de método
- Apple não publica números de índice de refração, intensidade especular ou parâmetros de shader. A busca pela sessão WWDC25 219 ("Meet Liquid Glass") não trouxe valores numéricos. Os valores precisam continuar sendo medidos na referência, como já é regra do projeto.

---

## Frente 2: Decorações de janela estilo macOS

### hyprbars (hyprwm/hyprland-plugins)
- URL: https://github.com/hyprwm/hyprland-plugins (plugin hyprbars)
- O que oferece: barra de título em janelas, com altura, cor e fonte configuráveis. Permite criar botões como elementos da barra (fechar, minimizar, maximizar). Não há preset de semáforo macOS.
- Licença: BSD-3-Clause (repo oficial hyprwm). Instalação oficial só por `hyprpm`.
- Atividade: pacotes atualizados em distros (0.53 e 0.55), então acompanha o Hyprland.
- Utilidade: **média**. Serve de base para os botões de semáforo, mas o nosso projeto já tem decoração própria; só vale se for usar a barra do próprio plugin.

### Aurorae (KDE)
- URL: https://invent.kde.org/plasma/aurorae (engine); referência de tema: https://git.org.ru/Katana_mirror/kde-workspace (theme-description)
- O que oferece: engine de decoração do KWin com temas em SVG (decoração + botões, estado ativo e inativo). Não encontramos tema macOS público nesta busca.
- Licença: LGPL (engine KDE, não verificado na página).
- Utilidade: **baixa** para nós, já que não rodamos KWin. Útil apenas se quiséssemos formato de tema SVG como referência.

---

## Frente 3: Temas GTK / Qt estilo macOS Tahoe

### MacTahoe GTK theme (vinceliuice)
- URL: https://github.com/vinceliuice/MacTahoe-gtk-theme
- O que oferece: tema GTK 2/3/4 declarado como "macOS Tahoe like", baseado no WhiteSur. Variantes: claro/escuro (`-c`), acentos (`-t`: blue, purple, pink, red, orange, yellow, green, grey), opacidade normal/solid (`-o`), botões normal/alt/all (`-a`), esquema standard/nord (`-s`). Variante `-b` (blur) mais transparente, que exige a extensão Blur My Shell. Não menciona Liquid Glass.
- Licença: MIT (confirmado, COPYING no repo).
- Atividade: 190 commits, sem release publicada. Um resumo de terceiros cita último push em 20/02/2026, não confirmado na página.
- Utilidade: **alta**. É o tema GTK mais próximo do Tahoe encontrado. Estudar o SCSS (medidas de raio, cor de botão, sombra) e comparar com as nossas medidas do GTK3. Não copiar sem cuidado com a licença MIT (manter o aviso).

### MacTahoe icon theme (vinceliuice)
- URL: https://github.com/vinceliuice/MacTahoe-icon-theme
- O que oferece: tema de ícones companheiro do GTK, com pasta `cursors` (cursor MacTahoe).
- Licença: não verificada.
- Utilidade: **média** para ícones. **Atenção:** o cursor está em conflito com a regra do usuário (manter o cursor do Linux, breeze_cursors). Não usar o cursor.

### WhiteSur GTK theme (vinceliuice)
- URL: https://github.com/vinceliuice/WhiteSur-gtk-theme
- O que oferece: versão anterior (Big Sur). Base do MacTahoe. Útil para comparar o histórico de medidas.
- Licença: MIT (confirmada por empacotadores; upstream não aberto diretamente).
- Utilidade: **média**. Base de código, não do Tahoe.

### Colloid GTK theme (vinceliuice)
- URL: https://github.com/vinceliuice/Colloid-gtk-theme
- O que oferece: tema GTK com variantes de cor e tamanho (standard/compact). Não encontramos variante Tahoe.
- Licença e atividade: não verificadas.
- Utilidade: **baixa** para Tahoe. Pode servir para comparar a estrutura de tema de tamanho compacto.

---

## Frente 4: Dock, Mission Control, Spotlight, Control Center, Notification Center

### nwg-dock-hyprland
- URL: https://github.com/nwg-piotr/nwg-dock-hyprland
- O que oferece: dock configurável escrito em Go para Hyprland. Não se apresenta como macOS, mas aceita CSS, o que permite aproximar o visual. Rodar de novo mata a instância existente, o que facilita alternar.
- Licença e atividade: não verificadas nesta busca (pacotes em Arch 0.3 e Arch ARM 0.4.5, indicando projeto mantido).
- Utilidade: **média**. Alternativa de dock se quisermos remover o dock próprio, mas o projeto já tem o dock em GTK3 e não há ganho claro.

### hyprexpo (hyprwm/hyprland-plugins)
- URL: https://github.com/hyprwm/hyprland-plugins
- O que oferece: visão geral de workspaces (overview) pelo plugin oficial, com opções de personalização. Há relato de bug de tela preta ao sair do overview (NixOS Discourse).
- Licença: BSD-3-Clause.
- Utilidade: **média**. Referência de comportamento do Mission Control, mas o projeto já tem pesquisa separada de Mission Control (agente pesquisa-mission-control). Não duplicar.

### Hyprspace (KZDKM)
- URL: https://github.com/KZDKM/Hyprspace
- O que oferece: visão de workspaces inspirada no KDE e no macOS, com controles de mouse, multi-monitor e arrastar janelas entre workspaces. Fork em https://github.com/0xl30/Hyprspace.
- Licença: GPL-2.0.
- Atividade: mantido, mas com manutenção reduzida (o autor reconhece pouco tempo; 79 issues e 11 PRs abertos). Requer Hyprland 0.55+ pela documentação.
- Utilidade: **média**. Mais próximo do Mission Control que o hyprexpo. Confirmar compatibilidade com Hyprland 0.56 antes de qualquer uso, e lembrar que GPL-2.0 não pode ser misturado sem cuidado ao código do projeto.

### animaios/ui (vibepanel) PR #1
- URL: https://github.com/animaios/ui/pull/1
- O que oferece: dock macOS para Hyprland (Rust, vibepanel), com auto-hide: some quando o mouse sai e reaparece ao encostar na borda inferior. Referência de comportamento.
- Licença e atividade: não verificadas.
- Utilidade: **média**. Referência de comportamento de auto-hide do dock; não é código Astal/AGS.

### Matshell (Neurarian)
- URL: https://gitblind.noratr.app/Neurarian/matshell (espelho; buscar o repo original)
- O que oferece: shell GTK4 em AGS/Astal, Material Design, com ambição "MacOS-esque" e barra de status. Visual Material, não macOS.
- Utilidade: **baixa** para fidelidade. Útil apenas como exemplo de arquitetura AGSv3.

### colorshell (Retrozinn/Olivier)
- URL: https://git.chiasson.cloud/Olivier/colorshell
- O que oferece: shell Astal/AGS com barra superior (botão de apps, workspace, janela focada, relógio). Trabalho em andamento, sem dock nos resultados.
- Utilidade: **baixa**.

---

## Frente 5: Ícones, cursores, fontes e símbolos

### SF Symbols convertidos (buzap/open-symbols)
- URL: https://gittrend.io/repo/buzap/open-symbols
- O que oferece: ícones de conjuntos abertos convertidos para o formato SF Symbols. Visual não é Apple, mas é um caminho para símbolos compatíveis.
- Licença: não verificada (checar antes de usar). 222 estrelas.
- Utilidade: **média**. Pode ajudar a fechar a lacuna de símbolos, mas verificar licença antes.

### Remix Icon
- URL: não buscado diretamente; citado em resultados de busca.
- O que oferece: conjunto de ícones neutros com estilo outline e filled. Descrito como gratuito para uso pessoal e comercial. Não imita Apple.
- Licença: Apache-2.0 (conhecimento prévio, não confirmado nesta busca).
- Utilidade: **baixa** para fidelidade; útil apenas como fallback.

### Cursores estilo macOS (WhiteSur cursors, McMojave cursors, MacTahoe cursor)
- URLs: https://gitea.soloconlinux.org.es/luisgulo/WhiteSur-cursors , https://joel-lenovo.alcancelibre.org/aldos/1.4/source/repoview/mcmojave-cursor-theme.html
- O que oferecem: cursores macOS em X (WhiteSur é Big Sur, McMojave é GPLv3+).
- Utilidade: **baixa, e bloqueada pela regra do usuário**. A memória do projeto diz para nunca trocar o cursor (breeze_cursors; hyprmac-cursors foi desativado a pedido). Não recomendar.

### Fontes SF
- SF Pro e SF Symbols têm licença restrita da Apple. Nenhum uso ou redistribuição deve ser feito. Só serve como referência de métricas.
- Não foi buscada fonte alternativa livre nesta rodada. Próxima busca sugerida: Inter (OFL) para comparar métricas de texto.

---

## Frente 6: Referências de design

### Apple Design Resources (macOS Tahoe 26)
- URL: https://developer.apple.com/design/resources
- O que oferece: kit Sketch "macOS Tahoe 26 Sketch Library" (cerca de 106,5 MB, segundo listagem de download) e "iOS 26, iPadOS 26 e macOS Tahoe 26". Para Figma, há kit de UI do iOS 26/iPadOS 26 e o template de ícone de app. Não confirmamos um kit Figma de UI do macOS Tahoe 26. Há também recursos do macOS 27 (ainda só Sketch para o kit de UI, segundo as notícias).
- Licença: termos de uso da Apple para recursos de design (uso para desenvolver apps). Não redistribuir.
- Utilidade: **alta**. É a fonte oficial de medidas de componentes. Abrir o Sketch exige ferramenta de leitura; conferir com o arquivo de referência do projeto antes de baixar algo.

### WWDC25 sessão 219 "Meet Liquid Glass"
- URL: https://developer.apple.com/videos/play/wwdc2025/219/ ; índice com transcrição: https://nonstrict.eu/wwdcindex/wwdc2025/219/
- O que oferece: princípios, propriedades ópticas (refração, reflexão especular, lente nas bordas, tempo real). Sem valores numéricos nas buscas.
- Utilidade: **alta** para entender o comportamento. Os números têm que vir de medição na referência.

### Adopting Liquid Glass (documentação)
- URL: link a partir da sessão 219 no developer.apple.com.
- Utilidade: **média**. Regras de uso, não parâmetros.

---

## Frente 7: Engenharia reversa de assets macOS

### acextract (bartoszj)
- URL: https://github.com/bartoszj/acextract
- O que oferece: extração de `Assets.car` com `-i` (entrada), `-o` (saída) e `-l` (listar). Lê tamanhos, slices, classes de memória e gráficos. PDF aparece como não suportado na tabela, mesmo com texto dizendo o contrário; testar antes.
- Licença: MIT.
- Atividade: 47 commits; último push informado por terceiros em 2022 (sem release).
- Utilidade: **alta**. Ponto de partida para extrair PNG do Tahoe, mas pode precisar de patch para catálogos mais novos.

### iOS-Asset-Extractor (Marxon13)
- URL: https://github.com/Marxon13/iOS-Asset-Extractor
- O que oferece: extração de PNG, PDF e CAR, com executável companheiro CARExtractor.
- Licença e atividade: não verificadas.
- Utilidade: **média**. Alternativa se acextract falhar em Tahoe.

### pcjbird/AssetsExtractor
- Descrição: ferramenta para PNG e PDF de Assets.car em OS X. Último push há cerca de seis anos (segundo listagem).
- Utilidade: **baixa**. Abandonado.

### cartool
- Não encontrado nas buscas. Não recomendado sem confirmação.

### Ponto de atenção
- Extrair assets do Tahoe exige um Assets.car real. O projeto já tem material privado extraído do IPSW (memória `pesquisa-ipsw-macos26`). Usar essas ferramentas sobre esse material, não baixar IPSW de terceiros.

---

## Top 12 achados (ordem de utilidade)

1. hyprglass (hyprnux), https://github.com/hyprnux/hyprglass: referência de máscara SDF, refração e aberração cromática. BSD-3.
2. MacTahoe GTK theme, https://github.com/vinceliuice/MacTahoe-gtk-theme: tema GTK mais próximo do Tahoe, MIT, medidas em SCSS.
3. Apple Design Resources, https://developer.apple.com/design/resources: medidas oficiais de componentes (kit Sketch do macOS Tahoe 26).
4. WWDC25 sessão 219, https://developer.apple.com/videos/play/wwdc2025/219/: comportamento oficial do Liquid Glass.
5. acextract, https://github.com/bartoszj/acextract: extração de Assets.car, MIT.
6. LiquidGlass (OverShifted), https://github.com/OverShifted/LiquidGlass: squircle com SDF em GLSL, MIT.
7. Hyprspace, https://github.com/KZDKM/Hyprspace: visão de workspaces estilo Mission Control, GPL-2.0, manutenção reduzida.
8. hyprbars, https://github.com/hyprwm/hyprland-plugins: barra de título e botões de janela, BSD-3.
9. animaios/ui PR #1, https://github.com/animaios/ui/pull/1: dock estilo macOS com auto-hide, referência de comportamento.
10. nwg-dock-hyprland, https://github.com/nwg-piotr/nwg-dock-hyprland: dock configurável por CSS.
11. iOS-Asset-Extractor, https://github.com/Marxon13/iOS-Asset-Extractor: alternativa de extração.
12. liquid-glass-studio, https://github.com/iyinchao/liquid-glass-studio: matemática de SDF e squircle em WebGL.

## Descartados
- Aurorae: não usamos KWin.
- pcjbird/AssetsExtractor: abandonado há cerca de seis anos.
- Cursores macOS (WhiteSur, McMojave, MacTahoe cursor): conflitam com a regra de manter o cursor do Linux.
- liquid-glass-js (SVG): não é shader.
- Matshell, colorshell: Material ou WIP, sem valor de fidelidade.

## Lacunas não cobertas
- Licenças não verificadas: MacTahoe icon theme, Colloid, nwg-dock-hyprland, hyprexpo (é BSD-3 pelo repo oficial), open-symbols.
- Sem valores numéricos de Liquid Glass em fonte pública. Medir na referência.
- Fonte livre equivalente a SF Pro: não buscada.
