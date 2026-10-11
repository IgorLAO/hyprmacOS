-- hyprmac — presets de Liquid Glass para o plugin hyprglass
-- Presets próprios e camadas só valem quando o Hyprland LÊ a config (o hyprglass os guarda
-- como "pendentes" e os ativa no configReloaded); por `hyprctl eval` não valem. Incluído
-- pelo fim do hyprmac.lua quando o plugin está carregado (vidro carregar → hyprctl reload):
--     if hl.plugin.hyprglass then dofile(os.getenv("HOME") .. "/Projects/hyprmac/hypr/vidro-presets.lua") end
-- Doc: BaseConhecimento/padroes/liquid-glass-hyprland.md
-- [COREMATERIAL] Valores extraídos de CoreMaterial.framework (Tahoe 26.6.1 25G76)
-- Ver BaseConhecimento/corematerial_mined_output.json
local hg = hl.plugin.hyprglass

-- Ponto de partida "Apple" = pomme embutido (já tem aberração 0, como o iOS 27 medido)
hg.preset("hyprmac-apple", {
    inherits = "pomme",
})

-- Resultado aprovado no laboratório em 2026-10-03 (referência, não definitivo)
hg.preset("hyprmac-lab-20261003", {
    inherits             = "pomme",
    refraction_strength  = 1.412,
    refraction_flow      = 0.751,
    edge_thickness       = 0.148,
    chromatic_aberration = 0.154,
    specular_strength    = 0.467,
    bevel_strength       = 0.687,
    dark = { tint_color = 0x1A1A1A4A },
})

-- CoreMaterial exact Liquid Glass color matrix (from platformPinched, platformContentGlass*)
-- m11=0.921, m22=0.735, m33=0.973, m15/m25/m35=0.235
-- These are the EXACT Apple values for the glass refraction color transform
local CM_COLOR_MATRIX = {
    m11 = 0.921, m12 = -0.265, m13 = -0.027, m14 = 0.0, m15 = 0.235,
    m21 = -0.079, m22 = 0.735, m23 = -0.027, m24 = 0.0, m25 = 0.235,
    m31 = -0.079, m32 = -0.265, m33 = 0.973, m34 = 0.0, m35 = 0.235,
    m41 = 0.0,   m42 = 0.0,   m43 = 0.0,   m44 = 1.0,  m45 = 0.0,
}

-- CoreMaterial Dock materials (exact from dockDark/dockLight.materialrecipe)
-- Dark: luminanceAmount=0.5, luminanceValues=[0.29,-0.2,0.375,0.65], blurRadius=30, saturation=1.6, backdropScale=0.25
-- Light: luminanceAmount=0.5, luminanceValues=[0.3,0.5,1.0,0.77], blurRadius=30, saturation=1.8, brightness=0.08, backdropScale=0.25

-- CoreMaterial platformChromeDark/Light (for menus, popovers, window chrome)
-- Dark: luminanceAmount=0.75, luminanceValues=[0.23,0.52,0.27,0.255], blurRadius=22.5, saturation=2.0, brightness=-0.1, backdropScale=0.25
-- Light: luminanceAmount=0.75, luminanceValues=[0.8,0.9,1.1,0.825], blurRadius=22.5, saturation=1.1, brightness=0.1, backdropScale=0.25
-- Reduce Transparency variants: luminanceAmount=0.85 (dark) / 0.75 (light), averageColorEnabled=true, no blur

-- CoreMaterial platformContentThin/Thick/UltraThin variants
-- Thin Dark: luminanceAmount=0.6, luminanceValues=[0.2,0.21,0.1,0.15], blurRadius=30, saturation=1.35
-- Thin Light: luminanceAmount=0.6, luminanceValues=[0.725,0.825,0.76,0.73], blurRadius=30, saturation=1.35, brightness=0.12
-- Thick Dark: luminanceAmount=0.88, luminanceValues=[0.14,0.16,0.1,0.03], blurRadius=45, saturation=1.5
-- Thick Light: luminanceAmount=0.88, luminanceValues=[0.99,0.95,0.98,0.905], blurRadius=45, saturation=1.5, brightness=0.045
-- UltraThin Dark: luminanceAmount=0.5, luminanceValues=[0.24,0.24,0.3,0.39], blurRadius=22.5, saturation=1.1
-- UltraThin Light: luminanceAmount=0.5, luminanceValues=[0.45,0.55,0.65,0.68], blurRadius=22.5, saturation=1.1, brightness=0.12

