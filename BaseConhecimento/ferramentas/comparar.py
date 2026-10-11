#!/usr/bin/env python3
"""Compara o hyprmac com a referência Apple usando comparacao/parametros.json.

  comparar.py              relê os valores atuais do hyprmac, recalcula status e gera
                           comparacao/MATRIZ.md + tabela `parametros` no base.db
  comparar.py --resumo     só imprime a nota por área no terminal
  comparar.py --pendentes  lista o que não está conforme, por prioridade

Parâmetros com `leitura` {arquivo, regex[, divisor_regex][, igual]} são medidos no código:
  - com `alvo` + `tolerancia`: conforme se |valor − alvo| ≤ tolerância; próximo se ≤ 3× a tolerância (ou 10% do alvo);
    senão diverge;
  - com `igual`: conforme se o texto lido (sem caixa) for igual.
Os demais usam o `status` escrito à mão no JSON.
Nota de uma área = Σ peso·pontos / Σ peso (conforme 1, próximo 0.5, diverge/ausente 0;
"limitacao" não entra).
"""
import json
import os
import re
import sqlite3
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(BASE)
PARAMS = os.path.join(BASE, "comparacao", "parametros.json")
MATRIZ = os.path.join(BASE, "comparacao", "MATRIZ.md")
DB = os.path.join(BASE, "base.db")
PONTOS = {"conforme": 1.0, "proximo": 0.5, "diverge": 0.0, "ausente": 0.0}
ICONE = {"conforme": "✅", "proximo": "🟡", "diverge": "🔴", "ausente": "⬜", "limitacao": "➖"}


def ler(p):
    """Lê o valor atual no repositório; devolve (texto, número ou None) ou (None, None)."""
    le = p.get("leitura")
    if not le:
        return None, None
    try:
        txt = open(os.path.join(REPO, le["arquivo"]), encoding="utf-8").read()
    except OSError:
        return "arquivo não encontrado", None
    m = re.search(le["regex"], txt, re.M)
    if not m:
        return "não encontrado (regex)", None
    val = m.group(1)
    if le.get("divisor_regex"):
        d = re.search(le["divisor_regex"], txt, re.M)
        if d:
            num = float(val) / float(d.group(1))
            return f"{val} ÷ {d.group(1)} = {num:.3f}", num
    try:
        return val, float(val)
    except ValueError:
        return val, None


def avaliar(p):
    texto, num = ler(p)
    if texto is not None:
        p["hyprmac"] = texto
        p["medido"] = True
        le = p["leitura"]
        if le.get("igual"):
            p["status"] = "conforme" if texto.lower() == le["igual"].lower() else "diverge"
        elif num is not None and "alvo" in p:
            dif = abs(num - p["alvo"])
            tol = p.get("tolerancia", 0)
            if dif <= tol + 1e-9:
                p["status"] = "conforme"
            elif dif <= max(3 * tol, 0.10 * abs(p["alvo"])):
                p["status"] = "proximo"
            else:
                p["status"] = "diverge"
        elif "status" not in p:
            p["status"] = "diverge"
    p.setdefault("status", "ausente")
    p.setdefault("hyprmac", "—")
    return p


def notas(ps):
    areas = {}
    for p in ps:
        a = areas.setdefault(p["area"], {"soma": 0.0, "peso": 0, "itens": []})
        a["itens"].append(p)
        if p["status"] in PONTOS:
            a["soma"] += PONTOS[p["status"]] * p.get("peso", 1)
            a["peso"] += p.get("peso", 1)
    return areas


