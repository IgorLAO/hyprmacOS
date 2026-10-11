"""CCN-02: editar a Central como no Tahoe (Mac User Guide ▸ Use Control Center) e pedidos
do usuário: ao arrastar sobre um controle os outros se realocam já durante o arrasto, e uma
alça estica/encolhe o controle nos tamanhos que ele aceita. Código real por AST, sem GTK.
"""

import ast
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
import unittest

SOURCE = Path(__file__).resolve().parents[1] / "shell" / "hyprmac-shell"
TREE = ast.parse(SOURCE.read_text())


def module_ns():
    nodes = [n for n in TREE.body if (isinstance(n, ast.FunctionDef) and n.name in
                                     ("cc_pack", "cc_reorder", "cc_fit_size"))
             or (isinstance(n, ast.Assign) and any(getattr(t, "id", "") == "SPANS" for t in n.targets))]
    ns = {}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(SOURCE), "exec"), ns)
    return ns


def load():
    ns = module_ns()
    cls = next(n for n in TREE.body if isinstance(n, ast.ClassDef) and n.name == "ControlCenter")
    body = [n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name in
            ("_edit_press", "_edit_motion", "_edit_release", "_resize", "_resize_press",
             "_resize_motion", "_resize_release")]
    klass = ast.ClassDef(name="ControlCenter", bases=[], keywords=[], body=body,
                         decorator_list=[], type_params=[])
    ns.update(Gdk=SimpleNamespace(ModifierType=SimpleNamespace(CONTROL_MASK=4)), CC_BLEED=4,
              C=66, GAP=12, math=__import__("math"), add_class=Mock(), set_class=Mock())
    exec(compile(ast.fix_missing_locations(ast.Module(body=[klass], type_ignores=[])), str(SOURCE), "exec"), ns)
    cc = ns["ControlCenter"].__new__(ns["ControlCenter"])
    # wifi M (cols 0-1, row 0) · bluetooth S (col 2) · dnd S (col 3) · sound W (row 1)
    cc.layout = [("wifi", "medium"), ("bluetooth", "small"), ("dnd", "small"), ("sound", "wide")]
    cc.catalog = {"wifi": (None, ("small", "medium")), "bluetooth": (None, ("small", "medium")),
                  "dnd": (None, ("small", "medium")), "sound": (None, ("wide",))}
    cc._drag, cc.ghosts, cc.wrappers = None, [], [Mock() for _ in cc.layout]
    cc.grid = Mock(get_allocation=lambda: SimpleNamespace(x=0, y=0, width=312, height=160))
    cc._change, cc._remove, cc._edit_menu, cc._apply_preview = Mock(), Mock(), Mock(), Mock()
    return cc, ns


def ev(button=1, state=0, x=0, y=0):
    return SimpleNamespace(button=button, state=state, x=x, y=y, x_root=x, y_root=y)


SHIELD = Mock(translate_coordinates=lambda grid, ex, ey: (ex, ey))
P = 78   # passo de uma célula (C + GAP)


class Packing(unittest.TestCase):
    def test_pack_and_reorder(self):
        ns = module_ns()
        sizes = ["medium", "small", "small", "wide"]
        self.assertEqual(ns["cc_pack"](sizes), [(0, 0, 2, 1), (2, 0, 1, 1), (3, 0, 1, 1), (0, 1, 4, 1)])
        order = [0, 1, 2, 3]
        self.assertEqual(ns["cc_reorder"](order, 2, (2, 0), sizes), [0, 2, 1, 3])   # toma o lugar
        self.assertEqual(ns["cc_reorder"](order, 2, (3, 0), sizes), order)          # sobre si mesmo
        self.assertEqual(ns["cc_reorder"](order, 1, (0, 5), sizes), [0, 2, 3, 1])   # vazio → fim

    def test_reorder_is_stable_under_pointer(self):
        ns = module_ns()
        sizes = ["medium", "small", "small", "wide"]
        once = ns["cc_reorder"]([0, 1, 2, 3], 2, (2, 0), sizes)
        self.assertEqual(ns["cc_reorder"](once, 2, (2, 0), sizes), once)       # não fica alternando

    def test_fit_size(self):
        fit = module_ns()["cc_fit_size"]
        self.assertEqual(fit(("small", "medium"), "small", (2, 1)), "medium")
        self.assertEqual(fit(("small", "medium"), "medium", (1, 1)), "small")
        self.assertEqual(fit(("small", "medium", "large"), "medium", (2, 2)), "large")
        self.assertEqual(fit(("small", "medium"), "medium", (4, 2)), "medium")   # não passa do maior


