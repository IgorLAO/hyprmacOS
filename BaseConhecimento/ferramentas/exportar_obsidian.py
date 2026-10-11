#!/usr/bin/env python3
"""Compila a Base de Conhecimento num vault do Obsidian.

  exportar_obsidian.py              gera/atualiza o vault em ~/Projects/hyprmac/hyprmac
  exportar_obsidian.py <pasta>      outro vault

Cada .md/.txt vira uma nota com propriedades (tags, fonte, aliases); links relativos viram
[[wikilinks]] (âncoras do GitHub viram [[Nota#Título]]); figuras, telas e o kit vão para
Anexos/; cada parâmetro da comparação vira uma nota com propriedades, listadas em
Comparação/Parâmetros.base (status vem da tabela `parametros` do base.db — rodar comparar.py antes).

Só apaga o que ele mesmo gerou da última vez (lista em <vault>/.base-conhecimento.json);
notas suas e .obsidian/ ficam intactas. Rodar de novo depois de indexar.py/comparar.py.
"""
import json
import os
import re
import shutil
import sqlite3
import sys
import unicodedata
from urllib.parse import quote

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
REPO = os.path.dirname(BASE)
VAULT = os.path.abspath(sys.argv[1]) if len(sys.argv) > 1 else os.path.join(REPO, "hyprmac")
MANIFESTO = os.path.join(VAULT, ".base-conhecimento.json")

IMAGEM = (".png", ".jpg", ".jpeg", ".webp", ".avif", ".svg", ".gif")
STATUS_ICONE = {"conforme": "✅", "proximo": "🟡", "diverge": "🔴", "ausente": "⬜", "limitacao": "➖"}

gerados = set()   # caminhos relativos ao vault escritos nesta execução


# ---------------------------------------------------------------- mapa origem → nota

def titulo_h1(caminho):
    with open(caminho, encoding="utf-8") as f:
        for linha in f:
            if linha.startswith("# "):
                return linha[2:].strip()
    return os.path.splitext(os.path.basename(caminho))[0]


def limpar_nome(nome):
    return re.sub(r'[\\/:*?"<>|#^\[\]]', " ", nome).replace("  ", " ").strip()


NOMES_FIXOS = {
    "README.md": ("", "Início", ["indice"]),
    "FONTES.md": ("", "Fontes", ["indice"]),
    "comparacao/MATRIZ.md": ("Comparação", "Matriz de comparação", ["comparacao"]),
    "padroes/liquid-glass.md": ("Padrões", "Liquid Glass e materiais", ["padrao"]),
    "padroes/forma-e-espacamento.md": ("Padrões", "Forma, raios e espaçamento", ["padrao"]),
    "padroes/cores-e-tipografia.md": ("Padrões", "Cores, vibrancy e tipografia", ["padrao"]),
    "padroes/movimento-escrita-e-principios.md": ("Padrões", "Princípios, movimento, escrita e menus", ["padrao"]),
    "padroes/atalhos-de-teclado.md": ("Padrões", "Atalhos de teclado", ["padrao"]),
    "componentes/barra-de-menus.md": ("Componentes", "Barra de menus", ["componente"]),
    "componentes/menus.md": ("Componentes", "Menus suspensos e de contexto", ["componente"]),
    "componentes/central-de-controle.md": ("Componentes", "Central de Controle", ["componente"]),
    "componentes/notificacoes.md": ("Componentes", "Notificações", ["componente"]),
    "componentes/dock.md": ("Componentes", "Dock", ["componente"]),
    "componentes/janelas-popovers-alertas.md": ("Componentes", "Janelas, popovers e alertas", ["componente"]),
    "componentes/controles.md": ("Componentes", "Controles", ["componente"]),
    "componentes/sistema-e-recursos.md": ("Componentes", "Recursos do sistema", ["componente"]),
    "tokens/macos27/cores.md": ("Tokens", "Cores do kit macOS 27", ["token"]),
    "tokens/macos27/tipografia.md": ("Tokens", "Tipografia do kit macOS 27", ["token"]),
    "tokens/macos27/estilos.md": ("Tokens", "Estilos de camada do kit macOS 27", ["token"]),
    "tokens/visionos/cores.md": ("Tokens", "Cores do kit visionOS", ["token"]),
    "tokens/visionos/tipografia.md": ("Tokens", "Tipografia do kit visionOS", ["token"]),
    "tokens/visionos/estilos.md": ("Tokens", "Estilos de camada do kit visionOS", ["token"]),
    "hig/wwdc/219-meet-liquid-glass.txt": ("HIG/WWDC", "WWDC25 219 — Meet Liquid Glass", ["wwdc"]),
    "hig/wwdc/356-new-design-system.txt": ("HIG/WWDC", "WWDC25 356 — Get to know the new design system", ["wwdc"]),
    "referencias/telas/INDICE.md": ("Referências", "Telas de referência", ["referencia", "tela"]),
    "referencias/pdfs/novidades-macos-tahoe.txt": ("Referências/PDFs", "Novidades do macOS Tahoe", ["referencia", "pdf"]),
    "referencias/pdfs/tahoe-course-companion.txt": ("Referências/PDFs", "The Guide To macOS Tahoe (MacMost)", ["referencia", "pdf"]),
    "referencias/pdfs/Apple_HIG_Quick_Index.md": ("Referências/PDFs", "HIG — índice rápido (terceiros)", ["referencia", "pdf"]),
}

