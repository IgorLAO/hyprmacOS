"""Local reminders for HyprMac, with no Apple account or sync service."""

import json
import os
from pathlib import Path
import tempfile
from uuid import uuid4

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

import sys
from pathlib import Path
TAHOE_CONTROLS_PATH = Path(__file__).parent.parent / "tahoe" / "controls"
sys.path.insert(0, str(TAHOE_CONTROLS_PATH))
from button import TahoeButton



DEFAULT_PATH = Path.home() / ".config/hyprmac/app-factory/reminders.json"


class ReminderStore:
    def __init__(self, path=DEFAULT_PATH):
        self.path = Path(path)
        self.items = self._load()

    def _load(self):
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return []
        if not isinstance(raw, list):
            return []
        items = []
        seen = set()
        for entry in raw:
            if not isinstance(entry, dict):
                continue
            identifier, title = entry.get("id"), entry.get("title")
            if (not isinstance(identifier, str) or not identifier or identifier in seen
                    or not isinstance(title, str) or not title.strip()):
                continue
            seen.add(identifier)
            items.append({"id": identifier, "title": title[:500],
                          "completed": entry.get("completed") is True})
        return items

    def _save(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = None
        try:
            with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=self.path.parent,
                                             prefix=".reminders-", suffix=".tmp",
                                             delete=False) as output:
                temporary = Path(output.name)
                os.chmod(output.name, 0o600)
                json.dump(self.items, output, ensure_ascii=False, indent=2)
                output.write("\n")
                output.flush()
                os.fsync(output.fileno())
            os.replace(temporary, self.path)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)

    def add(self, title):
        title = title.strip()
        if not title:
            return None
        entry = {"id": uuid4().hex, "title": title[:500], "completed": False}
        self.items.append(entry)
        self._save()
        return entry["id"]

    def complete(self, identifier, completed):
        for entry in self.items:
            if entry["id"] == identifier:
                entry["completed"] = bool(completed)
                self._save()
                return True
        return False

    def delete(self, identifier):
        retained = [entry for entry in self.items if entry["id"] != identifier]
        if len(retained) == len(self.items):
            return False
        self.items = retained
        self._save()
        return True


class RemindersPanel(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.store = ReminderStore()
        intro = Gtk.Label(label="Reminders saved on this computer")
        intro.set_halign(Gtk.Align.START)
        intro.get_style_context().add_class("dim-label")
        self.pack_start(intro, False, False, 0)

        entry_row = Gtk.Box(spacing=8)
        self.entry = Gtk.Entry()
        self.entry.set_placeholder_text("New reminder")
        self.entry.connect("activate", self._add)
        entry_row.pack_start(self.entry, True, True, 0)
        add = TahoeButton(label="Add")
        add.connect("clicked", self._add)
        entry_row.pack_start(add, False, False, 0)
        self.pack_start(entry_row, False, False, 0)

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.pack_start(scroll, True, True, 0)
        self.listbox = Gtk.ListBox()
        self.listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        scroll.add(self.listbox)
        self._refresh()

    def _add(self, *_args):
        if self.store.add(self.entry.get_text()) is not None:
            self.entry.set_text("")
            self._refresh()

    def _complete(self, button, identifier):
        self.store.complete(identifier, button.get_active())
        self._refresh()

    def _delete(self, _button, identifier):
        self.store.delete(identifier)
        self._refresh()

    def _refresh(self):
        for child in self.listbox.get_children():
            child.destroy()
        for item in sorted(self.store.items, key=lambda entry: entry["completed"]):
            row = Gtk.Box(spacing=10)
            row.set_border_width(6)
            from tahoe.controls.button import TahoeCheckButton
            check = TahoeCheckButton()
            check.set_active(item["completed"])
            check.connect("toggled", self._complete, item["id"])
            row.pack_start(check, False, False, 0)
            label = Gtk.Label(label=item["title"])
            label.set_halign(Gtk.Align.START)
            label.set_line_wrap(True)
            label.set_max_width_chars(60)
            if item["completed"]:
                label.get_style_context().add_class("dim-label")
            row.pack_start(label, True, True, 0)
            remove = TahoeButton(label="Remove")
            remove.set_tooltip_text("Delete reminder")
            remove.connect("clicked", self._delete, item["id"])
            row.pack_end(remove, False, False, 0)
            self.listbox.add(row)
        self.listbox.show_all()
