"""Edição no Gtk.Entry real; não altera atalhos de aplicações externas."""
import ast
import sys
from pathlib import Path
from types import SimpleNamespace
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'shell'))
from cocoa_entry import CocoaEntryKeys, Gtk, Gdk, is_modified_arrow


class CocoaEntryTests(unittest.TestCase):
    def setUp(self):
        Gtk.init([])
        self.entry = Gtk.Entry()
        self.keys = CocoaEntryKeys(self.entry)

    def press(self, key, state=Gdk.ModifierType.CONTROL_MASK):
        return self.keys.on_key(self.entry, SimpleNamespace(keyval=key, state=state))

    def test_navigation_kill_yank_and_selection(self):
        self.entry.set_text('one two')
        self.entry.set_position(4)
        self.assertTrue(self.press(Gdk.KEY_k))
        self.assertEqual(self.entry.get_text(), 'one ')
        self.entry.select_region(0, 3)
        self.press(Gdk.KEY_y)
        self.assertEqual(self.entry.get_text(), 'two ')
        self.press(Gdk.KEY_a)
        self.assertEqual(self.entry.get_position(), 0)
        self.press(Gdk.KEY_e)
        self.assertEqual(self.entry.get_position(), 4)
        self.press(Gdk.KEY_a, Gdk.ModifierType.SUPER_MASK)
        self.assertEqual(self.entry.get_selection_bounds(), (0, 4))

    def test_transpose_clusters_and_delete(self):
        for text, pos, expected in [('abcd', 2, 'acbd'), ('abcd', 4, 'abdc'),
                                     ('a\u0301b', 3, 'ba\u0301')]:
            self.entry.set_text(text)
            self.entry.set_position(pos)
            self.press(Gdk.KEY_t)
            self.assertEqual(self.entry.get_text(), expected)
        self.entry.set_text('one two')
        self.entry.set_position(-1)
        self.press(Gdk.KEY_BackSpace, Gdk.ModifierType.MOD1_MASK)
        self.assertEqual(self.entry.get_text(), 'one ')
        self.press(Gdk.KEY_BackSpace, Gdk.ModifierType.SUPER_MASK)
        self.assertEqual(self.entry.get_text(), '')

    def test_unrelated_combinations_propagate(self):
        self.assertFalse(self.press(Gdk.KEY_k, Gdk.ModifierType.CONTROL_MASK |
                                   Gdk.ModifierType.SHIFT_MASK))
        self.assertFalse(self.press(Gdk.KEY_u))
        self.assertFalse(self.press(Gdk.KEY_k, Gdk.ModifierType.SUPER_MASK))

    def test_word_selection_reverses_without_losing_anchor(self):
        for kind in (Gtk.Entry, Gtk.SearchEntry):
            with self.subTest(widget=kind.__name__):
                self.entry = kind()
                self.keys = CocoaEntryKeys(self.entry)
                self.entry.set_text('um café final')
                self.entry.set_position(0)
                option = Gdk.ModifierType.MOD1_MASK
                self.press(Gdk.KEY_Right, option)
                self.assertEqual(self.entry.get_position(), 2)
                self.press(Gdk.KEY_Right, option | Gdk.ModifierType.SHIFT_MASK)
                self.assertEqual(self.entry.get_selection_bounds(), (2, 7))
                self.press(Gdk.KEY_Left, option | Gdk.ModifierType.SHIFT_MASK)
                self.assertEqual(self.entry.get_selection_bounds(), (2, 3))
                self.press(Gdk.KEY_Left, option | Gdk.ModifierType.SHIFT_MASK)
                self.assertEqual(self.entry.get_selection_bounds(), (0, 2))
                self.press(Gdk.KEY_Right, option | Gdk.ModifierType.SHIFT_MASK)
                self.assertEqual(self.entry.get_selection_bounds(), ())
                self.assertEqual(self.entry.get_position(), 2)

    def test_line_document_and_paragraph_selection(self):
        for mask, left, right in (
                (Gdk.ModifierType.CONTROL_MASK, Gdk.KEY_Left, Gdk.KEY_Right),
                (Gdk.ModifierType.SUPER_MASK, Gdk.KEY_Left, Gdk.KEY_Right),
                (Gdk.ModifierType.SUPER_MASK, Gdk.KEY_Up, Gdk.KEY_Down),
                (Gdk.ModifierType.CONTROL_MASK, Gdk.KEY_A, Gdk.KEY_E)):
            with self.subTest(mask=mask, left=left):
                self.entry.set_text('um café final')
                self.entry.set_position(3)
                self.press(left, mask | Gdk.ModifierType.SHIFT_MASK)
                self.assertEqual(self.entry.get_selection_bounds(), (0, 3))
                self.press(right, mask | Gdk.ModifierType.SHIFT_MASK)
                self.assertEqual(self.entry.get_selection_bounds(), (3, 13))
                self.press(right, mask)
                self.assertEqual(self.entry.get_position(), 13)
                self.assertEqual(self.entry.get_selection_bounds(), ())

    def test_read_only_and_mixed_modifiers_do_not_edit(self):
        self.entry.set_text('unchanged')
        self.entry.set_position(4)
        self.entry.set_editable(False)
        self.assertFalse(self.press(Gdk.KEY_k))
        self.assertFalse(self.press(Gdk.KEY_BackSpace, Gdk.ModifierType.SUPER_MASK))
        self.assertEqual(self.entry.get_text(), 'unchanged')
        self.entry.set_editable(True)
        self.assertFalse(self.press(Gdk.KEY_Left, Gdk.ModifierType.CONTROL_MASK |
                                   Gdk.ModifierType.MOD1_MASK))
        self.assertEqual(self.entry.get_position(), 4)

    def test_option_paragraph_and_option_control_word_navigation(self):
        for kind in (Gtk.Entry, Gtk.SearchEntry):
            with self.subTest(widget=kind.__name__):
                self.entry = kind()
                self.keys = CocoaEntryKeys(self.entry)
                self.entry.set_text('one two three')
                self.entry.set_position(4)
                option = Gdk.ModifierType.MOD1_MASK
                word = option | Gdk.ModifierType.CONTROL_MASK
                self.assertTrue(self.press(Gdk.KEY_f, word | Gdk.ModifierType.SHIFT_MASK))
                self.assertEqual(self.entry.get_selection_bounds(), (4, 7))
                self.assertTrue(self.press(Gdk.KEY_b, word | Gdk.ModifierType.SHIFT_MASK))
                self.assertEqual(self.entry.get_selection_bounds(), ())
                self.assertEqual(self.entry.get_position(), 4)
                self.assertTrue(self.press(Gdk.KEY_Up, option | Gdk.ModifierType.SHIFT_MASK))
                self.assertEqual(self.entry.get_selection_bounds(), (0, 4))
                self.assertTrue(self.press(Gdk.KEY_Down, option | Gdk.ModifierType.SHIFT_MASK))
                self.assertEqual(self.entry.get_selection_bounds(), (4, 13))
                self.assertFalse(self.press(Gdk.KEY_f, word | Gdk.ModifierType.SUPER_MASK))


