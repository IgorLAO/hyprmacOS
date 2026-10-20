-- hyprmac — aparência macOS Tahoe (modo escuro) para Hyprland
-- Carregado no fim do hyprland.lua; tudo aqui sobrescreve os padrões de lá.

local home = os.getenv("HOME")
local hyprmac = home .. "/Projects/hyprmac"

--------------------------------------------------------------------------
-- Ambiente: apps Qt/KDE seguem o esquema de cores "Hyprmac Tahoe Dark"
--------------------------------------------------------------------------
hl.env("QT_QPA_PLATFORMTHEME", "kde")

-- Cursor: o hyprmac NÃO troca o cursor — fica o do sistema (breeze_cursors)

--------------------------------------------------------------------------
-- Molduras das janelas
--------------------------------------------------------------------------
-- Tahoe: cantos grandes e "contínuos" (squircle), borda de 1px quase
-- invisível que só pega luz, e sombra larga e suave em vez de bordas coloridas.
-- Contorno (kit macOS 27, estilos "Windows/*"): TODA janela tem um filete preto por fora
-- (sombra 0 0 1 #000/0.80); só a escura ATIVA tem ainda o aro interno 1px #FFF/0.20.
-- Medido em tahoe-dark.jpeg (Retina 2×, borda do Finder): 1 px quase preto (0,5 pt)
-- por fora + 2 px a 20 % de branco (1 pt) por dentro. Aqui a 1×:
--   filete = a borda de 1 px, preto/0.50 (o 0,5 pt preto cobrindo meio pixel)
--   aro    = o brilho interno (glow) de 1 px; ele pinta metade da cor no pixel da
--            borda, então #FFF/0.40 dá os 20 % medidos (conferido com grim: 0.200)
-- scripts/theme troca na hora com hyprctl eval.
local function dark_mode()
    local f = io.popen("gsettings get org.gnome.desktop.interface color-scheme 2>/dev/null")
    local v = f and f:read("*a") or ""
    if f then f:close() end
    return v:find("prefer%-dark") ~= nil
end
local DARK = dark_mode()
local border = { active_border = "rgba(00000080)", inactive_border = "rgba(00000080)" }

hl.config({
    general = {
        -- Referência (safari-escuro-barra-de-menus-abas.png): a janela encosta na
        -- barra e nas laterais do monitor, sem margem nenhuma — como no Mac com
        -- "Tiled windows have margins" desligado; por isso 0 entre janelas também.
        -- Embaixo, o Dock reserva o espaço.
        gaps_in     = 0,
        gaps_out    = 0,
        border_size = 1,

        col = border,

        resize_on_border = true,
        extend_border_grab_area = 12,
    },

    decoration = {
        -- Janela com barra de ferramentas do Tahoe: o canto mede ~22 pt na
        -- referência (concêntrico com os controles de 38 pt da barra).
        rounding       = 22,
        rounding_power = 3.2,   -- > 2 = curvatura contínua, como no macOS

        active_opacity   = 1.0,
        inactive_opacity = 1.0,
        dim_inactive     = false,

        -- Kit macOS 27: ativa 0 36 100 preto/40%, inativa 0 16 32 preto/20%.
        -- O Hyprland tem uma sombra só por janela: alcance ~metade do desfoque.
        shadow = {
            enabled        = true,
            range          = 50,
            render_power   = 3,
            sharp          = false,
            offset         = "0 18",
            color          = "rgba(00000066)",
            color_inactive = "rgba(00000033)",
        },

        -- Aro interno de luz (ver "Contorno" acima): só no escuro e só na janela ativa
        glow = {
            enabled        = DARK,
            range          = 1,
            render_power   = 1,
            color          = "rgba(ffffff66)",
            color_inactive = "rgba(ffffff00)",
        },

        -- Vidro: kit macOS 27 → materiais com desfoque 60 e saturação 1.45–1.9
        -- (Regular escuro). size 12 × 3 passes ≈ o mesmo espalhamento; vibrancy
        -- realça a cor do fundo como a saturação do material.
        blur = {
            enabled           = true,
            size              = 12,
            passes            = 3,
            noise             = 0.012,
            contrast          = 0.95,
            brightness        = 0.92,
            vibrancy          = 0.4,
            vibrancy_darkness = 0.2,
            popups            = true,
            new_optimizations = true,
            xray              = false,
        },
    },

    misc = {
        force_default_wallpaper = 0,
        disable_hyprland_logo   = true,
        disable_splash_rendering = true,
        background_color        = 0x0b1f4d,
        -- se a tela de bloqueio morrer, dá para relançá-la (em vez de travar de vez)
        allow_session_lock_restore = true,
        -- como no Mac, mexer o mouse ou teclar acorda a tela apagada (canto ativo "Put
        -- Display to Sleep" e o apagar por inatividade)
        mouse_move_enables_dpms = true,
        key_press_enables_dpms  = true,
    },
})

-- Painéis do hyprmac (Liquid Glass, WWDC25): entram com uma mola curta — nascem um
-- pouco menores e "flexionam" ao chegar — e saem rápido, sem fazer esperar.
-- macPop e a duração (3.2 = 320 ms) são as mesmas do POP_CURVE/POP_MS do hyprmac-shell.
hl.curve("macPop", { type = "bezier", points = { {0.2, 1.08}, {0.32, 1} } })
hl.curve("macOut", { type = "bezier", points = { {0.4, 0},    {1, 1}    } })
hl.animation({ leaf = "layersIn",      enabled = true, speed = 3.2, bezier = "macPop", style = "fade" })
hl.animation({ leaf = "layersOut",     enabled = true, speed = 1.6, bezier = "macOut", style = "fade" })
-- O shader usa o alfa para materializar a lente. Acompanhar os 320 ms da
-- expansão evita o reflexo já rígido aos 180 ms, com a superfície ainda crescendo.
-- Sincronia local; duração nativa pendente de gravação Tahoe equivalente.
hl.animation({ leaf = "fadeLayersIn",  enabled = true, speed = 3.2, bezier = "almostLinear" })
hl.animation({ leaf = "fadeLayersOut", enabled = true, speed = 1.4, bezier = "macOut" })

-- Reduzir Movimento (gsettings enable-animations = false): sem molas nem escalas —
-- os painéis só esmaecem e as mesas trocam com um fade curto
local function reduce_motion()
    local f = io.popen("gsettings get org.gnome.desktop.interface enable-animations 2>/dev/null")
    local v = f and f:read("*a") or ""
    if f then f:close() end
    return v:find("false") ~= nil
end
local RM = reduce_motion()

-- Ajustes ▸ Mouse grava "Tracking speed" e "Natural scrolling" no config.json; reaplica a
-- cada carga (o hyprctl keyword dos Ajustes some no próximo hyprctl reload). Sem a
-- chave, vale o que o hyprland.lua do usuário definiu.
do
    local f = io.open(os.getenv("HOME") .. "/.config/hyprmac/config.json", "r")
    local conf = f and f:read("*a") or ""
    if f then f:close() end
    local input = {}
    local nat = conf:match('"mouse_natural_scroll"%s*:%s*(%a+)')
    if nat == "true" or nat == "false" then input.natural_scroll = (nat == "true") end
    local sens = tonumber(conf:match('"mouse_sensitivity"%s*:%s*(%-?[%d%.]+)'))
    if sens then input.sensitivity = math.max(-1, math.min(1, sens)) end
    if next(input) then hl.config({ input = input }) end
end
local function pop(style) return RM and "fade" or style end

-- Spaces deslizam lateralmente, como no Mission Control
hl.curve("macSlide", { type = "bezier", points = { {0.25, 1}, {0.5, 1} } })
hl.animation({ leaf = "workspaces",    enabled = true, speed = 4.2, bezier = "macSlide", style = "slide" })
hl.animation({ leaf = "workspacesIn",  enabled = true, speed = 4.2, bezier = "macSlide", style = "slide" })
hl.animation({ leaf = "workspacesOut", enabled = true, speed = 4.2, bezier = "macSlide", style = "slide" })
hl.animation({ leaf = "specialWorkspace", enabled = true, speed = 3.5, bezier = "macSlide", style = "slidevert" })
if RM then
    hl.animation({ leaf = "layersIn",      enabled = true, speed = 1.8, bezier = "almostLinear", style = "fade" })
    hl.animation({ leaf = "windowsIn",     enabled = true, speed = 1.8, bezier = "almostLinear", style = "popin 100%" })
    hl.animation({ leaf = "windowsOut",    enabled = true, speed = 1.5, bezier = "almostLinear", style = "popin 100%" })
    hl.animation({ leaf = "windows",       enabled = true, speed = 2.5, bezier = "almostLinear" })
    hl.animation({ leaf = "workspaces",    enabled = true, speed = 2.0, bezier = "almostLinear", style = "fade" })
    hl.animation({ leaf = "workspacesIn",  enabled = true, speed = 2.0, bezier = "almostLinear", style = "fade" })
    hl.animation({ leaf = "workspacesOut", enabled = true, speed = 2.0, bezier = "almostLinear", style = "fade" })
    hl.animation({ leaf = "specialWorkspace", enabled = true, speed = 2.0, bezier = "almostLinear", style = "fade" })
end

--------------------------------------------------------------------------
-- Vidro nas camadas do hyprmac
--------------------------------------------------------------------------
hl.layer_rule({
    name  = "hyprmac-glass",
    match = { namespace = "^hyprmac-widgets$" },
    blur         = true,
    ignore_alpha = 0.1,
})

-- Central de Controle: mesmo vidro da Central de Notificações
-- Brota do ícone na barra (WWDC25: "springs from the action itself"): nasce com 90% e
-- cresce com a mola macPop; o hyprmac-shell move as margens para o ponto de origem
-- ficar parado (o popin do Hyprland escala em torno do centro)
hl.layer_rule({
    name  = "hyprmac-cc-glass",
    match = { namespace = "^hyprmac-cc$" },
    blur         = true,
    -- vidro CLARO do Tahoe: alfa baixo (~0.18) ainda desfoca porque o limiar é baixo.
    -- O fundo da janela é transparente (alfa 0) e fica fora do desfoque — só os blocos.
    ignore_alpha = 0.06,
    animation    = pop("popin 90%"),
})

-- Galeria de Widgets (botão direito na mesa ▸ Edit Widgets…): mesmo vidro, materializa
hl.layer_rule({
    name  = "hyprmac-widget-gallery",
    match = { namespace = "^hyprmac-widget-gallery$" },
    blur         = true,
    ignore_alpha = 0.3,
    animation    = pop("popin 96%"),
})

-- Galeria de Controles (modo de edição), ao lado da Central: materializa no lugar
hl.layer_rule({
    name  = "hyprmac-cc-gallery",
    match = { namespace = "^hyprmac-cc-gallery$" },
    blur         = true,
    ignore_alpha = 0.06,
    animation    = pop("popin 96%"),
})

hl.layer_rule({
    name  = "hyprmac-cc-catcher",
    match = { namespace = "^hyprmac-cc-catcher$" },
    no_anim = true,
})

-- Barra: desfoque atrás do modo "clara fosca" (fundo ~64%) e dos menus.
-- ignore_alpha 0.5 deixa de fora a sombra do texto no modo transparente.
hl.layer_rule({
    name  = "hyprmac-bar",
    match = { namespace = "^waybar$" },
    blur         = true,
    blur_popups  = true,
    ignore_alpha = 0.5,
})

-- Dock (hyprmac-shell): vidro quase sem desfoque, como o "Liquid Glass/Dock" do kit
-- (raio 1) — só o menu de contexto ganha o vidro dos menus.
hl.layer_rule({
    name  = "hyprmac-dock",
    match = { namespace = "^hyprmac-dock$" },
    blur_popups = true,
    ignore_alpha = 0.3,
    no_anim = true,          -- o próprio Dock anima ao se esconder/aparecer
})

hl.layer_rule({
    name  = "hyprmac-dock-trigger",
    match = { namespace = "^hyprmac-dock-trigger$" },
    no_anim = true,
})

-- Menu "Janela" do hyprmac-shell: popups com o mesmo vidro da barra
hl.layer_rule({
    name  = "hyprmac-menu",
    match = { namespace = "^hyprmac-menu$" },
    blur_popups  = true,
    ignore_alpha = 0.2,
    no_anim      = true,
})

-- A barra de captura e o menu Options são vidro próprio: desfocar o conteúdo
-- atrás deles preserva a leitura do texto quando aparecem sobre vídeos.
hl.layer_rule({
    name  = "hyprmac-capture-bar",
    match = { namespace = "^hyprmac-captura-barra$" },
    blur         = true,
    blur_popups  = true,
    ignore_alpha = 0.2,
    no_anim      = true,
})

-- Notificações: banners de vidro (desfoque) deslizando da direita
hl.layer_rule({
    name  = "hyprmac-notifications",
    match = { namespace = "^hyprmac-notifications$" },
    blur         = true,
    ignore_alpha = 0.3,
    animation    = pop("slide right"),
})

-- Central de Notificações (clique no relógio): mesmo vidro, desliza da direita
hl.layer_rule({
    name  = "hyprmac-nc",
    match = { namespace = "^hyprmac-nc$" },
    blur         = true,
    ignore_alpha = 0.3,
    animation    = pop("slide right"),
})

hl.layer_rule({
    name  = "hyprmac-nc-catcher",
    match = { namespace = "^hyprmac-nc-catcher$" },
    no_anim = true,
})

-- Histórico da área de transferência: painel de vidro no centro, como o
-- scratchpad (o fundo esmaecido é a própria camada; < ignore_alpha, sem desfoque)
hl.layer_rule({
    name  = "hyprmac-clipboard",
    match = { namespace = "^hyprmac-clipboard$" },
    blur         = true,
    ignore_alpha = 0.36,   -- o fundo esmaecido (35%) fica fora do desfoque
    animation    = "fade",
})

-- Menus dos extras da barra (Wi‑Fi, Bluetooth, Som) e cápsula de volume/brilho
hl.layer_rule({
    name  = "hyprmac-extras",
    match = { namespace = "^hyprmac-extras$" },
    blur         = true,
    ignore_alpha = 0.3,
    animation    = pop("popin 90%"),  -- brota do ícone (POP_FROM do shell)
})

hl.layer_rule({
    name  = "hyprmac-extras-catcher",
    match = { namespace = "^hyprmac-extras-catcher$" },
    no_anim = true,
})

hl.layer_rule({
    name  = "hyprmac-osd",
    match = { namespace = "^hyprmac-osd$" },
    blur         = true,
    ignore_alpha = 0.3,
    animation    = "fade",
})

-- Mission Control: anima as próprias janelas; fade da camada duplicaria o quadro
hl.layer_rule({
    name    = "hyprmac-overview",
    match   = { namespace = "^hyprmac-overview$" },
    no_anim = true,
})

-- Miniatura flutuante da captura de tela: entra deslizando pela direita
hl.layer_rule({
    name  = "hyprmac-captura",
    match = { namespace = "^hyprmac-captura$" },
    animation = pop("slide right"),
})

-- Player (clique no nome da música na barra): mesmo vidro, surge abaixo da barra
hl.layer_rule({
    name  = "hyprmac-media",
    match = { namespace = "^hyprmac-media$" },
    blur         = true,
    ignore_alpha = 0.3,
    animation    = pop("popin 90%"),  -- brota do ícone (POP_FROM do shell)
})

hl.layer_rule({
    name  = "hyprmac-media-catcher",
    match = { namespace = "^hyprmac-media-catcher$" },
    no_anim = true,
})

-- Alt+Tab: mesmo vidro, aparece/some com um fade rápido
hl.layer_rule({
    name  = "hyprmac-switcher",
    match = { namespace = "^hyprmac-switcher$" },
    blur         = true,
    ignore_alpha = 0.3,
    animation    = "fade",
})

-- Spotlight (hyprmac-shell): a camada cobre a tela (clique fora fecha), então o
-- desfoque fica só onde o vidro é opaco o bastante (ignore_alpha acima da sombra)
-- e entra esmaecendo — um popin escalaria a tela inteira e deslocaria o campo.
hl.layer_rule({
    name  = "hyprmac-spotlight",
    match = { namespace = "^hyprmac-spotlight$" },
    blur         = true,
    ignore_alpha = 0.35,
    animation    = "fade",
})

-- wofi (reserva do Spotlight sem o hyprmac-shell e confirmações)
hl.layer_rule({
    name  = "hyprmac-wofi",
    match = { namespace = "^wofi$" },
    blur         = true,
    ignore_alpha = 0.1,
    animation    = pop("popin 94%"),
})

--------------------------------------------------------------------------
-- Janelas
--------------------------------------------------------------------------
-- "Sobre este computador" (ghostty com fastfetch, aberto pelo menu )
hl.window_rule({
    name  = "hyprmac-about",
    match = { class = "^dev\\.hyprmac\\.about$" },
    float  = true,
    size   = "760 460",
    center = true,
})

-- Ajustes do Sistema (shell/hyprmac-ajustes): flutua no centro com o tamanho e o raio
-- da "Window" do kit macOS 27 (756 de largura = lateral 256 + formulário 460 + 2×20). O kit
-- pede raio 26, mas a regra de janela do Hyprland 0.56 aceita no máximo 20: fica o 22 global.
hl.window_rule({
    name  = "hyprmac-settings",
    match = { class = "^dev\\.hyprmac\\.Settings$" },
    float    = true,
    size     = "756 660",
    center   = true,
})

-- A App Factory owns only these new IDs. Existing app rules stay untouched.
for _, app in ipairs(dofile(hyprmac .. "/hypr/app-factory-classes.lua")) do
    hl.window_rule({
        name  = "hyprmac-factory-" .. app,
        match = { class = "^dev\\.hyprmac\\." .. app .. "$" },
        float = true,
        center = true,
    })
end

-- Janela de senha de rede/VPN do hyprmac-shell
hl.window_rule({
    name  = "hyprmac-agent",
    match = { class = "^hyprmac-shell$" },
    float  = true,
    center = true,
    pin    = true,
})

-- Diálogos pequenos flutuam centralizados, como folhas do macOS
hl.window_rule({
    name  = "hyprmac-dialogs",
    match = { class = "^(pavucontrol|org\\.pulseaudio\\.pavucontrol|nm-connection-editor|blueman-manager|\\.blueman-manager-wrapped)$" },
    float  = true,
    size   = "860 560",
    center = true,
})

--------------------------------------------------------------------------
-- Jogos: menos latência em tela cheia
--------------------------------------------------------------------------
-- tearing = frame vai direto pra tela sem esperar o vsync do compositor
-- direct_scanout 2 = em tela cheia, o jogo (content "game") pula a composição
-- (é o "unredirect" que o GNOME faz por padrão)
-- vrr 0 = FreeSync desligado: no AOC via HDMI o VRR fazia o monitor piscar
-- ao entrar em tela cheia (CS2 roda bem acima de 75 fps, então não faz falta)
hl.config({
    general = { allow_tearing = true },
    render  = { direct_scanout = 2 },
    misc    = { vrr = 0 },
})

hl.window_rule({
    name  = "hyprmac-games",
    match = { class = "^(cs2|steam_app_.*)$" },
    immediate = true,
    content   = "game",
})

--------------------------------------------------------------------------
-- Tela cheia (⌘F)
--------------------------------------------------------------------------
hl.bind("SUPER + F", hl.dsp.window.fullscreen({ mode = "fullscreen" }))

-- Recarrega o shell HyprMac sem reiniciar a sessão ou o compositor.
hl.unbind("SUPER + F5")
hl.bind("SUPER + F5", hl.dsp.exec_cmd(hyprmac .. "/shell/hyprmac-shell reload"))

--------------------------------------------------------------------------
-- Recuperação leve (Super+F8): redesenha sem depender do IPC do hyprctl.
-- A recarga da configuração roda fora do compositor e tem tempo limitado.
-- Um congelamento total do Hyprland também impede o processamento do atalho.
--------------------------------------------------------------------------
hl.unbind("SUPER + F8")
hl.bind("SUPER + F8", function()
    hl.dispatch(hl.dsp.force_renderer_reload())
    hl.dispatch(hl.dsp.exec_cmd("timeout --kill-after=1s 5s hyprctl reload"))
end)

--------------------------------------------------------------------------
-- Scratchpad (área especial "magic"): guardar a janela a esconde
-- (follow = false; sem isso o scratchpad abria junto e parecia que nada mudava)
-- e mostrar com ele vazio avisa como usar, em vez de não fazer nada.
--------------------------------------------------------------------------
-- No scratchpad as janelas ficam menores (60%), centralizadas e na frente de tudo,
-- com o resto da tela esmaecido atrás — não em tela cheia.
hl.config({
    dwindle = { special_scale_factor = 0.6 },
    master  = { special_scale_factor = 0.6 },
    decoration = { dim_special = 0.25 },
})

hl.unbind("SUPER + S")
hl.unbind("SUPER + SHIFT + S")
hl.bind("SUPER + S",         hl.dsp.exec_cmd(hyprmac .. "/scripts/scratchpad"))
hl.bind("SUPER + SHIFT + S", hl.dsp.window.move({ workspace = "special:magic", follow = false }))

--------------------------------------------------------------------------
-- Atalhos do macOS (⌘ = Super). Substituem os do hyprland.lua que brigavam
-- com o reflexo do Mac: Super+M encerrava a sessão e Super+Q abria o terminal.
--------------------------------------------------------------------------
local janela = home .. "/.local/bin/hyprmac-janela"
hl.unbind("SUPER + M")
hl.unbind("SUPER + Q")
-- Minimizar para o Dock (⌘M): o shell calcula o ícone de destino e pede o Genie ao hyprglass
-- (hypr/hyprglass/genie.patch); sem shell, move direto para a área "minimized"
hl.bind("SUPER + M", hl.dsp.exec_cmd("gdbus call --session --dest dev.hyprmac.Shell "
    .. "--object-path /dev/hyprmac/Shell --method dev.hyprmac.Shell.Command minimize >/dev/null "
    .. "|| hyprctl dispatch 'hl.dsp.window.move({ workspace = \"special:minimized\", follow = false })'"))
hl.bind("SUPER + Q",          hl.dsp.exec_cmd(janela .. " quit-app"))      -- Sair do app
hl.bind("SUPER + W",          hl.dsp.window.close())                       -- Fechar janela (Super+C continua)
hl.bind("SUPER + H",          hl.dsp.exec_cmd(janela .. " hide-app"))      -- Ocultar app
hl.bind("SUPER + ALT + H",    hl.dsp.exec_cmd(janela .. " hide-others"))   -- Ocultar os outros
hl.bind("SUPER + grave",        hl.dsp.exec_cmd(janela .. " next-window"))   -- ⌘` próxima janela do app
hl.bind("SUPER + SHIFT + grave", hl.dsp.exec_cmd(janela .. " prev-window"))  -- ⇧⌘` anterior
-- Navegação por teclado (HIG ▸ Keyboards): ⌃F4 / ⌃⇧F4 foco na próxima/anterior janela de
-- qualquer app; ⌃F3 foco no Dock (setas, Return, Esc)
hl.bind("CTRL + F4",          hl.dsp.exec_cmd(janela .. " next-any"))
hl.bind("CTRL + SHIFT + F4",  hl.dsp.exec_cmd(janela .. " prev-any"))
hl.bind("CTRL + F3",          hl.dsp.exec_cmd("gdbus call --session --dest dev.hyprmac.Shell "
    .. "--object-path /dev/hyprmac/Shell --method dev.hyprmac.Shell.Command dock-focus >/dev/null"))
hl.bind("SUPER + CTRL + F",   hl.dsp.window.fullscreen({ mode = "fullscreen" }))  -- Tela cheia (⌃⌘F)
-- Forçar Encerrar: a janela com a lista de apps, como o ⌥⌘Esc do Mac
hl.bind("SUPER + ALT + Escape", hl.dsp.exec_cmd("gdbus call --session --dest dev.hyprmac.Shell "
    .. "--object-path /dev/hyprmac/Shell --method dev.hyprmac.Shell.Command force-quit"))
hl.bind("SUPER + Return",     hl.dsp.exec_cmd("ghostty"))                  -- terminal (era Super+Q)
hl.bind("SUPER + CTRL + Q",   hl.dsp.exec_cmd(hyprmac .. "/shell/hyprmac-lock"))  -- Bloquear Tela (⌃⌘Q)
hl.bind("SUPER + ALT + D",    hl.dsp.exec_cmd(hyprmac .. "/shell/hyprmac-shell dock-autohide"))  -- Ocultar/Mostrar o Dock (⌥⌘D)
hl.bind("CTRL + Up",          hl.dsp.exec_cmd(hyprmac .. "/shell/hyprmac-overview toggle"))  -- Mission Control (⌃↑)
hl.bind("CTRL + Down",        hl.dsp.exec_cmd(hyprmac .. "/shell/hyprmac-overview app"))     -- App Exposé (⌃↓)

--------------------------------------------------------------------------
-- Spotlight (⌘ Espaço): abre, ou fecha se já estiver aberto
--------------------------------------------------------------------------
local spotlight = hyprmac .. "/scripts/spotlight"
hl.bind("SUPER + space", hl.dsp.exec_cmd(spotlight))
-- Super+Shift+V: abre/fecha o histórico da área de transferência direto no
-- hyprmac-shell (no Tahoe também dá para chegar por ⌘Espaço e depois ⌘4)
hl.bind("SUPER + SHIFT + V", hl.dsp.exec_cmd(
    "gdbus call --session --dest dev.hyprmac.Shell --object-path /dev/hyprmac/Shell "
    .. "--method dev.hyprmac.Shell.Command toggle-clipboard"))

-- Com o Spotlight aberto (o script entra neste submap e sai ao fechar):
-- Super+1 = apps, Super+2 = arquivos, Super+3 = ações, Super+4 = histórico da
-- área de transferência, como ⌘1–⌘4 no Tahoe.
-- As outras teclas seguem para o campo GTK do Spotlight.
hl.define_submap("spotlight", function ()
    hl.bind("SUPER + space", hl.dsp.exec_cmd(spotlight))
    hl.bind("SUPER + 1",     hl.dsp.exec_cmd(spotlight .. " mode apps"))
    hl.bind("SUPER + 2",     hl.dsp.exec_cmd(spotlight .. " mode files"))
    hl.bind("SUPER + 3",     hl.dsp.exec_cmd(spotlight .. " mode actions"))
    hl.bind("SUPER + 4",     hl.dsp.exec_cmd(spotlight .. " mode clipboard"))
end)

--------------------------------------------------------------------------
-- Alt+Tab como o ⌘Tab do macOS (seletor de apps do hyprmac-shell)
--------------------------------------------------------------------------
local shell_cmd = "gdbus call --session --dest dev.hyprmac.Shell --object-path /dev/hyprmac/Shell "
               .. "--method dev.hyprmac.Shell.Command "
hl.bind("ALT + Tab",         hl.dsp.exec_cmd(shell_cmd .. "switcher-next"))
hl.bind("ALT + SHIFT + Tab", hl.dsp.exec_cmd(shell_cmd .. "switcher-prev"))
-- ⌘Tab = Super+Tab (HIG ▸ Keyboards). Aberto por Super, o seletor entra no submap
-- "switcher": ⌘Q/⌘H agem no app selecionado (e não no app em foco), como no Mac.
hl.bind("SUPER + Tab",         hl.dsp.exec_cmd(shell_cmd .. "'switcher-next super'"))
hl.bind("SUPER + SHIFT + Tab", hl.dsp.exec_cmd(shell_cmd .. "'switcher-prev super'"))
hl.define_submap("switcher", function ()
    hl.bind("SUPER + Tab",         hl.dsp.exec_cmd(shell_cmd .. "'switcher-next super'"))
    hl.bind("SUPER + SHIFT + Tab", hl.dsp.exec_cmd(shell_cmd .. "'switcher-prev super'"))
    hl.bind("SUPER + Q",           hl.dsp.exec_cmd(shell_cmd .. "switcher-quit"))
    hl.bind("SUPER + H",           hl.dsp.exec_cmd(shell_cmd .. "switcher-hide"))
end)

--------------------------------------------------------------------------
-- Volume e brilho: como no Tahoe, o controle "se expande" na barra (cápsula
-- de vidro sob o ícone de som). Substituem os binds do hyprland.lua.
--------------------------------------------------------------------------
for _, k in ipairs({ "XF86AudioRaiseVolume", "XF86AudioLowerVolume", "XF86AudioMute",
                     "XF86MonBrightnessUp", "XF86MonBrightnessDown" }) do hl.unbind(k) end
local osd_vol = " && " .. shell_cmd .. "'osd volume'"
hl.bind("XF86AudioRaiseVolume", hl.dsp.exec_cmd("wpctl set-volume -l 1 @DEFAULT_AUDIO_SINK@ 5%+" .. osd_vol), { locked = true, repeating = true })
hl.bind("XF86AudioLowerVolume", hl.dsp.exec_cmd("wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%-" .. osd_vol),      { locked = true, repeating = true })
hl.bind("XF86AudioMute",        hl.dsp.exec_cmd("wpctl set-mute @DEFAULT_AUDIO_SINK@ toggle && " .. shell_cmd .. "'osd volume mute'"), { locked = true })
-- ⇧ + tecla de volume inverte "Play feedback when volume is changed", como no Mac
local osd_vol_shift = " && " .. shell_cmd .. "'osd volume shift'"
hl.bind("SHIFT + XF86AudioRaiseVolume", hl.dsp.exec_cmd("wpctl set-volume -l 1 @DEFAULT_AUDIO_SINK@ 5%+" .. osd_vol_shift), { locked = true, repeating = true })
hl.bind("SHIFT + XF86AudioLowerVolume", hl.dsp.exec_cmd("wpctl set-volume @DEFAULT_AUDIO_SINK@ 5%-" .. osd_vol_shift),      { locked = true, repeating = true })
-- brilho por DDC/CI no próprio shell (monitores externos; não há brightnessctl)
hl.bind("XF86MonBrightnessUp",   hl.dsp.exec_cmd(shell_cmd .. "'brightness up'"),   { locked = true, repeating = true })
hl.bind("XF86MonBrightnessDown", hl.dsp.exec_cmd(shell_cmd .. "'brightness down'"), { locked = true, repeating = true })

--------------------------------------------------------------------------
-- Capturas de tela (tecla Print)
--------------------------------------------------------------------------
local shot = hyprmac .. "/scripts/screenshot"
hl.bind("Print",          hl.dsp.exec_cmd(shot .. " region"))   -- área (⌘⇧4)
hl.bind("SHIFT + Print",  hl.dsp.exec_cmd(shot .. " screen"))   -- tela inteira (⌘⇧3)
hl.bind("CTRL + Print",   hl.dsp.exec_cmd(shot .. " window"))   -- janela ativa
-- Atalhos do Mac (HIG ▸ Keyboards, ⌘ = Super): ⇧⌘3 tela, ⇧⌘4 seleção, com ⌃ só para a
-- área de transferência. Tiram o "mover janela para a área 3/4/5" do hyprland.lua, que
-- disparava junto (o Hyprland executa todos os binds da mesma tecla).
hl.unbind("SUPER + SHIFT + 3")
hl.unbind("SUPER + SHIFT + 4")
hl.unbind("SUPER + SHIFT + 5")
hl.bind("SUPER + SHIFT + 3",        hl.dsp.exec_cmd(shot .. " screen"))
hl.bind("SUPER + SHIFT + 4",        hl.dsp.exec_cmd(shot .. " region"))
hl.bind("SUPER + SHIFT + CTRL + 3", hl.dsp.exec_cmd("env HYPRMAC_SHOT_CLIPBOARD=1 " .. shot .. " screen"))
hl.bind("SUPER + SHIFT + CTRL + 4", hl.dsp.exec_cmd("env HYPRMAC_SHOT_CLIPBOARD=1 " .. shot .. " region"))
-- Ferramenta de Captura e Gravação (⇧⌘5): barra com captura, gravação e opções
hl.bind("SUPER + SHIFT + 5", hl.dsp.exec_cmd(home .. "/.local/bin/hyprmac-capture-bar"))
hl.bind("SUPER + Print",     hl.dsp.exec_cmd(home .. "/.local/bin/hyprmac-capture-bar"))

--------------------------------------------------------------------------
-- Autostart
--------------------------------------------------------------------------
hl.on("hyprland.start", function ()
    hl.exec_cmd(hyprmac .. "/scripts/menu-extras start")
    hl.exec_cmd(hyprmac .. "/shell/hyprmac-shell")
    hl.exec_cmd(home .. "/.local/bin/hyprmac-clipboard watch")   -- histórico da área de transferência
    hl.exec_cmd(hyprmac .. "/shell/hyprmac-lock --warm-cache")   -- prepara o fundo da tela de bloqueio
    hl.exec_cmd(hyprmac .. "/scripts/ocioso start")   -- apaga a tela após 10 min sem uso (como o Mac)
    hl.exec_cmd(home .. "/.local/bin/hyprmac-aparencia start") -- aparência Auto: troca após 1 min ocioso
    hl.exec_cmd(hyprmac .. "/shell/hyprmac-overview")             -- Mission Control pronto para abrir rápido
    hl.exec_cmd(hyprmac .. "/scripts/vidro carregar")             -- Liquid Glass (hyprglass); compila na 1ª vez
end)

--------------------------------------------------------------------------
-- Liquid Glass (plugin hyprglass): presets e camadas de vidro
--------------------------------------------------------------------------
-- Inerte sem o plugin. No login, `vidro carregar` carrega e recarrega a config para
-- os presets/camadas valerem. Doc: BaseConhecimento/padroes/liquid-glass-hyprland.md
if hl.plugin and hl.plugin.hyprglass then
    dofile(hyprmac .. "/hypr/vidro-presets.lua")
end
