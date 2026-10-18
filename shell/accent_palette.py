"""Destaques AppKit Tahoe 26; não confundir com system*Color do kit."""

import json
from pathlib import Path

# nome → (escuro, claro): controlAccent*Color do macOS Tahoe 26.6.1 (25G76), lidos de
# SystemAppearance.bundle/{DarkAqua,Aqua}.car — as cores de destaque clássicas, não os
# systemBlue/systemPurple… (os valores anteriores vinham do kit macOS 27 "System Colors")
CORES = {item["name"]: (item["dark"], item["light"])
         for item in json.loads((Path(__file__).resolve().parents[1] / "core/accent/palette.json").read_text())}

GNOME_ACCENTS = {**{k: v for k, v in CORES.items() if k != "graphite"},
                 "slate": CORES["graphite"], "teal": CORES["blue"]}


def accent_hex(name, dark):
    return GNOME_ACCENTS.get(name, CORES["blue"])[0 if dark else 1]
