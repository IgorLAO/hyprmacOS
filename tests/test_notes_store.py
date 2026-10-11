"""Tests for shell/notes_store.py (hyprmac-notas core)."""
import sys
from pathlib import Path
import tempfile
import os
import shutil
import time
import datetime
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "shell"))

import unittest
from notes_store import (
    Note,
    strip_check,
    is_check,
    is_checked,
    toggle_check,
    checklist_off,
    move_checked_to_bottom,
    set_all,
    delete_checked,
    group_label,
    list_time,
    header_date,
    Store,
)


class TestNoteProperties(unittest.TestCase):
    """Test Note.title and Note.preview properties."""

    def test_title_first_non_empty_line(self):
        note = Note("/tmp/test.md", "My Title\nSome content")
        self.assertEqual(note.title, "My Title")

    def test_title_strips_checklist_marker(self):
        note = Note("/tmp/test.md", "- [ ] Buy milk\n- [x] Walk dog")
        self.assertEqual(note.title, "Buy milk")

    def test_title_checked_item(self):
        note = Note("/tmp/test.md", "- [x] Done task\nMore text")
        self.assertEqual(note.title, "Done task")

    def test_title_empty_note_returns_new_note(self):
        note = Note("/tmp/test.md", "")
        self.assertEqual(note.title, "New Note")

    def test_title_only_whitespace_returns_new_note(self):
        note = Note("/tmp/test.md", "   \n\n  ")
        self.assertEqual(note.title, "New Note")

    def test_preview_text_after_title(self):
        note = Note("/tmp/test.md", "Title\nLine 2\nLine 3")
        self.assertEqual(note.preview, "Line 2 Line 3")

    def test_preview_empty_note_returns_no_additional_text(self):
        note = Note("/tmp/test.md", "")
        self.assertEqual(note.preview, "No additional text")

    def test_preview_only_title_returns_no_additional_text(self):
        note = Note("/tmp/test.md", "Just a title")
        self.assertEqual(note.preview, "No additional text")

    def test_preview_strips_checklist_markers(self):
        note = Note("/tmp/test.md", "- [ ] First\n- [x] Second\n- [ ] Third")
        self.assertEqual(note.preview, "Second Third")

    def test_preview_multiple_spaces_collapsed(self):
        note = Note("/tmp/test.md", "Title\n  Line 2  \n   Line 3  ")
        self.assertEqual(note.preview, "Line 2 Line 3")


class TestStripCheck(unittest.TestCase):
    """Test strip_check helper."""

    def test_strip_unchecked(self):
        self.assertEqual(strip_check("- [ ] Task"), "Task")

    def test_strip_checked_lowercase(self):
        self.assertEqual(strip_check("- [x] Task"), "Task")

    def test_strip_checked_uppercase(self):
        self.assertEqual(strip_check("- [X] Task"), "Task")

    def test_strip_with_indent(self):
        self.assertEqual(strip_check("  - [ ] Indented"), "Indented")

    def test_strip_non_checklist_line(self):
        self.assertEqual(strip_check("Regular line"), "Regular line")

    def test_strip_empty_line(self):
        self.assertEqual(strip_check(""), "")


class TestIsCheck(unittest.TestCase):
    """Test is_check helper."""

    def test_unchecked(self):
        self.assertTrue(is_check("- [ ] Task"))

    def test_checked_lowercase(self):
        self.assertTrue(is_check("- [x] Task"))

    def test_checked_uppercase(self):
        self.assertTrue(is_check("- [X] Task"))

    def test_with_indent(self):
        self.assertTrue(is_check("  - [ ] Task"))

    def test_non_checklist(self):
        self.assertFalse(is_check("Regular line"))

    def test_empty(self):
        self.assertFalse(is_check(""))


class TestIsChecked(unittest.TestCase):
    """Test is_checked helper."""

    def test_unchecked_false(self):
        self.assertFalse(is_checked("- [ ] Task"))

    def test_checked_lowercase_true(self):
        self.assertTrue(is_checked("- [x] Task"))

    def test_checked_uppercase_true(self):
        self.assertTrue(is_checked("- [X] Task"))

    def test_non_checklist_false(self):
        self.assertFalse(is_checked("Regular line"))


