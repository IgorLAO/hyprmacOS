"""Integração do comando Rust de aparência automática com a configuração e o tema."""
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
BIN = ROOT / "core/appearance/target/release/hyprmac-aparencia"


class AutoAppearance(unittest.TestCase):
    def run_check(self, appearance_mode, scheme):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            config = root / ".config/hyprmac"
            config.mkdir(parents=True)
            (config / "config.json").write_text(json.dumps({"appearance_mode": appearance_mode}))
            scripts = root / "scripts"
            scripts.mkdir()
            theme = scripts / "theme"
            theme.write_text('#!/bin/sh\necho "$1" >> "$HYPRMAC_TEST_THEME_LOG"\n')
            theme.chmod(0o755)
            fake_settings = root / "gsettings"
            fake_settings.write_text(f"#!/bin/sh\necho 'prefer-{scheme}'\n")
            fake_settings.chmod(0o755)
            log = root / "theme.log"
            env = {**os.environ, "HOME": directory, "HYPRMAC_ROOT": directory,
                   "HYPRMAC_TEST_THEME_LOG": str(log),
                   "PATH": f"{directory}:{os.environ['PATH']}"}
            subprocess.run([BIN, "check"], env=env, check=True)
            return log.read_text().splitlines() if log.exists() else []

    def test_auto_switches_only_when_current_theme_differs(self):
        from datetime import datetime
        wanted = "light" if 7 <= datetime.now().hour < 19 else "dark"
        other = "dark" if wanted == "light" else "light"
        self.assertEqual(self.run_check("auto", other), [wanted])
        self.assertEqual(self.run_check("auto", wanted), [])
        self.assertEqual(self.run_check("dark", other), [])


if __name__ == "__main__":
    unittest.main()
