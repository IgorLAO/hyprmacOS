"""Conteúdo e política de atualização do Dock, sem GTK ou consultas ao compositor."""

import ctypes
import json
from pathlib import Path

REFRESH_EVENTS = frozenset((
    "openwindow", "closewindow", "movewindowv2", "activewindowv2",
    "windowtitlev2", "changefloatingmode", "fullscreen",
))


def needs_refresh(line):
    return line.split(">>", 1)[0] in REFRESH_EVENTS


def build_items(clients, pinned_items, key_of_class, info_of_class, display_name):
    """Compõe seções e associa janelas; ícones e miniaturas são resolvidos pela UI.

    Preserva a ordenação estável por foco do shell, inclusive janelas especiais.
    Não modifica o snapshot recebido nem os registros de apps fixos.
    """
    clients = sorted((c for c in clients if c.get("mapped")),
                     key=lambda c: c.get("focusHistoryID", 99))
    by_key = {}
    for client in clients:
        cls = client.get("class") or client.get("initialClass") or ""
        if cls and cls != "hyprmac-shell":
            by_key.setdefault(key_of_class(cls), []).append(client)
    items = [dict(item) for item in pinned_items]
    shown = {item["key"] for item in items}
    for key, windows in by_key.items():
        if key not in shown:
            if not any(item["kind"] == "sep" for item in items):
                items.append(dict(key="hyprmac:sep-recent", kind="sep"))
            cls = windows[0].get("class")
            items.append(dict(key=key, pin=None, kind="app", info=info_of_class(cls),
                              cls=cls, name=display_name(cls)))
    for item in items:
        item["windows"] = [] if item["kind"] == "sep" else by_key.get(item["key"], [])
    items.append(dict(key="hyprmac:sep", kind="sep"))
    for client in clients:
        if client["workspace"]["name"] == "special:minimized":
            cls = client.get("class") or client.get("initialClass") or ""
            items.append(dict(key="min:" + client["address"], kind="minimized", win=client,
                              cls=cls, info=info_of_class(cls),
                              name=client.get("title") or display_name(cls), windows=[]))
    items.extend((dict(key="hyprmac:downloads", kind="downloads", name="Downloads", windows=[]),
                  dict(key="hyprmac:trash", kind="trash", name="Trash", windows=[])))
    return items


def reorder_pinned(items, pinned, source, target):
    """Move uma vaga fixa; Finder, separadores e apps não fixos não são destinos."""
    def movable(item):
        return bool(item.get("pin") and item["pin"] != "hyprmac:finder")
    if not (0 <= source < len(items) and 0 <= target < len(items)):
        return False
    if source == target or not movable(items[source]) or not movable(items[target]):
        return False
    pin = items[source]["pin"]
    destination = pinned.index(items[target]["pin"])
    pinned.remove(pin)
    pinned.insert(destination, pin)
    items.insert(target, items.pop(source))
    return True


def pin_slot(items, pinned, x, origin_x, icon):
    """Return the insertion position in the fixed section for a Dock x coordinate."""
    slot = 0
    for item in items:
        if item.get("pin") not in pinned:
            break
        if x < origin_x + item["x"] + icon / 2:
            break
        slot += 1
    return max(1 if pinned and pinned[0] == "hyprmac:finder" else 0, slot)


def insert_pin(pinned, pin, slot):
    """Add or move an app without duplicates; Finder stays at the first slot."""
    if not pin or pin == "hyprmac:finder":
        return False
    before = list(pinned)
    old = pinned.index(pin) if pin in pinned else None
    if old is not None:
        pinned.pop(old)
        if old < slot:
            slot -= 1
    floor = 1 if pinned and pinned[0] == "hyprmac:finder" else 0
    pinned.insert(max(floor, min(slot, len(pinned))), pin)
    return pinned != before


# A view conserva estas assinaturas e os objetos Gio/Python. O núcleo Rust
# decide seções e política de fixação sem conhecer GTK nem abrir outro socket.
_LIB = (Path(__file__).resolve().parents[1]
        / "core/dock-model/target/release/libhyprmac_dock_model.so")
try:
    _rust = ctypes.CDLL(str(_LIB))
    _rust.hyprmac_dock_model.argtypes = [ctypes.c_char_p, ctypes.c_void_p, ctypes.c_size_t]
    _rust.hyprmac_dock_model.restype = ctypes.c_size_t