class TestToggleCheck(unittest.TestCase):
    """Test toggle_check function."""

    def test_toggle_unchecked_to_checked(self):
        self.assertEqual(toggle_check("- [ ] Task"), "- [x] Task")

    def test_toggle_checked_to_unchecked(self):
        self.assertEqual(toggle_check("- [x] Task"), "- [ ] Task")

    def test_toggle_uppercase_checked_to_unchecked(self):
        self.assertEqual(toggle_check("- [X] Task"), "- [ ] Task")

    def test_toggle_preserves_indent(self):
        self.assertEqual(toggle_check("  - [ ] Task"), "  - [x] Task")

    def test_toggle_regular_line_becomes_unchecked(self):
        self.assertEqual(toggle_check("Regular line"), "- [ ] Regular line")

    def test_toggle_empty_line(self):
        self.assertEqual(toggle_check(""), "- [ ] ")


class TestChecklistOff(unittest.TestCase):
    """Test checklist_off function."""

    def test_remove_unchecked(self):
        self.assertEqual(checklist_off("- [ ] Task"), "Task")

    def test_remove_checked(self):
        self.assertEqual(checklist_off("- [x] Task"), "Task")

    def test_preserves_indent(self):
        self.assertEqual(checklist_off("  - [ ] Task"), "  Task")

    def test_non_checklist_unchanged(self):
        self.assertEqual(checklist_off("Regular line"), "Regular line")


class TestMoveCheckedToBottom(unittest.TestCase):
    """Test move_checked_to_bottom function (by contiguous block)."""

    def test_single_block_moves_checked_to_bottom(self):
        text = "- [ ] A\n- [x] B\n- [ ] C"
        result = move_checked_to_bottom(text)
        self.assertEqual(result, "- [ ] A\n- [ ] C\n- [x] B")

    def test_multiple_blocks_handled_separately(self):
        text = "- [ ] A\n- [x] B\n\n- [ ] C\n- [x] D"
        result = move_checked_to_bottom(text)
        # First block: A, B -> A, B (B checked goes to bottom of block)
        # Second block: C, D -> C, D (D checked goes to bottom of block)
        self.assertEqual(result, "- [ ] A\n- [x] B\n\n- [ ] C\n- [x] D")

    def test_non_checklist_lines_break_blocks(self):
        text = "- [ ] A\n- [x] B\nSome text\n- [ ] C\n- [x] D"
        result = move_checked_to_bottom(text)
        self.assertEqual(result, "- [ ] A\n- [x] B\nSome text\n- [ ] C\n- [x] D")

    def test_all_unchecked_unchanged(self):
        text = "- [ ] A\n- [ ] B\n- [ ] C"
        result = move_checked_to_bottom(text)
        self.assertEqual(result, text)

    def test_all_checked_unchanged_order(self):
        text = "- [x] A\n- [x] B\n- [x] C"
        result = move_checked_to_bottom(text)
        self.assertEqual(result, text)

    def test_empty_text(self):
        self.assertEqual(move_checked_to_bottom(""), "")

    def test_no_checklist_items(self):
        text = "Line 1\nLine 2\nLine 3"
        self.assertEqual(move_checked_to_bottom(text), text)


class TestSetAll(unittest.TestCase):
    """Test set_all function (Check All / Uncheck All)."""

    def test_set_all_checked(self):
        text = "- [ ] A\n- [ ] B\n- [x] C"
        result = set_all(text, True)
        self.assertEqual(result, "- [x] A\n- [x] B\n- [x] C")

    def test_set_all_unchecked(self):
        text = "- [x] A\n- [x] B\n- [ ] C"
        result = set_all(text, False)
        self.assertEqual(result, "- [ ] A\n- [ ] B\n- [ ] C")

    def test_preserves_indent(self):
        text = "  - [ ] A\n  - [x] B"
        result = set_all(text, True)
        self.assertEqual(result, "  - [x] A\n  - [x] B")

    def test_non_checklist_lines_unchanged(self):
        text = "- [ ] A\nRegular line\n- [x] B"
        result = set_all(text, True)
        self.assertEqual(result, "- [x] A\nRegular line\n- [x] B")

    def test_empty_text(self):
        self.assertEqual(set_all("", True), "")


class TestDeleteChecked(unittest.TestCase):
    """Test delete_checked function."""

    def test_removes_checked_items(self):
        text = "- [ ] A\n- [x] B\n- [ ] C"
        result = delete_checked(text)
        self.assertEqual(result, "- [ ] A\n- [ ] C")

    def test_keeps_unchecked(self):
        text = "- [ ] A\n- [ ] B"
        result = delete_checked(text)
        self.assertEqual(result, text)

    def test_removes_all_checked(self):
        text = "- [x] A\n- [X] B"
        result = delete_checked(text)
        self.assertEqual(result, "")

    def test_non_checklist_unchanged(self):
        text = "- [x] A\nRegular line\n- [ ] B"
        result = delete_checked(text)
        self.assertEqual(result, "Regular line\n- [ ] B")

    def test_empty_text(self):
        self.assertEqual(delete_checked(""), "")


