"""Categorias, ordenação e cálculo do Spotlight; sem dependência de GTK.

As categorias legadas derivadas de frames rotulados macOS 27 exigem validação Tahoe 26.
"""
import re
import mimetypes


# categorias do Spotlight do Tahoe ← categorias do freedesktop (a primeira que casar)
SPOT_APP_CATS = (
    ("Productivity & Finance", {"Office", "Finance", "ProjectManagement", "Calendar",
                                "ContactManagement", "WordProcessor", "Spreadsheet",
                                "Presentation", "Email"}),
    ("Social", {"InstantMessaging", "Chat", "IRCClient", "VideoConference", "Telephony"}),
    ("Entertainment", {"Audio", "Music", "Player", "TV", "AudioVideo"}),
    ("Photo & Video", {"Photography", "ImageViewer", "Video", "AudioVideoEditing", "Recorder"}),
    ("Creativity", {"Graphics", "2DGraphics", "VectorGraphics", "RasterGraphics", "3DGraphics",
                    "Art", "Publishing"}),
    ("Developer Tools", {"Development", "IDE", "Debugger", "RevisionControl"}),
    ("Games", {"Game"}),
    ("Education", {"Education", "Science", "Math"}),
    # video/frames-ui/ui_0162 (macOS 27): "Information & Reading" (Books, Dictionary…)
    ("Information & Reading", {"News", "Dictionary", "Literature", "Documentation", "Feed",
                               "Maps"}),
    ("Utilities", {"Utility", "System", "Settings", "Accessories", "FileManager",
                   "TerminalEmulator", "Network", "WebBrowser", "Archiving", "Monitor"}),
)


def spot_app_category(cats):
    have = set((cats or "").split(";"))
    for name, keys in SPOT_APP_CATS:
        if have & keys:
            return name
    return None


SPOT_MODES = {"all": "Spotlight Search", "apps": "Applications", "files": "Files",
              "actions": "Actions", "clipboard": "Clipboard"}
# como no Spotlight, à mesma relevância apps e Ajustes vêm antes de ações, e ações
# antes de arquivos (um arquivo só passa na frente se o nome casar bem melhor)
SPOT_WEIGHT = {"calc": 30, "app": 12, "setting": 10, "action": 6, "file": -18}


def spot_fold(text):
    """minúsculas e sem acento: "Ações" casa com "acoes", como no Spotlight."""
    import unicodedata
    t = unicodedata.normalize("NFKD", (text or "").lower())
    return "".join(c for c in t if not unicodedata.combining(c))


def spot_filter_command(text):
    """Resolve /tipo + Return para escopos existentes, sem analisar uma consulta.

    O Guia Apple Tahoe 26 documenta /tipo seguido de Return. PDF e outros
    tipos sem um escopo implementado aqui continuam consultas comuns.
    """
    text = (text or "").strip()
    if not text.startswith("/"):
        return None
    name = spot_fold(text[1:].strip())
    return {"apps": "apps", "applications": "apps", "folders": "folders",
            "settings": "settings", "system settings": "settings",
            "actions": "actions"}.get(name)


# Só escopos já implementados; caminhos continuam consultas comuns.
SPOT_FILTERS = (
    ("apps", "Applications", "Apps", "system-software-install"),
    ("folders", "Folders", "Folders", "folder"),
    ("settings", "Settings", "Settings", "preferences-system"),
    ("actions", "Actions", "Actions", "system-run-symbolic"),
)


def spot_filters(include_sources=False):
    """Mantém os filtros legados para chamadores sem fontes do shell.

    FirstTimeExperience.loctable 26.6.1 confirma os nomes dos quatro modos;
    a posição de Folders/Settings entre eles ainda exige captura Tahoe.
    """
    if not include_sources:
        return SPOT_FILTERS
    return (SPOT_FILTERS[0], ("files", "Files", "Files", "text-x-generic-symbolic"),
            *SPOT_FILTERS[1:],
            ("clipboard", "Clipboard", "Clipboard", "edit-paste-symbolic"))


def spot_filter_results(text, include_sources=False):
    """None para consulta comum; lista (inclusive vazia) para /prefixo."""
    text = (text or "").strip()
    if not re.fullmatch(r"/[A-Za-z ]*", text):
        return None
    prefix = spot_fold(text[1:].strip())
    return [{"kind": "filter", "name": label, "id": "filter:" + key,
             "key": key, "icons": [icon], "sub": "Filter results"}
            for key, label, token, icon in spot_filters(include_sources)
            if spot_fold(label).startswith(prefix) or spot_fold(token).startswith(prefix)
            or (key == "settings" and "system settings".startswith(prefix))]


def spot_filter_scope(item, include_sources=False):
    """Resultado do seletor → token; não aceita tipos sem implementação."""
    if item.get("kind") == "filter":
        for key, label, _token, icon in spot_filters(include_sources):
            if item.get("key") == key:
                return {"key": key, "label": label, "icon": icon}
    return None


def spot_file_query(text):
    """Separa tipos conhecidos do nome; tokens desconhecidos ficam literais."""
    aliases = {"pdf": "pdf", "pdfs": "pdf", "image": "image", "images": "image",
               "folder": "folder", "folders": "folder"}
    kinds = []

    def take(match):
        kind = aliases.get(match.group(1).lower())
        if kind:
            kinds.append(kind)
            return ""
        return match.group(0)

    query = re.sub(r"(?<!\S)kind:([A-Za-z]+)(?!\S)", take, (text or "").strip(),
                   flags=re.IGNORECASE)
    words = query.split()
    if words and words[0].lower() in aliases:
        kinds.append(aliases[words.pop(0).lower()])
    return " ".join(words), tuple(dict.fromkeys(kinds))


