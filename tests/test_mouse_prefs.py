"""MIC-07: "Tracking speed" e "Natural scrolling" dos Ajustes sobrevivem ao hyprctl reload.

O hyprmac.lua lê mouse_* do config.json a cada carga; sem as chaves, não mexe no que o
hyprland.lua do usuário definiu. Executa o trecho Lua real com um hl falso.
"""

import json
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
STUB = 'hl={config=function(t) for k,v in pairs(t.input) do print(k.."="..tostring(v)) end end}'


def snippet():
    lines = (ROOT / "hypr" / "hyprmac.lua").read_text().splitlines()
    start = next(i for i, l in enumerate(lines) if l.startswith("-- Ajustes ▸ Mouse grava"))
    end = next(i for i in range(start, len(lines)) if lines[i] == "end")
    return "\n".join(lines[start:end + 1])


@unittest.skipUnless(shutil.which("lua"), "lua ausente")
class MousePrefs(unittest.TestCase):
    def apply(self, conf):
        with tempfile.TemporaryDirectory() as home:
            path = Path(home) / ".config" / "hyprmac"
            path.mkdir(parents=True)
            (path / "config.json").write_text(json.dumps(conf))
            script = Path(home) / "mouse.lua"
            script.write_text(snippet())
            out = subprocess.run(["lua", "-e", STUB, str(script)], capture_output=True, text=True,
                                 env={"HOME": home}, check=True).stdout
        return dict(line.split("=") for line in out.split())

    def test_without_keys_user_config_wins(self):
        self.assertEqual(self.apply({"reduce_motion": True}), {})

    def test_saved_choices_are_reapplied(self):
        self.assertEqual(self.apply({"mouse_natural_scroll": True, "mouse_sensitivity": -0.35}),
                         {"natural_scroll": "true", "sensitivity": "-0.35"})

    def test_sensitivity_is_clamped(self):
        self.assertEqual(self.apply({"mouse_sensitivity": 3})["sensitivity"], "1")

    def test_settings_pane_saves_both(self):
        source = (ROOT / "shell" / "hyprmac-ajustes").read_text()
        self.assertIn('set_clock_conf("mouse_natural_scroll"', source)
        self.assertIn('set_clock_conf("mouse_sensitivity"', source)


if __name__ == "__main__":
    unittest.main()
