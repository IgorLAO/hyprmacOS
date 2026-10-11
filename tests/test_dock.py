"""Regressão do núcleo do Dock e dos contratos entre núcleo, GTK e eventos."""

import ast
import math
import os
from pathlib import Path
import sys
from types import SimpleNamespace
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import Mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "shell"))
from dock_geometry import DockMetrics
from dock_model import build_items, needs_refresh, reorder_pinned
from dock_motion import DockMotion
from dock_drop import open_documents, supports_documents
from glass_motion import spring_step


# Carrega os métodos reais sem inicializar GTK, D-Bus ou um segundo shell.
source = Path(os.environ.get("HYPRMAC_DOCK_SOURCE", Path(__file__).resolve().parents[1] / "shell" / "hyprmac-shell"))
tree = ast.parse(source.read_text())
nodes = [node for node in tree.body
         if isinstance(node, (ast.FunctionDef, ast.ClassDef)) and node.name in ("Dock",)]
namespace = dict(math=math, spring_step=spring_step, dock_items=build_items, dock_needs_refresh=needs_refresh,
                 reorder_pinned=reorder_pinned, DOCK_SIDE=120,
                 dock_supports_documents=supports_documents, dock_open_documents=open_documents)
exec(compile(ast.Module(body=nodes, type_ignores=[]), str(source), "exec"), namespace)
Dock = namespace["Dock"]


def client(cls, address, focus=0, workspace="1", mapped=True):
    return dict(mapped=mapped, **{"class": cls}, address=address,
                focusHistoryID=focus, workspace={"name": workspace}, title=cls)


def pinned(*names):
    return [dict(key=name, pin=name, kind="finder" if name == "hyprmac:finder" else "app",
                 info=None, cls=None, name=name) for name in names]


class DockModelTests(unittest.TestCase):
    def test_sections_focus_order_and_minimized_keep_running_indicator(self):
        clients = [client("other", "a", 4), client("fixed", "b", 2),
                   client("recent", "c", 1, "special:minimized"),
                   client("recent", "d", 3, "special:magic"),
                   client("ignored", "e", mapped=False), client("hyprmac-shell", "f")]
        original = list(clients)
        fixed = pinned("fixed")
        items = build_items(clients, fixed, str.lower, lambda cls: cls, str)
        self.assertEqual([it["key"] for it in items], [
            "fixed", "hyprmac:sep-recent", "recent", "other", "hyprmac:sep",
            "min:c", "hyprmac:downloads", "hyprmac:trash"])
        self.assertEqual([w["address"] for w in items[2]["windows"]], ["c", "d"])
        self.assertEqual(items[5]["win"]["address"], "c")
        self.assertEqual(items[5]["windows"], [])
        self.assertEqual(clients, original)
        self.assertNotIn("windows", fixed[0])

    def test_empty_snapshot_has_one_separator_and_tail(self):
        items = build_items([], [], str, str, str)
        self.assertEqual([it["kind"] for it in items], ["sep", "downloads", "trash"])

    def test_reorder_preserves_finder_and_moves_existing_objects_both_ways(self):
        items = pinned("hyprmac:finder", "one", "two", "three")
        items.append(dict(key="recent", kind="app"))
        pins = [it["pin"] for it in items[:-1]]
        one = items[1]
        self.assertFalse(reorder_pinned(items, pins, 0, 2))
        self.assertFalse(reorder_pinned(items, pins, 1, 0))
        self.assertFalse(reorder_pinned(items, pins, 1, 4))
        self.assertTrue(reorder_pinned(items, pins, 1, 3))
        self.assertEqual(pins, ["hyprmac:finder", "two", "three", "one"])
        self.assertIs(items[3], one)
        self.assertTrue(reorder_pinned(items, pins, 3, 1))
        self.assertIs(items[1], one)


