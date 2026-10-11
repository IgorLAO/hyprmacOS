"""MIC-11: aparência Auto troca claro/escuro sozinha, só com o Mac ocioso (scripts/aparencia).

Mac User Guide (Tahoe 26): Auto segue a agenda do Night Shift e "won't switch the
appearance until your Mac has been idle for at least a minute" — o check roda pelo
vigia de inatividade de 60 s.
"""

import importlib.machinery
import importlib.util
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load():
    loader = importlib.machinery.SourceFileLoader("aparencia", str(ROOT / "scripts" / "aparencia"))
    spec = importlib.util.spec_from_loader("aparencia", loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


class AutoAppearance(unittest.TestCase):
    def setUp(self):
        self.ap = load()

    def test_auto_follows_the_day(self):
        self.assertEqual(self.ap.wanted("auto", 6), "dark")
        self.assertEqual(self.ap.wanted("auto", 7), "light")
        self.assertEqual(self.ap.wanted("auto", 18), "light")
        self.assertEqual(self.ap.wanted("auto", 19), "dark")

    def test_fixed_modes_are_left_alone(self):
        self.assertIsNone(self.ap.wanted("light", 23))
        self.assertIsNone(self.ap.wanted("dark", 12))

    def run_check(self, mode, hour, scheme):
        calls = []

        def fake_run(cmd, **kw):
            calls.append(cmd)
            return SimpleNamespace(stdout=f"'{scheme}'\n")
        with patch.object(self.ap, "mode", return_value=mode), \
             patch.object(self.ap.time, "localtime", return_value=SimpleNamespace(tm_hour=hour)), \
             patch.object(self.ap.subprocess, "run", side_effect=fake_run):
            self.ap.check()
        return [c for c in calls if c[0].endswith("theme")]

    def test_check_switches_only_when_needed(self):
        self.assertEqual(self.run_check("auto", 20, "prefer-light"), [[str(ROOT / "scripts" / "theme"), "dark"]])
        self.assertEqual(self.run_check("auto", 20, "prefer-dark"), [])
        self.assertEqual(self.run_check("dark", 10, "prefer-dark"), [])

    def test_watcher_name_escapes_ocioso_pkill(self):
        self.assertNotEqual(self.ap.WATCHER[:15], "hyprmac-ocioso")
        self.assertIn('"60"', (ROOT / "scripts" / "aparencia").read_text())


if __name__ == "__main__":
    unittest.main()
