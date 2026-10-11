#!/usr/bin/env python3
"""Monta o índice SQLite da Base de Conhecimento (BaseConhecimento/base.db).

  indexar.py            atualiza somente fontes textuais alteradas por SHA-256;
                        preserva metadados e registros curados no mesmo banco.

Tabelas:
  trechos (FTS5)  texto de tudo, quebrado por seção — busca de texto completo com ranking bm25
                  colunas: conteudo, titulo, secao, caminho, tipo
  cores           swatches dos kits (kit, grupo, nome, hex, css)
  tipografia      estilos de texto dos kits (kit, nome, fonte, tamanho, entrelinha, cor)
  estilos         estilos de camada dos kits (kit, nome, json) — materiais, vidro, controles
  imagens         figuras com descrição (caminho, descricao, origem)
  imagens_catalogo catálogo visual estruturado (categoria, estado, prioridade, dimensão, atlas)
  codigo_catalogo índice leve de arquivos, símbolos, imports e tags para recuperação progressiva
  parametros      matriz hyprmac × Apple (gerada por comparar.py, chamado no fim)

Tipos de trecho: componente, padrao, hig, wwdc, pdf, contorno, token, tela, outro.
"""
import hashlib
import json
import os
import re
import sqlite3
import subprocess
from pathlib import Path

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB = os.path.join(BASE, "base.db")
MIGRATIONS = Path(__file__).resolve().parent / "migrations"

HISTORICOS = (
    "ANALISE-", "APPS-SISTEMA-", "CONVERGENCIA-", "CORRECAO-",
    "EFEITOS-", "EXECUCAO-", "FONTES.md", "GAPS-", "INVESTIGACAO-",
    "SCRAPING_", "TAHOE-BLOCOS-", "VIDEO-INSIGHT-", "comparacao/MATRIZ.md",
    "INDICE-VISUAL-OTIMIZADO.md",
)


def metadados_iniciais(rel, texto):
    """Classificação conservadora: uma origem não examinada nunca vira verified."""
    status = "archived" if rel.startswith(HISTORICOS) or rel.startswith("historico/") else "experimental"
    if "macos27/" in rel or "kit-visionos/" in rel:
        versao = "macOS 27 (declared)" if "macos27/" in rel else "visionOS"
    elif re.search(r"macOS Tahoe 26|macOS 26|Tahoe 26", texto[:2500], re.I):
        versao = "Tahoe 26"
    elif re.search(r"macOS 27|Tahoe\s*/\s*27", texto[:2500], re.I):
        versao = "macOS 27 (declared)"
    else:
        versao = "unknown"
    componente = rel.split("/", 1)[1].rsplit(".", 1)[0] if rel.startswith("componentes/") else None
    url = re.search(r"https?://[^\s<>\)\]`]+", texto[:3500])
    linhas = [x.strip(" #>*\t") for x in texto.splitlines() if x.strip()]
    resumo = " ".join(linhas[1:3])[:350] if len(linhas) > 1 else (linhas[0][:350] if linhas else "")
    return status, versao, componente, url.group(0).rstrip(".,;") if url else None, resumo


def migrar(db):
    atual = db.execute("PRAGMA user_version").fetchone()[0]
    for arquivo in sorted(MIGRATIONS.glob("[0-9][0-9][0-9]_*.sql")):
        versao = int(arquivo.name.split("_", 1)[0])
        if versao > atual:
            db.executescript(arquivo.read_text(encoding="utf-8"))
            print(f"migração {versao}: {arquivo.name}")
            atual = versao


def tipo_de(rel):
    for prefixo, tipo in (("componentes/", "componente"), ("padroes/", "padrao"), ("hig/wwdc/", "wwdc"),
                          ("hig/", "hig"), ("referencias/pdfs/", "pdf"), ("referencias/kit/contornos/", "contorno"),
                          ("referencias/kit-visionos/contornos/", "contorno"), ("tokens/", "token"),
                          ("referencias/telas/", "tela"), ("dev/", "dev"), ("apple-support-scraped/", "suporte")):
        if rel.startswith(prefixo):
            return tipo
    return "outro"


def trechos_markdown(texto):
    """Quebra por títulos (#, ##, ###); cada trecho leva o caminho de títulos."""
    titulo, pilha, atual, out = "", [], [], []
    for linha in texto.splitlines():
        m = re.match(r"^(#{1,4})\s+(.*)", linha)
        if m:
            if atual and "".join(atual).strip():
                out.append((" › ".join(pilha), "\n".join(atual)))
            nivel, nome = len(m.group(1)), m.group(2).strip()
            if nivel == 1 and not titulo:
                titulo = nome
            pilha = pilha[:nivel - 1] + [nome]
            atual = [linha]
        else:
            atual.append(linha)
    if atual and "".join(atual).strip():
        out.append((" › ".join(pilha), "\n".join(atual)))
    return titulo, out


