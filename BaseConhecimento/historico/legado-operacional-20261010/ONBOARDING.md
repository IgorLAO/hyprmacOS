> Arquivo histórico anterior à consolidação de 2026-10-10. Consulte STATUS.md e o SQLite para o estado atual.

# 🚀 Onboarding — hyprmac (15-Minute Quick Start)

**Audience:** Any incoming AI agent or software engineer  
**Goal:** Rapidly grasp the architecture, rules, and sources of truth to start working immediately  
**Estimated Reading Time:** 15 minutes  

---

## 📍 Project Snapshot in 30 Seconds

```
Project:  macOS Tahoe / macOS 27 Design System implemented on Linux (Hyprland + Wayland)
Status:   94% visual & behavioral compliance (automated quantitative score)
Target:   99%+ fidelity across all P1 and P2 items
Priority: Dock material & magnification, Control Center inline sub-popovers, Finder visual experience
```

---

## ✅ Read in THIS Exact Order (15 min total)

### 1. Project Rules (2 min)
```bash
cat AGENTS.md
sed -n '1,220p' BaseConhecimento/INDICE-AGENTES.md
sed -n '1,220p' BaseConhecimento/GERENCIAMENTO-CONTEXTO.md
```
**Takeaway:** The goal is **MÁXIMA FIDELIDADE** com macOS Tahoe / macOS 27, não uma aproximação. `AGENTS.md` contém as regras; o índice aponta diretamente para código, referências e validação.

O agente trabalha com um working set limitado. Use `BaseConhecimento/codigo.json`
e `consultar.py --codigo` para localizar candidatos antes de abrir arquivos
inteiros.

---

### 2. General Status (2 min)
```bash
cat BaseConhecimento/comparacao/MATRIZ.md | head -35
# OR
./BaseConhecimento/ferramentas/comparar.py --resumo
```
**Takeaway:** Overall compliance is currently 94%. Remaining items are categorized into P1 (Critical), P2 (Significant), and P3 (Refinement).

---

### 3. Source of Truth #1: Real Code (3 min)
```bash
grep -A 15 "\.cc .tile" shell/style.css | head -20
```
**What you will see:**
```css
background-color: rgba(128, 128, 142, 0.22);  /* Real token */
transition: background-color 160ms ease-out;  /* Real timing */
box-shadow: inset 0 1px 1px rgba(255,255,255,0.22);  /* Real inner glow */
```
**Takeaway:** `shell/style.css` is the **single source of truth** for colors, transitions, materials, and styling. Always check actual code before relying on documentation.

---

### 4. Source of Truth #2: Automated Parameters (2 min)
```bash
./BaseConhecimento/ferramentas/consultar.py "dock" | head -20
# OR
cat BaseConhecimento/comparacao/parametros.json | jq '.parametros[] | select(.id=="SIS-01")'
```
**Takeaway:** `parametros.json` defines all audited parameters. Automated regex scanners parse real code files on each run to verify compliance.

---

### 5. Implementation Roadmap (4 min)
```bash
cat TODO.md
# For deep gap analysis:
cat BaseConhecimento/GAPS-SIS01-DOCK.md | head -100
```

---

### 6. Knowledge Map (2 min)
```bash
cat BaseConhecimento/INDICE-VISUAL-OTIMIZADO.md | head -40
```
**Takeaway:** Use this index to locate references, screenshots, and guidelines whenever deep context is required.

### 7. Visual Reference Triage (1 min)

Não abra todas as imagens originais para descobrir qual serve à task. Use o
catálogo semântico e o atlas de miniaturas primeiro:

```bash
# Busca por categoria, estado e uso recomendado
./BaseConhecimento/ferramentas/consultar.py --imagem "control center edit"
./BaseConhecimento/ferramentas/consultar.py --imagem "lock screen"

# Lista legível e atlas para triagem visual rápida
less BaseConhecimento/referencias/telas/CATALOGO-AGENTES.md
ls BaseConhecimento/referencias/telas/atlas/
```

