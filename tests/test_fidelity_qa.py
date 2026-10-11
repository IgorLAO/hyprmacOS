"""QA independente de gestos e atualização, executando métodos reais do Dock."""

from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch

import test_dock


class DockGestureLifecycleQA(unittest.TestCase):
    def setUp(self):
        fixture = test_dock.DockIntegrationTests()
        fixture.setUp()
        self.dock = fixture.gesture_dock()
        self.dock.hover = 1
        self.dock._pointer_x = 200
        self.gdk = SimpleNamespace(NotifyType=SimpleNamespace(INFERIOR=2),
                                   ModifierType=SimpleNamespace(BUTTON1_MASK=256))

    def test_leaving_surface_keeps_active_drag_for_grab_release(self):
        dock = self.dock
        x = 120 + dock.items[1]["x"] + 23
        dock._press(None, SimpleNamespace(button=1, state=0, x=x, y=60))
        dock._drag_motion(SimpleNamespace(x=x, y=-30))
        with patch.dict(test_dock.namespace, Gdk=self.gdk):
            dock._leave(None, SimpleNamespace(detail=0))
        self.assertTrue(dock.dragging)
        self.assertEqual(dock.pressed, 1)
        self.assertEqual(dock._pressed_key, "one")
        self.assertIn("one", dock.pinned)
        dock._release(None, SimpleNamespace(button=1, x=x, y=-30))
        self.assertNotIn("one", dock.pinned)
        dock._activate.assert_not_called()

    def test_leaving_before_drag_threshold_cancels_click(self):
        dock = self.dock
        x = 120 + dock.items[1]["x"] + 23
        dock._press(None, SimpleNamespace(button=1, state=0, x=x, y=60))
        with patch.dict(test_dock.namespace, Gdk=self.gdk):
            dock._leave(None, SimpleNamespace(detail=0))
        dock._release(None, SimpleNamespace(button=1, x=x, y=60))
        self.assertIsNone(dock.pressed)
        self.assertIsNone(dock._pressed_key)
        dock._activate.assert_not_called()
        dock._save.assert_not_called()

    def test_new_event_burst_can_rearm_after_completed_refresh(self):
        dock = self.dock
        dock.pinned = []
        dock.apps = SimpleNamespace(_info=str)
        dock._key_of_class = str
        dock._thumbs = {}
        dock._pixbuf = Mock(return_value=None)
        dock.motion = test_dock.DockMotion(test_dock.spring_step)
        dock._refresh_id = None
        timer = Mock(side_effect=[42, 43])
        with patch.dict(test_dock.namespace, GLib=SimpleNamespace(timeout_add=timer),
                        hypr_json=lambda _: [], display_name=str):
            for _ in range(100):
                dock._event("activewindowv2>>address")
            self.assertEqual(timer.call_count, 1)
            test_dock.Dock.refresh(dock)
            self.assertIsNone(dock._refresh_id)
            for _ in range(100):
                dock._event("windowtitlev2>>address,title")
            self.assertEqual(timer.call_count, 2)
        self.assertEqual([call.args[0] for call in timer.call_args_list], [120, 120])


if __name__ == "__main__":
    unittest.main()