class DockGeometryTests(unittest.TestCase):
    def test_magnified_layout_preserves_gaps_and_center_with_separators(self):
        m = DockMetrics.from_icon()
        items = [dict(kind="app"), dict(kind="app"), dict(kind="sep"), dict(kind="app")]
        width = m.layout(items)
        for growths in ([0, 0, 0, 0], [27.6, 16.1, 0, 4.2], [2.1, 19.3, 0, 27.6]):
            shifts = m.magnification_shifts(growths)
            lefts = [it["x"] + shift - grow / 2
                     for it, shift, grow in zip(items, shifts, growths)]
            sizes = [(m.sep_col if it["kind"] == "sep" else m.icon) + grow
                     for it, grow in zip(items, growths)]
            for i in range(1, len(items)):
                self.assertAlmostEqual(lefts[i] - lefts[i - 1] - sizes[i - 1], m.gap)
            self.assertAlmostEqual((lefts[0] + lefts[-1] + sizes[-1]) / 2, width / 2)
        self.assertEqual(m.magnification_shifts([]), [])

    def test_running_dot_remains_discreet_at_all_icon_sizes(self):
        for icon in (32, 36, 46, 72):
            m = DockMetrics.from_icon(icon)
            self.assertEqual((m.dot, m.dot_gap), (4, 4))
            self.assertLessEqual(m.pad_top + m.icon + m.dot_gap + m.dot, m.h)

    def test_metrics_and_layout_at_supported_icon_sizes(self):
        for icon in (32, 36, 46, 72):
            m = DockMetrics.from_icon(icon)
            self.assertEqual(m.h, round(58 * icon / 36))
            self.assertEqual(m.radius, 15 * (icon / 36))
            items = [dict(kind="app"), dict(kind="sep"), dict(kind="app")]
            width = m.layout(items)
            self.assertEqual([it["x"] for it in items], [m.pad_side,
                m.pad_side + m.icon + m.gap, m.pad_side + m.icon + m.sep_col + 2 * m.gap])
            self.assertEqual(width, 2 * m.pad_side + 2 * m.icon + m.sep_col + 2 * m.gap)

    def test_hit_testing_uses_visible_geometry_after_magnification(self):
        m = DockMetrics.from_icon(46)
        items = [dict(kind="app"), dict(kind="app")]
        m.layout(items)
        drawn = {0: (110, 30, 73.6), 1: (200, 40, 55)}
        self.assertEqual(m.index_at(items, drawn, 125, 35, 120, 50), 0)
        self.assertEqual(m.index_at(items, drawn, 198, 50, 120, 50), 1)
        self.assertIsNone(m.index_at(items, drawn, 190, 50, 120, 50))
        self.assertIsNone(m.index_at(items, drawn, 125, 3, 120, 50))
        self.assertEqual(m.index_at(items, {}, 120 + items[1]["x"], 50, 120, 50), 1)


