#!/usr/bin/env python3
"""Indicador do modo Sleep Focus local, ativado no menu de controles."""
import json
import os
from pathlib import Path

path = Path(os.environ.get("XDG_RUNTIME_DIR", "/tmp")) / "hyprmac-dnd"
config = Path.home() / ".config/hyprmac/barra.json"
try:
    active = path.read_text().strip() == "sleep"
except OSError:
    active = False
try:
    enabled = "sleep" not in json.loads(config.read_text()).get("hidden", [])
except (OSError, ValueError, AttributeError):
    enabled = False
active = active and enabled
print(json.dumps({"text": "󰒲" if active else "", "class": "on" if active else "off",
                  "tooltip": "Sleep Focus" if active else ""}))