# pastas citadas nos links → nota-índice (gerada mais abaixo)
PASTAS = {
    "padroes": "Padrões", "componentes": "Componentes", "hig": "HIG", "ferramentas": "Ferramentas",
    "tokens/macos27": "Tokens#macOS 27", "tokens/visionos": "Tokens#visionOS",
    "referencias/kit": "Kit macOS 27", "referencias/kit/contornos": "Contornos macOS 27",
    "referencias/kit-visionos/contornos": "Contornos visionOS",
    "referencias/kit/icones-apps": "Ícones de apps", "referencias/kit/ponteiros": "Ponteiros",
    "referencias/kit/papeis-de-parede": "Kit macOS 27#Papéis de parede",
    "referencias/kit/fontes": "Kit macOS 27#Fontes",
    "referencias/telas": "Telas de referência", "referencias/pdfs": "PDFs",
    "referencias/pdfs/macos-pour-windows": "macOS pour Windows",
    "comparacao": "Matriz de comparação",
}

notas = {}   # origem relativa à base → (pasta no vault, nome, tags)


def montar_mapa():
    notas.update(NOMES_FIXOS)
    for f in sorted(os.listdir(os.path.join(BASE, "hig"))):
        if f.endswith(".md"):
            notas[f"hig/{f}"] = ("HIG", limpar_nome(titulo_h1(os.path.join(BASE, "hig", f))), ["hig"])
    for kit, pasta, prefixo in (("kit", "Kit/Contornos macOS 27", "Kit"),
                                ("kit-visionos", "Kit/Contornos visionOS", "visionOS")):
        d = os.path.join(BASE, "referencias", kit, "contornos")
        for f in sorted(os.listdir(d)):
            if f.endswith(".txt"):
                nome = limpar_nome(f"{prefixo} — {f[:-4].replace('_', ' ')}")
                notas[f"referencias/{kit}/contornos/{f}"] = (pasta, nome, ["contorno"])
    for d in ("tokens/macos27", "tokens/visionos"):   # .json aponta para o .md legível
        for f in os.listdir(os.path.join(BASE, d)):
            if f.endswith(".json") and f"{d}/{f[:-5]}.md" in notas:
                notas[f"{d}/{f}"] = notas[f"{d}/{f[:-5]}.md"]
    nomes = [n for _, n, _ in NOMES_FIXOS.values()]
    repetidos = {n for n in nomes if nomes.count(n) > 1}
    assert not repetidos, repetidos


def nome_da_nota(origem):
    return notas[origem][1]


def caminho_da_nota(origem):
    pasta, nome, _ = notas[origem]
    return os.path.join(pasta, nome + ".md") if pasta else nome + ".md"


# ---------------------------------------------------------------- escrita

def escrever(rel, texto):
    destino = os.path.join(VAULT, rel)
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    with open(destino, "w", encoding="utf-8") as f:
        f.write(texto)
    gerados.add(rel)