O catálogo contém 65 telas com categoria, estado, prioridade (`golden`,
`canonical`, `secondary`), descrição, dimensões, hash e atlas correspondente.
Abra o original somente depois de escolher a referência, quando precisar medir
um detalhe ou comparar pixels. Frames de animação têm `sequencia.grupo`,
`ordem` e `total`, para serem lidos como uma sequência e não como telas soltas.

### Como uma IA multimodal deve ler uma referência

Uma imagem chega ao modelo como representação visual em regiões/tokens. O
modelo pode relacionar simultaneamente texto, posição, forma, cor, controles e
relações espaciais; ele não recebe apenas uma transcrição OCR.

Use este protocolo:

```text
1. catálogo      → encontre categoria, estado e prioridade
2. atlas         → reconheça composição, contexto e candidatos
3. original      → leia texto, detalhes, geometria e materiais
4. código        → compare a referência com a implementação real
5. decisão       → registre o que foi confirmado visualmente
```

O atlas é uma representação de triagem: serve para decidir qual imagem abrir e
para entender a composição geral. Não use a miniatura para medir tipografia,
alpha, raio, espaçamento ou pixels. Para esses detalhes, carregue o original e
observe a região relevante. Quando houver várias imagens do mesmo fluxo,
carregue a sequência na ordem indicada pelo catálogo para que o movimento e a
transformação entre estados sejam interpretados corretamente.

Se novas imagens forem adicionadas ou descrições mudarem:

```bash
python3 BaseConhecimento/ferramentas/catalogar_imagens.py
./BaseConhecimento/ferramentas/indexar.py
```

Para código, a recuperação equivalente é:

```bash
./BaseConhecimento/ferramentas/consultar.py --codigo "dock"
less BaseConhecimento/INDICE-CODIGO-AGENTES.md
```

Leia primeiro o resumo e os símbolos; carregue trechos e arquivos completos
somente quando a pergunta ainda não estiver respondida.

---

## 🔍 Standard Verification Workflow

Follow this procedure sequentially for any task or inspection:

```bash
# 1. ACTUAL CODE (Absolute source of truth)
grep -n "property-name" shell/style.css
# or inspect shell/hyprmac-shell, hypr/hyprmac.lua

# 2. STATUS & SPECS (Is it measured? What is the Apple reference?)
./BaseConhecimento/ferramentas/consultar.py "keyword"

# 3. VISUAL REFERENCE (cheap triage, then original)
./BaseConhecimento/ferramentas/consultar.py --imagem "keyword"
# inspect BaseConhecimento/referencias/telas/atlas/<categoria>.jpg
# open the original listed by the catalog only for measurement/comparison

# 4. IMPLEMENTATION & VALIDATION
# Make atomic changes, compile/test scripts, and re-run comparar.py
python3 -m py_compile shell/hyprmac-shell
./BaseConhecimento/ferramentas/comparar.py --resumo
```

---

## 🚨 Red Flags (Do NOT Trust)

| Pattern | Pitfall | Proper Source |
|---|---|---|
| Unverified numbers in markdown notes | May be stale or estimated | Check `shell/style.css` or `hypr/hyprmac.lua` |
| Guesses like "150ms", "250ms" | Unreferenced animation timing | Inspect CSS transitions in `shell/style.css` |
| "0.74 alpha on tiles" | Stale documentation | Real value is `0.22`–`0.50` (`shell/style.css:98`) |
| Unreferenced metrics | Numbers without `[real:file:line]` are guesses | Always verify against code and official kits |

---

## 📊 Where to Find Answers by Topic

```
"What is the actual background color of Control Center tiles?"
  → shell/style.css
  → search ".cc .tile" or ".cc .circle"

"Is parameter X implemented and verified?"
  → BaseConhecimento/comparacao/parametros.json
  → run ./BaseConhecimento/ferramentas/comparar.py --pendentes

"How should this component behave according to Apple HIG?"
  → BaseConhecimento/componentes/<component>.md
  → BaseConhecimento/padroes/<pattern>.md

"Which screenshot shows this UI in macOS Tahoe?"
  → BaseConhecimento/referencias/telas/CATALOGO-AGENTES.md
  → BaseConhecimento/referencias/telas/atlas/<categoria>.jpg
  → original listed by `consultar.py --imagem`

"What are the Hyprland window styling rules?"
  → hypr/hyprmac.lua (rounding = 22, rounding_power = 3.2, gaps = 0)
```