except OSError:
    _rust = None

RUST_MODEL_ACTIVE = _rust is not None
_python_needs_refresh = needs_refresh
_python_build_items = build_items
_python_reorder_pinned = reorder_pinned
_python_pin_slot = pin_slot
_python_insert_pin = insert_pin


def _call(request):
    raw = json.dumps(request, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    output = ctypes.create_string_buffer(len(raw) * 4 + 64)
    needed = _rust.hyprmac_dock_model(raw, output, len(output))
    if needed >= len(output):
        output = ctypes.create_string_buffer(needed + 1)
        _rust.hyprmac_dock_model(raw, output, len(output))
    return json.loads(output.value)


def needs_refresh(line):
    if _rust is None:
        return _python_needs_refresh(line)
    return _call({"op": "needs_refresh", "line": line})


def build_items(clients, pinned_items, key_of_class, info_of_class, display_name):
    if _rust is None:
        return _python_build_items(clients, pinned_items, key_of_class,
                                   info_of_class, display_name)
    ordered = sorted((client for client in clients if client.get("mapped")),
                     key=lambda client: client.get("focusHistoryID", 99))
    descriptors = []
    for client in ordered:
        cls = client.get("class") or client.get("initialClass") or ""
        key = key_of_class(cls) if cls and cls != "hyprmac-shell" else None
        if key is not None and not isinstance(key, str):
            return _python_build_items(clients, pinned_items, key_of_class,
                                       info_of_class, display_name)
        descriptors.append({"class": cls, "key": key,
                            "workspace": client["workspace"]["name"]})
    pinned = [{"key": item["key"], "kind": item["kind"]}
              for item in pinned_items]
    if any(not isinstance(item["key"], str) for item in pinned):
        return _python_build_items(clients, pinned_items, key_of_class,
                                   info_of_class, display_name)
    plan = _call({"op": "build_plan", "clients": descriptors, "pinned": pinned})
    items = []
    for entry in plan:
        kind = entry["type"]
        if kind == "pinned":
            item = dict(pinned_items[entry["index"]])
            item["windows"] = [ordered[index] for index in entry["windows"]]
        elif kind == "sep":
            item = {"key": entry["key"], "kind": "sep"}
            if entry["key"] != "hyprmac:sep":
                item["windows"] = []
        elif kind == "recent":
            client = ordered[entry["first"]]
            cls = client.get("class")
            item = {"key": entry["key"], "pin": None, "kind": "app",
                    "info": info_of_class(cls), "cls": cls, "name": display_name(cls),
                    "windows": [ordered[index] for index in entry["windows"]]}
        elif kind == "minimized":
            client = ordered[entry["index"]]
            cls = client.get("class") or client.get("initialClass") or ""
            item = {"key": "min:" + client["address"], "kind": "minimized",
                    "win": client, "cls": cls, "info": info_of_class(cls),
                    "name": client.get("title") or display_name(cls), "windows": []}
        else:
            item = {"key": "hyprmac:" + kind, "kind": kind,
                    "name": kind.capitalize(), "windows": []}
        items.append(item)
    return items


def reorder_pinned(items, pinned, source, target):
    if _rust is None:
        return _python_reorder_pinned(items, pinned, source, target)
    simple = [{"pin": item.get("pin")} for item in items]
    result = _call({"op": "reorder", "items": simple, "pinned": pinned,
                    "source": source, "target": target})
    if not result["changed"]:
        return False
    pinned[:] = result["pinned"]
    items.insert(target, items.pop(source))
    return True


def pin_slot(items, pinned, x, origin_x, icon):
    if _rust is None:
        return _python_pin_slot(items, pinned, x, origin_x, icon)
    simple = [{"pin": item.get("pin"), "x": item.get("x")}
              for item in items]
    return _call({"op": "pin_slot", "items": simple, "pinned": pinned,
                  "x": x, "origin_x": origin_x, "icon": icon})


def insert_pin(pinned, pin, slot):
    if _rust is None:
        return _python_insert_pin(pinned, pin, slot)
    result = _call({"op": "insert_pin", "pinned": pinned, "pin": pin,
                    "slot": slot})
    if result["changed"]:
        pinned[:] = result["pinned"]
    return result["changed"]