class DockMotionTests(unittest.TestCase):
    def test_pointer_sweep_is_continuous_across_slots_and_separator(self):
        m = DockMetrics.from_icon()
        items = [dict(key="a", kind="app"), dict(key="b", kind="app"),
                 dict(key="sep", kind="sep"), dict(key="c", kind="app")]
        width = m.layout(items)
        motion = DockMotion(spring_step)
        previous = None
        for step in range(int(width * 4)):
            growths, _, _ = motion.scales_for_frame(
                items, m.icon, m.gap, 0, step / 4, True, False, True, step / 240)
            shifts = m.magnification_shifts(growths)
            current = [it["x"] + shift - grow / 2
                       for it, shift, grow in zip(items, shifts, growths)]
            self.assertEqual(growths[2], 0)
            if previous is not None:
                self.assertLess(max(abs(a - b) for a, b in zip(current, previous)), 0.25)
            previous = current

    def test_hold_preserves_curve_anchor_and_envelope_stays_bounded(self):
        motion = DockMotion(spring_step)
        items = [dict(key="a", kind="app", x=10), dict(key="b", kind="app", x=68)]
        before, _, _ = motion.scales_for_frame(items, 46, 12, 0, 33, True, False, True, 0)
        held, _, _ = motion.scales_for_frame(items, 46, 12, 0, 91, True, True, False, 1)
        self.assertEqual(held, before)
        self.assertEqual(motion.pointer_x, 33)
        after, _, _ = motion.scales_for_frame(items, 46, 12, 0, None, False, False, False, 1)
        self.assertEqual(after, before)
        for envelope in (-0.02, 1.02):
            motion.envelope = envelope
            growths, _, _ = motion.scales_for_frame(items, 46, 12, 0, 33, True, False, False, 1)
            self.assertTrue(all(0 <= grow <= 46 * 0.6 + 1e-10 for grow in growths))

    def test_reorder_rebases_growth_shift_without_center_jump(self):
        motion = DockMotion(spring_step)
        item = dict(key="a", x=10)
        position, _ = motion.position(item, 0, False, shift=-14)
        center = position - 14
        item["x"] = 68
        position, moving = motion.position(item, 0, False, shift=9)
        self.assertEqual(position + 9, center)
        self.assertTrue(moving)
        for _ in range(180):
            position, moving = motion.position(item, 1 / 60, False, shift=9)
        self.assertEqual((position, moving), (68, False))

    def test_shifted_neighbors_keep_spacing_while_springing_into_vacancy(self):
        m = DockMetrics.from_icon()
        items = pinned("a", "b", "c", "d")
        m.layout(items)
        motion = DockMotion(spring_step)
        motion.retain_positions(items)
        self.assertTrue(reorder_pinned(items, ["a", "b", "c", "d"], 0, 3))
        m.layout(items)
        for _ in range(180):
            positions = [motion.position(it, 1 / 60, False)[0] for it in items[:3]]
            self.assertTrue(all(abs(b - a - m.icon - m.gap) < 1e-8
                                for a, b in zip(positions, positions[1:])))
        self.assertEqual(positions, [it["x"] for it in items[:3]])

    def test_magnification_curve_hold_reduced_motion_and_clock_reset(self):
        motion = DockMotion(spring_step)
        items = [dict(key="a", kind="app", x=10), dict(key="sep", kind="sep", x=67)]
        growths, moving, dt = motion.scales_for_frame(items, 46, 12, 120, 153,
                                                      True, False, True, 1)
        self.assertAlmostEqual(growths[0], 46 * 0.6)
        self.assertEqual(growths[1], 0)
        self.assertFalse(moving)
        self.assertEqual(dt, 0)
        motion.scales_for_frame(items, 46, 12, 120, None, False, True, False, 2)
        self.assertAlmostEqual(motion.scales["a"], 1.6)
        motion.reset_clock()
        _, _, dt = motion.scales_for_frame(items, 46, 12, 120, None, False, False, False, 100)
        self.assertEqual(dt, 0)
        for frame in range(240):
            motion.scales_for_frame(items, 46, 12, 120, None, False, False, False, 100 + frame / 60)
        self.assertEqual(motion.scales["a"], 1)
        self.assertEqual(motion.velocities["a"], 0)

    def test_magnification_shape_tracks_pointer_and_envelope_springs(self):
        motion = DockMotion(spring_step)
        items = [dict(key="a", kind="app", x=10), dict(key="b", kind="app", x=68)]
        motion.scales_for_frame(items, 46, 12, 0, 33, True, False, False, 0)
        growths, moving, _ = motion.scales_for_frame(items, 46, 12, 0, 33, True, False, False, 1 / 60)
        self.assertTrue(0 < growths[0] < 46 * 0.6)       # intensidade ainda entrando
        self.assertTrue(moving)
        for frame in range(2, 60):
            motion.scales_for_frame(items, 46, 12, 0, 33, True, False, False, frame / 60)
        # curva já cheia: mover o ponteiro muda o ícone maior no MESMO quadro
        growths, _, _ = motion.scales_for_frame(items, 46, 12, 0, 91, True, False, False, 61 / 60)
        self.assertAlmostEqual(growths[1], 46 * 0.6, places=2)
        self.assertLess(growths[0], growths[1])
        # ao sair, a curva fica no último ponteiro e só esvazia
        growths, moving, _ = motion.scales_for_frame(items, 46, 12, 0, None, False, False, False, 62 / 60)
        self.assertTrue(0 < growths[0] < growths[1] < 46 * 0.6)
        self.assertTrue(moving)
        for frame in range(63, 180):
            growths, moving, _ = motion.scales_for_frame(items, 46, 12, 0, None, False, False, False, frame / 60)
        self.assertEqual(growths, [0.0, 0.0])
        self.assertFalse(moving)

    def test_reordering_spring_drag_and_reduced_motion(self):
        motion = DockMotion(spring_step)
        item = dict(key="a", x=10)
        self.assertEqual(motion.position(item, 0, False), (10, False))
        item["x"] = 80
        position, moving = motion.position(item, 1 / 60, False)
        self.assertTrue(10 < position < 80)
        self.assertTrue(moving)
        self.assertEqual(motion.position(item, 1 / 60, False, 125), (125, False))
        self.assertEqual(motion.position(item, 1 / 60, True), (80, False))
        motion.retain_positions([])
        self.assertEqual(motion.positions, {})

    def test_bounce_height_expiry_and_accessibility(self):
        motion = DockMotion(spring_step)
        motion.bounces["a"] = 0
        lift, moving = motion.bounce("a", 0.31, 46, False)
        self.assertAlmostEqual(lift, 46 * 0.55)
        self.assertTrue(moving)
        self.assertEqual(motion.bounce("a", 8.01, 46, False), (0, False))
        motion.bounces["a"] = 10
        self.assertEqual(motion.bounce("a", 10.1, 46, True), (0, False))
        self.assertNotIn("a", motion.bounces)


