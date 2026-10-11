#!/usr/bin/env python3
"""Delega tarefas pequenas a modelos auxiliares pelo gateway FreeLLM.

O gateway (http://localhost:3001) só oferece inferência compatível com OpenAI;
não há runtime de agentes. Cada "agente" é uma chamada sem estado e sem
ferramentas: o orquestrador escolhe o contexto, o auxiliar responde e o
orquestrador valida. Nada aqui altera arquivos do projeto.

  agentes.py modelos                         modelos expostos pelo gateway
  agentes.py rodar ID -p papel -t tarefa.md [-c arq[:ini-fim] ...] [-m modelo]
  agentes.py lote manifesto.json [-j 3]      tarefas independentes em paralelo
  agentes.py estado [ID]                     histórico registrado em .agentes/

Chave: FREELLMAPI_API_KEY ou a configuração local do gateway
(FREELLM_DB, padrão ~/Projects/freellmapi/server/data/freeapi.db). Nunca é
impressa nem gravada. Respostas iguais (modelo + mensagens) vêm do cache.
"""
import argparse
import concurrent.futures
import hashlib
import json
import os
import sqlite3
import sys
import time
import urllib.error
import urllib.request

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DIR = os.path.join(RAIZ, ".agentes")
URL = os.environ.get("FREELLM_URL", "http://localhost:3001")
DB = os.environ.get("FREELLM_DB", os.path.expanduser("~/Projects/freellmapi/server/data/freeapi.db"))
MODELO_PADRAO = os.environ.get("FREELLM_MODELO", "auto")
LIMITE_CONTEXTO = 60_000  # caracteres por tarefa; contexto mínimo é a regra

PAPEIS = {
    "pesquisa": "Você é um agente de pesquisa do projeto HyprMac (reprodução do macOS Tahoe 26 no Hyprland). "
                "Responda só com base no contexto fornecido. Separe fatos citados (com arquivo:linha) de inferências. "
                "Se o contexto não sustentar uma conclusão, diga 'sem evidência'.",
    "engenharia-reversa": "Você analisa recursos extraídos do macOS Tahoe 26 (plists, strings, dumps de símbolos). "
                          "Cite exatamente o trecho que sustenta cada parâmetro. Nunca invente valores numéricos.",
    "implementacao": "Você implementa tarefas pequenas em Python seguindo o estilo do código fornecido. "
                     "Responda apenas com blocos de código completos e uma lista curta de suposições. Não use dependências novas.",
    "auditoria-visual": "Você compara implementação e referência descritas no contexto. Liste diferenças objetivas "
                        "(geometria, cor, tipografia, comportamento) com valores. Não afirme validações que não realizou.",
    "testes": "Você escreve testes unittest/pytest determinísticos para o código fornecido, cobrindo bordas. "
              "Responda só com o código do teste e uma lista do que não foi coberto.",
}


def chave():
    k = os.environ.get("FREELLMAPI_API_KEY")
    if k:
        return k
    try:
        con = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
        row = con.execute("SELECT value FROM settings WHERE key='unified_api_key'").fetchone()
        con.close()
    except sqlite3.Error:
        row = None
    if not row:
        sys.exit("FreeLLM: defina FREELLMAPI_API_KEY ou FREELLM_DB (chave não encontrada)")
    return row[0]