-- CoreMaterial moduleFill/moduleStroke visualstylesets (Control Center modules)
-- moduleFill: vibrantColorMatrix for moduleItemOff (m15=0.12), moduleHighlight (m15=0.97), moduleRuleOnDark (vibrantDark)
-- moduleStroke: vibrantColorMatrix for moduleSecondary (m15=0.35), moduleRuleOnDark (vibrantDark)
-- modulesBackground: luminanceAmount=0.4, luminanceValues=[0.38,0,1,0.76], blurRadius=25, saturation=1.6, zoom=0.04

-- CoreMaterial platterFill/Stroke visualstylesets
-- platterFillLight: m15=-0.08; platterFillDark: m15=0.06
-- platterStrokeLightPrimary: alpha=0.9; platterStrokeDarkPrimary: alpha=0.9

--------------------------------------------------------------------------
-- Onde vai o vidro (HIG/WWDC25: só a camada de controles flutuantes)
--------------------------------------------------------------------------
-- Ajustes ▸ Aparência ▸ Liquid Glass (macOS 27: "from ultraclear to fully tinted"):
-- ~/.config/hyprmac/aparencia.json "glass_tint" 0 (Clear) … 100 (Tinted). Acessibilidade ▸
-- Reduzir Transparência vira vidro fosco quase opaco, sem lente.
local function ler(caminho)
    local f = io.open(caminho)
    if not f then return "" end
    local t = f:read("*a")
    f:close()
    return t
end
local conf = os.getenv("HOME") .. "/.config/hyprmac/"
local tinta = tonumber(ler(conf .. "aparencia.json"):match('"glass_tint"%s*:%s*([%d%.]+)')) or 5
tinta = math.max(0, math.min(100, tinta)) / 100
local fosco = ler(conf .. "acessibilidade.json"):match('"reduce_transparency"%s*:%s*true') ~= nil
if fosco then tinta = 1 end
local function cor(rgb, alfa) return rgb * 256 + math.floor(alfa * 255 + 0.5) end

