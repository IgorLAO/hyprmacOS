"""Spaces e App Exposé: lógica real do overview, sem importar GTK ou criar janelas."""
import ast
import math
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest.mock import Mock


SOURCE = Path(__file__).resolve().parents[1] / "shell/hyprmac-overview"


def load_logic():
    tree = ast.parse(SOURCE.read_text())
    functions = {"desktop_name", "spaces_layout", "space_hit", "inside", "lerp",
                 "lerp_rect", "ease_out", "ease_in_out", "layout_windows"}
    classes = {"Win", "Desk", "Screen", "Overview"}
    nodes = [n for n in tree.body if
             (isinstance(n, ast.Assign) and isinstance(n.value, ast.Constant)) or
             (isinstance(n, ast.FunctionDef) and n.name in functions) or
             (isinstance(n, ast.ClassDef) and n.name in classes)]
    keys = {name: name for name in ("Escape", "Up", "Down", "Left", "Right",
                                   "Return", "KP_Enter", "space", "Tab")}
    ns = {"math": math, "time": SimpleNamespace(monotonic=Mock(return_value=10.0)),
          "os": SimpleNamespace(environ={}), "dispatch": Mock(), "hypr_json": Mock(),
          "scaled_surface": Mock(),
          "Gdk": SimpleNamespace(**{"KEY_" + k: v for k, v in keys.items()},
                                 ModifierType=SimpleNamespace(CONTROL_MASK=1))}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(SOURCE), "exec"), ns)
    return ns


def monitor(name="DP-1", active=1, focused=True, scale=1):
    return {"name": name, "width": 1920, "height": 1080, "scale": scale,
            "x": 0, "y": 0, "focused": focused, "activeWorkspace": {"id": active}}


def client(address, cls="Editor", wid=1, name=None, **extra):
    return {"address": address, "class": cls, "mapped": True,
            "at": [100, 100], "size": [800, 600],
            "workspace": {"id": wid, "name": name or str(wid)}, **extra}


def screen(ns, app=None, animations=False, clients=None, mon=None, workspaces=None):
    obj = ns["Screen"].__new__(ns["Screen"])
    obj.ov = SimpleNamespace(app_cls=app, extras={}, state="open", mode="fly",
                             iface=SimpleNamespace(get_boolean=Mock(return_value=animations)),
                             apps=SimpleNamespace(lookup=lambda cls: (cls, None)),
                             wall=SimpleNamespace(get=lambda *args: (None, None, None)),
                             kick=Mock(), close=Mock())
    obj.area = Mock()
    obj.prepare(mon or monitor(), clients or [], workspaces or [], 0)
    return obj


def event(x=0, y=0, button=1, keyval=None):
    return SimpleNamespace(x=x, y=y, button=button, keyval=keyval, state=0)


class SpacesLayoutTests(unittest.TestCase):
    def setUp(self):
        self.ns = load_logic()

    def test_names_use_tahoe_english_format(self):
        self.assertEqual([self.ns["desktop_name"](n) for n in (1, 2, 12)],
                         ["Desktop 1", "Desktop 2", "Desktop 12"])

    def test_layout_fits_many_spaces_and_reserves_plus(self):
        for width, height in ((1920, 1080), (1280, 720), (960, 540), (800, 1280)):
            for count in (0, 1, 2, 8, 20, 40):
                with self.subTest(width=width, count=count):
                    rects, plus = self.ns["spaces_layout"](width, height, count)
                    self.assertEqual(len(rects), count)
                    last = 0
                    for x, y, w, h in rects:
                        self.assertGreaterEqual(x, last)
                        self.assertGreater(w, 0)
                        self.assertGreater(h, 0)
                        self.assertAlmostEqual(w / h, width / height)
                        self.assertLess(x + w, plus[0])
                        last = x + w
                    self.assertLessEqual(plus[0] + plus[2], width)

    def test_drop_maps_each_thumbnail_and_rejects_background(self):
        rects, plus = self.ns["spaces_layout"](1920, 1080, 12)
        hit = self.ns["space_hit"]
        for i, (x, y, w, h) in enumerate(rects):
            self.assertEqual(hit(x + w / 2, y + h / 2, rects, plus, 1), ("desk", i))
        self.assertEqual(hit(plus[0] + 22, plus[1] + 22, rects, plus, 1), ("plus",))
        self.assertIsNone(hit(10, 600, rects, plus, 1))
        a, b = rects[:2]
        self.assertIsNone(hit((a[0] + a[2] + b[0]) / 2, a[1] + 10, rects, plus, 1))

    def test_collapsed_names_are_targets_but_thumbnails_are_not(self):
        rects, plus = self.ns["spaces_layout"](1920, 1080, 3)
        hit = self.ns["space_hit"]
        for i, (x, y, w, h) in enumerate(rects):
            self.assertEqual(hit(x + w / 2, 22, rects, plus, 0), ("desk", i))
            self.assertIsNone(hit(x + w / 2, y + h / 2, rects, plus, 0))
        self.assertIsNone(hit(plus[0] + 22, plus[1] + 22, rects, plus, 0))

    def test_name_target_stays_stable_during_expansion(self):
        rects, plus = self.ns["spaces_layout"](1920, 1080, 3)
        for expansion in (0, 0.2, 0.7, 1):
            for i, (x, y, w, h) in enumerate(rects):
                self.assertEqual(self.ns["space_hit"](x + w / 2, 22, rects, plus, expansion),
                                 ("desk", i))

    def test_prepare_keeps_current_empty_space_and_separates_monitors(self):
        workspaces = [{"id": 1, "name": "custom", "monitor": "DP-1", "windows": 1},
                      {"id": 4, "name": "4", "monitor": "DP-2", "windows": 1}]
        obj = screen(self.ns, mon=monitor(active=2, scale=2), workspaces=workspaces)
        self.assertEqual((obj.W, obj.H), (960, 540))
        self.assertEqual([(d.id, d.name, d.current) for d in obj.desks],
                         [(1, "Desktop 1", False), (2, "Desktop 2", True)])
        self.assertEqual(obj._band_expansion(), 0)


