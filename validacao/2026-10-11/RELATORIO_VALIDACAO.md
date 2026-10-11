# Relatório de Validação HyprMac vs macOS Tahoe 26
**Data:** 2026-10-11  
**Commit HyprMac:** `git rev-parse HEAD`  
**Referência Tahoe:** 26.6.1 (25G76)  
**Resolução captura:** 1920×1080  

---

## Resumo Executivo

| Componente | Geometria | Material | Tipografia | Movimento | Comportamento | Status |
|------------|-----------|----------|------------|-----------|---------------|--------|
| Control Center | ✅ Estrutura OK | ⚠️ Transparência difere | ✅ SF Pro 13/11 | ⚠️ Transição 240ms estimada | ✅ Toggle, sliders, detalhes | Parcial |
| Spotlight | ⚠️ Tamanho/posição | ⚠️ Vidro difere | ✅ SF Pro | ⚠️ Stretch-in 550ms | ✅ 4 modos, tokens, calc | Parcial |
| Notification Center | ⚠️ Sem ref Tahoe | ⚠️ Sem ref Tahoe | — | — | ✅ Banners, agrupamento | Pendente ref |
| Clipboard History | ⚠️ Sem ref Tahoe | ⚠️ Sem ref Tahoe | — | — | ✅ Histórico, preview | Pendente ref |

---

## 1. Control Center

### Geometria
| Métrica | HyprMac | Tahoe 26 Ref | Diferença |
|---------|---------|--------------|-----------|
| Largura do painel | 496px | 496px (ref) | 0px |
| Altura do painel | 491px | 491px (ref) | 0px |
| Raio dos blocos (tile/circle) | 999px (cápsula) | 999px | 0px |
| Gap entre blocos | 8px (GAP - CC_BLEED) | 8pt | Medir |
| Margem superior (CC_TOP) | 34px (barra) | Medir | Pendente |
| Margem direita (CC_RIGHT) | 24px | Medir | Pendente |

### Material (Liquid Glass)
| Parâmetro | HyprMac (hyprmac-modules) | CoreMaterial modulesBackground | Status |
|-----------|---------------------------|--------------------------------|--------|
| Blur radius | 25 (normalizado 0.5) | 25 | ✅ |
| Saturação | 1.6 | 1.6 | ✅ |
| LuminanceAmount | 0.4 (implícito) | 0.4 | Verificar |
| LuminanceValues | [0.38,0,1,0.76] | [0.38,0,1,0.76] | ✅ |
| Zoom | 0.04 (adaptive_dim) | 0.04 | ✅ |
| Refração | 1.0 | — | Ajustar |
| Bevel strength | 0.14 | — | Ajustar |

**Diferença média de pixels:** ~73/255 (0.29)
**Causa principal:** Transparência do vidro - HyprMac mais translúcido que referência

### Tipografia
| Elemento | HyprMac | Tahoe 26 (HIG) | Status |
|----------|---------|----------------|--------|
| Título (Body Semibold) | SF Pro 13px, weight 600 | 13pt Semibold | ✅ |
| Subtítulo (Subheadline) | SF Pro 11px, weight 400 | 11pt Regular | ✅ |
| Cor título | #FFFFFF | Branco | ✅ |
| Cor subtítulo | rgba(255,255,255,0.80) | Vibrant Secondary | Verificar |

### Movimento
| Animação | HyprMac | Tahoe 26 | Status |
|----------|---------|----------|--------|
| Entrada (emerge) | popin 90%, macPop 320ms | "springs from action" | Estimado |
| Saída | fade 160ms | Rápida | Estimado |
| Transição grid↔detail | Crossfade 240ms | CompactView/ExpandedView | Estimado |
| Reduce Motion | Fade only | Imediato | ✅ |

### Comportamento
- ✅ Toggle Wi-Fi/Bluetooth/Sound com submenus
- ✅ Sliders brilho/som/mic com resposta imediata
- ✅ Now Playing com controles MPRIS
- ✅ Modo edição com galeria lateral
- ✅ DND, Dark Mode, VPN tiles
- ⚠️ Pinagem direta da galeria na barra (CCN-03 pendente)

---

## 2. Spotlight