-- Desde o hyprglass v0.9.0, numa camada cada peça opaca (cada bloco da Central, cada banner)
-- é vidro com máscara de alfa. A antiga implementação local dessa capacidade não está na árvore.
-- Nesse modo a
-- faixa do chanfro é edge_thickness × 133 px: 0.15 = os 20 pt do iOS 27 medido, com perfil
-- de quarto de círculo. refraction_strength × 50 = deslocamento máximo (Apple: 60 pt → 1.2).
-- Sem aberração cromática (o iOS 27 não dispersa). Aro fino e claro (bevel 2 px).
--
-- O VIDRO É O MESMO NO CLARO E NO ESCURO (medido em tahoe-dark.jpeg e na Central oficial
-- clara): é o fundo desfocado e saturado, um pouco mais claro — no escuro, bloco sobre céu
-- (66,88,127) → (90,115,146), sobre o Finder (34) → ~65: ≈ fundo + 13 % de branco. O escuro
-- vem do que está atrás, nunca de uma tinta. Os estilos "Dark" do kit (#1A1A1A/0.50,
-- #5A5A5A/0.50) são mistura LUMINOSITY: só puxam a luminância para um tom médio e mantêm a
-- cor do fundo — aqui, compressão de contraste em torno do meio (preset hyprmac-texto).
-- A tinta só entra pelo ajuste Clear ↔ Tinted.
local function tinta_de(rgb) return cor(rgb, 0.70 * tinta) end

-- Controles sobre o papel de parede (Central, OSD, botões do Spotlight): vidro claro
-- [COREMATERIAL] platformContentGlass/Dark/Light: blurRadius=45, saturation=1.1 (ultra thin) to 1.5 (thin/thick)
-- Using platformContentGlass (blurRadius=45, colorMatrix exact) as base
hg.preset("hyprmac-painel", {
    inherits             = "pomme",
    blur_strength        = fosco and 2.0 or 0.9,  -- CoreMaterial: 45/50 normalized ≈ 0.9
    refraction_strength  = fosco and 0 or 1.2,
    edge_thickness       = 0.15,  -- 20pt bevel per iOS 27 measured
    chromatic_aberration = 0,     -- iOS 27 no chromatic dispersion
    specular_strength    = fosco and 0 or 0.6,
    fresnel_strength     = fosco and 0 or 0.35,
    bevel_strength       = 0.9,
    bevel_size           = 2,
    -- CoreMaterial exact values: platformContentGlass saturation=1.5, backdropScale=0.25
    -- platformPinched colorMatrix: m11=0.921, m22=0.735, m33=0.973, m15/m25/m35=0.235
    dark  = { tint_color = tinta_de(0x1A1A1A), brightness = 1.0, contrast = 1.0, saturation = 1.5,
              vibrancy = 0.3, adaptive_dim = 0.32, adaptive_boost = 0 },
    light = { tint_color = tinta_de(0xF2F2F2), brightness = 1.0, contrast = 1.0, saturation = 1.5,
              vibrancy = 0.3, adaptive_dim = 0.32, adaptive_boost = 0 },
})

-- Central: o fundo continua reconhecível e dobra nas bordas (cc-sobre-janela-clara,
-- cc-tahoe-alvo-usuario).
-- [COREMATERIAL] modulesBackground: luminanceAmount=0.4, luminanceValues=[0.38,0,1,0.76], blurRadius=25, saturation=1.6, zoom=0.04
-- moduleFill/moduleStroke visualstylesets define vibrant color matrices for modules
-- Ajustado: reference cc-tahoe-alvo-usuario.png mostra vidro MENOS translúcido que o atual
hg.preset("hyprmac-central", {
    inherits             = "hyprmac-painel",
    -- CoreMaterial modulesBackground blurRadius=25 → normalized 25/50=0.5
    blur_strength        = fosco and 2.0 or 0.5,
    -- a lente das bordas é o que faz o Liquid Glass: o fundo dobra na faixa do chanfro
    -- (edge_thickness 0,15 herdado = ~20 pt); o miolo segue sólido pelo tom (brilho/contraste)
    refraction_strength  = fosco and 0 or 1.0,
    specular_strength    = fosco and 0 or 0.4,
    fresnel_strength     = fosco and 0 or 0.35,
    -- aro (filete de ~1 pt): o CSS dá a parte uniforme; o chanfro acende o lado da luz.
    -- Medido: tahoe-dark topo +40, base +36…+50, direita +70, esquerda +8; WWDC topo +60,
    -- base +25 — luz de cima-direita
    bevel_strength       = 0.14,
    bevel_angle          = 45,
    -- CoreMaterial modulesBackground saturation=1.6, zoom=0.04 ≈ adaptive_dim
    -- Menos translúcido: contrast mantido, adaptive_dim maior para comprimir fundo
    dark  = { tint_color = tinta_de(0x1A1A1A), brightness = 1.0, contrast = 0.87, saturation = 1.6,
              vibrancy = 0.1, adaptive_dim = 0.08, adaptive_boost = 0 },
    light = { tint_color = tinta_de(0xF2F2F2), brightness = 1.0, contrast = 0.87, saturation = 1.6,
              vibrancy = 0.1, adaptive_dim = 0.08, adaptive_boost = 0 },
})

-- Peças pequenas (OSD, banners): lente um pouco mais curta
hg.preset("hyprmac-pequeno", {
    inherits             = "hyprmac-painel",
    refraction_strength  = 0.9,
})

-- Painéis com texto (menus, notificações, Spotlight, Alt+Tab, histórico): o "luminosity" do
-- kit — a luminância vai para perto do meio (fundo escuro clareia, fundo branco escurece) e
-- a cor do fundo fica; o texto branco lê sobre qualquer coisa sem o vidro virar um bloco.
-- No claro, o mesmo vidro com mais branco por cima (CSS) e texto escuro.
-- [COREMATERIAL] platformContentDark: luminanceAmount=0.75, luminanceValues=[0.16,0.26,0.1,0.1], blurRadius=30, saturation=1.5, brightness=0, backdropScale=0.25
-- platformContentLight: luminanceAmount=0.75, luminanceValues=[0.9,0.83,0.925,0.815], blurRadius=30, saturation=1.5, brightness=0.1, backdropScale=0.25
hg.preset("hyprmac-texto", {
    inherits             = "hyprmac-painel",
    -- CoreMaterial platformContentDark/Light blurRadius=30 → normalized 30/50=0.6
    blur_strength        = fosco and 2.0 or 0.6,
    -- ESCURO medido (escuro-spotlight-apps-sobre-claro, escuro-menu-contexto-sobre-rosa): o
    -- painel ESCURECE forte e mantém o matiz — por dentro L 0,03–0,11 com o fundo de 0,10 a
    -- 0,84 (verde-claro 206,246,207 → 85,95,72; rosa 223,96,166 → 106,46,88; escuro 43 → 52).
    -- Ajuste na ordem do shader (×brilho, contraste em 0,5): brilho 0,27, contraste 0,64.
    -- CoreMaterial platformContentDark: saturation=1.5, brightness=0
    dark  = { tint_color = tinta_de(0x1A1A1A), brightness = 0.27, contrast = 0.64, saturation = 1.5,
              adaptive_dim = 0, adaptive_boost = 0 },
    -- CoreMaterial platformContentLight: saturation=1.5, brightness=0.1
    light = { tint_color = tinta_de(0xF2F2F2), brightness = 1.12, contrast = 0.65, saturation = 1.5,
              adaptive_dim = 0, adaptive_boost = 0 },
})

-- Spotlight: preset dedicado com ColorMatrix EXATO do CoreMaterial (platformPinched/platformContentGlass)
-- m11=0.921, m22=0.735, m33=0.973, m15/m25/m35=0.235
-- Este ColorMatrix é a refração do Liquid Glass; deve ser aplicado no shader hyprglass
hg.preset("hyprmac-spotlight", {
    inherits             = "hyprmac-texto",
    -- CoreMaterial platformContentGlass: blurRadius=45, saturation=1.5
    blur_strength        = fosco and 2.0 or 0.9,  -- 45/50
    -- ColorMatrix exato para refração do vidro (definido em CM_COLOR_MATRIX acima)
    -- O hyprglass precisa receber esta matriz para o efeito de lente correto
    dark  = { tint_color = tinta_de(0x1A1A1A), brightness = 0.27, contrast = 0.64, saturation = 1.5,
              adaptive_dim = 0, adaptive_boost = 0,
              color_matrix = CM_COLOR_MATRIX },
    light = { tint_color = tinta_de(0xF2F2F2), brightness = 1.12, contrast = 0.65, saturation = 1.5,
              adaptive_dim = 0, adaptive_boost = 0,
              color_matrix = CM_COLOR_MATRIX },
})

-- janelas: lista branca (tag hyprglass_enabled, vidro.janela); um reload zera as opções,
-- então isto repete o que o `vidro carregar` põe
-- o tema das camadas é o global do plugin: segue o do sistema (scripts/theme troca ao vivo)
local f = io.popen("gsettings get org.gnome.desktop.interface color-scheme 2>/dev/null")
local esquema = f and f:read("*a") or ""
if f then f:close() end
hg.config({
    enabled       = false,
    default_theme = esquema:find("dark") and "dark" or "light",
    layers        = { enabled = true },
})

-- Camadas do hyprmac-shell. Em camada o vidro vai onde o alfa passa de mask_threshold: o
-- preenchimento agora é só um véu branco leve (shell/vidro-camadas.css, ~0.06–0.10), então o
-- limiar é 0.04; no histórico fica acima do fundo esmaecido (0.35). Sombras em CSS saem.
-- Fora: barra (transparente no Tahoe), Dock (vidro próprio, raio 1), widgets da mesa
-- (camada de conteúdo, material comum), coletores de clique.
for ns, opts in pairs({
    ["hyprmac-cc"]             = { mask_threshold = 0.025, preset = "hyprmac-central" },
    ["hyprmac-cc-gallery"]     = { mask_threshold = 0.025, preset = "hyprmac-texto" },
    ["hyprmac-notifications"]  = { mask_threshold = 0.025, preset = "hyprmac-texto" },
    ["hyprmac-nc"]             = { mask_threshold = 0.025, preset = "hyprmac-texto" },
    ["hyprmac-extras"]         = { mask_threshold = 0.025, preset = "hyprmac-texto" },
    ["hyprmac-media"]          = { mask_threshold = 0.025, preset = "hyprmac-painel" },
    ["hyprmac-switcher"]       = { mask_threshold = 0.025, preset = "hyprmac-texto" },
    ["hyprmac-spotlight"]      = { mask_threshold = 0.025, preset = "hyprmac-spotlight" },
    ["hyprmac-clipboard"]      = { mask_threshold = 0.36, preset = "hyprmac-texto" },
    ["hyprmac-widget-gallery"] = { mask_threshold = 0.025, preset = "hyprmac-texto" },
    ["hyprmac-osd"]            = { mask_threshold = 0.025, preset = "hyprmac-pequeno" },
    -- barra de Captura de Tela (⇧⌘5, scripts/captura): vidro com a barra inteira como peça
    ["hyprmac-captura-barra"]  = { mask_threshold = 0.025, preset = "hyprmac-texto" },
    -- menus (popups GTK) da barra e do hyprmac-shell: com o patch, o passe de popups da
    -- camada vira vidro próprio ("<namespace>:popups"; a camada em si continua sem vidro)
    ["waybar:popups"]          = { mask_threshold = 0.025, preset = "hyprmac-texto" },
    ["hyprmac-menu:popups"]    = { mask_threshold = 0.025, preset = "hyprmac-texto" },
    ["hyprmac-dock:popups"]    = { mask_threshold = 0.025, preset = "hyprmac-texto" },
}) do
    opts.preset = opts.preset or "hyprmac-painel"
    hg.layer(ns, opts)
end

-- Os popups com vidro não levam mais o desfoque do Hyprland (ficaria por cima da lente,
-- desenhado como conteúdo do menu): as regras do hyprmac.lua são redeclaradas sem blur_popups.
hl.layer_rule({
    name  = "hyprmac-bar",
    match = { namespace = "^waybar$" },
    blur         = true,
    blur_popups  = false,
    ignore_alpha = 0.5,
})
hl.layer_rule({
    name  = "hyprmac-menu",
    match = { namespace = "^hyprmac-menu$" },
    blur_popups  = false,
    ignore_alpha = 0.2,
    no_anim      = true,
})
hl.layer_rule({
    name  = "hyprmac-dock",
    match = { namespace = "^hyprmac-dock$" },
    blur_popups = false,
    ignore_alpha = 0.3,
    no_anim = true,
})

-- Ajustes do Sistema: barra lateral (kit Sidebar/Background/Dark/Active: desfoque 80, saturação 2,
-- distorção 0,5 sob #0C0C0C/0.85 pintado pelo app) e cápsula < > (Regular - Small) são vidro.
-- O preset ainda fornece vidro para a janela. O antigo comando local `hyprglass shape`, que
-- separava barra lateral e cápsula em peças, não existe no upstream v0.9.0; não dependa dele.
hg.preset("hyprmac-lateral", {
    inherits             = "pomme",
    blur_strength        = 2.2,
    refraction_strength  = 1.0,
    edge_thickness       = 0.12,   -- forma declarada: faixa = 0.12 × 133 ≈ 16 px
    chromatic_aberration = 0,
    specular_strength    = 0.5,
    fresnel_strength     = 0.3,
    bevel_strength       = 0.7,
    bevel_size           = 1.5,
    dark  = { tint_color = 0x00000000, saturation = 2.0, brightness = 1.0, adaptive_dim = 0 },
    light = { tint_color = 0x00000000, saturation = 1.4, adaptive_dim = 0 },
})
for _, tag in ipairs({ "hyprglass_enabled", "hyprglass_preset_hyprmac-lateral" }) do
    hl.window_rule({
        name  = "vidro-ajustes-" .. tag,
        match = { class = "^dev\\.hyprmac\\.Settings$" },
        tag   = "+" .. tag,
    })
end

-- Dock: vidro próprio usando CoreMaterial dockDark/dockLight.materialrecipe
-- [COREMATERIAL] dockDark: luminanceAmount=0.5, luminanceValues=[0.29,-0.2,0.375,0.65], blurRadius=30, saturation=1.6, backdropScale=0.25
-- [COREMATERIAL] dockLight: luminanceAmount=0.5, luminanceValues=[0.3,0.5,1.0,0.77], blurRadius=30, saturation=1.8, brightness=0.08, backdropScale=0.25
-- Dock has continuous corners (rounding_power=3.2) and radius=1 (per hyprmac.lua)
hg.preset("hyprmac-dock", {
    inherits             = "pomme",
    blur_strength        = 0.6,  -- 30/50 normalized
    refraction_strength  = 0.8,
    edge_thickness       = 0.15,
    chromatic_aberration = 0,
    specular_strength    = 0.5,
    fresnel_strength     = 0.3,
    bevel_strength       = 0.5,
    bevel_size           = 2,
    -- Dock Dark: saturation=1.6, backdropScale=0.25
    dark  = { tint_color = tinta_de(0x1A1A1A), brightness = 1.0, contrast = 1.0, saturation = 1.6,
              vibrancy = 0.2, adaptive_dim = 0.16, adaptive_boost = 0 },
    -- Dock Light: saturation=1.8, brightness=0.08, backdropScale=0.25
    light = { tint_color = tinta_de(0xF2F2F2), brightness = 1.08, contrast = 1.0, saturation = 1.8,
              vibrancy = 0.2, adaptive_dim = 0.16, adaptive_boost = 0 },
})
-- Apply Dock preset to hyprmac-dock layer
hg.layer("hyprmac-dock", { mask_threshold = 0.3, preset = "hyprmac-dock" })

-- ============================================================================
-- NOVOS PRESETS baseados em CoreMaterial framework (Tahoe 26.6.1)
-- ============================================================================

-- platformChromeDark/Light — para menus, popovers, chrome de janelas
-- Dark: luminanceAmount=0.75, luminanceValues=[0.23,0.52,0.27,0.255], blurRadius=22.5, saturation=2.0, brightness=-0.1, backdropScale=0.25
-- Light: luminanceAmount=0.75, luminanceValues=[0.8,0.9,1.1,0.825], blurRadius=22.5, saturation=1.1, brightness=0.1, backdropScale=0.25
hg.preset("hyprmac-chrome", {
    inherits             = "pomme",
    blur_strength        = fosco and 2.0 or 0.45,  -- 22.5/50 normalized
    refraction_strength  = fosco and 0 or 0.9,
    edge_thickness       = 0.14,
    chromatic_aberration = 0,
    specular_strength    = fosco and 0 or 0.5,
    fresnel_strength     = fosco and 0 or 0.3,
    bevel_strength       = 0.6,
    bevel_size           = 1.5,
    dark  = { tint_color = tinta_de(0x1A1A1A), brightness = 0.9, contrast = 1.0, saturation = 2.0,
              vibrancy = 0.2, adaptive_dim = 0, adaptive_boost = 0 },
    light = { tint_color = tinta_de(0xF2F2F2), brightness = 1.1, contrast = 1.0, saturation = 1.1,
              vibrancy = 0.2, adaptive_dim = 0, adaptive_boost = 0 },
})

-- platformChrome*ReduceTransparency — fallback quando Reduzir Transparência ativo
-- Dark: luminanceAmount=0.85, luminanceValues=[0.225,0.31,0.25,0.2], averageColorEnabled=true
-- Light: luminanceAmount=0.75, luminanceValues=[0.95,0.9,1.1,0.825], saturation=0.8, brightness=0.1, averageColorEnabled=true
hg.preset("hyprmac-chrome-reduce", {
    inherits             = "pomme",
    blur_strength        = 2.0,  -- sem blur real, só fosco
    refraction_strength  = 0,
    edge_thickness       = 0.1,
    chromatic_aberration = 0,
    specular_strength    = 0,
    fresnel_strength     = 0,
    bevel_strength       = 0.3,
    bevel_size           = 1,
    dark  = { tint_color = tinta_de(0x1A1A1A), brightness = 0.9, contrast = 1.0, saturation = 1.0,
              vibrancy = 0, adaptive_dim = 0, adaptive_boost = 0 },
    light = { tint_color = tinta_de(0xF2F2F2), brightness = 1.1, contrast = 1.0, saturation = 0.8,
              vibrancy = 0, adaptive_dim = 0, adaptive_boost = 0 },
})

-- platformContentThin — vidro mais fino (menus, popovers)
-- Dark: luminanceAmount=0.6, luminanceValues=[0.2,0.21,0.1,0.15], blurRadius=30, saturation=1.35
-- Light: luminanceAmount=0.6, luminanceValues=[0.725,0.825,0.76,0.73], blurRadius=30, saturation=1.35, brightness=0.12
hg.preset("hyprmac-texto-thin", {
    inherits             = "hyprmac-texto",
    blur_strength        = fosco and 2.0 or 0.6,  -- 30/50
    dark  = { tint_color = tinta_de(0x1A1A1A), brightness = 0.35, contrast = 0.65, saturation = 1.35,
              adaptive_dim = 0, adaptive_boost = 0 },
    light = { tint_color = tinta_de(0xF2F2F2), brightness = 1.15, contrast = 0.65, saturation = 1.35,
              adaptive_dim = 0, adaptive_boost = 0 },
})

-- platformContentThick — vidro mais grosso (sidebars, painéis maiores)
-- Dark: luminanceAmount=0.88, luminanceValues=[0.14,0.16,0.1,0.03], blurRadius=45, saturation=1.5
-- Light: luminanceAmount=0.88, luminanceValues=[0.99,0.95,0.98,0.905], blurRadius=45, saturation=1.5, brightness=0.045
hg.preset("hyprmac-texto-thick", {
    inherits             = "hyprmac-texto",
    blur_strength        = fosco and 2.0 or 0.9,  -- 45/50
    dark  = { tint_color = tinta_de(0x1A1A1A), brightness = 0.2, contrast = 0.6, saturation = 1.5,
              adaptive_dim = 0, adaptive_boost = 0 },
    light = { tint_color = tinta_de(0xF2F2F2), brightness = 1.08, contrast = 0.65, saturation = 1.5,
              adaptive_dim = 0, adaptive_boost = 0 },
})

-- platformContentUltraThin — vidro ultrafino (tooltips, overlays leves)
-- Dark: luminanceAmount=0.5, luminanceValues=[0.24,0.24,0.3,0.39], blurRadius=22.5, saturation=1.1
-- Light: luminanceAmount=0.5, luminanceValues=[0.45,0.55,0.65,0.68], blurRadius=22.5, saturation=1.1, brightness=0.12
hg.preset("hyprmac-ultra-thin", {
    inherits             = "pomme",
    blur_strength        = fosco and 2.0 or 0.45,  -- 22.5/50
    refraction_strength  = fosco and 0 or 0.6,
    edge_thickness       = 0.12,
    chromatic_aberration = 0,
    specular_strength    = fosco and 0 or 0.3,
    fresnel_strength     = fosco and 0 or 0.2,
    bevel_strength       = 0.4,
    bevel_size           = 1,
    dark  = { tint_color = tinta_de(0x1A1A1A), brightness = 0.5, contrast = 0.8, saturation = 1.1,
              adaptive_dim = 0, adaptive_boost = 0 },
    light = { tint_color = tinta_de(0xF2F2F2), brightness = 1.15, contrast = 0.8, saturation = 1.1,
              adaptive_dim = 0, adaptive_boost = 0 },
})

-- CoreMaterial modulesBackground — fundo da Central de Controle
-- luminanceAmount=0.4, luminanceValues=[0.38,0,1,0.76], blurRadius=25, saturation=1.6, zoom=0.04
-- moduleFill/moduleStroke visualstylesets definem as cores vibrantes dos módulos
-- Ajustado: reference cc-tahoe-alvo-usuario.png mostra vidro MENOS translúcido que o atual
hg.preset("hyprmac-modules", {
    inherits             = "hyprmac-central",
    -- moduleFill visualstyleset: moduleItemOff (m15=0.12), moduleHighlight (m15=0.97), moduleRuleOnDark (vibrantDark)
    -- moduleStroke visualstyleset: moduleSecondary (m15=0.35), moduleRuleOnDark (vibrantDark)
    -- Estes são aplicados via CSS nas peças individuais dos módulos
    dark  = { tint_color = tinta_de(0x1A1A1A), brightness = 1.0, contrast = 0.87, saturation = 1.6,
              vibrancy = 0.1, adaptive_dim = 0.08, adaptive_boost = 0 },
    light = { tint_color = tinta_de(0xF2F2F2), brightness = 1.0, contrast = 0.87, saturation = 1.6,
              vibrancy = 0.1, adaptive_dim = 0.08, adaptive_boost = 0 },
})

-- platterFill/Stroke — para QuickLook panels, cards, widgets
-- platterFillLight: m15=-0.08; platterFillDark: m15=0.06
-- platterStrokeLightPrimary: alpha=0.9; platterStrokeDarkPrimary: alpha=0.9
hg.preset("hyprmac-platter", {
    inherits             = "pomme",
    blur_strength        = fosco and 2.0 or 0.6,  -- 30/50
    refraction_strength  = fosco and 0 or 0.8,
    edge_thickness       = 0.14,
    chromatic_aberration = 0,
    specular_strength    = fosco and 0 or 0.4,
    fresnel_strength     = fosco and 0 or 0.25,
    bevel_strength       = 0.5,
    bevel_size           = 2,
    dark  = { tint_color = tinta_de(0x1A1A1A), brightness = 1.0, contrast = 0.9, saturation = 1.8,
              vibrancy = 0.2, adaptive_dim = 0.06, adaptive_boost = 0 },
    light = { tint_color = tinta_de(0xF2F2F2), brightness = 1.05, contrast = 1.0, saturation = 2.0,
              vibrancy = 0.2, adaptive_dim = 0.06, adaptive_boost = 0 },
})

-- previewBackground — para preview de imagens/PDFs
-- tintAlpha=0.088, blurRadius=11.2, zoom=0.024
hg.preset("hyprmac-preview", {
    inherits             = "pomme",
    blur_strength        = fosco and 2.0 or 0.22,  -- 11.2/50
    refraction_strength  = fosco and 0 or 0.4,
    edge_thickness       = 0.1,
    chromatic_aberration = 0,
    specular_strength    = fosco and 0 or 0.2,
    fresnel_strength     = fosco and 0 or 0.15,
    bevel_strength       = 0.3,
    bevel_size           = 1,
    dark  = { tint_color = tinta_de(0x1A1A1A), brightness = 1.0, contrast = 1.0, saturation = 1.0,
              vibrancy = 0, adaptive_dim = 0.024, adaptive_boost = 0 },
    light = { tint_color = tinta_de(0xF2F2F2), brightness = 1.0, contrast = 1.0, saturation = 1.0,
              vibrancy = 0, adaptive_dim = 0.024, adaptive_boost = 0 },
})

-- Aplicar presets adicionais às camadas relevantes
for ns, opts in pairs({
    -- Menus e popovers usam platformChrome
    ["hyprmac-menu:popups"]    = { mask_threshold = 0.025, preset = "hyprmac-chrome" },
    ["waybar:popups"]          = { mask_threshold = 0.025, preset = "hyprmac-chrome" },
    ["hyprmac-dock:popups"]    = { mask_threshold = 0.025, preset = "hyprmac-chrome" },
    -- Módulos da Central usam preset específico com moduleFill/moduleStroke
    ["hyprmac-cc"]             = { mask_threshold = 0.025, preset = "hyprmac-modules" },
}) do
    opts.preset = opts.preset or "hyprmac-painel"
    hg.layer(ns, opts)
end
