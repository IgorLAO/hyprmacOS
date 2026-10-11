# ⚠️ CORRECTION — Real Code Metrics vs Unverified Estimates

**Date:** 2026-10-03  
**Problem:** Early draft documents contained unverified timing and opacity estimates.  
**Solution:** This document explicitly distinguishes between **REAL metrics in actual code** and **ESTIMATES inferred from video frames**.

---

## 🔴 UNVERIFIED NUMBERS (DO NOT USE)

### In EFEITOS-ANIMACOES-DETALHES.md

| Unverified Draft Number | Status | Real Value in Code | Code Source |
|---|---|---|---|
| "150ms hover" | ❌ Guess | 160ms | `shell/style.css:108` |
| "250ms window" | ❌ Unverified | Needs code measurement | `hypr/hyprmac.lua` |
| "200ms glow" | ❌ Guess | 40ms (active), 260ms (dissipate) | `shell/style.css:136-108` |
| "100ms press" | ❌ Unverified | Needs code measurement | `shell/style.css` |

### In ANALISE-COMPLETA.md

| Unverified Draft Number | Status | Real Value in Code | Code Source |
|---|---|---|---|
| "Dock α 0.74" | ❌ **ERRONEOUS** | 0.22 (rest), 0.30 (hover), 0.50 (active) | `shell/style.css:98, 125, 133` |
| "Control Center α 0.74" | ❌ **ERRONEOUS** | 0.22 (rest), 0.30 (hover), 0.50 (active) | Same as above |
| "Menus α 0.50" | 🟡 Unverified | Verify in `shell/hyprmac-shell` / `waybar` | CSS styles |
| "Glow inset box-shadow" | ✅ Verified | `inset 0 0 18px rgba(255,255,255,0.34)` | `shell/style.css:134` |

---

## ✅ CONFIRMED METRICS (SOURCE CODE)

**Source:** `shell/style.css`

### Control Center Tiles (`.cc .tile`, `.cc .circle`)

```css
/* Rest */
background-color: rgba(128, 128, 142, 0.22);
border-color: rgba(255, 255, 255, 0.55) 0.18 / 0.08 / 0.18;
box-shadow: inset 0 1px 1px rgba(255, 255, 255, 0.22),
            inset 0 -1px 1px rgba(0, 0, 0, 0.04);

/* Hover */
background-color: rgba(152, 152, 166, 0.30);

/* Active (glow "illuminates from within") */
background-color: rgba(175, 175, 186, 0.50);
box-shadow: inset 0 0 18px rgba(255, 255, 255, 0.34),
            inset 0 1px 1px rgba(255, 255, 255, 0.30);

/* Timing */
transition: background-color 160ms ease-out, box-shadow 260ms ease-out;
/* When activating glow */
transition: background-color 40ms ease-out, box-shadow 40ms ease-out;
```

**Interpretation:**
- Rest: **α 0.22** (translucent, lets background pass through)
- Hover: **α 0.30** (subtle highlight)
- Active: **α 0.50** (strong inner illumination)
- Inner glow color: **rgba(255,255,255,0.34)** on active
- Standard transition: **160ms background + 260ms shadow**
- Activation transition: **40ms** (instant sensory feedback)

### Borders & Lighting Highlights

```css
/* Top specular edge highlight */
border-color: rgba(255,255,255, 0.55) /* top */
              rgba(255,255,255, 0.18) /* right */
              rgba(255,255,255, 0.08) /* bottom */
              rgba(255,255,255, 0.18); /* left */

/* Top inner bevel shadow */
inset 0 1px 1px rgba(255,255,255, 0.22);

/* Bottom inner ambient occlusion */
inset 0 -1px 1px rgba(0,0,0, 0.04);
```

---

## 🟡 ESTIMATED METRICS (USE WITH CAUTION)

Inferred from visual inspection of 4K video frames:

| Element | Visual Estimate | Confidence | Note |
|---|---|---|---|
| Window open/close | ~250ms | LOW | Inferred from video; Hyprland config governs actual timing |
| Menu item hover | ~150–160ms | MEDIUM | Consistent with actual code (`160ms`) |
| Scroll transitions | ~200ms | LOW | Speculative |
| Modal appearance | ~300ms | LOW | Visual estimate |

**Rule:** Only rely on estimated metrics when actual code implementations do not yet exist.

---

## 🔧 Agent Guidance

1. **Verify every number:** Check code (`shell/style.css`, `hypr/hyprmac.lua`) before documenting.
2. **Flag estimates:** Label any inferred metric with "🟡 ESTIMATED" along with its frame or video citation.
3. **Primary source of truth:** Code files and `parametros.json` with regex measurement.