class SpacesInteractionTests(unittest.TestCase):
    def setUp(self):
        self.ns = load_logic()
        self.obj = screen(self.ns, clients=[client("0x123"), client("0x456")],
                          workspaces=[{"id": 2, "monitor": "DP-1", "windows": 1}])
        self.obj._compose_desk = Mock()
        self.obj.finish([])

    def test_hover_expands_and_leaving_collapses_without_motion(self):
        obj = self.obj
        obj._motion(None, event(300, 20))
        self.assertEqual(obj._band_expansion(), 1)
        self.assertIsNone(obj.band_t0)
        self.assertIsNone(obj.relayout_t0)
        self.assertTrue(all(w.prev is None for w in obj.wins))
        self.assertTrue(all(w.grid[1] >= obj.band_h for w in obj.wins))
        obj._leave()
        self.assertEqual(obj._band_expansion(), 0)
        self.assertEqual(obj.band_h, self.ns["BAND_COLLAPSED"])

    def test_expansion_reverses_without_jump(self):
        obj = self.obj
        obj.ov.iface.get_boolean.return_value = True
        obj._expand_band(True)
        self.ns["time"].monotonic.return_value = 10.1
        before = obj._band_expansion()
        rect = obj._win_rect(obj.wins[0], 1)
        obj._expand_band(False)
        self.assertAlmostEqual(obj._band_expansion(), before)
        self.assertEqual(obj.wins[0].prev, rect)
        self.assertEqual(obj._win_rect(obj.wins[0], 0), obj.wins[0].real)
        self.ns["time"].monotonic.return_value = 11
        self.assertEqual(obj._band_expansion(), 0)

    def test_drag_to_space_dispatches_without_follow_and_updates_models(self):
        obj = self.obj
        obj._expand_band(True)
        w = obj.wins[0]
        current, target = obj.desks
        current.items = [(None, None, x.real) for x in obj.wins]
        obj.press = (("win", 0), 200, 200)
        obj.drag = {"win": w, "x": 200, "y": 200}
        x, y, dw, dh = target.rect
        obj._release(None, event(x + dw / 2, y + dh / 2))
        self.ns["dispatch"].assert_called_once_with(
            'hl.dsp.window.move({ workspace = 2, follow = false, window = "address:0x123" })')
        self.assertNotIn(w, obj.wins)
        self.assertEqual(target.items, [(None, None, w.real)])
        self.assertEqual(len(current.items), 1)
        self.assertIsNone(obj.relayout_t0)
        self.assertIsNone(obj.drag)
        obj.ov.close.assert_not_called()

    def test_drop_on_current_space_or_background_does_not_move(self):
        obj = self.obj
        obj._expand_band(True)
        x, y, dw, dh = obj.desks[0].rect
        for ev in (event(x + dw / 2, y + dh / 2), event(10, 800)):
            obj.press = (("win", 0), 200, 200)
            obj.drag = {"win": obj.wins[0]}
            obj._release(None, ev)
        self.ns["dispatch"].assert_not_called()
        self.assertEqual(len(obj.wins), 2)

    def test_click_desktop_selects_workspace_and_monitor(self):
        obj = self.obj
        obj._expand_band(True)
        x, y, dw, dh = obj.desks[1].rect
        ev = event(x + dw / 2, y + dh / 2)
        obj._press(None, ev)
        obj._release(None, ev)
        obj.ov.close.assert_called_once_with(workspace=(2, "DP-1"))

    def test_click_name_survives_expansion_between_press_and_release(self):
        obj = self.obj
        x, y, dw, dh = obj.desks[1].rect
        ev = event(x + dw / 2, 22)
        obj._press(None, ev)
        obj._expand_band(True)
        obj._release(None, ev)
        obj.ov.close.assert_called_once_with(workspace=(2, "DP-1"))

    def test_drag_into_collapsed_bar_expands_and_retains_window(self):
        obj = self.obj
        obj.ov.iface.get_boolean.return_value = True
        x, y, w, h = obj.wins[0].grid
        obj._press(None, event(x + w / 2, y + h / 2))
        obj._motion(None, event(900, 20))
        self.assertIs(obj.drag["win"], obj.wins[0])
        self.assertEqual(obj.band_to, 1)
        obj._motion(None, event(900, 80))
        self.assertEqual(obj.band_to, 1)


