"""Itens da barra de menus que podem ser mostrados/ocultados (Menu Bar Controls).

Compartilhado por Ajustes ▸ Menu Bar e pela galeria da Central de Controle ("Add to Menu
Bar"/"Remove from Menu Bar", strings de BentoGallery.loctable do ControlCenter 26.6.1).
Estado em ~/.config/hyprmac/barra.json {"hidden": [...]}; a Waybar lê o CSS gerado
waybar/barra-ocultos.css e recarrega com SIGUSR2.
"""
import json
import os
import subprocess

CONF_DIR = os.path.expanduser("~/.config/hyprmac")
ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

# chave → seletor do módulo na Waybar (só o que a barra do hyprmac tem)
SELECTORS = {
    "headphones": "#custom-headphones",
    "sleep": "#custom-sleep",
    "wifi": "#network",
    "battery": "#battery",
    "vpn": "#custom-vpn",
    "focus": "#custom-focus",
    "nowplaying": "#mpris",
    "spotlight": "#custom-spotlight",
}
DEFAULT_HIDDEN = {"headphones", "sleep"}
# controle da Central → item da barra correspondente
CC_TO_BAR = {"wifi": "wifi", "vpn": "vpn", "dnd": "focus", "nowplaying": "nowplaying"}


def _conf_path(conf_dir):
    return os.path.join(conf_dir or CONF_DIR, "barra.json")


def hidden(conf_dir=None):
    try:
        with open(_conf_path(conf_dir)) as fh:
            return set(json.load(fh).get("hidden", []))
    except FileNotFoundError:
        return set(DEFAULT_HIDDEN)
    except (OSError, ValueError, AttributeError):
        return set()


def css_for(hidden_keys):
    sels = [SELECTORS[k] for k in sorted(hidden_keys) if k in SELECTORS]
    return "/* gerado por Ajustes ▸ Menu Bar — não editar */\n" + "".join(
        f"window#waybar {sel} {{ font-size: 0; padding: 0; margin: 0; min-width: 0; "
        "border: none; background: none; }\n" for sel in sels)


def set_shown(key, on, conf_dir=None, root=None, reload_bar=True):
    """Mostra/oculta o item; devolve o conjunto de ocultos resultante."""
    h = hidden(conf_dir)
    (h.discard if on else h.add)(key)
    path = _conf_path(conf_dir)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    try:
        with open(path) as fh:
            data = json.load(fh)
        if not isinstance(data, dict):
            data = {}
    except (OSError, ValueError):
        data = {}
    data["hidden"] = sorted(h)
    with open(path, "w") as fh:
        json.dump(data, fh, indent=1)
    try:
        with open(os.path.join(root or ROOT, "waybar", "barra-ocultos.css"), "w") as fh:
            fh.write(css_for(h))
    except OSError:
        return h
    if reload_bar:
        subprocess.Popen(["pkill", "-SIGUSR2", "-x", "waybar"], stdout=subprocess.DEVNULL,
                         stderr=subprocess.DEVNULL, start_new_session=True)
    return h
