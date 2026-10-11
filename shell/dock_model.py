"""Conteúdo e política de atualização do Dock, sem GTK ou consultas ao compositor."""

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
