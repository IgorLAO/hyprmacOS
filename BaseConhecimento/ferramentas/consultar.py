#!/usr/bin/env python3
"""Consulta a Base de Conhecimento (base.db).

  consultar.py <termos>                 busca de texto completo (FTS5, ranking bm25; 5 fontes)
  consultar.py <termos> -t hig          filtra por tipo: componente padrao hig wwdc dev pdf contorno token tela
  consultar.py <termos> -n 20           quantidade de resultados (padrão 5)
  consultar.py <termos> --completo      mostra o trecho inteiro, não só o recorte
  consultar.py --cor blue               cores dos kits cujo nome contém o termo
  consultar.py --tipo body              estilos de texto
  consultar.py --estilo "glass/dark/menus"  estilos de camada (materiais, vidro…) com a receita
  consultar.py --imagem "control center"    catálogo visual por categoria, estado e descrição
  consultar.py --codigo "dock"              arquivos e símbolos candidatos, sem ler o código inteiro
  consultar.py --registro "hyprglass"        decisões e análises curadas
  consultar.py --documento "componentes/dock.md"  proveniência e estado da fonte
  consultar.py "dock" --historico            somente fontes arquivadas/substituídas/inválidas
  consultar.py --sql "SELECT …"          SQL somente leitura

Sintaxe FTS5: "frase exata", termo*, A OR B, NOT C, NEAR(a b, 5). Sem acentos/caixa.
"""
import argparse
import json
import os
import re
import sqlite3
import sys
import unicodedata

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(BASE, "base.db")


def fts_query(texto):
    """Termos soltos viram AND com prefixo; se já tem sintaxe FTS, usa como veio."""
    if re.search(r'["()*]|\b(OR|AND|NOT|NEAR)\b', texto):
        return texto
    termos = re.findall(r"[\w#./-]+", texto, re.UNICODE)
    return " ".join(f'"{t}"*' for t in termos)