def copiar(origem_abs, rel):
    destino = os.path.join(VAULT, rel)
    os.makedirs(os.path.dirname(destino), exist_ok=True)
    st = os.stat(origem_abs)
    if not (os.path.exists(destino) and os.path.getsize(destino) == st.st_size
            and int(os.path.getmtime(destino)) == int(st.st_mtime)):
        shutil.copy2(origem_abs, destino)
    gerados.add(rel)
    return rel


def anexo(origem_rel):
    """Copia um arquivo da base para Anexos/ e devolve o caminho no vault."""
    rel = origem_rel
    for de, para in (("hig/imagens/", "hig/"), ("referencias/telas/", "telas/"),
                     ("referencias/pdfs/macos-pour-windows/", "macos-pour-windows/"),
                     ("referencias/kit-visionos/", "kit-visionos/"), ("referencias/kit/", "kit/")):
        if rel.startswith(de):
            rel = para + rel[len(de):]
            break
    return copiar(os.path.join(BASE, origem_rel), "Anexos/" + rel)


def propriedades(**campos):
    linhas = ["---"]
    for k, v in campos.items():
        if v in (None, "", []):
            continue
        if isinstance(v, list):
            linhas.append(f"{k}:")
            linhas += [f"  - {json.dumps(x, ensure_ascii=False)}" for x in v]
        else:
            linhas.append(f"{k}: {json.dumps(v, ensure_ascii=False)}")
    return "\n".join(linhas + ["---", ""])


# ---------------------------------------------------------------- links

def slug_github(titulo):
    t = re.sub(r"[`*_~]|<[^>]+>", "", titulo).strip().lower()
    t = re.sub(r"[^\w\- ]", "", t)
    return t.replace(" ", "-")


def titulo_obsidian(titulo):
    return re.sub(r"\s+", " ", re.sub(r"[#|^:\[\]]|%%", " ", titulo)).strip()


_ancoras = {}


def ancoras(origem):
    if origem not in _ancoras:
        mapa, vistos = {}, {}
        caminho = os.path.join(BASE, origem)
        if origem.endswith(".md") and os.path.exists(caminho):
            dentro_de_codigo = False
            for linha in open(caminho, encoding="utf-8"):
                if linha.startswith("```"):
                    dentro_de_codigo = not dentro_de_codigo
                m = None if dentro_de_codigo else re.match(r"#{1,6} +(.+?)\s*$", linha)
                if m:
                    s = slug_github(m.group(1))
                    n = vistos.get(s, 0)
                    vistos[s] = n + 1
                    mapa[s if n == 0 else f"{s}-{n}"] = titulo_obsidian(m.group(1))
        _ancoras[origem] = mapa
    return _ancoras[origem]


def wikilink(alvo, texto=None, tabela=False):
    if texto and (texto == alvo or "/" in texto or texto.endswith((".md", ".txt", ".json"))):
        texto = None
    sep = "\\|" if tabela else "|"
    return f"[[{alvo}{sep}{texto}]]" if texto else f"[[{alvo}]]"


def resolver(destino, origem_dir):
    """Link relativo de um arquivo da base → (alvo do wikilink | None, caminho resolvido)."""
    caminho, _, ancora = destino.partition("#")
    rel = os.path.normpath(os.path.join(origem_dir, caminho)).replace(os.sep, "/")
    if rel in notas:
        alvo = nome_da_nota(rel)
        if ancora:
            titulo = ancoras(rel).get(ancora)
            if titulo:
                alvo += "#" + titulo
        return alvo, rel
    if rel.rstrip("/") in PASTAS:
        return PASTAS[rel.rstrip("/")], rel
    if rel == "comparacao/parametros.json":
        return "Parâmetros.base", rel
    return None, rel


