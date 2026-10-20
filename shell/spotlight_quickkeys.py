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

# A view GTK conserva esta interface enquanto a lógica roda no módulo Rust.
# O código acima fica como reserva para um checkout ainda não compilado.
import ctypes
from pathlib import Path

_LIB = (Path(__file__).resolve().parents[1]
        / "core/spotlight-quickkeys/target/release/libhyprmac_spotlight_quickkeys.so")
try:
    _rust = ctypes.CDLL(str(_LIB))
    _rust.hyprmac_quickkeys.argtypes = [ctypes.c_char_p, ctypes.c_void_p, ctypes.c_size_t]
    _rust.hyprmac_quickkeys.restype = ctypes.c_size_t
except OSError:
    _rust = None

RUST_ACTIVE = _rust is not None
_python_load, _python_save = load, save
_python_normalize, _python_effective = normalize, effective
_python_suggest, _python_assign, _python_after_run = suggest, assign, after_run


def _call(request):
    raw = json.dumps(request, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    buffer = ctypes.create_string_buffer(len(raw) * 4 + 64)
    needed = _rust.hyprmac_quickkeys(raw, buffer, len(buffer))
    if needed >= len(buffer):
        buffer = ctypes.create_string_buffer(needed + 1)
        _rust.hyprmac_quickkeys(raw, buffer, len(buffer))
    return json.loads(buffer.value)


def load(path=PATH):
    if _rust is None:
        return _python_load(path)
    return _call({"op": "load", "path": os.fspath(path)})


def save(overrides, path=PATH):
    if _rust is None:
        return _python_save(overrides, path)
    result = _call({"op": "save", "path": os.fspath(path), "overrides": overrides})
    if isinstance(result, dict) and "error" in result:
        raise OSError(result["error"])


def normalize(text):
    if _rust is None:
        return _python_normalize(text)
    return _call({"op": "normalize", "text": text or ""})


def effective(actions, overrides):
    if _rust is None:
        return _python_effective(actions, overrides)
    simple = [{"id": action["id"], "key": action.get("key") or ""} for action in actions]
    return _call({"op": "effective", "actions": simple, "overrides": overrides})


def suggest(label, taken):
    if _rust is None:
        return _python_suggest(label, taken)
    return _call({"op": "suggest", "label": label or "", "taken": list(taken)})


def assign(overrides, action_id, key, keys):
    if _rust is None:
        return _python_assign(overrides, action_id, key, keys)
    return _call({"op": "assign", "overrides": overrides, "action_id": action_id,
                  "key": key or "", "keys": keys})


def after_run(overrides, action, keys):
    if _rust is None:
        return _python_after_run(overrides, action, keys)
    simple = {field: action[field] for field in ("id", "label", "name") if field in action}
    result = _call({"op": "after_run", "overrides": overrides,
                    "action": simple, "keys": keys})
    return result["value"] if result["changed"] else overrides