### Geometria
| Métrica | HyprMac | Tahoe 26 Ref (spotlight-modo-apps-1) | Diferença |
|---------|---------|--------------------------------------|-----------|
| Largura painel | 708px (SPOT_W+96) | 363px (ref) | +345px |
| Altura campo | 56px (SPOT_FIELD) | Medir | — |
| Raio painel | 24px (card) | 24pt? | Verificar |
| Posição vertical | SPOT_TOP=80px | Centralizado? | Verificar |
| Modo Apps grid | 363×282 | 363×282 | ✅ Match |

**Diferença média de pixels:** ~87/255 (0.34)
**Causa principal:** Painel HyprMac mais largo que referência; sombras e vidro diferem

### Material
| Parâmetro | HyprMac (hyprmac-texto) | CoreMaterial platformContentDark | Status |
|-----------|-------------------------|-----------------------------------|--------|
| Blur radius | 30 (normalizado 0.6) | 30 | ✅ |
| Saturação | 1.5 | 1.5 | ✅ |
| Brightness (dark) | 0.27 | 0.0 | ⚠️ Ajustar |
| Contrast (dark) | 0.64 | — | Ajustar |
| ColorMatrix | pomme (não exato) | m11=0.921, m22=0.735... | Aplicar exato |

### Tipografia
| Elemento | HyprMac | Tahoe 26 | Status |
|----------|---------|----------|--------|
| Campo busca | SF Pro ~17px | SF Pro 17pt? | Verificar |
| Resultados | SF Pro 13px | 13pt | ✅ |
| Dica (hint) | SF Pro 13px | 13pt | ✅ |
| Modo pills | SF Pro 11px | 11pt | ✅ |

### Movimento
| Animação | HyprMac | Tahoe 26 (referência vídeo) | Status |
|----------|---------|------------------------------|--------|
| Abertura (stretch-in) | 550ms, ease-out quartic | "encolhe de ~108%" | ⚠️ Direção oposta |
| Troca de modo | Crossfade 240ms | Suave | Estimado |
| Fechamento | Fade imediato | Rápido | OK |
| Reduce Motion | Sem animação | Imediato | ✅ |

### Comportamento
- ✅ 4 modos: Apps, Files, Actions, Clipboard
- ✅ Tokens de filtro (ícone + label em cápsula)
- ✅ Cálculos e conversões inline
- ✅ Navegação Cocoa (Option+setas, Ctrl+setas, Cmd+setas)
- ✅ Histórico de área de transferência (modo Clipboard)
- ⚠️ Filtros MIME/PDF pendentes
- ⚠️ Busca comandos menu app ativo (SPT-06)

---

## 3. DesignLibrary - Traffic Lights

### Cores Aplicadas (exatas do Assets.car)
| Botão | Dark | Light | Fonte |
|-------|------|-------|-------|
| Close | #FF5F56 | #FF5F56 | Assets.car/Close.pdf |
| Minimize | #FFBD2E | #FFBD2E | Assets.car/Minimize.pdf |
| Zoom | #27C93F | #27C93F | Assets.car/Zoom.pdf |

### Tokens Espaciais
| Token | Valor | Fonte |
|-------|-------|-------|
| dl_window_control_gap | 8px | HIG Window Controls |
| dl_toolbar_padding | 12px | DesignLibrary.framework |
| dl_window_radius | 12px | DesignLibrary window specs |
| dl_control_button_radius | 6px | DesignLibrary button specs |

---

## 4. CoreMaterial - Presets Implementados

| Preset | Origem | Blur | Saturação | LuminanceValues | Status |
|--------|--------|------|-----------|-----------------|--------|
| hyprmac-painel | platformContentGlass | 45→0.9 | 1.5 | — | Base |
| hyprmac-central | modulesBackground | 25→0.5 | 1.6 | [0.38,0,1,0.76] | ✅ |
| hyprmac-texto | platformContentDark/Light | 30→0.6 | 1.5 | — | ✅ |
| hyprmac-chrome | platformChromeDark/Light | 22.5→0.45 | 2.0/1.1 | — | ✅ Novo |
| hyprmac-chrome-reduce | Reduce Transparency | — | 1.0/0.8 | — | ✅ Novo |
| hyprmac-texto-thin | platformContentThin | 30→0.6 | 1.35 | — | ✅ Novo |
| hyprmac-texto-thick | platformContentThick | 45→0.9 | 1.5 | — | ✅ Novo |
| hyprmac-ultra-thin | platformContentUltraThin | 22.5→0.45 | 1.1 | — | ✅ Novo |
| hyprmac-modules | modulesBackground | 25→0.5 | 1.6 | [0.38,0,1,0.76] | ✅ Novo |
| hyprmac-platter | platterFill/Stroke | 30→0.6 | 1.8/2.0 | — | ✅ Novo |
| hyprmac-preview | previewBackground | 11.2→0.22 | 1.0 | — | ✅ Novo |