def trechos_contorno(texto):
    """Contornos do kit: um trecho por símbolo/artboard de nível 0."""
    out, atual, nome = [], [], ""
    for linha in texto.splitlines():
        if not linha.startswith(" ") and not linha.startswith("#"):
            if atual:
                out.append((nome, "\n".join(atual)))
            m = re.match(r"\w+ '([^']*)'", linha)
            nome, atual = (m.group(1) if m else linha[:60]), [linha]
        elif linha.strip():
            atual.append(linha)
    if atual:
        out.append((nome, "\n".join(atual)))
    return out


def trechos_texto(texto, linhas=60):
    ls = [ln for ln in texto.splitlines() if ln.strip()]
    return [(f"linhas {i + 1}–{i + linhas}", "\n".join(ls[i:i + linhas])) for i in range(0, len(ls), linhas)]


def main():
    # A matriz é derivada do código e dos parâmetros: gere antes de calcular os
    # hashes e trechos, para que o índice nunca aponte para a versão anterior.
    subprocess.run([os.path.join(os.path.dirname(os.path.abspath(__file__)), "comparar.py")], check=True)
    db = sqlite3.connect(DB)
    db.execute("PRAGMA foreign_keys=ON")
    db.execute("PRAGMA busy_timeout=5000")
    db.executescript("""
        CREATE VIRTUAL TABLE IF NOT EXISTS trechos USING fts5(
            conteudo, titulo, secao, caminho UNINDEXED, tipo UNINDEXED,
            tokenize = "unicode61 remove_diacritics 2");
        CREATE TABLE IF NOT EXISTS cores (kit TEXT, grupo TEXT, nome TEXT, hex TEXT, css TEXT);
        CREATE TABLE IF NOT EXISTS tipografia (kit TEXT, nome TEXT, fonte TEXT, tamanho REAL, entrelinha REAL, cor TEXT);
        CREATE TABLE IF NOT EXISTS estilos (kit TEXT, nome TEXT, json TEXT);
        CREATE TABLE IF NOT EXISTS imagens (caminho TEXT, descricao TEXT, origem TEXT);
        CREATE TABLE IF NOT EXISTS imagens_catalogo (
            id TEXT PRIMARY KEY, caminho TEXT, categoria TEXT, estado TEXT,
            prioridade TEXT, titulo TEXT, descricao TEXT, ancoras TEXT,
            uso TEXT, largura INT, altura INT, proporcao REAL, sha256 TEXT,
            triagem TEXT, sequencia TEXT, classificacao_fonte TEXT, confianca TEXT
        );
        CREATE TABLE IF NOT EXISTS codigo_catalogo (
            caminho TEXT PRIMARY KEY, linguagem TEXT, linhas INT, bytes INT,
            resumo TEXT, simbolos TEXT, imports TEXT, tags TEXT, sha256 TEXT
        );
        CREATE TABLE IF NOT EXISTS meta (chave TEXT PRIMARY KEY, valor TEXT);
    """)
    migrar(db)
    db.execute("BEGIN IMMEDIATE")
    for tabela in ("cores", "tipografia", "estilos", "imagens", "imagens_catalogo", "codigo_catalogo"):
        db.execute(f"DELETE FROM {tabela}")
    n = 0
    inalterados = 0
    vistos = set()
    for raiz, dirs, arqs in os.walk(BASE):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d not in ("imagens", "icones-apps", "ponteiros",
                                                                          "papeis-de-parede", "macos-pour-windows",
                                                                          "models", "backups")]
        for a in sorted(arqs):
            caminho = os.path.join(raiz, a)
            rel = os.path.relpath(caminho, BASE)
            if not a.endswith((".md", ".txt")) or rel.startswith("ferramentas/"):
                continue
            dados = Path(caminho).read_bytes()
            texto = dados.decode("utf-8", errors="replace")
            digest = hashlib.sha256(dados).hexdigest()
            tipo = tipo_de(rel)
            vistos.add(rel)
            anterior = db.execute("SELECT sha256,confianca FROM documentos WHERE caminho=?", (rel,)).fetchone()
            if anterior is None:
                estado, versao, componente, url, resumo = metadados_iniciais(rel, texto)
                db.execute("INSERT INTO documentos(caminho,sha256,presente,tipo,estado,versao_macos,componente,fonte,url_fonte,resumo) "
                           "VALUES (?,?,1,?,?,?,?,?,?,?)",
                           (rel, digest, tipo, estado, versao, componente, rel, url, resumo))
            else:
                db.execute("UPDATE documentos SET sha256=?,presente=1,tipo=?,atualizado_em=CURRENT_TIMESTAMP WHERE caminho=?",
                           (digest, tipo, rel))
                if anterior[0] != digest and anterior[1] == "unverified":
                    _estado, versao, componente, url, resumo = metadados_iniciais(rel, texto)
                    db.execute("UPDATE documentos SET versao_macos=?,componente=?,url_fonte=?,resumo=? WHERE caminho=?",
                               (versao, componente, url, resumo, rel))
            # A tabela de imagens é derivada; os trechos só mudam se o conteúdo mudar.
            mudou = anterior is None or anterior[0] != digest
            if mudou:
                db.execute("DELETE FROM trechos WHERE caminho=?", (rel,))
            else:
                inalterados += 1
            if not mudou and a.endswith(".md"):
                for alt, src in re.findall(r"!\[([^\]]*)\]\(([^)]+)\)", texto):
                    db.execute("INSERT INTO imagens VALUES (?,?,?)",
                               (os.path.normpath(os.path.join(os.path.dirname(rel), src)), alt, rel))
                continue
            if not mudou:
                continue
            if tipo == "contorno":
                titulo, partes = a[:-4].replace("_", " "), trechos_contorno(texto)
            elif a.endswith(".md"):
                titulo, partes = trechos_markdown(texto)
                titulo = titulo or a[:-3]
                # figuras com texto alternativo → tabela de imagens
                for alt, src in re.findall(r"!\[([^\]]*)\]\(([^)]+)\)", texto):
                    db.execute("INSERT INTO imagens VALUES (?,?,?)",
                               (os.path.normpath(os.path.join(os.path.dirname(rel), src)), alt, rel))
            else:
                titulo, partes = a[:-4], trechos_texto(texto)
            for secao, conteudo in partes:
                db.execute("INSERT INTO trechos VALUES (?,?,?,?,?)", (conteudo, titulo, secao, rel, tipo))
                n += 1

    # Um arquivo retirado da árvore pode ter sido a única cópia de uma fonte.
    # Preserve seu texto no FTS legado e retire-o apenas da busca padrão.
    for (rel,) in db.execute("SELECT DISTINCT caminho FROM trechos"):
        if rel in vistos:
            continue
        if db.execute("SELECT 1 FROM documentos WHERE caminho=?", (rel,)).fetchone():
            db.execute("UPDATE documentos SET presente=0, estado=CASE WHEN estado IN ('verified','experimental') "
                       "THEN 'archived' ELSE estado END WHERE caminho=?", (rel,))
        else:
            db.execute("INSERT INTO documentos(caminho,presente,tipo,estado,fonte,resumo) VALUES (?,0,?,'archived',?,?)",
                       (rel, tipo_de(rel), "legacy FTS snapshot", "Fonte ausente da árvore; texto preservado no índice legado."))

    # telas: linhas da tabela do INDICE.md viram imagens descritas
    ind = os.path.join(BASE, "referencias/telas/INDICE.md")
    if os.path.exists(ind):
        for linha in open(ind):
            m = re.match(r"\|\s*`([^`]+)`[^|]*\|\s*([^|]+)\|\s*([^|]+)\|", linha)
            if m:
                db.execute("INSERT INTO imagens VALUES (?,?,?)",
                           ("referencias/telas/" + m.group(1).split(" ")[0], f"{m.group(2).strip()} — {m.group(3).strip()}",
                            "referencias/telas/INDICE.md"))
    for d, origem in (("referencias/kit/icones-apps", "ícone de app (kit macOS 27)"),
                      ("referencias/kit/ponteiros", "ponteiro do macOS (kit)"),
                      ("referencias/kit/papeis-de-parede", "papel de parede oficial do macOS 27")):
        if not os.path.isdir(os.path.join(BASE, d)):
            continue
        for a in sorted(os.listdir(os.path.join(BASE, d))):
            nome = os.path.splitext(a)[0].replace("_", " ").replace("-", " ")
            db.execute("INSERT INTO imagens VALUES (?,?,?)", (f"{d}/{a}", nome, origem))

    # frames curados do vídeo (curar_frames.py → frames-meta.json): a descrição
    # junta title + component + shows para o --imagem e o FTS acharem.
    meta = os.path.join(BASE, "video/frames-meta.json")
    if os.path.exists(meta):
        for fr in json.load(open(meta, encoding="utf-8")):
            desc = " — ".join(x for x in (fr.get("title", "").strip(),
                                          fr.get("component", "").strip(),
                                          ", ".join(fr.get("shows", []))) if x)
            db.execute("INSERT INTO imagens VALUES (?,?,?)",
                       (fr["arquivo"], desc or "(frame sem descrição — preencher)",
                       f"vídeo macOS 27 ({fr.get('origem', '')})"))

    # catálogo leve das telas de referência: a busca semântica evita abrir todos
    # os originais; o JSON continua sendo a fonte dos metadados completos.
    catalogo = os.path.join(BASE, "referencias/telas/catalogo.json")
    if os.path.exists(catalogo):
        for item in json.load(open(catalogo, encoding="utf-8")).get("items", []):
            d = item.get("dimensoes_px", {})
            db.execute("INSERT OR REPLACE INTO imagens_catalogo VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (
                item.get("id"), item.get("arquivo"), item.get("categoria"),
                ", ".join(item.get("estado", [])), item.get("prioridade"),
                item.get("titulo"), item.get("descricao"),
                ", ".join(item.get("ancoras_visuais", [])),
                ", ".join(item.get("usar_para", [])), d.get("largura"),
                d.get("altura"), item.get("proporcao"), item.get("sha256"),
                item.get("triagem"), json.dumps(item.get("sequencia"), ensure_ascii=False),
                item.get("classificacao_fonte"), item.get("confianca")))

    codigo = os.path.join(BASE, "codigo.json")
    if os.path.exists(codigo):
        for item in json.load(open(codigo, encoding="utf-8")).get("items", []):
            db.execute("INSERT OR REPLACE INTO codigo_catalogo VALUES (?,?,?,?,?,?,?,?,?)", (
                item.get("path"), item.get("language"), item.get("lines"), item.get("bytes"),
                item.get("summary"), ", ".join(item.get("symbols", [])),
                ", ".join(item.get("imports", [])), ", ".join(item.get("tags", [])), item.get("sha256")))

    # tokens estruturados
    for kit in ("macos27", "visionos"):
        p = os.path.join(BASE, "tokens", kit)
        for c in json.load(open(os.path.join(p, "cores.json"))):
            grupo, _, nome = c["nome"].rpartition("/")
            db.execute("INSERT INTO cores VALUES (?,?,?,?,?)", (kit, grupo, nome, c["hex"], c["css"]))
        for t in json.load(open(os.path.join(p, "tipografia.json"))):
            db.execute("INSERT INTO tipografia VALUES (?,?,?,?,?,?)",
                       (kit, t["nome"], t.get("fonte"), t.get("tamanho"), t.get("entrelinha"), t.get("cor")))
        for e in json.load(open(os.path.join(p, "estilos.json"))):
            nome = e.pop("nome")
            db.execute("INSERT INTO estilos VALUES (?,?,?)", (kit, nome, json.dumps(e, ensure_ascii=False)))

    db.execute("INSERT OR REPLACE INTO meta VALUES ('trechos', ?)",
               (str(db.execute('SELECT count(*) FROM trechos').fetchone()[0]),))
    for ident, titulo, resumo, evidencia, fonte, url, antigo in db.execute(
            "SELECT id,titulo,resumo,evidencia,fonte_caminho,fonte_url,sha256 FROM registros").fetchall():
        conteudo = json.dumps([titulo, resumo, evidencia, fonte, url], ensure_ascii=False)
        digest = hashlib.sha256(conteudo.encode("utf-8")).hexdigest()
        if digest != antigo:
            db.execute("UPDATE registros SET sha256=? WHERE id=?", (digest, ident))
    db.commit()
    for t in ("trechos", "cores", "tipografia", "estilos", "imagens", "imagens_catalogo", "codigo_catalogo"):
        print(f"{t:12s} {db.execute(f'SELECT count(*) FROM {t}').fetchone()[0]}")
    print(f"fontes alteradas: {len(vistos) - inalterados}; inalteradas: {inalterados}; trechos novos: {n}")
    duplicados = db.execute("SELECT count(*) FROM (SELECT sha256 FROM documentos "
                           "WHERE presente=1 AND sha256 IS NOT NULL GROUP BY sha256 HAVING count(*)>1)").fetchone()[0]
    print(f"fontes textuais exatamente duplicadas (SHA-256): {duplicados}")
    duplicados_registros = db.execute("SELECT count(*) FROM (SELECT sha256 FROM registros "
                                     "WHERE sha256 IS NOT NULL GROUP BY sha256 HAVING count(*)>1)").fetchone()[0]
    print(f"registros curados exatamente duplicados (SHA-256): {duplicados_registros}")
    db.close()
    print("→", DB)


if __name__ == "__main__":
    main()