def converter_links(texto, origem, nota_rel):
    """Troca links relativos por wikilinks e copia as imagens citadas para Anexos/."""
    origem_dir = os.path.dirname(origem)
    nota_dir = os.path.dirname(nota_rel)

    def troca(m, tabela):
        exclam, rotulo, destino = m.group(1), m.group(2), m.group(3)
        if re.match(r"[a-z]+:", destino):
            return m.group(0)
        if destino.lower().split("#")[0].endswith(IMAGEM):
            rel = os.path.normpath(os.path.join(origem_dir, destino)).replace(os.sep, "/")
            if os.path.exists(os.path.join(BASE, rel)):
                no_vault = anexo(rel)
                caminho = quote(os.path.relpath(no_vault, nota_dir or "."))
                return f"{exclam}[{rotulo.replace('|', '/')}]({caminho})"
        alvo, rel = resolver(destino, origem_dir)
        if alvo:
            if rotulo == os.path.splitext(os.path.basename(rel.rstrip("/")))[0]:
                rotulo = None   # rótulo era só o nome do arquivo
            return wikilink(alvo, rotulo, tabela)
        return f"{rotulo} (`{rel}`)" if rotulo != rel else f"`{rel}`"

    padrao = re.compile(r"(!?)\[([^\]]*)\]\(([^)\s]+)\)")
    saida, codigo = [], False
    for linha in texto.split("\n"):
        if linha.lstrip().startswith("```"):
            codigo = not codigo
        if not codigo:
            tabela = linha.lstrip().startswith("|")
            linha = padrao.sub(lambda m: troca(m, tabela), linha)
        saida.append(linha)
    return "\n".join(saida)


# ---------------------------------------------------------------- notas a partir da base

def nota_markdown(origem, extra_props=None, prefixo="", sufixo=""):
    pasta, nome, tags = notas[origem]
    rel = caminho_da_nota(origem)
    texto = open(os.path.join(BASE, origem), encoding="utf-8").read()
    texto = converter_links(texto, origem, rel)
    props = dict(tags=tags, fonte=f"BaseConhecimento/{origem}", aliases=[os.path.basename(origem)])
    props.update(extra_props or {})
    escrever(rel, propriedades(**props) + prefixo + texto.rstrip() + "\n" + sufixo)


def nota_texto(origem, cabecalho, bloco=False):
    pasta, nome, tags = notas[origem]
    texto = open(os.path.join(BASE, origem), encoding="utf-8").read().rstrip()
    if bloco:
        texto = "````text\n" + texto + "\n````"
    props = propriedades(tags=tags, fonte=f"BaseConhecimento/{origem}", aliases=[os.path.basename(origem)])
    escrever(caminho_da_nota(origem), props + f"# {nome}\n\n{cabecalho}\n\n{texto}\n")


def lista(origens):
    return "\n".join(f"- [[{nome_da_nota(o)}]]" for o in origens)


def gerar_conteudo():
    for origem in NOMES_FIXOS:
        if origem.endswith(".md") and origem not in ("referencias/telas/INDICE.md", "comparacao/MATRIZ.md"):
            prefixo = ""
            if origem == "README.md":
                prefixo = ("> [!tip] Vault gerado por `BaseConhecimento/ferramentas/exportar_obsidian.py`\n"
                           "> Edite os arquivos em `BaseConhecimento/` e rode o exportador de novo — "
                           "estas notas são sobrescritas. Notas suas, em outras pastas, ficam intactas.\n\n")
            if origem.endswith("Apple_HIG_Quick_Index.md"):
                prefixo = ("> [!warning] Resumo de terceiros: os números são do **iOS** (Body 17 pt etc.). "
                           "Para macOS valem os do kit — ver [[Tipografia do kit macOS 27]].\n\n")
            nota_markdown(origem, prefixo=prefixo)
    for origem in notas:
        if origem.startswith("hig/") and origem.endswith(".md"):
            nota_markdown(origem)

    nota_texto("hig/wwdc/219-meet-liquid-glass.txt",
               "Transcrição da sessão da WWDC25. Ver também [[Materials]] e [[Liquid Glass e materiais]].")
    nota_texto("hig/wwdc/356-new-design-system.txt",
               "Transcrição da sessão da WWDC25. Ver também [[Liquid Glass e materiais]] e [[Forma, raios e espaçamento]].")
    nota_texto("referencias/pdfs/novidades-macos-tahoe.txt",
               "Texto do PDF oficial *All New Features — macOS Tahoe* (set/2025, pt-BR), extraído com `pdftotext -layout`.",
               bloco=True)
    nota_texto("referencias/pdfs/tahoe-course-companion.txt",
               "Texto do livro do curso MacMost (72 p.), extraído com `pdftotext`.")

    for origem, (pasta, nome, _) in notas.items():
        if "/contornos/" in origem:
            kit = "macOS 27" if "/kit/" in origem else "visionOS"
            nota_texto(origem, f"Árvore de camadas da página do kit {kit} (Sketch): classe, nome, LxA @(x,y), "
                               f"raio `r=` (contínuo), `pad=` topo/dir/base/esq, `flex(...)`, estilo compartilhado "
                               f"em `[...]` e, nos textos, «conteúdo» fonte tamanho cor. "
                               f"Índice: [[Contornos {kit}]].", bloco=True)

    gerar_telas()
    gerar_matriz_e_parametros()
    gerar_indices()


