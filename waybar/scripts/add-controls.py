#!/usr/bin/env python3
"""O + aparece na barra somente durante a edição da Central de Controle."""
import json
import os
from pathlib import Path

active = (Path(os.environ.get("XDG_RUNTIME_DIR", "/tmp")) / "hyprmac-cc-edit").exists()
print(json.dumps({"text": "+" if active else "", "class": "on" if active else "off",
                  "tooltip": "Add Controls to Menu Bar" if active else ""}))
