"""SPT-04: histórico da área de transferência conforme o Mac User Guide (Tahoe 26).

"Click the copy icon to the right of the item, or select the item and press
Command-C"; "click the More button to the right of the search field, then choose
Clear History". Métodos reais do ClipboardPanel carregados por AST, sem GTK.
"""

import ast
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
import unittest

SOURCE = Path(__file__).resolve().parents[1] / "shell" / "hyprmac-shell"
TEXT = SOURCE.read_text()


def load(names):
    tree = ast.parse(TEXT)
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "ClipboardPanel")
    body = [n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name in names]
    klass = ast.ClassDef(name="ClipboardPanel", bases=[], keywords=[], body=body,
                         decorator_list=[], type_params=[])
    keys = SimpleNamespace(KEY_Escape=1, KEY_Down=2, KEY_Up=3, KEY_c=99, KEY_C=67,
                           ModifierType=SimpleNamespace(CONTROL_MASK=4))
    ns = dict(Gdk=keys, in_thread=lambda fn, *a: fn(*a), is_modified_arrow=lambda ev: False)
    exec(compile(ast.fix_missing_locations(ast.Module(body=[klass], type_ignores=[])), str(SOURCE), "exec"), ns)
    return ns["ClipboardPanel"]


class ClipboardHistory(unittest.TestCase):
    def panel(self, selection=()):
        cls = load({"_on_key", "_selected_row"})
        p = cls.__new__(cls)
        row = SimpleNamespace(item={"kind": "text", "text": "olá"})
        p.list = Mock(get_selected_row=lambda: row, get_children=lambda: [row])
        p._filter = lambda r: True
        p.search = Mock(get_selection_bounds=lambda: selection)
        p._to_clipboard, p.hide = Mock(), Mock()
        return p, row

    def test_control_c_copies_selected_item(self):
        p, row = self.panel()
        self.assertTrue(p._on_key(None, SimpleNamespace(keyval=99, state=4)))
        p._to_clipboard.assert_called_once_with(row.item)
        p.hide.assert_not_called()                     # copiar não fecha nem cola

    def test_control_c_with_text_selected_in_field_copies_text(self):
        p, _row = self.panel(selection=(0, 3))
        self.assertFalse(p._on_key(None, SimpleNamespace(keyval=99, state=4)))
        p._to_clipboard.assert_not_called()

    def test_ui_is_english_with_more_menu_and_copy_icon(self):
        self.assertIn('Gtk.MenuItem(label="Clear History")', TEXT)
        self.assertIn('copy.set_tooltip_text("Copy")', TEXT)
        clip = TEXT[TEXT.index("def clip_ago"):TEXT.index("class ClipboardPanel")]
        self.assertNotIn("há ", clip)
        self.assertNotIn("agora", clip)


if __name__ == "__main__":
    unittest.main()
