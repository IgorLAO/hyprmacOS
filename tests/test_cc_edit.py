"""CCN-02: editar a Central como no Tahoe (Mac User Guide ▸ Use Control Center).

"Drag items to a different position"; "Drag the item out of Control Center" (remove);
"Control-click an item in Control Center, then choose a different size". Métodos reais
do ControlCenter carregados por AST, sem GTK.
"""

import ast
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
import unittest

SOURCE = Path(__file__).resolve().parents[1] / "shell" / "hyprmac-shell"


def load():
    tree = ast.parse(SOURCE.read_text())
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "ControlCenter")
    body = [n for n in cls.body if isinstance(n, ast.FunctionDef)
            and n.name in ("_edit_press", "_edit_motion", "_edit_release", "_resize")]
    klass = ast.ClassDef(name="ControlCenter", bases=[], keywords=[], body=body,
                         decorator_list=[], type_params=[])
    gdk = SimpleNamespace(ModifierType=SimpleNamespace(CONTROL_MASK=4))
    ns = dict(Gdk=gdk, CC_BLEED=10, math=__import__("math"), add_class=Mock(), set_class=Mock())
    exec(compile(ast.fix_missing_locations(ast.Module(body=[klass], type_ignores=[])), str(SOURCE), "exec"), ns)
    cc = ns["ControlCenter"].__new__(ns["ControlCenter"])
    cc.layout = [("wifi", "medium"), ("bluetooth", "small"), ("sound", "wide")]
    cc.catalog = {"wifi": (None, ("small", "medium")), "bluetooth": (None, ("small", "medium")),
                  "sound": (None, ("wide",))}
    cc._drag, cc.ghosts = None, []
    cc.wrappers = [Mock(), Mock(), Mock()]
    for i, w in enumerate(cc.wrappers):
        w.get_visible.return_value = True
        w.get_allocation.return_value = SimpleNamespace(x=0, y=i * 70, width=300, height=64)
    cc.grid = Mock(get_allocation=lambda: SimpleNamespace(x=0, y=0, width=300, height=220))
    cc._change, cc._remove, cc._edit_menu = Mock(), Mock(), Mock()
    return cc


def ev(button=1, state=0, x=0, y=0):
    return SimpleNamespace(button=button, state=state, x=x, y=y, x_root=x, y_root=y)


def shield_at(x, y):
    return Mock(translate_coordinates=lambda grid, ex, ey: (ex, ey))


class EditControls(unittest.TestCase):
    def drag(self, cc, idx, to):
        w = shield_at(*to)
        cc._edit_press(w, ev(x=10, y=idx * 70 + 10), idx)
        cc._edit_motion(w, ev(x=to[0], y=to[1]))
        cc._edit_release(w, ev(x=to[0], y=to[1]), idx)

    def test_drag_reorders(self):
        cc = load()
        self.drag(cc, 0, (100, 150))                 # sobre o 3º controle
        cc._change.assert_called_once_with([("bluetooth", "small"), ("sound", "wide"), ("wifi", "medium")])

    def test_drag_out_removes(self):
        cc = load()
        self.drag(cc, 1, (500, 100))                 # fora da Central
        cc._remove.assert_called_once_with(1)
        cc._change.assert_not_called()

    def test_plain_click_does_not_resize(self):
        cc = load()
        w = shield_at(10, 10)
        cc._edit_press(w, ev(), 0)
        cc._edit_release(w, ev(), 0)
        cc._change.assert_not_called()

    def test_control_click_and_right_click_open_size_menu(self):
        for e in (ev(button=1, state=4), ev(button=3)):
            cc = load()
            self.assertTrue(cc._edit_press(shield_at(0, 0), e, 0))
            cc._edit_menu.assert_called_once()
            self.assertIsNone(cc._drag)

    def test_resize_keeps_position(self):
        cc = load()
        cc._resize(0, "small")
        cc._change.assert_called_once_with([("wifi", "small"), ("bluetooth", "small"), ("sound", "wide")])


if __name__ == "__main__":
    unittest.main()