def spot_file_matches(item, kinds):
    """MIME calculado por Gio no shell; extensão para itens sem metadata."""
    if not kinds:
        return True
    is_dir = item.get("is_dir", False)
    mime = item.get("mime") or mimetypes.guess_type(item.get("path") or item["name"])[0] or ""
    return all((is_dir if kind == "folder" else
                not is_dir and (mime == "application/pdf" if kind == "pdf"
                                else mime.startswith("image/"))) for kind in kinds)


def spot_app_scope(item):
    """App + Tab → escopo com identidade e ícone preservados."""
    if not item or item.get("kind") != "app":
        return None
    name = spot_fold(item["name"])
    desktop = (item.get("id") or "").rsplit("/", 1)[-1].removesuffix(".desktop")
    target = "windows"
    if name in ("finder", "files", "nautilus") or desktop == "org.gnome.Nautilus":
        target = "files"
    elif name in ("system settings", "settings") or desktop in (
            "hyprmac-ajustes", "dev.hyprmac.Settings", "org.gnome.Settings"):
        target = "settings"
    identities = {spot_fold(v) for v in (desktop, desktop.rsplit(".", 1)[-1],
                  item["name"], item.get("wm_class", ""), item.get("executable", "")) if v}
    return {"key": "app:" + item["id"], "label": item["name"],
            "gicon": item.get("gicon"), "app": item, "target": target,
            "identities": identities}


def spot_app_results(scope, query, clients=(), actions=(), files=(), settings=()):
    """Busca em app sem GTK nem IPC; clientes e ações vêm do chamador."""
    q = spot_fold(query.strip())
    target = scope["target"]
    if target == "files":
        query, kinds = spot_file_query(query)
        q = spot_fold(query)
        candidates = [it for it in files if spot_file_matches(it, kinds)]
    elif target == "settings":
        candidates = list(settings)
    else:
        identities = scope["identities"]
        candidates = [{"kind": "window", "name": c.get("title") or scope["label"],
                       "sub": scope["label"], "id": c["address"],
                       "address": c["address"], "gicon": scope.get("gicon")}
                      for c in clients if c.get("address") and c.get("mapped", True)
                      and not c.get("hidden") and any(spot_fold(c.get(k)) in identities
                                                     for k in ("class", "initialClass"))]
        candidates.extend(actions)
    ranked = [(spot_score(q, it["name"], it.get("extra", "")), it) for it in candidates]
    return [it for score, it in sorted(ranked, key=lambda t: -t[0]) if score][:200]


def spot_score(q, name, extra=""):
    n = spot_fold(name)
    if not q:
        return 1
    if n == q:
        return 100
    if n.startswith(q):
        return 90 - min(len(n) - len(q), 30) * 0.1
    words = [w for w in re.split(r"[\s\-_.()/]+", n) if w]
    if any(w.startswith(q) for w in words):
        return 75
    if "".join(w[0] for w in words).startswith(q) and len(q) > 1:
        return 70
    if q in n:
        return 60
    # várias palavras: todas no nome, em qualquer ordem ("base conhecimento" acha
    # "BaseConhecimento"; "chrome google" acha "Google Chrome")
    qs = q.split()
    if len(qs) > 1:
        if q.replace(" ", "") in n.replace(" ", ""):
            return 58
        if all(w in n for w in qs):
            return 50
    if extra:
        e = spot_fold(extra)
        if any(w.startswith(q) for w in re.split(r"[\s\-_.()/;]+", e) if w):
            return 55       # "term" acha o Ghostty pelo nome genérico "Terminal"
        if len(q) > 2 and q in e:
            return 35
    # letras na ordem ("gcc" → "Google Chrome Canary"): só com 4+ letras e no começo
    # das palavras, senão "som" casaria com "About This Computer"
    if len(q) >= 4 and n[:1] == q[:1]:
        it = iter(n)
        if all(c in it for c in q):
            return 18
    return 0


def spot_calc(q):
    """Conta simples digitada no campo ("12*7+1", "2^10", "15% de 80")."""
    import ast
    import operator as op
    s = q.replace(",", ".").replace("×", "*").replace("÷", "/").replace("^", "**")
    m = re.fullmatch(r"\s*([\d.]+)\s*%\s*(?:de|of)\s*([\d.]+)\s*", s)
    if m:
        s = f"{m.group(1)}/100*{m.group(2)}"
    if not re.fullmatch(r"[\d.\s+\-*/()%]+", s) or not re.search(r"\d\s*[-+*/%]", s):
        return None
    ops = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul, ast.Div: op.truediv,
           ast.Pow: op.pow, ast.Mod: op.mod, ast.USub: op.neg, ast.UAdd: op.pos}

    def ev(n):
        if isinstance(n, ast.Constant) and isinstance(n.value, (int, float)):
            return n.value
        if isinstance(n, ast.BinOp) and type(n.op) in ops:
            if isinstance(n.op, ast.Pow) and abs(ev(n.right)) > 100:
                raise ValueError
            return ops[type(n.op)](ev(n.left), ev(n.right))
        if isinstance(n, ast.UnaryOp) and type(n.op) in ops:
            return ops[type(n.op)](ev(n.operand))
        raise ValueError
    try:
        v = ev(ast.parse(s, mode="eval").body)
    except Exception:
        return None
    if isinstance(v, float):
        v = round(v, 10)
        v = int(v) if v.is_integer() else v
    return f"{v:,}".replace(",", " ") if isinstance(v, int) else str(v)