---

## 🔎 How to Query SQLite (`base.db`)

The database contains ~7,800 indexed documentation snippets with FTS5.

```bash
cd BaseConhecimento

# Text search across knowledge base
./ferramentas/consultar.py "dock glass"
./ferramentas/consultar.py "control center material"

# View full snippet text
./ferramentas/consultar.py "liquid glass" --completo

# Search specific document types (-t)
./ferramentas/consultar.py "dock" -t componente
./ferramentas/consultar.py "dock" -t hig

# Search by color name
./ferramentas/consultar.py --cor blue

# Search by typography style
./ferramentas/consultar.py --tipografia body

# Search screenshots by visual description
./ferramentas/consultar.py --imagem "control center"

# Search code metadata without loading full files
./ferramentas/consultar.py --codigo "control center"

# Search the structured visual catalog; returns category, state, priority,
# dimensions, description, and the triage atlas path
./ferramentas/consultar.py --imagem "control center edit"

# Direct SQL query
./ferramentas/consultar.py --sql "SELECT id, parametro, status FROM parametros WHERE status='conforme'"
```

---

## 🗂️ Project Directory Tree

```
hyprmac/
├── CLAUDE.md ............................ Core rules & instructions for AI
├── ONBOARDING.md ........................ This 15-minute quick start guide
├── TODO.md .............................. Roadmap & pending tasks
├── install.sh ........................... Idempotent installation script
│
├── shell/ ............................... Python / GTK Wayland LayerShell apps
│   ├── hyprmac-shell .................... Main shell (Dock, Control Center, Spotlight, Widgets)
│   ├── hyprmac-ajustes .................. System Settings replica
│   ├── hyprmac-lock ..................... Session lock screen (PAM + ext-session-lock)
│   ├── hyprmac-overview ................. Mission Control & App Exposé
│   ├── style.css ........................ ⭐ SOURCE OF TRUTH FOR STYLES & TOKENS
│   └── ocioso/ .......................... Idle monitor daemon
│
├── hypr/ ................................ Hyprland configuration
│   ├── hyprmac.lua ...................... Window rules, squircle rounding, shadows, blur
│   └── hyprglass/ ....................... Liquid Glass shader patches
│
├── waybar/ .............................. Top menu bar (34pt)
│   ├── config.jsonc ..................... Dynamic global menu bar & tray modules
│   └── style.css ........................ Waybar styling
│
├── scripts/ ............................. CLI tools
│   ├── theme ............................ Dark/light mode switcher
│   ├── captura .......................... Screenshots & screen recording (⇧⌘3, ⇧⌘4, ⇧⌘5)
│   ├── janela ........................... Window minimization & app management
│   └── acessibilidade ................... Transparency & contrast toggles
│
└── BaseConhecimento/ .................... Knowledge Base
    ├── base.db .......................... SQLite FTS5 + code/image catalogs
    ├── ferramentas/ ..................... CLI lookup, indexing, & comparison scripts
    ├── comparacao/ ...................... parametros.json & MATRIZ.md
    ├── componentes/ ..................... Component design specifications
    ├── padroes/ ......................... Cross-cutting design patterns
    ├── referencias/ ..................... Screenshots, catalog, atlases, UI kits, fonts, cursors
    └── hig/ ............................. Apple Human Interface Guidelines
```

---

## ⏱️ Pre-Work Checklist

- [x] Read `AGENTS.md` and `BaseConhecimento/INDICE-AGENTES.md` (project rules and task map)
- [x] Verified `shell/style.css` is the source of truth for styles
- [x] Tested `./BaseConhecimento/ferramentas/consultar.py`
- [x] Used the visual catalog/atlas before opening a reference original
- [x] Checked current compliance with `./BaseConhecimento/ferramentas/comparar.py --resumo`
- [x] Located pending items in `TODO.md`
- [x] Remember: measure, verify, and validate against code—never guess!