class DockDocumentTests(unittest.TestCase):
    def app(self, files=True, uris=False):
        return SimpleNamespace(supports_files=lambda: files, supports_uris=lambda: uris,
                               launch=Mock(return_value=True), launch_uris=Mock(return_value=True))

    def test_local_document_with_spaces_is_delivered_as_file_without_shell(self):
        with TemporaryDirectory() as directory:
            document = Path(directory) / "my document; $(literal).txt"
            document.touch()
            info = self.app()
            file = SimpleNamespace(get_path=lambda: str(document))
            constructor = Mock(return_value=file)
            context = object()
            self.assertTrue(open_documents(info, [document.as_uri()], constructor, context))
            constructor.assert_called_once_with(document.as_uri())
            info.launch.assert_called_once_with([file], context)
            info.launch_uris.assert_not_called()

    def test_remote_document_requires_uri_support_and_launch_error_rejects(self):
        constructor = Mock()
        info = self.app()
        self.assertFalse(open_documents(info, ["https://example.org/doc.pdf"], constructor))
        info.launch.assert_not_called()
        info = self.app(files=False, uris=True)
        uri = "https://example.org/my%20document.pdf"
        self.assertTrue(open_documents(info, [uri], constructor))
        info.launch_uris.assert_called_once_with([uri], None)
        constructor.assert_not_called()
        info.launch_uris.side_effect = RuntimeError("launcher failed")
        self.assertFalse(open_documents(info, [uri], constructor))
        info.launch_uris.side_effect = None
        info.launch_uris.return_value = False
        self.assertFalse(open_documents(info, [uri], constructor))

    def test_invalid_batch_missing_files_and_unsupported_app_never_launch(self):
        info = self.app(uris=True)
        constructor = Mock(return_value=SimpleNamespace(get_path=lambda: None))
        for uris in ([], ["relative.txt"], ["file:///missing"], ["https://"],
                     ["https://example.org/a b"], ["https://example.org/%00"],
                     ["https://example.org/%invalid"], ["file:///a?query"],
                     ["https://example.org/valid", "invalid"]):
            self.assertFalse(open_documents(info, uris, constructor), uris)
        info.launch.assert_not_called()
        info.launch_uris.assert_not_called()
        self.assertFalse(supports_documents(None))
        self.assertFalse(open_documents(self.app(files=False), ["https://example.org/doc"], constructor))


