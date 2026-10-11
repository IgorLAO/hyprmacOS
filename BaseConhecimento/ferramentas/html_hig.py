#!/usr/bin/env python3
"""Converte páginas do HIG salvas pelo navegador ("Página completa") em Markdown.

  html_hig.py <página.html> <pasta-hig-de-saída>

Gera <saída>/<slug>.md com títulos, parágrafos, listas, tabelas e as figuras no lugar
(copiadas para <saída>/imagens/<slug>/), descartando menus do site, scripts e vídeos.
"""
import html
import os
import re
import shutil
import sys
import urllib.request
from html.parser import HTMLParser

SKIP_TAGS = {"script", "style", "noscript", "svg", "nav", "header", "footer", "button", "form"}
BLOCK = {"p", "li", "h1", "h2", "h3", "h4", "h5", "td", "th", "figcaption", "caption", "dt", "dd"}


class Conv(HTMLParser):
    def __init__(self, base_dir, img_out, img_rel):
        super().__init__(convert_charrefs=True)
        self.base_dir, self.img_out, self.img_rel = base_dir, img_out, img_rel
        self.out = []
        self.buf = []
        self.skip = 0
        self.stack = []
        self.list_depth = 0
        self.in_main = False
        self.row = None
        self.images = 0

    def flush(self, prefix=""):
        text = re.sub(r"\s+", " ", "".join(self.buf)).strip()
        self.buf = []
        if text:
            self.out.append(prefix + text)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "main" or (tag == "div" and "content" in (a.get("class") or "") and not self.in_main
                             and a.get("id") == "main"):
            self.in_main = True
        if tag in SKIP_TAGS:
            self.skip += 1
        if self.skip:
            return
        self.stack.append(tag)
        if tag in ("ul", "ol"):
            self.list_depth += 1
        if tag in BLOCK:
            self.buf = []
        if tag == "tr":
            self.row = []
        if tag == "img" and self.in_main:
            self.image(a)
        if tag == "br":
            self.buf.append(" ")

    def image(self, a):
        src = a.get("src") or ""
        if not src or "wide_250x141" in src or src.startswith("data:") or "checkmark@" in src or "crossout@" in src:
            if "checkmark@" in src:
                self.buf.append(" ✅ ")
            elif "crossout@" in src:
                self.buf.append(" ❌ ")
            return
        src = html.unescape(src)
        os.makedirs(self.img_out, exist_ok=True)
        name = os.path.basename(src.split("?")[0])
        dst = os.path.join(self.img_out, name)
        if src.startswith("http"):
            # figura não salva localmente: baixa do site da Apple
            if not os.path.exists(dst):
                try:
                    urllib.request.urlretrieve(src, dst)
                except Exception:
                    return
        else:
            path = os.path.normpath(os.path.join(self.base_dir, src))
            if not os.path.exists(path):
                return
            shutil.copy(path, dst)
        alt = (a.get("alt") or name).replace("\n", " ").strip()
        self.flush()
        self.out.append(f"![{alt}]({self.img_rel}/{name})")
        self.images += 1

    def handle_endtag(self, tag):
        if tag in SKIP_TAGS:
            self.skip = max(0, self.skip - 1)
            return
        if self.skip:
            return
        if self.stack and self.stack[-1] == tag:
            self.stack.pop()
        if not self.in_main:
            self.buf = []
            return
        if tag in ("h1", "h2", "h3", "h4", "h5"):
            self.flush("\n" + "#" * int(tag[1]) + " ")
        elif tag == "li":
            self.flush("  " * (self.list_depth - 1) + "- ")
        elif tag in ("p", "figcaption", "dt", "dd", "caption"):
            self.flush()
        elif tag in ("td", "th"):
            text = re.sub(r"\s+", " ", "".join(self.buf)).strip()
            self.buf = []
            if self.row is not None:
                self.row.append(text)
        elif tag == "tr" and self.row is not None:
            if any(self.row):
                self.out.append("| " + " | ".join(self.row) + " |")
            self.row = None
        elif tag in ("ul", "ol"):
            self.list_depth = max(0, self.list_depth - 1)

    def handle_data(self, data):
        if not self.skip:
            self.buf.append(data)


def real_title(text):
    """O nome do arquivo salvo pode não bater com o conteúdo: vale o <h1 class="title">."""
    m = re.search(r'<h1[^>]*class="title"[^>]*>(.*?)</h1>', text, re.S)
    return html.unescape(re.sub(r"<[^>]+>", "", m.group(1))).strip() if m else None


def main(src, outdir):
    raw = open(src, encoding="utf-8", errors="replace").read()
    title = real_title(raw) or os.path.basename(src).split(" _ ")[0]
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    base_dir = os.path.dirname(os.path.abspath(src))
    conv = Conv(base_dir, os.path.join(outdir, "imagens", slug), f"imagens/{slug}")
    conv.feed(raw)
    lines = conv.out
    # do título da página até antes de "Resources"/"Change log"
    start = next((i for i, ln in enumerate(lines) if ln.strip() == f"# {title}"), 0)
    end = next((i for i, ln in enumerate(lines) if i > start and re.match(r"\n?## (Resources|Change log)", ln)),
               len(lines))
    body = "\n\n".join(lines[start:end])
    body = re.sub(r"\n{3,}", "\n\n", body).strip()
    with open(os.path.join(outdir, f"{slug}.md"), "w") as f:
        f.write(f"<!-- fonte: {os.path.basename(src)} (HIG salvo do navegador) -->\n\n{body}\n")
    print(f"{slug}.md: {len(body.split())} palavras, {conv.images} figuras")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