def gerar_telas():
    origem = "referencias/telas/INDICE.md"
    rel = caminho_da_nota(origem)
    pasta_telas = os.path.join(BASE, "referencias/telas")
    arquivos = sorted(f for f in os.listdir(pasta_telas) if f.lower().endswith(IMAGEM))
    por_raiz = {os.path.splitext(f)[0]: f for f in arquivos if not f.endswith(".avif")}

    def real(nome):
        if nome in arquivos:
            return nome
        return por_raiz.get(os.path.splitext(nome)[0])

    texto = open(os.path.join(BASE, origem), encoding="utf-8").read()
    texto = converter_links(texto, origem, rel)

    def celula(m):
        f = real(m.group(1))
        if not f:
            return m.group(0)
        caminho = anexo(f"referencias/telas/{f}")
        return f"[[{caminho}\\|{m.group(1)}]]"
    texto = re.sub(r"(?m)^\| `([^`]+)` \|", lambda m: "| " + celula(m) + " |", texto)

    galeria = ["", "## Galeria", ""]
    for f in arquivos:
        if f.endswith(".avif") and os.path.splitext(f)[0] in por_raiz:
            continue
        galeria += [f"![[{anexo('referencias/telas/' + f)}|900]]", f"*{f}*", ""]
    props = propriedades(tags=["referencia", "tela"], fonte=f"BaseConhecimento/{origem}", aliases=["INDICE.md"])
    escrever(rel, props + texto.rstrip() + "\n" + "\n".join(galeria))


