#!/usr/bin/env -S python3 -S
"""Um resultado de menu por foco; o shell sinaliza a Waybar quando a classe muda.

Uso: app-menu.py <rótulo> <regex de classe>. O snapshot atômico do shell evita
uma consulta hyprctl por módulo. Sem shell, consulta a janela ativa diretamente.
"""
import json
import os
import re
import sys


def active_class():
    path = os.path.join(os.environ.get("XDG_RUNTIME_DIR", "/tmp"),
                        "hyprmac-active-class.json")
    try:
        with open(path, encoding="utf-8") as f:
            state = json.load(f)
        os.kill(state["pid"], 0)
        return state["class"]
    except (OSError, ValueError, KeyError, TypeError):
        pass
    try:
        import subprocess
        result = subprocess.run(["hyprctl", "activewindow", "-j"],
                                capture_output=True, text=True, timeout=2)
        return json.loads(result.stdout or "{}").get("class", "")
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return ""


def main():
    if len(sys.argv) != 3:
        raise SystemExit("uso: app-menu.py <rótulo> <regex de classe>")
    label, pattern = sys.argv[1], re.compile(sys.argv[2])
    print(json.dumps({"text": label if pattern.search(active_class()) else ""}))


if __name__ == "__main__":
    main()
