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
    source = ROOT / "shell" / "dock_widget.py"
    tree = ast.parse(source.read_text())
    wanted = {"focus_keyboard", "_end_keyboard", "_kb_move", "_key"}
    dock = next(n for n in ast.walk(tree) if isinstance(n, ast.ClassDef) and n.name == "Dock")
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




class CommandTab(unittest.TestCase):
    """⌘Tab = Super+Tab: o seletor lembra o modificador e desvia ⌘Q/⌘H pelo submap."""

    def load(self):
        source = ROOT / "shell" / "session_overlays.py"
        tree = ast.parse(source.read_text())
        cls = next(n for n in ast.walk(tree) if isinstance(n, ast.ClassDef) and n.name == "AppSwitcher")
        methods = [n for n in cls.body if isinstance(n, ast.FunctionDef)
                   and n.name in ("next", "prev", "_step", "close", "_key_release", "_check_alt")]
        klass = ast.ClassDef(name="AppSwitcher", bases=[], keywords=[], body=methods,
                             decorator_list=[], type_params=[])
        self.state = 0
        keymap = SimpleNamespace(get_modifier_state=lambda: self.state)
        gdk = SimpleNamespace(KEY_Super_L=1, KEY_Super_R=2, KEY_Alt_L=3, KEY_Alt_R=4, KEY_Meta_L=5,
                              KEY_Meta_R=6,
                              ModifierType=SimpleNamespace(SUPER_MASK=64, MOD4_MASK=128, MOD1_MASK=8),
                              Keymap=SimpleNamespace(get_for_display=lambda d: keymap),
                              Display=SimpleNamespace(get_default=lambda: None))
        dispatch = Mock()
        ns = dict(Gdk=gdk, dispatch=dispatch)
        exec(compile(ast.fix_missing_locations(ast.Module(body=[klass], type_ignores=[])),
                     str(source), "exec"), ns)
        sw = ns["AppSwitcher"].__new__(ns["AppSwitcher"])
        sw.open, sw.items, sw.win = False, [1, 2, 3], Mock()
        sw._collect, sw._build, sw._highlight = (lambda: True), Mock(), Mock()
        sw._show = lambda: setattr(sw, "open", True)
        sw.activate = Mock(side_effect=sw.close)
        return sw, dispatch, gdk

    def test_super_tab_enters_and_leaves_switcher_submap(self):
        sw, dispatch, gdk = self.load()
        sw.next("super")
        dispatch.assert_called_with('hl.dsp.submap("switcher")')
        sw._key_release(None, SimpleNamespace(keyval=gdk.KEY_Alt_L))   # Alt não conta
        sw.activate.assert_not_called()
        sw._key_release(None, SimpleNamespace(keyval=gdk.KEY_Super_L))
        sw.activate.assert_called_once()
        dispatch.assert_called_with('hl.dsp.submap("reset")')

    def test_alt_tab_keeps_working_without_submap(self):
        sw, dispatch, gdk = self.load()
        sw.next()
        dispatch.assert_not_called()
        sw._key_release(None, SimpleNamespace(keyval=gdk.KEY_Super_L))
        sw.activate.assert_not_called()
        sw._key_release(None, SimpleNamespace(keyval=gdk.KEY_Alt_L))
        sw.activate.assert_called_once()
        dispatch.assert_not_called()

    def test_quick_tap_checks_the_right_modifier(self):
        sw, _dispatch, _gdk = self.load()
        sw.next("super")
        self.state = 64                       # Super ainda segurado: continua aberto
        sw._check_alt()
        sw.activate.assert_not_called()
        self.state = 8                        # só Alt: Super foi solto, troca direto
        sw._check_alt()
        sw.activate.assert_called_once()



class MacShortcuts(unittest.TestCase):
    """HIG ▸ Keyboards com ⌘ = Super: ⇧⌘3/⇧⌘4/⇧⌘5 capturam e ⌘Tab troca de app, sem
    binds duplicados do hyprland.lua disparando junto."""

    lua = (ROOT / "hypr" / "hyprmac.lua").read_text()

    def test_capture_keys_replace_workspace_moves(self):
        for key in ("3", "4", "5"):
            unbind = self.lua.index(f'hl.unbind("SUPER + SHIFT + {key}")')
            bind = self.lua.index(f'hl.bind("SUPER + SHIFT + {key}"')
            self.assertLess(unbind, bind)
        self.assertIn('"SUPER + SHIFT + 3",        hl.dsp.exec_cmd(shot .. " screen")', self.lua)
        self.assertIn('"SUPER + SHIFT + 4",        hl.dsp.exec_cmd(shot .. " region")', self.lua)
        self.assertIn('HYPRMAC_SHOT_CLIPBOARD=1 " .. shot .. " region', self.lua)

    def test_command_tab_and_submap(self):
        self.assertIn('hl.bind("SUPER + Tab"', self.lua)
        self.assertIn('hl.define_submap("switcher"', self.lua)


if __name__ == "__main__":
    unittest.main()