def like(db, tabela, colunas, termo):
    cond = " AND ".join(f"lower({' || \" \" || '.join(colunas)}) LIKE ?" for _ in termo.split())
    return db.execute(f"SELECT * FROM {tabela} WHERE {cond}", [f"%{t.lower()}%" for t in termo.split()]).fetchall()


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("termos", nargs="*")
    ap.add_argument("-t", "--tipo-trecho", dest="tipo")
    ap.add_argument("-n", type=int, default=5)
    ap.add_argument("--completo", action="store_true")
    ap.add_argument("--cor")
    ap.add_argument("--tipo-texto", "--tipografia", dest="tipografia")
    ap.add_argument("--estilo")
    ap.add_argument("--imagem")
    ap.add_argument("--codigo")
    ap.add_argument("--registro")
    ap.add_argument("--documento")
    grupo = ap.add_mutually_exclusive_group()
    grupo.add_argument("--historico", action="store_true")
    grupo.add_argument("--todos", action="store_true")
    ap.add_argument("--sql")
    a = ap.parse_args()
    if not 1 <= a.n <= 20:
        ap.error("-n deve estar entre 1 e 20")
    if not os.path.exists(DB):
        sys.exit(f"sem índice: rode {os.path.join(BASE, 'ferramentas/indexar.py')}")
    # Até --sql é leitura: consultas de agentes não podem alterar a fonte canônica.
    db = sqlite3.connect(f"file:{DB}?mode=ro", uri=True)
    db.execute("PRAGMA query_only=ON")

    if a.sql:
        for r in db.execute(a.sql):
            print(" | ".join(str(x) for x in r))
        return
    if a.documento:
        db.row_factory = sqlite3.Row
        row = db.execute("SELECT * FROM documentos WHERE caminho=?", (a.documento,)).fetchone()
        print(json.dumps(dict(row), ensure_ascii=False, indent=2) if row else "documento não registrado")
        return
    if a.registro:
        estados = "" if a.todos else (" AND r.estado IN ('archived','superseded','invalid')" if a.historico
                                  else " AND r.estado IN ('verified','experimental')")
        rows = db.execute("SELECT r.id,r.tipo,r.componente,r.estado,r.versao_macos,r.titulo,r.resumo,"
                          "r.evidencia,r.fonte_caminho,r.fonte_url,r.confianca,r.implementacao,"
                          "bm25(registros_fts) AS rank FROM registros_fts "
                          "JOIN registros r ON r.rowid=registros_fts.rowid "
                          "WHERE registros_fts MATCH ?" + estados + " ORDER BY rank LIMIT ?",
                          (fts_query(a.registro), a.n)).fetchall()
        for ident, tipo, comp, estado, versao, titulo, resumo, evid, fonte, url, conf, impl, _ in rows:
            print(f"\n■ {ident} [{estado}; {versao}; {conf}] {tipo} · {comp or '—'}\n  {titulo}\n  {resumo}")
            print(f"  Evidência: {evid or '—'} · Fonte: {url or fonte or '—'} · Código: {impl or '—'}")
        if not rows:
            print("nenhum registro com estes filtros")
        return
    if a.cor:
        for kit, grupo, nome, hx, css in like(db, "cores", ["kit", "grupo", "nome"], a.cor)[:a.n]:
            print(f"{kit:9s} {grupo + '/' + nome:62s} {hx:12s} {css}")
        return
    if a.tipografia:
        for r in like(db, "tipografia", ["kit", "nome", "fonte"], a.tipografia)[:a.n]:
            print(f"{r[0]:9s} {r[1]:55s} {r[2]} {r[3]:g}/{r[4] or 0:g} {r[5]}")
        return
    if a.estilo:
        for kit, nome, js in like(db, "estilos", ["kit", "nome"], a.estilo)[:a.n]:
            print(f"\n■ {kit} · {nome}")
            for k, v in json.loads(js).items():
                print(f"   {k}: {json.dumps(v, ensure_ascii=False)}")
        return
    if a.imagem:
        # O catálogo estruturado é a primeira camada: retorna sem abrir o
        # original e expõe o atlas de triagem, a prioridade e os estados.
        try:
            termos = a.imagem.lower().split()
            todos = db.execute(
                "SELECT caminho, categoria, estado, prioridade, titulo, descricao, uso, largura, altura, triagem, classificacao_fonte, confianca, sequencia "
                "FROM imagens_catalogo ORDER BY CASE prioridade WHEN 'golden' THEN 0 WHEN 'canonical' THEN 1 ELSE 2 END, caminho").fetchall()

            def sem_acento(texto):
                return "".join(c for c in unicodedata.normalize("NFD", texto.lower())
                               if unicodedata.category(c) != "Mn")

            def casa(row):
                texto = sem_acento(" ".join(str(x or "") for x in row))
                return all(re.search(r"(?<![\w])" + re.escape(sem_acento(t)) + r"(?![\w])", texto)
                           for t in termos)

            rows = [row for row in todos if casa(row)][:a.n]
        except sqlite3.OperationalError:
            rows = []
        for caminho, categoria, estado, prioridade, titulo, desc, uso, largura, altura, triagem, fonte, confianca, sequencia in rows:
            print(f"\n■ [{prioridade}] {categoria} · {estado}\n  {os.path.join(BASE, caminho)}")
            print(f"  {titulo} — {desc}")
            seq = ""
            if sequencia and sequencia != "null":
                try:
                    s = json.loads(sequencia)
                    seq = f" · sequência: {s['grupo']} {s['ordem']}/{s['total']}"
                except (KeyError, TypeError, json.JSONDecodeError):
                    seq = f" · sequência: {sequencia}"
            print(f"  uso: {uso} · dimensão: {largura}×{altura} · triagem: {os.path.join(BASE, 'referencias/telas', triagem)}")
            print(f"  classificação: {fonte} ({confianca}){seq}")
        if rows:
            return
        for caminho, desc, origem in like(db, "imagens", ["caminho", "descricao"], a.imagem)[:a.n]:
            print(f"{os.path.join(BASE, caminho)}\n    {desc[:220]}  [{origem}]")
        return
    if a.codigo:
        try:
            termos = a.codigo.lower().split()
            rows = db.execute(
                "SELECT caminho, linguagem, linhas, resumo, simbolos, imports, tags "
                "FROM codigo_catalogo ORDER BY linhas DESC").fetchall()
            def norm(texto):
                sem_acento = "".join(c for c in unicodedata.normalize("NFD", str(texto or "").lower())
                                     if unicodedata.category(c) != "Mn")
                return re.sub(r"[_/.-]+", " ", sem_acento)
            rows = [r for r in rows if all(re.search(r"(?<![\w])" + re.escape(norm(t)) + r"(?![\w])",
                                                       norm(" ".join(str(x or "") for x in r))) for t in termos)]
            rows.sort(key=lambda r: (not all(t in norm(os.path.basename(r[0])).split() for t in termos),
                                     -r[2]))
            rows = rows[:a.n]
        except sqlite3.OperationalError:
            rows = []
        for caminho, linguagem, linhas, resumo, simbolos, imps, tags in rows:
            print(f"\n■ {caminho} · {linguagem} · {linhas} linhas")
            print(f"  {resumo}")
            compact_symbols = ", ".join((simbolos or "").split(", ")[:12])
            print(f"  símbolos: {compact_symbols or '—'}")
            print(f"  imports: {imps or '—'} · tags: {tags or '—'}")
        return
    if not a.termos:
        ap.print_help()
        return

    q = fts_query(" ".join(a.termos))
    estados = "" if a.todos else (" AND d.estado IN ('archived','superseded','invalid')" if a.historico
                                  else " AND d.estado IN ('verified','experimental')")
    # Agregue pelo arquivo antes de gerar snippets. Isso evita dezenas de
    # trechos do mesmo contorno/relatório e limita o trabalho ao resultado final.
    sql = ("WITH candidatos AS MATERIALIZED ("
           "SELECT trechos.rowid AS rid, trechos.caminho, trechos.tipo, trechos.titulo, trechos.secao, "
           "d.estado, d.versao_macos, "
           "(bm25(trechos, 1.0, 4.0, 3.0) "
           "- CASE trechos.tipo WHEN 'componente' THEN 0.15 WHEN 'padrao' THEN 0.10 ELSE 0 END "
           "- CASE d.versao_macos WHEN 'Tahoe 26' THEN 0.08 WHEN 'macOS 27 (declared)' THEN -0.05 ELSE 0 END) AS rank "
           "FROM trechos JOIN documentos d ON d.caminho=trechos.caminho WHERE trechos MATCH ?"
           + estados + (" AND trechos.tipo = ?" if a.tipo else "")
           + ") SELECT caminho,tipo,titulo,secao,estado,versao_macos,rid,MIN(rank) AS melhor "
           "FROM candidatos GROUP BY caminho ORDER BY melhor LIMIT ?")
    args = [q] + ([a.tipo] if a.tipo else []) + [a.n]
    rows = db.execute(sql, args).fetchall()
    if not rows:
        print(f"nada para: {q}")
    for caminho, tipo, titulo, secao, estado, versao, rid, _r in rows:
        if a.completo:
            texto = db.execute("SELECT conteudo FROM trechos WHERE rowid=?", (rid,)).fetchone()[0]
        else:
            texto = db.execute("SELECT snippet(trechos, 0, '»', '«', ' … ', 40) FROM trechos "
                               "WHERE trechos MATCH ? AND rowid=?", (q, rid)).fetchone()[0]
        print(f"\n■ [{tipo}; {estado}; {versao}] {titulo} › {secao}\n  {os.path.join(BASE, caminho)}")
        print("  " + texto.strip().replace("\n", "\n  "))


if __name__ == "__main__":
    main()