def gerar_matriz_e_parametros():
    cfg = json.load(open(os.path.join(BASE, "comparacao/parametros.json"), encoding="utf-8"))
    atuais = {}
    db = os.path.join(BASE, "base.db")
    if os.path.exists(db):
        con = sqlite3.connect(db)
        con.row_factory = sqlite3.Row
        try:
            atuais = {r["id"]: dict(r) for r in con.execute("SELECT * FROM parametros")}
        except sqlite3.OperationalError:
            pass
    nomes = {}
    for p in cfg["parametros"]:
        a = atuais.get(p["id"], {})
        nome = limpar_nome(f"{p['id']} {p['parametro']}")
        nomes[p["id"]] = nome
        fontes = []
        for trecho in re.split(r"\s*·\s*", p.get("fonte", "")):
            alvo, _ = resolver(trecho.strip(), "")
            fontes.append(f"[[{alvo}]]" if alvo else trecho.strip())
        status = a.get("status") or p.get("status", "")
        props = dict(
            tags=["parametro"], aliases=[p["id"]], id=p["id"], area=p["area"], parametro=p["parametro"],
            apple=p.get("apple"), hyprmac=a.get("hyprmac") or p.get("hyprmac"),
            status=status, icone=STATUS_ICONE.get(status, ""), prioridade=p.get("prioridade"),
            peso=p.get("peso"), onde=p.get("onde"), medir=p.get("medir"), fonte=fontes,
            nota=a.get("nota") or p.get("nota"),
        )
        corpo = [f"# {p['id']} — {p['parametro']}", "",
                 f"{STATUS_ICONE.get(status, '')} **{status}** · {p.get('prioridade', '')} · área *{p['area']}*", "",
                 f"- **Apple:** {p.get('apple', '')}",
                 f"- **hyprmac:** {props['hyprmac'] or '—'}",
                 f"- **Onde:** `{p.get('onde', '')}`",
                 f"- **Como medir:** {p.get('medir', '')}",
                 f"- **Fonte:** {' · '.join(fontes)}"]
        if props["nota"]:
            corpo.append(f"- **Nota:** {props['nota']}")
        if "leitura" in p:
            corpo += ["", f"Lido do código por `comparar.py`: `{p['leitura']['arquivo']}` "
                          f"com a regex `{p['leitura']['regex']}`."]
        corpo += ["", "Todos: [[Parâmetros.base]] · [[Matriz de comparação]]"]
        escrever(f"Comparação/Parâmetros/{nome}.md", propriedades(**props) + "\n".join(corpo) + "\n")

    escrever("Comparação/Parâmetros.base", BASE_PARAMETROS)

    origem = "comparacao/MATRIZ.md"
    texto = open(os.path.join(BASE, origem), encoding="utf-8").read()
    texto = converter_links(texto, origem, caminho_da_nota(origem))
    caminhos = sorted((o for o in notas if "/" in o), key=len, reverse=True)
    saida = []
    for linha in texto.split("\n"):
        tabela = linha.startswith("|")
        linha = re.sub(r"\b([A-Z]{2,4}-\d{2})\b",
                       lambda m: wikilink(nomes[m.group(1)], m.group(1), tabela) if m.group(1) in nomes else m.group(0),
                       linha)
        if tabela:
            ultima = linha.rstrip().rstrip("|").rsplit("|", 1)
            if len(ultima) == 2 and re.search(r"\.(md|txt)\b", ultima[1]):
                cel = ultima[1]
                for c in caminhos:
                    cel = cel.replace(c, f"[[{nome_da_nota(c)}]]")
                linha = ultima[0] + "|" + cel + " |"
        saida.append(linha)
    props = propriedades(tags=["comparacao"], fonte="BaseConhecimento/comparacao/MATRIZ.md", aliases=["MATRIZ.md"])
    aviso = ("> [!info] Gerada por `comparar.py`; a mesma lista com filtros está em [[Parâmetros.base]]. "
             "Cada ID abre a nota do parâmetro.\n\n")
    escrever(caminho_da_nota(origem), props + aviso + "\n".join(saida).rstrip() + "\n")


BASE_PARAMETROS = """filters:
  and:
    - file.inFolder("Comparação/Parâmetros")
properties:
  icone:
    displayName: " "
  parametro:
    displayName: Parâmetro
  area:
    displayName: Área
  apple:
    displayName: Apple
  hyprmac:
    displayName: hyprmac
  prioridade:
    displayName: Prio
  onde:
    displayName: Onde
views:
  - type: table
    name: Pendentes
    filters:
      and:
        - status != "conforme"
        - status != "limitacao"
    groupBy:
      property: prioridade
      direction: ASC
    order:
      - icone
      - id
      - parametro
      - area
      - apple
      - hyprmac
      - onde
    sort:
      - property: prioridade
        direction: ASC
      - property: id
        direction: ASC
  - type: table
    name: Por área
    groupBy:
      property: area
      direction: ASC
    order:
      - icone
      - id
      - parametro
      - apple
      - hyprmac
      - prioridade
      - onde
    sort:
      - property: id
        direction: ASC
  - type: table
    name: P1
    filters:
      and:
        - prioridade == "P1"
    order:
      - icone
      - id
      - parametro
      - area
      - apple
      - hyprmac
    sort:
      - property: id
        direction: ASC
"""


# ---------------------------------------------------------------- índices e galerias

def doc_do_script(caminho):
    m = re.search(r'"""(.*?)\n', open(caminho, encoding="utf-8").read(), re.S)
    return m.group(1).strip() if m else ""


