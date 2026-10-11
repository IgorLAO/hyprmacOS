"""MIC-04: foco global pelo teclado (HIG ▸ Keyboards).

⌃F4 / ⌃⇧F4 percorrem as janelas de qualquer app (scripts/janela next-any/prev-any);
⌃F3 leva o foco ao Dock: ←/→ percorrem os ícones (pulando separadores), Return ou
Espaço abrem, Esc devolve o foco. Métodos reais do Dock carregados por AST.
"""

import ast
import importlib.machinery
import importlib.util
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load_janela():
    loader = importlib.machinery.SourceFileLoader("janela", str(ROOT / "scripts" / "janela"))
    spec = importlib.util.spec_from_loader("janela", loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


KEYS = SimpleNamespace(KEY_Left=1, KEY_Right=2, KEY_Home=3, KEY_End=4, KEY_Return=5,
                       KEY_KP_Enter=6, KEY_space=7, KEY_Escape=8, KEY_a=9)


def load_dock():
    source = ROOT / "shell" / "hyprmac-shell"
    tree = ast.parse(source.read_text())
    wanted = {"focus_keyboard", "_end_keyboard", "_kb_move", "_key"}
    dock = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "Dock")
    methods = [n for n in dock.body if isinstance(n, ast.FunctionDef) and n.name in wanted]
    klass = ast.ClassDef(name="Dock", bases=[], keywords=[], body=methods,
                         decorator_list=[], type_params=[])
    ls = SimpleNamespace(set_keyboard_mode=Mock(),
                         KeyboardMode=SimpleNamespace(EXCLUSIVE="exclusive", NONE="none"))
    glib = SimpleNamespace(timeout_add=Mock(return_value=1))
    ns = dict(Gdk=KEYS, LS=ls, GLib=glib)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[klass], type_ignores=[])),
                 str(source), "exec"), ns)
    dock = ns["Dock"].__new__(ns["Dock"])
    dock.items = [{"kind": "app", "key": "finder"}, {"kind": "app", "key": "safari"},
                  {"kind": "sep", "key": "sep"}, {"kind": "app", "key": "music"},
                  {"kind": "trash", "key": "trash"}]
    dock.autohide, dock.hover, dock.win, dock.area = False, None, Mock(), Mock()
    dock._reveal, dock._activate, dock._conceal = Mock(), Mock(), Mock()
    return dock, ls, glib


def press(dock, key):
    return dock._key(None, SimpleNamespace(keyval=key))


class WindowCycle(unittest.TestCase):
    def setUp(self):
        self.janela = load_janela()
        self.wins = [{"address": "0xc", "stableId": 3}, {"address": "0xa", "stableId": 1},
                     {"address": "0xb", "stableId": 2}]

    def test_next_and_previous_follow_opening_order_and_wrap(self):
        proxima = self.janela.proxima
        self.assertEqual(proxima(self.wins, {"address": "0xa"}, 1)["address"], "0xb")
        self.assertEqual(proxima(self.wins, {"address": "0xc"}, 1)["address"], "0xa")
        self.assertEqual(proxima(self.wins, {"address": "0xa"}, -1)["address"], "0xc")

    def test_without_active_window_focuses_first_or_last(self):
        proxima = self.janela.proxima
        self.assertEqual(proxima(self.wins, None, 1)["address"], "0xa")
        self.assertEqual(proxima(self.wins, {}, -1)["address"], "0xc")
        self.assertIsNone(proxima([], None, 1))


class DockKeyboard(unittest.TestCase):
    def test_control_f3_highlights_first_icon_and_takes_keyboard(self):
        dock, ls, _glib = load_dock()
        dock.focus_keyboard()
        self.assertEqual(dock.hover, 0)
        ls.set_keyboard_mode.assert_called_with(dock.win, "exclusive")
        dock._reveal.assert_called_once()

    def test_arrows_skip_separator_and_stop_at_ends(self):
        dock, _ls, _glib = load_dock()
        dock.focus_keyboard()
        press(dock, KEYS.KEY_Left)
        self.assertEqual(dock.hover, 0)
        for expected in (1, 3, 4, 4):
            press(dock, KEYS.KEY_Right)
            self.assertEqual(dock.hover, expected)
        press(dock, KEYS.KEY_Home)
        self.assertEqual(dock.hover, 0)
        press(dock, KEYS.KEY_End)
        self.assertEqual(dock.hover, 4)

    def test_return_opens_item_and_releases_keyboard(self):
        dock, ls, _glib = load_dock()
        dock.focus_keyboard()
        press(dock, KEYS.KEY_Right)
        press(dock, KEYS.KEY_Return)
        dock._activate.assert_called_once_with(dock.items[1])
        ls.set_keyboard_mode.assert_called_with(dock.win, "none")
        self.assertIsNone(dock.hover)

    def test_escape_releases_without_opening(self):
        dock, ls, _glib = load_dock()
        dock.focus_keyboard()
        press(dock, KEYS.KEY_Escape)
        dock._activate.assert_not_called()
        ls.set_keyboard_mode.assert_called_with(dock.win, "none")
        self.assertFalse(press(dock, KEYS.KEY_Right))   # fora do modo, a tecla segue adiante

    def test_preview_highlights_without_keyboard(self):
        dock, ls, glib = load_dock()
        dock.focus_keyboard("preview 2")
        self.assertEqual(dock.hover, 3)
        ls.set_keyboard_mode.assert_not_called()
        glib.timeout_add.assert_called_once()


if __name__ == "__main__":
    unittest.main()
