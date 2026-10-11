"""Pastas do Notes: persistência isolada e integração GTK 3 quando há display."""
import importlib.machinery
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import unittest
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "shell"))
import notes_store


class NotesFoldersTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.store = notes_store.Store(os.path.join(self.temp.name, "notas"))
        self.trash = os.path.join(self.temp.name, "Trash")
        patcher = mock.patch("notes_store.os.path.expanduser", return_value=self.trash)
        patcher.start()
        self.addCleanup(patcher.stop)

    def test_counts_and_default_api_do_not_include_subfolders(self):
        root_note = self.store.new()
        work = self.store.create_folder("Work")
        personal = self.store.create_folder("Personal")
        self.store.new(work)
        self.store.new(work)
        Path(work, "ignore.txt").write_text("not a note")
        Path(work, "directory.md").mkdir()
        folders = {f.name: f.count for f in notes_store.list_folders(self.store.root)}
        self.assertEqual(folders, {"Notes": 1, "Personal": 0, "Work": 2, "Work/directory.md": 0})
        self.assertEqual(self.store.load()[0].path, root_note.path)
        self.assertEqual(len(self.store.load(work)), 2)
        self.assertEqual(self.store.load(personal), [])

    def test_unique_folder_names_and_rename_persist(self):
        first = self.store.create_folder()
        second = self.store.create_folder()
        self.assertEqual(os.path.basename(first), "New Folder")
        self.assertEqual(os.path.basename(second), "New Folder 2")
        note = self.store.new(first)
        note.text = "Title\nBody"
        self.store.save(note)
        renamed = self.store.rename_folder(first, "  Personal  ")
        self.assertFalse(os.path.exists(first))
        self.assertEqual(self.store.load(renamed)[0].text, note.text)
        with self.assertRaises(FileExistsError):
            self.store.rename_folder(renamed, "New Folder 2")
        with self.assertRaises(ValueError):
            self.store.rename_folder(self.store.root, "Renamed Notes")

    def test_invalid_names_and_paths_cannot_escape_root(self):
        for name in ("", " ", ".", "..", "../escape", "a/b", "bad\x00name"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                self.store.create_folder(name)
        with self.assertRaises(ValueError):
            self.store.new(self.temp.name)
        outside = Path(self.temp.name, "outside")
        outside.mkdir()
        link = Path(self.store.root, "link")
        link.symlink_to(outside, target_is_directory=True)
        self.assertEqual([f.name for f in self.store.list_folders()], ["Notes"])
        with self.assertRaises(ValueError):
            self.store.new(str(link))

    def test_move_preserves_text_mtime_and_does_not_overwrite(self):
        work = self.store.create_folder("Work")
        note = self.store.new()
        note.text = "Moving\n- [x] Checked"
        self.store.save(note)
        old_path, old_time = note.path, note.mtime
        collision = Path(work, os.path.basename(note.path))
        collision.write_text("Existing")
        self.assertIs(self.store.move_note(note, work), note)
        self.assertFalse(os.path.exists(old_path))
        self.assertEqual(Path(note.path).read_text(), note.text)
        self.assertEqual(os.path.getmtime(note.path), old_time)
        self.assertEqual(collision.read_text(), "Existing")
        self.assertEqual(len(self.store.load(work)), 2)
        self.assertIs(self.store.move_note(note, work), note)
        self.store.move_note(note)
        self.assertEqual(len(self.store.load()), 1)

    def test_recently_deleted_only_contains_notes_from_this_root(self):
        work = self.store.create_folder("Work")
        note = self.store.new(work)
        note.text = "Deleted\nBody"
        self.store.save(note)
        self.store.delete(note)
        other_store = notes_store.Store(os.path.join(self.temp.name, "notas-other"))
        other_store.delete(other_store.new())
        Path(self.trash, "info", "broken.trashinfo").write_text("[Trash Info]\n")
        self.assertEqual(self.store.load(work), [])
        deleted = self.store.recently_deleted()
        self.assertEqual(len(deleted), 1)
        self.assertEqual(deleted[0].text, "Deleted\nBody")
        self.assertTrue(os.path.isfile(deleted[0].path))


try:
    import gi
    gi.require_version("Gtk", "3.0")
    gi.require_version("Gdk", "3.0")
    from gi.repository import Gdk, Gtk
    HAS_DISPLAY = bool(Gdk.Display.get_default())
except ImportError:
    HAS_DISPLAY = False


@unittest.skipUnless(HAS_DISPLAY, "sem display GTK")
class NotesFoldersAppTests(unittest.TestCase):
    def setUp(self):
        NotesFoldersTests.setUp(self)
        path = Path(__file__).resolve().parents[1] / "shell" / "hyprmac-notas"
        loader = importlib.machinery.SourceFileLoader("notes_folders_app", str(path))
        spec = importlib.util.spec_from_loader(loader.name, loader)
        self.app = importlib.util.module_from_spec(spec)
        loader.exec_module(self.app)
        self.store.new()
        self.work = self.store.create_folder("Work")
        self.store.new(self.work)
        self.win = Gtk.OffscreenWindow()
        self.view = self.app.NotesView(self.store, self.win)
        self.win.add(self.view)
        self.win.show_all()
        self.addCleanup(self.win.destroy)

    def select_folder(self, name):
        row = next(r for r in self.view.folders_list.get_children() if r.label.get_text() == name)
        self.view.folders_list.select_row(row)
        return row

    def test_toggle_keeps_notes_list_visible(self):
        self.assertFalse(self.view.folders_sidebar.get_visible())
        self.view.on_toggle_list_clicked(None)
        self.assertTrue(self.view.folders_sidebar.get_visible())
        self.view.on_toggle_list_clicked(None)
        self.assertFalse(self.view.folders_sidebar.get_visible())
        self.assertTrue(self.view.notes_sidebar.get_visible())

    def test_select_create_and_switch_to_empty_folder(self):
        self.select_folder("Work")
        event = mock.Mock(state=Gdk.ModifierType.CONTROL_MASK, keyval=Gdk.KEY_n)
        self.assertTrue(self.view.on_key_press(self.view, event))
        self.assertEqual(os.path.dirname(self.view.current_note.path), self.work)
        self.assertEqual(len(self.view.notes_list.get_children()), 2)
        self.store.create_folder("Empty")
        self.view.update_folders_list()
        self.select_folder("Empty")
        self.assertIsNone(self.view.current_note)
        self.assertEqual(self.view.textview.get_buffer().get_char_count(), 0)

    def test_switch_folder_flushes_pending_edits(self):
        path = self.view.current_note.path
        self.view.textview.get_buffer().set_text("Keep this edit")
        self.select_folder("Work")
        self.assertEqual(Path(path).read_text(), "Keep this edit")
        self.assertIsNone(self.view.auto_save_id)
        self.select_folder("Notes")
        self.assertEqual(self.view.current_note.text, "Keep this edit")

    def test_inline_folder_rename_and_validation(self):
        self.view.on_toggle_list_clicked(None)
        self.view.create_new_folder()
        row = self.view.folders_list.get_selected_row()
        self.assertTrue(row.entry.get_visible())
        row.entry.set_text("../invalid")
        self.view.finish_folder_rename(row.entry, row)
        self.assertTrue(row.entry.get_visible())
        row.entry.set_text("Projects")
        self.view.finish_folder_rename(row.entry, row)
        self.assertFalse(row.entry.get_visible())
        self.assertEqual(self.view.selected_folder, os.path.join(self.store.root, "Projects"))
        self.view.create_new_note()
        self.assertEqual(os.path.dirname(self.view.current_note.path), self.view.selected_folder)

    def test_delete_pending_edit_and_read_only_trash(self):
        note_path = self.view.current_note.path
        buf = self.view.textview.get_buffer()
        buf.set_text("Unsaved\n- [ ] Item")
        self.view.delete_selected_note()
        self.assertFalse(os.path.exists(note_path))
        self.assertIsNone(self.view.auto_save_id)
        self.select_folder("Recently Deleted")
        self.assertEqual(self.view.current_note.text, "Unsaved\n- [ ] Item")
        self.assertFalse(self.view.textview.get_editable())
        self.view.toggle_checklist_on_current_line()
        self.view.create_new_note()
        self.assertTrue(self.view.textview.get_editable())
        self.assertEqual(os.path.dirname(self.view.current_note.path), self.store.root)

    def test_both_snapshot_modes_generate_png(self):
        for folders in (False, True):
            with self.subTest(folders=folders):
                path = os.path.join(self.temp.name, f"snapshot-{folders}.png")
                self.app.run_snapshot(path, folders=folders)
                self.assertEqual(Path(path).read_bytes()[:8], b"\x89PNG\r\n\x1a\n")


if __name__ == "__main__":
    unittest.main()