def gerar_indices():
    so = lambda prefixo: [o for o in notas if o.startswith(prefixo) and not o.endswith(".json")]
    escrever("Padrões/Padrões.md", propriedades(tags=["indice"]) +
             "# Padrões\n\nRegras transversais destiladas do kit, do HIG e das telas.\n\n" + lista(so("padroes/")) + "\n")
    escrever("Componentes/Componentes.md", propriedades(tags=["indice"]) +
             "# Componentes\n\nMedidas e comportamento de cada peça do macOS Tahoe/27.\n\n" + lista(so("componentes/")) + "\n")
    hig = sorted(so("hig/") , key=nome_da_nota)
    escrever("HIG/HIG.md", propriedades(tags=["indice"]) +
             "# HIG — Human Interface Guidelines\n\n49 páginas do HIG em Markdown (texto da Apple, em inglês) "
             "e duas sessões da WWDC25.\n\n## Páginas\n\n" + lista([o for o in hig if o.endswith(".md")]) +
             "\n\n## WWDC25\n\n" + lista([o for o in hig if o.endswith(".txt")]) + "\n")
    escrever("Tokens/Tokens.md", propriedades(tags=["indice"]) +
             "# Tokens\n\nExtraídos dos kits do Sketch (`extrair_kit.py`). Os `.json` ficam em "
             "`BaseConhecimento/tokens/`.\n\n## macOS 27\n\n" + lista(so("tokens/macos27/")) +
             "\n\n## visionOS\n\n" + lista(so("tokens/visionos/")) + "\n")

    for kit, nome, pasta in (("kit", "macOS 27", "Kit/Contornos macOS 27"),
                             ("kit-visionos", "visionOS", "Kit/Contornos visionOS")):
        paginas = so(f"referencias/{kit}/contornos/")
        previa = ""
        if kit == "kit-visionos":
            previa = f"![[{anexo('referencias/kit-visionos/kit-preview.png')}]]\n\n"
        escrever(f"{pasta}/Contornos {nome}.md", propriedades(tags=["indice", "contorno"]) +
                 f"# Contornos do kit {nome}\n\n{previa}Uma nota por página do kit, com a árvore de camadas e "
                 f"todas as medidas (gerado por `contorno_kit.py`).\n\n" + lista(sorted(paginas, key=nome_da_nota)) + "\n")

    kit = "referencias/kit"
    papeis = sorted(f for f in os.listdir(os.path.join(BASE, kit, "papeis-de-parede")) if "mini" not in f)
    template = sorted(os.listdir(os.path.join(BASE, kit, "icone-app-template")))
    fontes = sorted(os.listdir(os.path.join(BASE, kit, "fontes")))
    texto = ["# Kit macOS 27", "",
             "Material do *Apple macOS 27 UI Kit* (Sketch, Apple Design Resources).", "",
             f"![[{anexo(kit + '/kit-preview.png')}]]", "",
             f"![[{anexo(kit + '/library-preview.png')}]]", "",
             "- [[Contornos macOS 27]] — medidas de todas as páginas",
             "- [[Tokens]] — cores, tipografia e estilos de camada",
             "- [[Ícones de apps]] · [[Ponteiros]]", "",
             "## Papéis de parede", ""]
    texto += [f"![[{anexo(kit + '/papeis-de-parede/' + f)}|900]]\n*{f}*\n" for f in papeis]
    texto += ["## Modelo de ícone de app", "",
              " ".join(f"![[{anexo(kit + '/icone-app-template/' + f)}|160]]" for f in template), "",
             "## Fontes", "",
             "SF Pro (família \"SF Pro\", variável) e SF Pro Rounded Medium — não copiadas para o vault; ficam em "
             "`BaseConhecimento/referencias/kit/fontes/`:", ""]
    texto += [f"- `{f}`" for f in fontes]
    escrever("Kit/Kit macOS 27.md", propriedades(tags=["indice", "kit"]) + "\n".join(texto) + "\n")

    icones = sorted(os.listdir(os.path.join(BASE, kit, "icones-apps")))
    texto = ["# Ícones de apps", "", f"{len(icones)} ícones do kit macOS 27 (variantes Default, Dark, Clear…).", ""]
    texto += [f"![[{anexo(kit + '/icones-apps/' + f)}|96]]" for f in icones]
    escrever("Kit/Ícones de apps.md", propriedades(tags=["kit"]) + "\n".join(texto) + "\n")

    ponteiros = sorted(os.listdir(os.path.join(BASE, kit, "ponteiros")))
    texto = ["# Ponteiros", "", f"{len(ponteiros)} ponteiros do kit macOS 27 em SVG.", "",
             "| Ponteiro | Nome |", "|---|---|"]
    texto += [f"| ![[{anexo(kit + '/ponteiros/' + f)}\\|48]] | {f[:-4]} |" for f in ponteiros]
    escrever("Kit/Ponteiros.md", propriedades(tags=["kit"]) + "\n".join(texto) + "\n")

    slides = sorted(os.listdir(os.path.join(BASE, "referencias/pdfs/macos-pour-windows")))
    texto = ["# macOS pour Windows", "",
             "Slides do PDF *macOS pour les utilisateurs de Windows* (Sequoia). Resumo por página em "
             "[[Telas de referência]].", ""]
    texto += [f"![[{anexo('referencias/pdfs/macos-pour-windows/' + f)}]]\n*{f[:-4]}*\n" for f in slides]
    escrever("Referências/PDFs/macOS pour Windows.md", propriedades(tags=["referencia", "pdf"]) + "\n".join(texto) + "\n")

    escrever("Referências/PDFs/PDFs.md", propriedades(tags=["indice"]) +
             "# PDFs\n\n" + lista(so("referencias/pdfs/")) + "\n- [[macOS pour Windows]]\n")

    ferramentas = sorted(f for f in os.listdir(os.path.join(BASE, "ferramentas")) if f.endswith(".py"))
    readme = open(os.path.join(BASE, "README.md"), encoding="utf-8").read()
    bloco = re.search(r"```sh\n(.*?)```", readme, re.S)
    texto = ["# Ferramentas", "",
             "Scripts em `BaseConhecimento/ferramentas/` (rodar no terminal).", "",
             "## Consultar", "", "```sh", bloco.group(1).rstrip() if bloco else "", "```", "",
             "## Scripts", ""]
    texto += [f"- `{f}` — {doc_do_script(os.path.join(BASE, 'ferramentas', f))}" for f in ferramentas]
    texto += ["", "Depois de mudar a base: `indexar.py` → `comparar.py` → `exportar_obsidian.py`."]
    escrever("Ferramentas.md", propriedades(tags=["indice"]) + "\n".join(texto) + "\n")


