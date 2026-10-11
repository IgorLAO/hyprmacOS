"""Journal: lógica e callbacks sem criar janelas GTK."""
import datetime
import importlib.machinery
import importlib.util
import os
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch


ROOT = Path(__file__).resolve().parents[1]
loader = importlib.machinery.SourceFileLoader(
    "journal_features", str(ROOT / "shell" / "hyprmac-diario"))
spec = importlib.util.spec_from_loader("journal_features", loader)
journal = importlib.util.module_from_spec(spec)
loader.exec_module(journal)


class JournalFeaturesTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = self.tmp.name

    def entry(self, day, title="Title", text="Body"):
        path = journal.save_entry(title, text, root=self.root)
        stamp = datetime.datetime.combine(day, datetime.time(12)).timestamp()
        os.utime(path, (stamp, stamp))
        return next(e for e in journal.load_entries(self.root) if e.path == path)

    def view(self, entry=None):
        buffer = journal.Gtk.TextBuffer()
        buffer.create_tag("titulo", weight=journal.Pango.Weight.BOLD,
                          size=20 * journal.Pango.SCALE)
        buffer.connect("changed", lambda b: journal.JournalView.on_buffer_changed(None, b))
        view = SimpleNamespace(
            root_dir=self.root, current_entry=entry, window=None,
            textview=Mock(), content_stack=Mock(), header_right_stack=Mock(),
            load_and_refresh=Mock())
        view.textview.get_buffer.return_value = buffer
        return view, buffer

    def test_streak_counts_days_once_and_stops_at_gap(self):
        today = datetime.date(2026, 10, 11)
        entries = [self.entry(today), self.entry(today),
                   self.entry(today - datetime.timedelta(days=1)),
                   self.entry(today - datetime.timedelta(days=3)),
                   self.entry(today + datetime.timedelta(days=1))]
        self.assertEqual(journal.entry_streak(entries, today), 2)

    def test_streak_requires_today(self):
        today = datetime.date(2026, 10, 11)
        self.assertEqual(journal.entry_streak([], today), 0)
        self.assertEqual(journal.entry_streak([self.entry(today)], today), 1)
        yesterday = self.entry(today - datetime.timedelta(days=1))
        self.assertEqual(journal.entry_streak([yesterday], today), 0)

    def test_streak_crosses_month_and_year(self):
        today = datetime.date(2027, 1, 1)
        entries = [self.entry(today - datetime.timedelta(days=i)) for i in range(3)]
        self.assertEqual(journal.entry_streak(entries, today), 3)

    def test_insights_draws_streak_only_from_two_days(self):
        widget = Mock()
        widget.get_allocated_width.return_value = 216
        widget.get_allocated_height.return_value = 136
        for streak in (0, 1, 2, 5):
            with self.subTest(streak=streak):
                cr = Mock()
                journal.InsightsCard.on_draw(SimpleNamespace(count=7, streak=streak), widget, cr)
                labels = [call.args[0] for call in cr.show_text.call_args_list]
                self.assertEqual(labels[:4], ["Insights", "7", "Entries", "This Year"])
                self.assertEqual(labels[4:], [f"{streak}-day streak"] if streak >= 2 else [])

    def test_month_groups_sorted_with_english_labels_and_years(self):
        older = self.entry(datetime.date(2025, 10, 12))
        september = self.entry(datetime.date(2026, 9, 30))
        first = self.entry(datetime.date(2026, 10, 1))
        last = self.entry(datetime.date(2026, 10, 11))
        groups = journal.group_entries_by_month([older, first, september, last])
        self.assertEqual([label for label, _ in groups],
                         ["October 2026", "September 2026", "October 2025"])
        self.assertEqual(groups[0][1], [last, first])
        self.assertEqual(journal.group_entries_by_month([]), [])

    def test_search_matches_title_or_body_case_insensitively(self):
        day = datetime.date(2026, 10, 11)
        title = self.entry(day, "Trip to TOKYO", "Ramen")
        body = self.entry(day, "Holiday", "Exploring Tokyo")
        other = self.entry(day, "Home", "Reading")
        entries = [title, body, other]
        self.assertEqual(journal.filter_entries(entries, "tOkYo"), [title, body])
        self.assertEqual(journal.filter_entries(entries, "RAMEN"), [title])
        self.assertEqual(journal.filter_entries(entries, "missing"), [])
        self.assertEqual(journal.filter_entries(entries, ""), entries)
        self.assertEqual(len(journal.group_entries_by_month(
            journal.filter_entries(entries, "TOKYO"))[0][1]), 2)

    def test_open_edit_done_saves_same_entry_and_formats_first_line(self):
        entry = self.entry(datetime.date(2026, 10, 11), "Original", "Body\nLast line")
        view, buffer = self.view()
        row = Mock(spec=journal.EntryRow)
        row.entry = entry
        journal.JournalView.on_entry_activated(view, None, row)
        self.assertIs(view.current_entry, entry)
        self.assertEqual(buffer.get_text(*buffer.get_bounds(), False),
                         "Original\nBody\nLast line")
        view.content_stack.set_visible_child_name.assert_called_with("edit")
        view.header_right_stack.set_visible_child_name.assert_called_with("edit")
        tag = buffer.get_tag_table().lookup("titulo")
        self.assertEqual(tag.get_property("size"), 20 * journal.Pango.SCALE)
        self.assertEqual(tag.get_property("weight"), journal.Pango.Weight.BOLD)
        self.assertTrue(buffer.get_start_iter().has_tag(tag))
        self.assertFalse(buffer.get_iter_at_offset(9).has_tag(tag))
        buffer.set_text("Updated\nNew body")
        journal.JournalView.on_done_clicked(view)
        entries = journal.load_entries(self.root)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].path, entry.path)
        self.assertEqual((entries[0].title, entries[0].text), ("Updated", "New body"))
        view.load_and_refresh.assert_called_once()
        self.assertIsNone(view.current_entry)

    def test_done_can_clear_existing_entry_but_skips_empty_new_entry(self):
        entry = self.entry(datetime.date(2026, 10, 11))
        view, buffer = self.view(entry)
        journal.JournalView.on_done_clicked(view)
        self.assertEqual(Path(entry.path).read_text(), "\n")
        journal.JournalView.on_done_clicked(view)
        self.assertEqual(len(journal.load_entries(self.root)), 1)

    def test_new_entries_in_same_second_do_not_overwrite(self):
        with patch.object(journal.time, "time", return_value=123):
            first = journal.save_entry("First", "One", root=self.root)
            second = journal.save_entry("Second", "Two", root=self.root)
        self.assertNotEqual(first, second)
        self.assertEqual(len(journal.load_entries(self.root)), 2)

    def test_delete_cancel_keeps_entry_and_accept_uses_system_trash(self):
        entry = self.entry(datetime.date(2026, 10, 11))
        view, _ = self.view(entry)
        with patch.object(journal.Gtk, "MessageDialog") as dialog_class, \
                patch.object(journal.Gio.File, "new_for_path") as new_file:
            dialog = dialog_class.return_value
            dialog.run.return_value = journal.Gtk.ResponseType.CANCEL
            journal.JournalView.on_delete_entry(view, entry)
            new_file.assert_not_called()
            view.load_and_refresh.assert_not_called()
            self.assertTrue(Path(entry.path).exists())
            dialog_class.assert_called_with(
                transient_for=None, modal=True,
                message_type=journal.Gtk.MessageType.QUESTION,
                buttons=journal.Gtk.ButtonsType.NONE, text="Delete this entry?")
            dialog.add_buttons.assert_called_with(
                "Cancel", journal.Gtk.ResponseType.CANCEL,
                "Delete", journal.Gtk.ResponseType.ACCEPT)
            dialog.run.return_value = journal.Gtk.ResponseType.ACCEPT
            journal.JournalView.on_delete_entry(view, entry)
            new_file.assert_called_once_with(entry.path)
            new_file.return_value.trash.assert_called_once_with(None)
            view.load_and_refresh.assert_called_once()
            self.assertIsNone(view.current_entry)

    def test_right_click_menu_deletes_clicked_entry(self):
        entry = self.entry(datetime.date(2026, 10, 11))
        view = SimpleNamespace(on_delete_entry=Mock())
        row = SimpleNamespace(entry=entry)
        with patch.object(journal.Gtk, "Menu") as menu, \
                patch.object(journal.Gtk, "MenuItem") as item:
            self.assertFalse(journal.JournalView.on_entry_button_press(
                view, row, SimpleNamespace(button=1)))
            menu.assert_not_called()
            event = SimpleNamespace(button=3)
            self.assertTrue(journal.JournalView.on_entry_button_press(view, row, event))
            item.assert_called_once_with(label="Delete Entry")
            menu.return_value.popup_at_pointer.assert_called_once_with(event)
            signal, callback = item.return_value.connect.call_args.args
            self.assertEqual(signal, "activate")
            callback(None)
            view.on_delete_entry.assert_called_once_with(entry)

    def test_trash_failure_keeps_entry_and_reports_error(self):
        entry = self.entry(datetime.date(2026, 10, 11))
        view, _ = self.view(entry)
        with patch.object(journal.Gtk, "MessageDialog") as dialog_class, \
                patch.object(journal.Gio.File, "new_for_path") as new_file:
            dialog_class.return_value.run.return_value = journal.Gtk.ResponseType.ACCEPT
            error = journal.GLib.Error("Trash unavailable")
            new_file.return_value.trash.side_effect = error
            journal.JournalView.on_delete_entry(view, entry)
            view.load_and_refresh.assert_not_called()
            self.assertIs(view.current_entry, entry)
            self.assertTrue(Path(entry.path).exists())
            dialog_class.return_value.format_secondary_text.assert_called_with(str(error))


if __name__ == "__main__":
    unittest.main()
