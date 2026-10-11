"""MIC-14: com Reduce Motion, o shell não agenda animações elásticas nem de deslocamento.

Evidência Apple (WWDC25 219, Meet Liquid Glass): "Reduced Motion decreases the
intensity of some effects and disables any elastic properties for the material."
Os métodos reais do hyprmac-shell são carregados por AST, sem GTK nem D-Bus.
"""

import ast
from pathlib import Path
from unittest.mock import Mock
import unittest

SOURCE = Path(__file__).resolve().parents[1] / "shell" / "hyprmac-shell"
WANTED = {"Spotlight": {"_stretch_in", "_grow_grid", "_fade_grid"},
          "MediaPanel": {"_cycle_layout"}}


def load(reduced):
    tree = ast.parse(SOURCE.read_text())
    namespace = dict(reduce_motion=lambda: reduced, SPOT_W=640, SPOT_FIELD=52,
                     SPOT_PANEL_H=520, POP_MS=320, MEDIA_LAYOUTS=["compact", "wide"],
                     MEDIA_ANIM_MS=300, ease_in_out=lambda t: t,
                     time=__import__("time"))
    classes = {}
    for node in tree.body:
        if isinstance(node, ast.ClassDef) and node.name in WANTED:
            methods = [n for n in node.body if isinstance(n, ast.FunctionDef) and n.name in WANTED[node.name]]
            klass = ast.ClassDef(name=node.name, bases=[], keywords=[], body=methods, decorator_list=[], type_params=[])
            module = ast.fix_missing_locations(ast.Module(body=[klass], type_ignores=[]))
            exec(compile(module, str(SOURCE), "exec"), namespace)
            classes[node.name] = namespace[node.name]
    return classes


def spotlight(cls):
    spot = cls.__new__(cls)
    spot.panel, spot.field, spot.gscroll, spot.gbox = Mock(), Mock(), Mock(), Mock()
    spot._stretch_tick = spot._grow_tick = None
    return spot


def media(cls):
    panel = cls.__new__(cls)
    panel.layout, panel._anim = "compact", None
    panel.rects = {"cover": (0, 0, 10, 10)}
    panel._layout_rects = lambda name: {"cover": (5, 5, 20, 20)}
    panel._save_layout = panel._apply_rects = Mock()
    panel.fixed, panel.cover = Mock(), Mock()
    return panel


class ReducedMotionShell(unittest.TestCase):
    def test_spotlight_entrance_has_no_stretch(self):
        spot = spotlight(load(True)["Spotlight"])
        spot._stretch_in()
        spot.panel.add_tick_callback.assert_not_called()
        spot.panel.set_size_request.assert_called_once_with(640 + 96, -1)
        spot.field.set_size_request.assert_called_once_with(-1, 52)

    def test_spotlight_grid_does_not_grow_but_still_fades(self):
        spot = spotlight(load(True)["Spotlight"])
        spot._grow_grid()
        spot.gscroll.add_tick_callback.assert_not_called()
        spot.gscroll.set_size_request.assert_called_with(-1, 520 - 52 - 1)
        spot.gbox.add_tick_callback.assert_called_once()     # esmaecer é permitido

    def test_media_layout_jumps_to_final_rects(self):
        panel = media(load(True)["MediaPanel"])
        self.assertTrue(panel._cycle_layout())
        panel.fixed.add_tick_callback.assert_not_called()
        self.assertEqual(panel.rects, {"cover": (5, 5, 20, 20)})
        self.assertEqual(panel.layout, "wide")

    def test_normal_motion_still_animates(self):
        classes = load(False)
        spot = spotlight(classes["Spotlight"])
        spot._stretch_in()
        spot._grow_grid()
        spot.panel.add_tick_callback.assert_called_once()
        spot.gscroll.add_tick_callback.assert_called_once()
        panel = media(classes["MediaPanel"])
        panel._cycle_layout()
        panel.fixed.add_tick_callback.assert_called_once()


if __name__ == "__main__":
    unittest.main()