# ---------------------------------------------------------------- grafo

def cores_do_grafo():
    caminho = os.path.join(VAULT, ".obsidian", "graph.json")
    if not os.path.exists(caminho):
        return
    g = json.load(open(caminho, encoding="utf-8"))
    if g.get("colorGroups"):
        return   # o usuário já escolheu cores
    paleta = [("tag:#padrao", 0x0088FF), ("tag:#componente", 0x34C759), ("tag:#hig", 0xFF9500),
              ("tag:#token", 0xAF52DE), ("tag:#contorno", 0x8E8E93), ("tag:#parametro", 0xFF383C),
              ("tag:#referencia", 0x00C3D0), ("tag:#indice", 0xFFCC00)]
    g["colorGroups"] = [{"query": q, "color": {"a": 1, "rgb": c}} for q, c in paleta]
    json.dump(g, open(caminho, "w", encoding="utf-8"), indent=2)


def main():
    if not os.path.isdir(os.path.join(VAULT, ".obsidian")):
        sys.exit(f"{VAULT} não parece um vault do Obsidian (sem .obsidian/)")
    anteriores = set(json.load(open(MANIFESTO))) if os.path.exists(MANIFESTO) else set()
    montar_mapa()
    gerar_conteudo()
    for rel in anteriores - gerados:   # o que sumiu da base
        p = os.path.join(VAULT, rel)
        if os.path.exists(p):
            os.remove(p)
    for raiz, dirs, arquivos in os.walk(VAULT, topdown=False):
        if raiz != VAULT and ".obsidian" not in raiz and not os.listdir(raiz):
            os.rmdir(raiz)
    json.dump(sorted(gerados), open(MANIFESTO, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    cores_do_grafo()
    notas_md = sum(1 for g in gerados if g.endswith(".md"))
    print(f"{VAULT}: {notas_md} notas, {len(gerados) - notas_md} anexos/bases")


if __name__ == "__main__":
    main()
