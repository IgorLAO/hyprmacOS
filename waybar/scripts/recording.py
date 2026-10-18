#!/usr/bin/env python3
"""Estado da gravação HyprMac para o ícone de parada da Waybar."""
import json
import os
from pathlib import Path

pidfile = Path(os.environ.get("XDG_RUNTIME_DIR", "/tmp")) / "hyprmac-gravacao.pid"
try:
    pid = int(pidfile.read_text())
    os.kill(pid, 0)
except (OSError, ValueError):
    print(json.dumps({"text": "", "class": "off"}))
else:
    print(json.dumps({"text": "   ", "class": "on", "tooltip": "Stop Screen Recording"}))