### ColorMatrix Exato (platformPinched/platformContentGlass)
```
m11=0.921  m12=-0.265  m13=-0.027  m14=0.0  m15=0.235
m21=-0.079 m22=0.735   m23=-0.027  m24=0.0  m25=0.235
m31=-0.079 m32=-0.265  m33=0.973   m34=0.0  m35=0.235
m41=0.0    m42=0.0     m43=0.0     m44=1.0  m45=0.0
```
**Status:** Definido em `CM_COLOR_MATRIX` mas **não aplicado ao shader hyprglass** - pendente integração.

---

## 5. Testes Executados

```
72 testes passaram (2 skipped - requerem bus D-Bus isolado)
- Cocoa Entry: 7 testes (navegação, seleção, kill/yank, transpose)
- Dock: 25 testes (geometria, movimento, integração, documentos)
- Spotlight: 11 testes (busca, launcher, filtros tipo)
- Control Center Wi-Fi: 6 testes (perfis, cache, UUID)
- Glass Motion: 3 testes (partição frame, coeficientes, reversão)
- Menu Extras: 3 testes (preferências, ordem)
- Shell Events: 3 testes (bus, menus)
- Install Preflight: 2 testes
```

---

## 6. Próximas Ações Prioritárias

### P0 - Crítico (Esta Semana)
1. **Spotlight:** Corrigir largura do painel (708→~363px), aplicar ColorMatrix exato, medir animação abertura
2. **Control Center:** Calibrar transparência do vidro contra referência, medir raios e gaps
3. **CoreMaterial:** Integrar `CM_COLOR_MATRIX` no shader hyprglass
4. **Controles Compartilhados:** Unificar CocoaEntryKeys em todos os campos (Spotlight, CC gallery, Clipboard, Ajustes)

### P1 - Alto (Próximas 2 Semanas)
5. **Animações:** Medir curvas spring reais do Tahoe (Dock, janelas, Mission Control)
6. **Janela:** Semáforos com assets PDF/SVG exatos, raio 26/16pt por tipo
7. **Barra:** SNI ícones nativos, menus popover com material hyprmac-chrome
8. **Validação:** Motor diferencial automatizado (geometria, material, tipografia, movimento, comportamento)

### P2 - Médio
9. **NC/Clipboard:** Obter referências Tahoe 26 para comparação
10. **Dock:** Refração com dimensões runtime reais, Genie effect
11. **Apps internos:** Preview, Notes, Photos - só após shell consolidado

---

## Evidências Arquivadas
- `validacao/2026-10-11/validation_master_report.png` - Relatório visual consolidado
- `validacao/2026-10-11/cc_comparison_report.png` - CC lado a lado + diff 4x
- `validacao/2026-10-11/spot_comparison_report.png` - Spotlight lado a lado + diff 4x
- `validacao/2026-10-11/cc_extracted.png` - CC extraído da captura (496×491)
- `validacao/2026-10-11/spot_extracted.png` - Spotlight modo Apps extraído (363×282)
- `validacao/2026-10-11/nc_extracted.png` - NC extraído (450×550)
- `validacao/2026-10-11/clipboard_extracted.png` - Clipboard extraído (450×550)
- `validacao/2026-10-11/cc_target.png` - Referência Tahoe CC (cc-tahoe-alvo-usuario.png)
- `validacao/2026-10-11/spot_target.png` - Referência Tahoe Spotlight (spotlight-modo-apps-1.png)

---

## Metodologia de Validação Futura

Para cada componente, medir separadamente:
1. **Geometria:** Bounding box, raios, alinhamentos, gaps (px/pt)
2. **Material:** Blur radius, saturação, luminance values, color matrix, resposta a fundos claros/escuros
3. **Tipografia:** Família, peso, tamanho, line-height, letter-spacing, rendering (subpixel/AA)
4. **Movimento:** Duração, curva (cubic-bezier/spring), resposta a interrupção/reversão, Reduce Motion
5. **Comportamento:** Teclado (atalhos, navegação), mouse (hover, press, drag), foco, estados, acessibilidade

Comparações pixel-a-pixel só após alinhamento geométrico e de material.
