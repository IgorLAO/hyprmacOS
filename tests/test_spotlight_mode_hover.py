"""MIC-09: o hover nos botões de modo do Spotlight antecipa o nome e o atalho no campo.

Referência Tahoe 26: referencias/telas/spotlight-controles-2…6 — ponteiro sobre
Files mostra "Files ⌘2", sobre Actions "Actions ⌘3"; a lupa não muda e o modo
só troca no clique. Métodos reais carregados por AST, sem GTK.
"""

import ast
from pathlib import Path
import sys
from unittest.mock import Mock
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "shell"))
from spotlight_search import SPOT_MODES  # noqa: E402


def method(path, cls_name, name, ns):
    tree = ast.parse(path.read_text())
    cls = next(n for n in ast.walk(tree) if isinstance(n, ast.ClassDef) and n.name == cls_name)
    fn = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == name)
    klass = ast.ClassDef(name=cls_name, bases=[], keywords=[], body=[fn], decorator_list=[], type_params=[])
    exec(compile(ast.fix_missing_locations(ast.Module(body=[klass], type_ignores=[])), str(path), "exec"), ns)
    return getattr(ns[cls_name], name)


class FakeEntry:
    def __init__(self, text=""):
        self.text, self.placeholder = text, None

    def get_text(self):
        return self.text

    def set_placeholder_text(self, value):
        self.placeholder = value


class FakeLabel:
    text = ""

    def set_text(self, value):
        self.text = value


def spotlight(mode="all", text="", scope=None):
    spot = Mock()
    spot.mode, spot.scope = mode, scope
    spot.entry, spot.key_num = FakeEntry(text), FakeLabel()
    return spot


HOVER = method(ROOT / "shell" / "spotlight_view.py", "Spotlight", "_hover_mode", {"SPOT_MODES": SPOT_MODES})


class ModeHover(unittest.TestCase):
    def test_hover_shows_mode_name_and_shortcut(self):
        spot = spotlight()
        for mode, name, num in (("files", "Files", "2"), ("actions", "Actions", "3"),
                                ("clipboard", "Clipboard", "4"), ("apps", "Applications", "1")):
            HOVER(spot, mode)
            self.assertEqual((spot.entry.placeholder, spot.key_num.text), (name, num))
            spot.keys.set_visible.assert_called_with(True)
        spot.glass_icon.set_text.assert_not_called()       # a lupa não muda no hover
        self.assertEqual(spot.mode, "all")                  # o modo só troca no clique

    def test_leaving_restores_current_mode(self):
        spot = spotlight()
        HOVER(spot, "files")
        HOVER(spot, None)
        self.assertEqual(spot.entry.placeholder, "Spotlight Search")
        spot.keys.set_visible.assert_called_with(False)
        spot = spotlight(mode="files")
        HOVER(spot, "actions")
        HOVER(spot, None)
        self.assertEqual((spot.entry.placeholder, spot.key_num.text), ("Files", "2"))

    def test_typed_text_or_filter_is_left_alone(self):
        for spot in (spotlight(text="saf"), spotlight(scope={"key": "folders"})):
            HOVER(spot, "files")
            self.assertIsNone(spot.entry.placeholder)
            spot.keys.set_visible.assert_not_called()

    def test_controls_report_hover_changes(self):
        set_hover = method(ROOT / "shell" / "spotlight_controls.py", "SpotControls", "_set_hover", {})
        ctl = Mock()
        ctl.hover, ctl.MODES = -1, ("apps", "files", "actions", "clipboard")
        set_hover(ctl, 1)
        ctl.spot._hover_mode.assert_called_with("files")
        set_hover(ctl, 1)                                   # mesmo botão: não repete
        self.assertEqual(ctl.spot._hover_mode.call_count, 1)
        set_hover(ctl, -1)
        ctl.spot._hover_mode.assert_called_with(None)



class NarrowScreen(unittest.TestCase):
    """MIC-13: em tela estreita (escala 2 num monitor 1080p = 960 pt) os 4 botões cabem."""

    def setUp(self):
        tree = ast.parse((ROOT / "shell" / "hyprmac-shell").read_text())
        fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "spot_shift")
        ns = {}
        exec(compile(ast.Module(body=[fn], type_ignores=[]), "spot_shift", "exec"), ns)
        self.shift = ns["spot_shift"]

    def test_wide_screen_keeps_capsule_centered(self):
        self.assertEqual(self.shift(1920, 640, 26, 282), 0)
        self.assertEqual(self.shift(1440, 640, 26, 282), 0)

    def test_narrow_screen_moves_just_enough(self):
        for width in (960, 1024, 1100):
            s = self.shift(width, 640, 26, 282)
            right = width / 2 - s + 640 / 2 - 26 + 282
            self.assertLessEqual(right, width - 8 + 0.5)
            self.assertGreater(s, 0)


if __name__ == "__main__":
    unittest.main()