class TestGroupLabel(unittest.TestCase):
    """Test group_label function with fixed 'now'."""

    def setUp(self):
        # Fixed reference time: 2025-10-15 (Wednesday)
        self.now = datetime.datetime(2025, 10, 15, 12, 0, 0)

    def test_today(self):
        # Same day
        mtime = datetime.datetime(2025, 10, 15, 10, 0, 0).timestamp()
        self.assertEqual(group_label(mtime, self.now), "Today")

    def test_yesterday(self):
        mtime = datetime.datetime(2025, 10, 14, 10, 0, 0).timestamp()
        self.assertEqual(group_label(mtime, self.now), "Yesterday")

    def test_previous_7_days(self):
        # 2 to 7 days ago
        for days in range(2, 8):
            mtime = datetime.datetime(2025, 10, 15 - days, 10, 0, 0).timestamp()
            self.assertEqual(group_label(mtime, self.now), "Previous 7 Days")

    def test_previous_30_days(self):
        # 8 to 30 days ago
        for days in range(8, 31):
            dt = self.now - datetime.timedelta(days=days)
            mtime = dt.timestamp()
            self.assertEqual(group_label(mtime, self.now), "Previous 30 Days")

    def test_current_year_month(self):
        # September 1, 2025 (same year as now, more than 30 days ago)
        mtime = datetime.datetime(2025, 9, 1, 10, 0, 0).timestamp()
        self.assertEqual(group_label(mtime, self.now), "September")

    def test_previous_year(self):
        # October 2024 (previous year)
        mtime = datetime.datetime(2024, 10, 1, 10, 0, 0).timestamp()
        self.assertEqual(group_label(mtime, self.now), "2024")

    def test_future_date_returns_today(self):
        # Future date (days <= 0)
        mtime = datetime.datetime(2025, 10, 16, 10, 0, 0).timestamp()
        self.assertEqual(group_label(mtime, self.now), "Today")


class TestListTime(unittest.TestCase):
    """Test list_time function (24h and 12h)."""

    def setUp(self):
        self.now = datetime.datetime(2025, 10, 15, 12, 0, 0)

    def test_today_24h(self):
        mtime = datetime.datetime(2025, 10, 15, 17, 30, 0).timestamp()
        self.assertEqual(list_time(mtime, self.now, h24=True), "17:30")

    def test_today_12h_am(self):
        mtime = datetime.datetime(2025, 10, 15, 9, 5, 0).timestamp()
        self.assertEqual(list_time(mtime, self.now, h24=False), "9:05 AM")

    def test_today_12h_pm(self):
        mtime = datetime.datetime(2025, 10, 15, 17, 30, 0).timestamp()
        self.assertEqual(list_time(mtime, self.now, h24=False), "5:30 PM")

    def test_today_12h_midnight(self):
        mtime = datetime.datetime(2025, 10, 15, 0, 0, 0).timestamp()
        self.assertEqual(list_time(mtime, self.now, h24=False), "12:00 AM")

    def test_today_12h_noon(self):
        mtime = datetime.datetime(2025, 10, 15, 12, 0, 0).timestamp()
        self.assertEqual(list_time(mtime, self.now, h24=False), "12:00 PM")

    def test_yesterday(self):
        mtime = datetime.datetime(2025, 10, 14, 17, 30, 0).timestamp()
        self.assertEqual(list_time(mtime, self.now, h24=True), "Yesterday")
        self.assertEqual(list_time(mtime, self.now, h24=False), "Yesterday")

    def test_older_date_format(self):
        mtime = datetime.datetime(2025, 9, 1, 17, 30, 0).timestamp()
        self.assertEqual(list_time(mtime, self.now, h24=True), "9/1/25")
        self.assertEqual(list_time(mtime, self.now, h24=False), "9/1/25")

    def test_year_rollover(self):
        mtime = datetime.datetime(2024, 12, 31, 17, 30, 0).timestamp()
        self.assertEqual(list_time(mtime, self.now, h24=True), "12/31/24")