def http(caminho, corpo=None, timeout=420):
    req = urllib.request.Request(URL + caminho, method="POST" if corpo else "GET",
                                 data=json.dumps(corpo).encode() if corpo else None,
                                 headers={"Authorization": f"Bearer {chave()}", "Content-Type": "application/json"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def contexto(especs):
    """'arq', 'arq:10-80' ou 'arq:10' → blocos numerados; caminhos relativos à raiz."""
    partes = []
    for e in especs or []:
        arq, _, faixa = e.partition(":") if not os.path.exists(e) else (e, "", "")
        cam = arq if os.path.isabs(arq) else os.path.join(RAIZ, arq)
        linhas = open(cam, encoding="utf-8", errors="replace").read().splitlines()
        ini, fim = 1, len(linhas)
        if faixa:
            a, _, b = faixa.partition("-")
            ini, fim = int(a), int(b or a)
        corpo = "\n".join(f"{n}\t{linhas[n - 1]}" for n in range(ini, min(fim, len(linhas)) + 1))
        partes.append(f"### {os.path.relpath(cam, RAIZ)}:{ini}-{fim}\n{corpo}")
    texto = "\n\n".join(partes)
    if len(texto) > LIMITE_CONTEXTO:
        sys.exit(f"contexto com {len(texto)} caracteres excede {LIMITE_CONTEXTO}; recorte as faixas")
    return texto


def rodar(tid, papel, tarefa, especs=(), modelo=None, criterios="", tentativas=3, max_tokens=16000):
    modelo = modelo or MODELO_PADRAO
    ctx = contexto(especs)
    usuario = f"## Tarefa {tid}\n{tarefa}\n"
    if criterios:
        usuario += f"\n## Critérios de conclusão\n{criterios}\n"
    if ctx:
        usuario += f"\n## Contexto\n{ctx}\n"
    msgs = [{"role": "system", "content": PAPEIS[papel]}, {"role": "user", "content": usuario}]
    h = hashlib.sha256(json.dumps([modelo, msgs], ensure_ascii=False).encode()).hexdigest()[:16]
    pasta = os.path.join(DIR, tid)
    os.makedirs(pasta, exist_ok=True)
    meta_p = os.path.join(pasta, "meta.json")
    if os.path.exists(meta_p):
        meta = json.load(open(meta_p))
        if meta.get("hash") == h and meta.get("estado") == "respondido":
            meta["cache"] = True
            return meta
    open(os.path.join(pasta, "prompt.md"), "w").write(usuario)
    meta = {"id": tid, "papel": papel, "modelo_pedido": modelo, "hash": h, "contexto": list(especs),
            "inicio": time.strftime("%Y-%m-%dT%H:%M:%S"), "estado": "executando", "tentativas": 0}
    erro = None
    for n in range(1, tentativas + 1):
        meta["tentativas"] = n
        t0 = time.monotonic()
        try:
            d = http("/v1/chat/completions", {"model": modelo, "messages": msgs, "max_tokens": max_tokens,
                                              "temperature": 0.2})
        except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as e:
            corpo = e.read().decode(errors="replace")[:300] if isinstance(e, urllib.error.HTTPError) else ""
            erro = f"{type(e).__name__}: {e} {corpo}".strip()
            time.sleep(2 * n)
            continue
        txt = ((d.get("choices") or [{}])[0].get("message") or {}).get("content") or ""
        if not txt.strip():
            erro = f"resposta vazia: {json.dumps(d)[:300]}"
            continue
        open(os.path.join(pasta, "resposta.md"), "w").write(txt)
        meta.update(estado="respondido", modelo_usado=d.get("model"), uso=d.get("usage"),
                    segundos=round(time.monotonic() - t0, 1), erro=None, revisao="pendente")
        break
    else:
        meta.update(estado="falhou", erro=erro)
    json.dump(meta, open(meta_p, "w"), ensure_ascii=False, indent=1)
    return meta


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("modelos")
    r = sub.add_parser("rodar")
    r.add_argument("id")
    r.add_argument("-p", "--papel", choices=PAPEIS, required=True)
    r.add_argument("-t", "--tarefa", required=True, help="texto ou caminho de arquivo")
    r.add_argument("-c", "--contexto", nargs="*", default=[])
    r.add_argument("-k", "--criterios", default="")
    r.add_argument("-m", "--modelo")
    lt = sub.add_parser("lote")
    lt.add_argument("manifesto")
    lt.add_argument("-j", type=int, default=3)
    e = sub.add_parser("estado")
    e.add_argument("id", nargs="?")
    e.add_argument("--revisao", choices=["aprovado", "corrigido", "rejeitado"])
    e.add_argument("--nota", default="")
    a = ap.parse_args()

    if a.cmd == "modelos":
        for m in http("/v1/models").get("data", []):
            print(m["id"])
    elif a.cmd == "rodar":
        t = open(a.tarefa).read() if os.path.isfile(a.tarefa) else a.tarefa
        m = rodar(a.id, a.papel, t, a.contexto, a.modelo, a.criterios)
        print(json.dumps({k: m.get(k) for k in ("id", "estado", "modelo_usado", "segundos", "uso", "erro", "cache")},
                         ensure_ascii=False))
    elif a.cmd == "lote":
        tarefas = json.load(open(a.manifesto))
        with concurrent.futures.ThreadPoolExecutor(max_workers=max(1, min(a.j, 6))) as ex:
            futs = {ex.submit(rodar, t["id"], t["papel"],
                              open(t["tarefa"]).read() if os.path.isfile(t["tarefa"]) else t["tarefa"],
                              t.get("contexto", []), t.get("modelo"), t.get("criterios", "")): t["id"] for t in tarefas}
            for f in concurrent.futures.as_completed(futs):
                m = f.result()
                print(f"{m['id']}: {m['estado']} {m.get('modelo_usado') or ''} {m.get('segundos') or ''}s {m.get('erro') or ''}")
    elif a.cmd == "estado":
        if a.id and a.revisao:
            p = os.path.join(DIR, a.id, "meta.json")
            m = json.load(open(p))
            m.update(revisao=a.revisao, nota_revisao=a.nota, revisado_em=time.strftime("%Y-%m-%dT%H:%M:%S"))
            json.dump(m, open(p, "w"), ensure_ascii=False, indent=1)
        ids = [a.id] if a.id else sorted(os.listdir(DIR)) if os.path.isdir(DIR) else []
        for i in ids:
            if not os.path.isfile(os.path.join(DIR, i, "meta.json")):
                continue   # fila.db, iso/ e tarefas do orquestra.py
            m = json.load(open(os.path.join(DIR, i, "meta.json")))
            print(f"{i}\t{m['papel']}\t{m['estado']}\t{m.get('modelo_usado')}\trevisão={m.get('revisao')}\t{m.get('nota_revisao', '')}")


if __name__ == "__main__":
    main()