def main():
    d = json.load(open(PARAMS))
    obrigatorios = {"id", "area", "parametro", "apple", "prioridade"}
    for i, p in enumerate(d["parametros"]):
        faltam = obrigatorios - p.keys()
        if faltam:
            raise ValueError(f"parametros.json: registro {i} sem {', '.join(sorted(faltam))}")
    ps = [avaliar(p) for p in d["parametros"]]
    areas = notas(ps)
    total_s = sum(a["soma"] for a in areas.values())
    total_p = sum(a["peso"] for a in areas.values())

    if "--resumo" in sys.argv:
        for nome, a in areas.items():
            print(f"{nome:28s} {100 * a['soma'] / a['peso']:5.0f}%  ({len(a['itens'])} parâmetros)")
        print(f"{'TOTAL':28s} {100 * total_s / total_p:5.0f}%")
        return
    if "--pendentes" in sys.argv:
        for prio in ("P1", "P2", "P3"):
            for p in ps:
                if p["prioridade"] == prio and p["status"] not in ("conforme", "limitacao"):
                    print(f"{prio} {ICONE[p['status']]} {p['id']:8s} {p['parametro']} — Apple: {p['apple']} · hyprmac: {p['hyprmac']}")
        return

    out = ["# Matriz de comparação — hyprmac × Apple (macOS Tahoe/27)", "",
           "Gerada por `ferramentas/comparar.py` a partir de `comparacao/parametros.json`. "
           "Valores marcados com 📏 foram **lidos do código agora**; os outros foram avaliados à mão.", "",
           "Legenda: ✅ conforme · 🟡 próximo · 🔴 diverge · ⬜ ausente · ➖ limitação do Linux (não conta). "
           "Prioridade: **P1** visível/perigoso · **P2** notável · **P3** detalhe.", "",
           f"## Nota geral: **{100 * total_s / total_p:.0f}%**", "",
           "| Área | Nota | ✅ | 🟡 | 🔴 | ⬜ |", "|---|---|---|---|---|---|"]
    for nome, a in areas.items():
        c = {s: sum(1 for p in a["itens"] if p["status"] == s) for s in ICONE}
        out.append(f"| {nome} | {100 * a['soma'] / a['peso']:.0f}% | {c['conforme']} | {c['proximo']} | "
                   f"{c['diverge']} | {c['ausente']} |")
    out += ["", "## Pendências P1", ""]
    for p in ps:
        if p["prioridade"] == "P1" and p["status"] not in ("conforme", "limitacao"):
            out.append(f"- {ICONE[p['status']]} **{p['id']} {p['parametro']}** — Apple: {p['apple']}; hyprmac: {p['hyprmac']}")
    for nome, a in areas.items():
        out += ["", f"## {nome} — {100 * a['soma'] / a['peso']:.0f}%", "",
                "| ID | Parâmetro | Apple | hyprmac | | Prio | Onde | Fonte |", "|---|---|---|---|---|---|---|---|"]
        for p in a["itens"]:
            med = " 📏" if p.get("medido") else ""
            nota = f"<br>_{p['nota']}_" if p.get("nota") else ""
            out.append(f"| {p['id']} | {p['parametro']} | {p['apple']} | {p['hyprmac']}{med}{nota} | "
                       f"{ICONE[p['status']]} | {p['prioridade']} | `{p.get('onde', '')}` | {p.get('fonte', '')} |")
    out += ["", "## Como medir cada um", ""]
    out += [f"- **{p['id']}** — {p.get('medir', '')}" for p in ps]
    open(MATRIZ, "w").write("\n".join(out) + "\n")

    if os.path.exists(DB):
        db = sqlite3.connect(DB)
        db.execute("DROP TABLE IF EXISTS parametros")
        db.execute("CREATE TABLE parametros (id TEXT PRIMARY KEY, area TEXT, parametro TEXT, apple TEXT, "
                   "hyprmac TEXT, status TEXT, prioridade TEXT, peso INT, onde TEXT, fonte TEXT, medir TEXT, nota TEXT)")
        db.executemany("INSERT INTO parametros VALUES (?,?,?,?,?,?,?,?,?,?,?,?)",
                       [(p["id"], p["area"], p["parametro"], p["apple"], p["hyprmac"], p["status"], p["prioridade"],
                         p.get("peso", 1), p.get("onde"), p.get("fonte"), p.get("medir"), p.get("nota")) for p in ps])
        db.commit()
    print(f"{len(ps)} parâmetros · nota geral {100 * total_s / total_p:.0f}% → {MATRIZ}")


if __name__ == "__main__":
    main()