class TestHeaderDate(unittest.TestCase):
    """Test header_date function (24h and 12h)."""

    def test_24h_format(self):
        mtime = datetime.datetime(2025, 10, 22, 17, 43, 0).timestamp()
        self.assertEqual(header_date(mtime, h24=True), "October 22, 2025 at 17:43")

    def test_12h_format_am(self):
        mtime = datetime.datetime(2025, 10, 22, 9, 5, 0).timestamp()
        self.assertEqual(header_date(mtime, h24=False), "October 22, 2025 at 9:05 AM")

    def test_12h_format_pm(self):
        mtime = datetime.datetime(2025, 10, 22, 17, 43, 0).timestamp()
        self.assertEqual(header_date(mtime, h24=False), "October 22, 2025 at 5:43 PM")

    def test_12h_midnight(self):
        mtime = datetime.datetime(2025, 10, 22, 0, 0, 0).timestamp()
        self.assertEqual(header_date(mtime, h24=False), "October 22, 2025 at 12:00 AM")

    def test_12h_noon(self):
        mtime = datetime.datetime(2025, 10, 22, 12, 0, 0).timestamp()
        self.assertEqual(header_date(mtime, h24=False), "October 22, 2025 at 12:00 PM")


class TestStore(unittest.TestCase):
    """Test Store class with temporary directories."""

    def setUp(self):
        # Create temporary directories for notes and trash
        self.temp_dir = tempfile.mkdtemp()
        self.notes_dir = os.path.join(self.temp_dir, "notas")
        self.trash_dir = os.path.join(self.temp_dir, "Trash")
        self.trash_files = os.path.join(self.trash_dir, "files")
        self.trash_info = os.path.join(self.trash_dir, "info")
        os.makedirs(self.notes_dir, exist_ok=True)
        os.makedirs(self.trash_files, exist_ok=True)
        os.makedirs(self.trash_info, exist_ok=True)

        # Patch os.path.expanduser to return our temp trash dir
        self.expanduser_patcher = mock.patch("notes_store.os.path.expanduser")
        self.mock_expanduser = self.expanduser_patcher.start()
        self.mock_expanduser.side_effect = lambda path: path.replace("~/.local/share/Trash", self.trash_dir).replace("~/.local/share/hyprmac/notas", self.notes_dir)

        self.store = Store(root=self.notes_dir)

    def tearDown(self):
        self.expanduser_patcher.stop()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_new_creates_note_with_timestamp_filename(self):
        note = self.store.new()
        self.assertTrue(note.path.endswith(".md"))
        self.assertTrue(os.path.exists(note.path))
        self.assertEqual(note.text, "")
        self.assertEqual(note.title, "New Note")

    def test_new_creates_unique_filenames(self):
        note1 = self.store.new()
        time.sleep(0.01)  # Ensure different timestamp
        note2 = self.store.new()
        self.assertNotEqual(note1.path, note2.path)

    def test_save_writes_text_and_updates_mtime(self):
        note = self.store.new()
        note.text = "Test content\n- [ ] Item"
        old_mtime = note.mtime
        time.sleep(0.01)
        self.store.save(note)
        self.assertGreater(note.mtime, old_mtime)
        with open(note.path, encoding="utf-8") as f:
            self.assertEqual(f.read(), "Test content\n- [ ] Item")

    def test_load_returns_notes_sorted_by_mtime_desc(self):
        # Create notes with different mtimes
        note1 = self.store.new()
        note1.text = "Note 1"
        self.store.save(note1)
        time.sleep(0.01)

        note2 = self.store.new()
        note2.text = "Note 2"
        self.store.save(note2)
        time.sleep(0.01)

        note3 = self.store.new()
        note3.text = "Note 3"
        self.store.save(note3)

        notes = self.store.load()
        self.assertEqual(len(notes), 3)
        # Should be sorted by mtime desc (newest first)
        self.assertEqual(notes[0].text, "Note 3")
        self.assertEqual(notes[1].text, "Note 2")
        self.assertEqual(notes[2].text, "Note 1")

    def test_load_ignores_non_md_files(self):
        # Create a non-md file
        with open(os.path.join(self.notes_dir, "readme.txt"), "w") as f:
            f.write("not a note")
        note = self.store.new()
        note.text = "Valid note"
        self.store.save(note)

        notes = self.store.load()
        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0].text, "Valid note")

    def test_delete_moves_to_trash_files_with_trashinfo(self):
        note = self.store.new()
        note.text = "To be deleted"
        self.store.save(note)
        original_path = note.path

        self.store.delete(note)

        # Original file should be gone
        self.assertFalse(os.path.exists(original_path))

        # Should be in trash/files
        trash_files = os.listdir(self.trash_files)
        self.assertEqual(len(trash_files), 1)
        trash_file = trash_files[0]
        trash_path = os.path.join(self.trash_files, trash_file)
        with open(trash_path, encoding="utf-8") as f:
            self.assertEqual(f.read(), "To be deleted")

        # Should have .trashinfo in trash/info
        trash_info_files = os.listdir(self.trash_info)
        self.assertEqual(len(trash_info_files), 1)
        info_file = trash_info_files[0]
        self.assertTrue(info_file.endswith(".trashinfo"))
        info_path = os.path.join(self.trash_info, info_file)
        with open(info_path, encoding="utf-8") as f:
            content = f.read()
            self.assertIn("[Trash Info]", content)
            self.assertIn(f"Path={original_path}", content)
            self.assertIn("DeletionDate=", content)

    def test_delete_handles_duplicate_names_in_trash(self):
        # Create first note and delete it
        note1 = self.store.new()
        note1.text = "Note 1"
        self.store.save(note1)
        base_name = os.path.basename(note1.path)
        self.store.delete(note1)

        # Create second note with same basename (simulate collision)
        note2_path = os.path.join(self.notes_dir, base_name)
        with open(note2_path, "w") as f:
            f.write("Note 2")
        note2 = Note(note2_path, "Note 2", os.path.getmtime(note2_path))

        self.store.delete(note2)

        trash_files = os.listdir(self.trash_files)
        self.assertEqual(len(trash_files), 2)
        # One file should be renamed with prefix
        self.assertTrue(any(f.startswith("2-") and f.endswith(base_name) for f in trash_files))
        trash_info_files = os.listdir(self.trash_info)
        self.assertEqual(len(trash_info_files), 2)

    def test_matches_empty_query_returns_true(self):
        note = Note("/tmp/test.md", "Some content")
        self.assertTrue(Store.matches(note, ""))
        self.assertTrue(Store.matches(note, "   "))

    def test_matches_case_insensitive(self):
        note = Note("/tmp/test.md", "Hello World")
        self.assertTrue(Store.matches(note, "hello"))
        self.assertTrue(Store.matches(note, "WORLD"))
        self.assertTrue(Store.matches(note, "Hello World"))

    def test_matches_partial(self):
        note = Note("/tmp/test.md", "The quick brown fox")
        self.assertTrue(Store.matches(note, "quick"))
        self.assertTrue(Store.matches(note, "brown fox"))

    def test_matches_no_match(self):
        note = Note("/tmp/test.md", "Hello World")
        self.assertFalse(Store.matches(note, "goodbye"))
        self.assertFalse(Store.matches(note, "xyz"))


