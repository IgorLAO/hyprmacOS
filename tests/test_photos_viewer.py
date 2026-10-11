"""Lógica e handlers do visualizador, sem instanciar widgets ou abrir janelas."""
import importlib.machinery
import importlib.util
import os
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
loader = importlib.machinery.SourceFileLoader("photos_viewer_tests", str(ROOT / "shell/hyprmac-fotos"))
spec = importlib.util.spec_from_loader(loader.name, loader)
APP = importlib.util.module_from_spec(spec)
loader.exec_module(APP)


class PhotosViewerTests(unittest.TestCase):
    def setUp(self):
        self.state = APP.PhotoViewerState()

    def test_empty_navigation(self):
        self.assertIsNone(self.state.move(1))
        self.assertFalse(self.state.open([], "absent.jpg"))
        self.assertIsNone(self.state.close())

    def test_grid_order_and_boundaries(self):
        files = ["z.jpg", "a.mov", "b.png"]
        self.assertTrue(self.state.open(files, "a.mov"))
        self.assertEqual(self.state.move(-1), "z.jpg")
        self.assertEqual(self.state.move(-1), "z.jpg")
        self.assertEqual(self.state.move(1), "a.mov")
        self.assertEqual(self.state.move(1), "b.png")
        self.assertEqual(self.state.move(1), "b.png")

    def test_order_survives_grid_change(self):
        files = ["b.png", "a.jpg"]
        self.state.open(files, "b.png")
        files.reverse()
        files.append("new.jpg")
        self.assertEqual(self.state.move(1), "a.jpg")
        self.assertEqual(self.state.files, ("b.png", "a.jpg"))

    def test_filtered_order_from_library(self):
        with tempfile.TemporaryDirectory() as directory:
            for name, stamp in (("a.jpg", 100), ("b.png", 300), ("c.mov", 200)):
                path = Path(directory) / name
                path.touch()
                os.utime(path, (stamp, stamp))
            grid = APP.get_media_files(directory)
            self.state.open(grid, grid[0])
            self.assertEqual(Path(self.state.current).name, "b.png")
            self.assertEqual(Path(self.state.move(1)).name, "c.mov")
            self.assertEqual(Path(self.state.move(1)).name, "a.jpg")

    def test_close_returns_current_selection_and_reopen(self):
        self.state.open(["a", "b"], "a")
        self.state.move(1)
        self.assertEqual(self.state.close(), "b")
        self.assertIsNone(self.state.current)
        self.state.open(["c"], "c")
        self.assertEqual(self.state.move(1), "c")

    def test_invalid_open_preserves_current(self):
        self.state.open(["a"], "a")
        self.assertFalse(self.state.open([], "b"))
        self.assertEqual(self.state.current, "a")

    def test_favorites_toggle_and_persist(self):
        with tempfile.TemporaryDirectory() as directory:
            with mock.patch.object(APP, "FAVORITOS_PATH", str(Path(directory) / "favorites.json")):
                favorites = {"other.jpg"}
                APP.toggle_favorite_path(favorites, "photo.jpg")
                APP.save_favoritos(favorites)
                self.assertEqual(APP.load_favoritos(), {"other.jpg", "photo.jpg"})
                APP.toggle_favorite_path(favorites, "photo.jpg")
                APP.toggle_favorite_path(favorites, None)
                self.assertEqual(favorites, {"other.jpg"})

    def test_date_english_without_zero_padding(self):
        with mock.patch.object(APP.os.path, "getmtime", return_value=datetime(2026, 10, 11, 12).timestamp()):
            self.assertEqual(APP.photo_date("photo.jpg"), "October 11, 2026")
        with mock.patch.object(APP.os.path, "getmtime", return_value=datetime(2025, 1, 2, 12).timestamp()):
            self.assertEqual(APP.photo_date("photo.jpg"), "January 2, 2025")

    def test_missing_date(self):
        with mock.patch.object(APP.os.path, "getmtime", side_effect=OSError):
            self.assertEqual(APP.photo_date("missing.jpg"), "Unknown Date")

    def test_reduce_motion_setting_and_failure(self):
        with mock.patch.object(APP.Gio.Settings, "new") as settings:
            settings.return_value.get_boolean.return_value = False
            self.assertFalse(APP.animations_enabled())
            settings.return_value.get_boolean.assert_called_once_with("enable-animations")
            settings.return_value.get_boolean.return_value = True
            self.assertTrue(APP.animations_enabled())
            settings.side_effect = RuntimeError()
            self.assertFalse(APP.animations_enabled())

    def test_stack_transition_respects_setting(self):
        view = SimpleNamespace(page_stack=mock.Mock())
        for enabled, duration in ((False, 0), (True, 160)):
            with mock.patch.object(APP, "animations_enabled", return_value=enabled):
                APP.PhotosAppView.switch_page(view, "viewer")
            view.page_stack.set_transition_duration.assert_called_with(duration)
            view.page_stack.set_visible_child_name.assert_called_with("viewer")

    def fake_view(self):
        return SimpleNamespace(window=None, viewer_state=self.state, selected_filepath="a.jpg",
                               open_viewer=mock.Mock(), close_viewer=mock.Mock(),
                               update_viewer=mock.Mock(), toggle_favorite=mock.Mock(),
                               delete_selected=mock.Mock())

    def test_keyboard_opens_and_toggles(self):
        view = self.fake_view()
        for key in (APP.Gdk.KEY_space, APP.Gdk.KEY_Return, APP.Gdk.KEY_KP_Enter):
            self.assertTrue(APP.PhotosAppView.on_key_pressed(view, None, key, 0, 0))
            view.open_viewer.assert_called_with("a.jpg")
        APP.PhotosAppView.on_key_pressed(view, None, APP.Gdk.KEY_F, 0, 0)
        view.toggle_favorite.assert_called_once()

    def test_viewer_arrows_and_escape(self):
        view = self.fake_view()
        self.state.open(["a.jpg", "b.jpg"], "a.jpg")
        APP.PhotosAppView.on_key_pressed(view, None, APP.Gdk.KEY_Right, 0, 0)
        self.assertEqual(self.state.current, "b.jpg")
        APP.PhotosAppView.on_key_pressed(view, None, APP.Gdk.KEY_Left, 0, 0)
        self.assertEqual(self.state.current, "a.jpg")
        APP.PhotosAppView.on_key_pressed(view, None, APP.Gdk.KEY_Escape, 0, 0)
        view.close_viewer.assert_called_once()
        self.assertEqual(view.update_viewer.call_count, 2)

    def test_double_click_selects_and_opens(self):
        cell = mock.Mock(filepath="a.jpg")
        view = SimpleNamespace(select_cell=mock.Mock(), open_viewer=mock.Mock())
        event = SimpleNamespace(button=1, type=APP.Gdk.EventType.DOUBLE_BUTTON_PRESS)
        self.assertTrue(APP.PhotosAppView.on_cell_button_press(view, cell, event))
        view.select_cell.assert_called_once_with(cell)
        view.open_viewer.assert_called_once_with("a.jpg")

    def test_escape_restores_current_cell(self):
        self.state.open(["a.jpg", "b.jpg"], "b.jpg")
        child = mock.Mock()
        child.get_child.return_value = SimpleNamespace(filepath="b.jpg")
        view = SimpleNamespace(viewer_state=self.state, switch_page=mock.Mock(), viewer_info=mock.Mock(),
                               flowbox=mock.Mock(), select_cell=mock.Mock())
        view.flowbox.get_children.return_value = [child]
        APP.PhotosAppView.close_viewer(view)
        view.switch_page.assert_called_once_with("grid")
        view.select_cell.assert_called_once_with(child.get_child())
        child.grab_focus.assert_called_once()
        self.assertIsNone(self.state.current)

    def test_video_launch_uses_file_uri(self):
        self.state.open(["/tmp/my video.mov"], "/tmp/my video.mov")
        view = SimpleNamespace(viewer_state=self.state)
        with mock.patch.object(APP.Gio.AppInfo, "launch_default_for_uri") as launch:
            APP.PhotosAppView.play_video(view, None)
            launch.assert_called_once_with("file:///tmp/my%20video.mov", None)

    def test_favorite_handler_updates_badge_without_reload(self):
        cell = mock.Mock(filepath="a.jpg", favorite=False)
        child = mock.Mock()
        child.get_child.return_value = cell
        view = SimpleNamespace(selected_filepath="a.jpg", favoritos=set(), favorite_button=mock.Mock(),
                               current_filter="Library", flowbox=mock.Mock(), load_items=mock.Mock())
        view.flowbox.get_children.return_value = [child]
        with mock.patch.object(APP, "save_favoritos") as save:
            APP.PhotosAppView.toggle_favorite(view)
            save.assert_called_once_with({"a.jpg"})
        self.assertTrue(cell.favorite)
        cell.queue_draw.assert_called_once()
        view.favorite_button.set_label.assert_called_once_with("♥")
        view.load_items.assert_not_called()

    def test_snapshot_viewer_dispatch(self):
        with mock.patch.object(APP.sys, "argv", ["hyprmac-fotos", "--snapshot-viewer", "out.png"]):
            with mock.patch.object(APP, "run_snapshot") as snapshot:
                self.assertEqual(APP.main(), 0)
                snapshot.assert_called_once_with("out.png", viewer=True)


if __name__ == "__main__":
    unittest.main()