class ResultNavigationTests(unittest.TestCase):
    """Executa handlers reais num Gtk.Window, incluindo propagação ao campo."""

    @classmethod
    def setUpClass(cls):
        shell_dir = Path(__file__).resolve().parents[1] / 'shell'
        cls.handlers = {}
        for name, path in (('Spotlight', shell_dir / 'spotlight_view.py'),
                           ('ClipboardPanel', shell_dir / 'hyprmac-shell')):
            tree = ast.parse(path.read_text())
            for node in ast.walk(tree):
                if not isinstance(node, ast.ClassDef) or node.name != name:
                    continue
                method = next(n for n in node.body if isinstance(n, ast.FunctionDef)
                              and n.name == '_on_key')
                namespace = {'Gdk': Gdk, 'is_modified_arrow': is_modified_arrow}
                exec(compile(ast.Module(body=[method], type_ignores=[]), str(path), 'exec'), namespace)
                cls.handlers[node.name] = namespace['_on_key']

    def test_modified_arrows_reach_entry_plain_arrows_still_navigate(self):
        for name, handler in self.handlers.items():
            with self.subTest(panel=name):
                entry = Gtk.SearchEntry() if name == 'ClipboardPanel' else Gtk.Entry()
                CocoaEntryKeys(entry)
                window = Gtk.Window()
                window.add(entry)
                moves = []
                rows = [Gtk.ListBoxRow(), Gtk.ListBoxRow()]
                result_list = Gtk.ListBox()
                for row in rows:
                    result_list.add(row)
                model = SimpleNamespace(entry=entry, search=entry, scope=None,
                                        _files_view=lambda: True,
                                        _move_cell=lambda *args: moves.append(args),
                                        _filter=lambda row: True,
                                        list=SimpleNamespace(get_children=lambda: rows,
                                            get_selected_row=lambda: rows[0],
                                            select_row=lambda row: moves.append(rows.index(row))))
                window.connect('key-press-event', lambda w, ev: handler(model, w, ev))
                try:
                    window.show_all()
                    entry.grab_focus()
                    while Gtk.events_pending():
                        Gtk.main_iteration_do(False)
                    entry.set_text('um café final')
                    entry.set_position(3)
                    event = Gdk.Event.new(Gdk.EventType.KEY_PRESS)
                    event.window = window.get_window()
                    event.send_event = True
                    event.set_device(Gdk.Display.get_default().get_default_seat().get_keyboard())
                    event.keyval = Gdk.KEY_Right
                    event.state = Gdk.ModifierType.MOD1_MASK | Gdk.ModifierType.SHIFT_MASK
                    self.assertTrue(window.emit('key-press-event', event))
                    self.assertEqual(entry.get_selection_bounds(), (3, 7))
                    event.keyval = Gdk.KEY_Up
                    event.state = Gdk.ModifierType.SUPER_MASK
                    self.assertTrue(window.emit('key-press-event', event))
                    self.assertEqual(entry.get_position(), 0)
                    self.assertEqual(moves, [])
                    event.keyval = Gdk.KEY_Down
                    event.state = Gdk.ModifierType(0)
                    self.assertTrue(window.emit('key-press-event', event))
                    self.assertEqual(len(moves), 1)
                finally:
                    window.destroy()

if __name__ == '__main__':
    unittest.main()