class DockIntegrationTests(unittest.TestCase):
    def setUp(self):
        namespace["Gdk"] = SimpleNamespace(ModifierType=SimpleNamespace(CONTROL_MASK=4, BUTTON1_MASK=256),
                                          NotifyType=SimpleNamespace(INFERIOR=2))

    def gesture_dock(self):
        dock = Dock.__new__(Dock)
        dock.motion = DockMotion(spring_step)
        dock.metrics = DockMetrics.from_icon()
        dock.icon, dock.gap, dock.above, dock.h = 46, 12, 42, 74
        dock.items = pinned("hyprmac:finder", "one", "two")
        dock.w = dock.metrics.layout(dock.items)
        dock.pinned = [it["pin"] for it in dock.items]
        dock._draw_geom = {}
        dock.area = SimpleNamespace(queue_draw=Mock())
        dock._layout = Mock(side_effect=lambda: dock.metrics.layout(dock.items))
        dock._save, dock._activate, dock.refresh = Mock(), Mock(), Mock()
        dock._cancel_hide, dock._menu = Mock(), Mock()
        dock.autohide = False
        return dock

    def test_release_between_draws_starts_return_at_actual_pointer(self):
        dock = self.gesture_dock()
        x = 120 + dock.items[1]["x"] + 23
        dock._press(None, SimpleNamespace(button=1, x=x + 5, y=60))
        target = 120 + dock.items[2]["x"] + 23
        dock._drag_motion(SimpleNamespace(x=target + 5, y=60))
        # Nenhum draw ocorreu; o release tem uma coordenada mais recente.
        dock._release(None, SimpleNamespace(button=1, x=target + 17, y=60))
        item = next(it for it in dock.items if it["key"] == "one")
        position, moving = dock.motion.position(item, 0, False)
        self.assertAlmostEqual(position, item["x"] + 12)
        self.assertTrue(moving)
        for _ in range(180):
            position, moving = dock.motion.position(item, 1 / 60, False)
        self.assertEqual((position, moving), (item["x"], False))
        dock._activate.assert_not_called()

    def drop_area(self):
        target = SimpleNamespace(name=lambda: "text/uri-list")
        launch_context = SimpleNamespace(set_timestamp=Mock())
        display = SimpleNamespace(get_app_launch_context=lambda: launch_context)
        return SimpleNamespace(queue_draw=Mock(), drag_dest_find_target=Mock(return_value=target),
                               drag_get_data=Mock(), get_display=lambda: display)

    def test_document_destination_filters_special_icons_and_internal_drag(self):
        dock = self.gesture_dock()
        info = SimpleNamespace(supports_files=lambda: True, supports_uris=lambda: False)
        dock.items[1]["info"] = info
        x = 120 + dock.items[1]["x"] + 23
        self.assertEqual(dock._document_app_at(x, 60), 1)
        for kind in ("finder", "apps", "settings", "downloads", "trash", "minimized", "sep"):
            dock.items[1]["kind"] = kind
            self.assertIsNone(dock._document_app_at(x, 60), kind)
        dock.items[1]["kind"] = "app"
        dock.dragging = True
        self.assertIsNone(dock._document_app_at(x, 60))
        dock.dragging = False
        dock.menu_open = True
        self.assertIsNone(dock._document_app_at(x, 60))

    def test_document_drop_binds_app_and_receiver_reports_result_never_delete(self):
        dock = self.gesture_dock()
        dock.area = self.drop_area()
        info = SimpleNamespace(supports_files=lambda: False, supports_uris=lambda: True,
                               launch_uris=Mock(return_value=True))
        dock.items[1]["info"] = info
        context = SimpleNamespace(get_actions=lambda: 2)
        namespace["Gdk"].DragAction = type("DragAction", (int,), {"COPY": 2})
        finish = Mock()
        namespace["Gtk"] = SimpleNamespace(drag_finish=finish)
        namespace["Gio"] = SimpleNamespace(File=SimpleNamespace(new_for_uri=Mock()))
        x = 120 + dock.items[1]["x"] + 23
        self.assertTrue(dock._document_drop(dock.area, context, x, 60, 100))
        dock.area.drag_get_data.assert_called_once()
        dock._document_drag_leave(dock.area, context, 100)
        dock.items[1]["info"] = Mock()  # Mudança de snapshot não troca o receptor.
        data = SimpleNamespace(get_target=lambda: SimpleNamespace(name=lambda: "text/uri-list"),
                               get_length=lambda: 32, get_uris=lambda: ["https://example.org/doc.pdf"])
        dock._document_received(dock.area, context, x, 60, data, 0, 110)
        info.launch_uris.assert_called_once()
        finish.assert_called_once_with(context, True, False, 110)
        self.assertIsNone(dock._document_pending)
        dock._activate.assert_not_called()
        finish.reset_mock()
        dock._document_received(dock.area, context, x, 60, data, 0, 120)
        finish.assert_called_once_with(context, False, False, 120)

    def test_drop_receiver_invalid_selection_and_failure_reject(self):
        dock = self.gesture_dock()
        dock.area = self.drop_area()
        info = SimpleNamespace(supports_files=lambda: False, supports_uris=lambda: True,
                               launch_uris=Mock(side_effect=RuntimeError("launch failed")))
        context = SimpleNamespace(get_actions=lambda: 2)
        finish = Mock()
        namespace["Gtk"] = SimpleNamespace(drag_finish=finish)
        namespace["Gio"] = SimpleNamespace(File=SimpleNamespace(new_for_uri=Mock()))
        for target, length, uris in (("text/plain", 30, ["https://example.org/doc.pdf"]),
                                     ("text/uri-list", -1, None),
                                     ("text/uri-list", 30, ["https://example.org/doc.pdf"])):
            dock._document_pending = (context, "one", info)
            data = SimpleNamespace(get_target=lambda: SimpleNamespace(name=lambda: target),
                                   get_length=lambda: length, get_uris=lambda: uris)
            dock._document_received(dock.area, context, 0, 0, data, 0, 100)
            self.assertEqual(finish.call_args.args, (context, False, False, 100))
        info.launch_uris.assert_called_once()

    def test_document_motion_advertises_copy_only_over_supported_app(self):
        dock = self.gesture_dock()
        dock.area = self.drop_area()
        dock.items[1]["info"] = SimpleNamespace(supports_files=lambda: True, supports_uris=lambda: False)
        namespace["Gdk"].DragAction = type("DragAction", (int,), {"COPY": 2})
        status = Mock()
        namespace["Gdk"].drag_status = status
        context = SimpleNamespace(get_actions=lambda: 2)
        x = 120 + dock.items[1]["x"] + 23
        self.assertTrue(dock._document_drag_motion(dock.area, context, x, 60, 100))
        status.assert_called_once_with(context, 2, 100)
        self.assertEqual(dock.hover, 1)
        context = SimpleNamespace(get_actions=lambda: 4)  # MOVE sem COPY: rejeitado.
        dock._document_drag_motion(dock.area, context, x, 60, 110)
        self.assertEqual(status.call_args.args, (context, 0, 110))
        self.assertFalse(dock._document_drop(dock.area, context, x, 60, 110))
        dock.area.drag_get_data.assert_not_called()

    def test_control_click_opens_menu_and_release_never_activates(self):
        for button, state in ((1, 4), (1, 5), (3, 0)):
            dock = self.gesture_dock()
            x = 120 + dock.items[1]["x"] + 23
            event = SimpleNamespace(button=button, state=state, x=x, y=60)
            dock._press(None, event)
            dock._menu.assert_called_once_with(1, event)
            self.assertIsNone(dock.pressed)
            dock._release(None, event)
            dock._activate.assert_not_called()

    def test_vertical_drag_removes_pin_only_after_release(self):
        dock = self.gesture_dock()
        x = 120 + dock.items[1]["x"] + 23
        dock._press(None, SimpleNamespace(button=1, x=x, y=60))
        self.assertFalse(dock._drag_motion(SimpleNamespace(x=x, y=53)))
        self.assertTrue(dock._drag_motion(SimpleNamespace(x=x, y=-30)))
        self.assertTrue(dock._drag_remove)
        self.assertIn("one", dock.pinned)
        dock._save.assert_not_called()
        dock._release(None, SimpleNamespace(button=1, x=x, y=-30))
        self.assertEqual(dock.pinned, ["hyprmac:finder", "two"])
        dock._save.assert_called_once()
        dock.refresh.assert_called_once()
        dock._activate.assert_not_called()
        self.assertFalse(dock._drag_remove)

    def test_crossing_before_first_drag_motion_preserves_button_grab(self):
        dock = self.gesture_dock()
        x = 120 + dock.items[1]["x"] + 23
        dock._press(None, SimpleNamespace(button=1, x=x, y=60))
        dock._leave(None, SimpleNamespace(detail=0, state=256))
        self.assertEqual(dock.pressed, 1)
        self.assertTrue(dock._drag_motion(SimpleNamespace(x=x, y=-30)))
        dock._release(None, SimpleNamespace(button=1, x=x, y=-30))
        self.assertNotIn("one", dock.pinned)

    def test_returning_to_dock_cancels_remove_and_protected_items_cannot_drag(self):
        dock = self.gesture_dock()
        x = 120 + dock.items[1]["x"] + 23
        dock._press(None, SimpleNamespace(button=1, x=x, y=60))
        dock._drag_motion(SimpleNamespace(x=x, y=-30))
        dock._drag_motion(SimpleNamespace(x=x, y=60))
        self.assertFalse(dock._drag_remove)
        dock._release(None, SimpleNamespace(button=1, x=x, y=60))
        self.assertIn("one", dock.pinned)
        dock.refresh.assert_not_called()
        dock._activate.assert_not_called()
        for item in (dock.items[0], dict(kind="trash"), dict(kind="downloads"), dict(kind="app")):
            self.assertFalse(dock._removable(item))
        x = 120 + dock.items[0]["x"] + 23
        dock._press(None, SimpleNamespace(button=1, x=x, y=60))
        self.assertFalse(dock._drag_motion(SimpleNamespace(x=x, y=-30)))
        self.assertIn("hyprmac:finder", dock.pinned)

    def test_release_position_is_authoritative_for_removal(self):
        dock = self.gesture_dock()
        x = 120 + dock.items[1]["x"] + 23
        dock._press(None, SimpleNamespace(button=1, x=x, y=60))
        dock._drag_motion(SimpleNamespace(x=x, y=-30))
        dock._release(None, SimpleNamespace(button=2, x=x, y=-30))
        self.assertTrue(dock.dragging)
        dock._release(None, SimpleNamespace(button=1, x=x, y=60))
        self.assertIn("one", dock.pinned)
        dock.refresh.assert_not_called()

    def test_snapshot_during_drag_tracks_key_and_missing_item_cancels(self):
        dock = self.gesture_dock()
        x = 120 + dock.items[1]["x"] + 23
        dock._press(None, SimpleNamespace(button=1, x=x, y=60))
        dock._drag_motion(SimpleNamespace(x=x, y=-30))
        dock.special_ids = {}
        dock.apps = SimpleNamespace(_info=lambda cls: cls)
        dock._key_of_class = str.lower
        dock._pixbuf = Mock(return_value="pixbuf")
        dock._capture_thumb = Mock()
        dock.motion = DockMotion(spring_step)
        dock._thumbs = {}
        namespace["app_info"] = lambda p: SimpleNamespace(get_name=lambda: p)
        namespace["hypr_json"] = lambda _: []
        namespace["display_name"] = str
        dock.pinned = ["two", "one"]
        Dock.refresh(dock)
        self.assertEqual(dock.items[dock.pressed]["key"], "one")
        self.assertTrue(dock.dragging)
        dock.pinned = ["two"]
        Dock.refresh(dock)
        self.assertIsNone(dock.pressed)
        self.assertFalse(dock.dragging)
        dock._release(None, SimpleNamespace(button=1, x=x, y=60))
        dock._activate.assert_not_called()

    def test_unpin_running_app_keeps_its_window_and_recent_item(self):
        dock = self.gesture_dock()
        dock.special_ids = {}
        dock.apps = SimpleNamespace(_info=lambda cls: cls)
        dock._key_of_class = str.lower
        dock._pixbuf = Mock(return_value="pixbuf")
        dock._capture_thumb = Mock()
        dock.motion = DockMotion(spring_step)
        dock._thumbs = {}
        namespace["app_info"] = lambda p: SimpleNamespace(get_name=lambda: p)
        namespace["hypr_json"] = lambda _: [client("one", "running-window")]
        namespace["display_name"] = str
        dock.pinned = ["one", "two"]
        Dock.refresh(dock)
        x = 120 + dock.items[0]["x"] + 23
        dock._press(None, SimpleNamespace(button=1, x=x, y=60))
        dock._drag_motion(SimpleNamespace(x=x, y=-30))
        dock.refresh = lambda: Dock.refresh(dock)
        dock._release(None, SimpleNamespace(button=1, x=x, y=-30))
        self.assertNotIn("one", dock.pinned)
        running = next(it for it in dock.items if it["key"] == "one")
        self.assertEqual(running["windows"][0]["address"], "running-window")
        self.assertIsNone(running.get("pin"))
        dock._activate.assert_not_called()

    def test_event_burst_coalesces_into_one_gtk_refresh(self):
        dock = Dock.__new__(Dock)
        dock._refresh_id = None
        timer = Mock(return_value=42)
        namespace["GLib"] = SimpleNamespace(timeout_add=timer)
        for event in ("openwindow", "closewindow", "movewindowv2", "activewindowv2",
                      "windowtitlev2", "changefloatingmode", "fullscreen"):
            self.assertTrue(needs_refresh(event + ">>payload"))
            self.assertFalse(dock._event(event + ">>payload"))
        dock._event("workspace>>2")
        timer.assert_called_once_with(120, dock.refresh)

    def test_drag_threshold_release_save_and_click_are_distinct(self):
        dock = Dock.__new__(Dock)
        dock.motion = DockMotion(spring_step)
        dock.metrics = DockMetrics.from_icon()
        dock.icon, dock.gap, dock.above, dock.h = 46, 12, 42, 74
        dock.items = pinned("hyprmac:finder", "one", "two")
        dock.w = dock.metrics.layout(dock.items)
        dock.pinned = [it["pin"] for it in dock.items]
        dock._draw_geom = {}
        dock.area = SimpleNamespace(queue_draw=Mock())
        dock._layout = Mock(side_effect=lambda: dock.metrics.layout(dock.items))
        dock._save, dock._activate = Mock(), Mock()
        dock._cancel_hide = Mock()
        dock.autohide = False
        x = 120 + dock.items[1]["x"] + 23
        dock._press(None, SimpleNamespace(button=1, x=x, y=60))
        self.assertFalse(dock._drag_motion(SimpleNamespace(x=x + 7)))
        target = 120 + dock.items[2]["x"] + 23
        self.assertTrue(dock._drag_motion(SimpleNamespace(x=target)))
        self.assertEqual(dock.pinned, ["hyprmac:finder", "two", "one"])
        dock._release(None, SimpleNamespace(button=1, x=target, y=60))
        dock._save.assert_called_once()
        dock._activate.assert_not_called()
        dock._press(None, SimpleNamespace(button=1, x=x, y=60))
        dock._release(None, SimpleNamespace(button=1, x=x, y=60))
        dock._activate.assert_called_once()

    def test_refresh_hydrates_icons_removes_stale_thumbnails_and_cancels_bounce(self):
        dock = Dock.__new__(Dock)
        dock.pinned = ["hyprmac:apps"]
        dock.special_ids = {}
        dock.apps = SimpleNamespace(_info=lambda cls: "desktop:" + str(cls))
        dock._key_of_class = str.lower
        dock._pixbuf = Mock(return_value="pixbuf")
        dock._capture_thumb, dock._layout = Mock(), Mock()
        dock.motion = DockMotion(spring_step)
        dock.motion.bounces["app"] = 0
        dock._thumbs = {"stale": "old", "b": "thumb"}
        namespace["hypr_json"] = lambda _: [client("app", "a"), client("app", "b", 1, "special:minimized")]
        namespace["display_name"] = str
        self.assertFalse(dock.refresh())
        self.assertEqual(dock._thumbs, {"b": "thumb"})
        self.assertNotIn("app", dock.motion.bounces)
        self.assertEqual([it["pb"] for it in dock.items if it["kind"] != "sep"], ["pixbuf"] * 5)
        dock._capture_thumb.assert_called_once()
        dock._layout.assert_called_once()


if __name__ == "__main__":
    unittest.main()