class EditControls(unittest.TestCase):
    def drag(self, cc, idx, frm, to):
        cc._edit_press(SHIELD, ev(x=frm[0], y=frm[1]), idx)
        for p in to:
            cc._edit_motion(SHIELD, ev(x=p[0], y=p[1]))
        cc._edit_release(SHIELD, ev(x=to[-1][0], y=to[-1][1]), idx)

    def test_others_reflow_during_drag_and_commit_on_release(self):
        cc, _ = load()
        self.drag(cc, 2, (3 * P + 10, 10), [(2 * P + 20, 20)])     # dnd sobre o bluetooth
        cc._apply_preview.assert_called_with([0, 2, 1, 3], ["medium", "small", "small", "wide"])
        cc._change.assert_called_once_with([("wifi", "medium"), ("dnd", "small"),
                                            ("bluetooth", "small"), ("sound", "wide")])

    def test_drag_out_removes(self):
        cc, _ = load()
        self.drag(cc, 1, (2 * P + 10, 10), [(600, 100)])
        cc._remove.assert_called_once_with(1)
        cc._change.assert_not_called()

    def test_plain_click_does_not_resize(self):
        cc, _ = load()
        cc._edit_press(SHIELD, ev(x=10, y=10), 0)
        cc._edit_release(SHIELD, ev(x=10, y=10), 0)
        cc._change.assert_not_called()

    def test_control_click_and_right_click_open_size_menu(self):
        for e in (ev(button=1, state=4), ev(button=3)):
            cc, _ = load()
            self.assertTrue(cc._edit_press(SHIELD, e, 0))
            cc._edit_menu.assert_called_once()

    def test_handle_stretches_and_shrinks(self):
        cc, _ = load()
        cc._resize_press(None, ev(x=100, y=100), 1)                # bluetooth small → puxa 1 célula
        cc._resize_motion(None, ev(x=100 + P, y=100))
        cc._apply_preview.assert_called_with([0, 1, 2, 3], ["medium", "medium", "small", "wide"])
        cc._resize_release(None, ev())
        cc._change.assert_called_once_with([("wifi", "medium"), ("bluetooth", "medium"),
                                            ("dnd", "small"), ("sound", "wide")])
        cc, _ = load()
        cc._resize_press(None, ev(x=100, y=100), 0)                # wifi medium → empurra para dentro
        cc._resize_motion(None, ev(x=100 - P, y=100))
        cc._resize_release(None, ev())
        cc._change.assert_called_once_with([("wifi", "small"), ("bluetooth", "small"),
                                            ("dnd", "small"), ("sound", "wide")])

    def test_handle_without_change_does_nothing(self):
        cc, _ = load()
        cc._resize_press(None, ev(x=100, y=100), 1)
        cc._resize_motion(None, ev(x=110, y=104))
        cc._resize_release(None, ev())
        cc._change.assert_not_called()



class LivePreviewInGtk(unittest.TestCase):
    """_apply_preview move os widgets de verdade num Gtk.Grid, sem reconstruir."""

    def test_widgets_and_ghosts_move(self):
        import gi
        gi.require_version("Gtk", "3.0")
        from gi.repository import Gtk
        ns = module_ns()
        cls = next(n for n in TREE.body if isinstance(n, ast.ClassDef) and n.name == "ControlCenter")
        fn = [n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == "_apply_preview"]
        klass = ast.ClassDef(name="CC", bases=[], keywords=[], body=fn, decorator_list=[], type_params=[])
        exec(compile(ast.fix_missing_locations(ast.Module(body=[klass], type_ignores=[])), str(SOURCE), "exec"), ns)
        cc = ns["CC"]()
        cc.editing, cc.grid = True, Gtk.Grid()
        sizes = ["medium", "small", "small", "wide"]
        cc.wrappers = [Gtk.Label(label=str(i)) for i in range(4)]
        for w, (c, r, cw, ch) in zip(cc.wrappers, ns["cc_pack"](sizes)):
            cc.grid.attach(w, c, r, cw, ch)
        cc.ghosts = [Gtk.Label() for _ in range(4)]
        for k, g in enumerate(cc.ghosts):
            cc.grid.attach(g, k, 2, 1, 1)
        cc._apply_preview([0, 2, 1, 3], sizes)
        pos = lambda w: tuple(cc.grid.child_get_property(w, p) for p in ("left-attach", "top-attach"))
        self.assertEqual(pos(cc.wrappers[2]), (2, 0))
        self.assertEqual(pos(cc.wrappers[1]), (3, 0))
        self.assertEqual({pos(g) for g in cc.ghosts}, {(0, 2), (1, 2), (2, 2), (3, 2)})
        cc._apply_preview([0, 1, 2, 3], ["medium", "medium", "small", "wide"])   # alça esticou o 1
        self.assertEqual(cc.grid.child_get_property(cc.wrappers[1], "width"), 2)
        self.assertEqual(pos(cc.wrappers[2]), (0, 1))                           # o 2 desceu
        self.assertEqual(pos(cc.wrappers[3]), (0, 2))


if __name__ == "__main__":
    unittest.main()