class AppExposeTests(unittest.TestCase):
    def setUp(self):
        self.ns = load_logic()

    def test_only_focused_app_including_its_hidden_windows(self):
        clients = [client("visible"), client("other", cls="Browser"),
                   client("hidden", wid=-1, name="special:minimized"),
                   client("hidden-other", cls="Browser", wid=-1, name="special:minimized"),
                   client("unmapped", mapped=False),
                   client("initial", cls="", initialClass="Editor")]
        obj = screen(self.ns, app="Editor", clients=clients)
        self.assertEqual({w.addr for w in obj.wins}, {"visible", "hidden", "initial"})
        self.assertEqual(obj.desks, [])
        self.assertIsNotNone(obj.shelf_y)
        obj._expand_band(True)
        self.assertEqual(obj.band_to, 0)
        self.assertIsNone(obj._desk_at(300, 20))

    def test_hidden_windows_only_on_focused_monitor(self):
        obj = screen(self.ns, app="Editor", mon=monitor("DP-2", 2, False),
                     clients=[client("main", wid=1), client("second", wid=2),
                              client("hidden", wid=-1, name="special:minimized")])
        self.assertEqual([w.addr for w in obj.wins], ["second"])

    def test_escape_and_background_click_close_without_selecting(self):
        obj = screen(self.ns, app="Editor", clients=[client("visible")])
        obj._key(None, event(keyval="Escape"))
        obj.ov.close.assert_called_once_with()
        obj.ov.close.reset_mock()
        ev = event(5, 500)
        obj._press(None, ev)
        obj._release(None, ev)
        obj.ov.close.assert_called_once_with()

    def test_app_pointer_movement_does_not_create_invisible_drag(self):
        obj = screen(self.ns, app="Editor", clients=[client("visible")])
        x, y, w, h = obj.wins[0].grid
        obj._press(None, event(x + w / 2, y + h / 2))
        obj._motion(None, event(x + w / 2 + 20, y + h / 2))
        self.assertIsNone(obj.drag)

    def test_toggle_app_uses_focused_class_and_handles_missing_active_window(self):
        ov = self.ns["Overview"].__new__(self.ns["Overview"])
        ov.state, ov.open, ov.close = "closed", Mock(), Mock()
        for active in ({"class": "Editor"}, {"initialClass": "Editor"}):
            self.ns["hypr_json"].return_value = active
            ov.toggle_app()
            ov.open.assert_called_with(app="Editor")
        ov.open.reset_mock()
        self.ns["hypr_json"].return_value = []
        ov.toggle_app()
        ov.open.assert_not_called()
        ov.state = "open"
        ov.toggle_app()
        ov.close.assert_called_once_with()

    def test_cancel_restores_fly_mode_without_dispatch(self):
        ov = self.ns["Overview"].__new__(self.ns["Overview"])
        ov.state, ov.mode, ov.after = "open", "fly", None
        ov.screens = {"DP-1": SimpleNamespace(hover=("win", 0), drag={}, press=(None, 0, 0))}
        ov._animate = Mock()
        ov.close()
        ov._animate.assert_called_once_with(-1)
        self.assertEqual(ov.mode, "fly")
        self.assertIsNone(ov.after)
        self.assertIsNone(ov.screens["DP-1"].press)
        self.ns["dispatch"].assert_not_called()

    def test_flight_reversal_preserves_visible_progress(self):
        ov = self.ns["Overview"].__new__(self.ns["Overview"])
        ov.t, ov.dir, ov.kick = 0.45, 1, Mock()
        ov.iface = SimpleNamespace(get_boolean=Mock(return_value=True))
        before = ov.eased()
        ov._animate(-1)
        self.assertAlmostEqual(ov.eased(), before, places=6)
        self.assertEqual(ov.state, "closing")
        ov._animate(1)
        self.assertAlmostEqual(ov.eased(), before, places=6)

    def test_reduce_motion_finishes_open_and_close_immediately(self):
        ov = self.ns["Overview"].__new__(self.ns["Overview"])
        ov.t, ov.dir, ov.kick = 0, 1, Mock()
        ov.iface = SimpleNamespace(get_boolean=Mock(return_value=False))
        ov._animate(1)
        self.assertEqual(ov.t, 1)
        ov._animate(-1)
        self.assertEqual(ov.t, 0)


if __name__ == "__main__":
    unittest.main()
