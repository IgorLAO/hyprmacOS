"""Quick keys do Spotlight (macOS Tahoe 26), sem GTK.

Mac User Guide ▸ "Take actions and shortcuts in Spotlight": "Click 'Add quick keys' next
to an action, then enter the keyboard shortcut"; "Click the assigned quick key field, make
your change, then press Return"; "Suggested quick keys are automatically assigned after
running an action once"; digitar a tecla no Spotlight leva à ação ("ft Ashley").

As teclas fixas do scripts/spotlight-itens (nt, sc, lk…) valem como sugestões; o que a
pessoa escolhe fica em ~/.config/hyprmac/spotlight-quickkeys.json ({id: tecla}; "" =
sem tecla) e tem prioridade.
"""

import json
import os
import re

PATH = os.path.expanduser("~/.config/hyprmac/spotlight-quickkeys.json")
MAX_LEN = 8


def load(path=PATH):
    try:
        with open(path) as f:
            data = json.load(f)
        return {str(k): str(v) for k, v in data.items()} if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def save(overrides, path=PATH):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w") as f:
        json.dump(overrides, f, ensure_ascii=False, indent=1, sort_keys=True)
    os.replace(tmp, path)


def normalize(text):
    """Tecla como a pessoa digitou, sem espaços nem pontuação, em minúsculas."""
    return re.sub(r"[^0-9a-zà-ÿ]", "", (text or "").lower())[:MAX_LEN]


def effective(actions, overrides):
    """{id: tecla} valendo agora: escolha da pessoa, senão a sugestão fixa da ação."""
    keys = {}
    for a in actions:
        key = overrides.get(a["id"], a.get("key") or "")
        if key:
            keys[a["id"]] = key
    return keys


def suggest(label, taken):
    """Iniciais das palavras ("Start FaceTime Call" → "sfc"); se já usada, acrescenta letras
    da última palavra até ficar única."""
    words = re.findall(r"[0-9A-Za-zÀ-ÿ]+", label or "")
    if not words:
        return ""
    base = normalize("".join(w[0] for w in words))
    if len(base) == 1 and len(words[0]) > 1:
        base = normalize(words[0][:2])
    key, extra = base, words[-1][1:]
    for ch in normalize(extra):
        if key not in taken:
            break
        key = (key + ch)[:MAX_LEN]
    n = 2
    while key in taken:
        key, n = f"{base}{n}", n + 1
    return key


def assign(overrides, action_id, key, keys):
    """Grava a tecla escolhida para a ação; tecla de outra ação passa para esta.
    Devolve o dicionário novo (vazio remove a tecla)."""
    key = normalize(key)
    out = dict(overrides)
    if key:
        for other, k in keys.items():
            if k == key and other != action_id:
                out[other] = ""
    out[action_id] = key
    return out


def after_run(overrides, action, keys):
    """Depois de rodar uma ação sem tecla, atribui a sugerida (só na primeira vez:
    uma tecla removida pela pessoa fica removida)."""
    if action["id"] in overrides or keys.get(action["id"]):
        return overrides
    key = suggest(action.get("label") or action.get("name", ""), set(keys.values()))
    if not key:
        return overrides
    out = dict(overrides)
    out[action["id"]] = key
    return out
