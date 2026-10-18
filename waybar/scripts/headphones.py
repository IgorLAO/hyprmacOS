#!/usr/bin/env python3
"""Mostra fones apenas quando a saída PipeWire ativa é um fone/headset."""
import json
import subprocess
from pathlib import Path

config = Path.home() / ".config/hyprmac/barra.json"
try:
    enabled = "headphones" not in json.loads(config.read_text()).get("hidden", [])
except FileNotFoundError:
    enabled = False
except (OSError, ValueError, AttributeError):
    enabled = False

try:
    out = subprocess.run(["wpctl", "inspect", "@DEFAULT_AUDIO_SINK@"],
                         capture_output=True, text=True, timeout=2).stdout.lower()
except (OSError, subprocess.TimeoutExpired):
    out = ""
connected = enabled and any(word in out for word in ("bluez_output", "headphones", "headset", "earbuds"))
print(json.dumps({"text": "󰋋" if connected else "", "class": "on" if connected else "off",
                  "tooltip": "Headphones · Sound Outputs" if connected else ""}))