class TestStoreIntegration(unittest.TestCase):
    """Integration tests for Store with realistic scenarios."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.notes_dir = os.path.join(self.temp_dir, "notas")
        self.trash_dir = os.path.join(self.temp_dir, "Trash")
        os.makedirs(self.notes_dir, exist_ok=True)
        os.makedirs(os.path.join(self.trash_dir, "files"), exist_ok=True)
        os.makedirs(os.path.join(self.trash_dir, "info"), exist_ok=True)

        self.expanduser_patcher = mock.patch("notes_store.os.path.expanduser")
        self.mock_expanduser = self.expanduser_patcher.start()
        self.mock_expanduser.side_effect = lambda path: path.replace("~/.local/share/Trash", self.trash_dir).replace("~/.local/share/hyprmac/notas", self.notes_dir)

        self.store = Store(root=self.notes_dir)

    def tearDown(self):
        self.expanduser_patcher.stop()
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_full_workflow_create_edit_delete(self):
        # Create
        note = self.store.new()
        self.assertEqual(note.title, "New Note")

        # Edit
        note.text = "Shopping List\n- [ ] Milk\n- [x] Bread\n- [ ] Eggs"
        self.store.save(note)

        # Verify title and preview
        self.assertEqual(note.title, "Shopping List")
        self.assertEqual(note.preview, "Milk Bread Eggs")

        # Load and verify persistence
        notes = self.store.load()
        self.assertEqual(len(notes), 1)
        loaded = notes[0]
        self.assertEqual(loaded.text, note.text)
        self.assertEqual(loaded.title, "Shopping List")

        # Delete
        self.store.delete(loaded)
        notes = self.store.load()
        self.assertEqual(len(notes), 0)

        # Verify trash
        trash_files = os.listdir(os.path.join(self.trash_dir, "files"))
        self.assertEqual(len(trash_files), 1)

    def test_multiple_notes_sorted_by_edit_time(self):
        # Create 3 notes
        notes = []
        for i in range(3):
            n = self.store.new()
            n.text = f"Note {i}"
            self.store.save(n)
            notes.append(n)
            time.sleep(0.01)

        # Edit note 0 (oldest) to make it newest
        notes[0].text = "Note 0 updated"
        self.store.save(notes[0])

        # Load should have note 0 first
        loaded = self.store.load()
        self.assertEqual(loaded[0].text, "Note 0 updated")
        self.assertEqual(loaded[1].text, "Note 2")
        self.assertEqual(loaded[2].text, "Note 1")


if __name__ == "__main__":
    unittest.main()