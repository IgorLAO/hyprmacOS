"""Local calendar pilot, with events saved in the user's HyprMac config."""

import datetime as dt
import json
import os
import tempfile
import uuid
from pathlib import Path

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Pango

import sys
from pathlib import Path
TAHOE_CONTROLS_PATH = Path(__file__).parent.parent / "tahoe" / "controls"
sys.path.insert(0, str(TAHOE_CONTROLS_PATH))
from button import TahoeButton



DEFAULT_PATH = Path.home() / ".config/hyprmac/app-factory/calendar.json"


class CalendarStore:
    def __init__(self, path=DEFAULT_PATH):
        self.path = Path(path)
        try:
            raw = json.loads(self.path.read_text(encoding="utf-8"))
            self.events = raw if isinstance(raw, dict) else {}
        except (OSError, ValueError, TypeError):
            self.events = {}

    def for_day(self, date):
        day = self.events.get(date, [])
        if not isinstance(day, list):
            return []
        return sorted((item for item in day if isinstance(item, dict)
                       and isinstance(item.get("id"), str)
                       and isinstance(item.get("title"), str)),
                      key=lambda item: (item.get("time", ""), item["title"].casefold()))

    def save_event(self, date, title, time="", event_id=None):
        dt.date.fromisoformat(date)
        title = title.strip()
        if not title:
            raise ValueError("Event title is required")
        time = time.strip()
        if time:
            if len(time) != 5 or time[2] != ":":
                raise ValueError("Time must use HH:MM")
            hour, minute = time[:2], time[3:]
            if not hour.isdigit() or not minute.isdigit() or int(hour) > 23 or int(minute) > 59:
                raise ValueError("Time must use HH:MM")
        entries = self.events.setdefault(date, [])
        if event_id is not None:
            for item in entries:
                if isinstance(item, dict) and item.get("id") == event_id:
                    item.update(title=title, time=time)
                    self._write()
                    return event_id
            raise ValueError("Event no longer exists")
        event_id = uuid.uuid4().hex
        entries.append({"id": event_id, "title": title, "time": time})
        self._write()
        return event_id

    def remove_event(self, date, event_id):
        entries = self.events.get(date, [])
        if not isinstance(entries, list):
            return False
        remaining = [item for item in entries
                     if not isinstance(item, dict) or item.get("id") != event_id]
        if len(remaining) == len(entries):
            return False
        if remaining:
            self.events[date] = remaining
        else:
            self.events.pop(date, None)
        self._write()
        return True

    def _write(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        temporary = None
        try:
            with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=self.path.parent,
                                             prefix=".calendar-", delete=False) as stream:
                temporary = stream.name
                json.dump(self.events, stream, ensure_ascii=False, indent=2, sort_keys=True)
                stream.write("\n")
            os.replace(temporary, self.path)
        finally:
            if temporary and os.path.exists(temporary):
                os.unlink(temporary)


class CalendarPanel(Gtk.Box):
    """Calendar and selected day's events; all data stays in the local JSON file."""

    def __init__(self, store_path=DEFAULT_PATH):
        super().__init__(orientation=Gtk.Orientation.HORIZONTAL, spacing=20)
        self.store = CalendarStore(store_path)
        self.editing_id = None

        self.calendar = Gtk.Calendar()
        self.calendar.connect("day-selected", self._date_changed)
        self.calendar.connect("month-changed", self._date_changed)
        self.pack_start(self.calendar, False, False, 0)

        right = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.pack_start(right, True, True, 0)
        self.day_label = Gtk.Label()
        self.day_label.set_halign(Gtk.Align.START)
        self.day_label.get_style_context().add_class("title")
        right.pack_start(self.day_label, False, False, 0)

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.event_list = Gtk.ListBox()
        self.event_list.set_selection_mode(Gtk.SelectionMode.NONE)
        scroll.add(self.event_list)
        right.pack_start(scroll, True, True, 0)

        form = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.time_entry = Gtk.Entry()
        self.time_entry.set_placeholder_text("HH:MM")
        self.time_entry.set_width_chars(5)
        self.time_entry.set_max_length(5)
        form.pack_start(self.time_entry, False, False, 0)
        self.title_entry = Gtk.Entry()
        self.title_entry.set_placeholder_text("Event title")
        self.title_entry.connect("activate", self._save)
        form.pack_start(self.title_entry, True, True, 0)
        self.save_button = TahoeButton(label="Add")
        self.save_button.connect("clicked", self._save)
        form.pack_start(self.save_button, False, False, 0)
        right.pack_start(form, False, False, 0)
        self.message = Gtk.Label()
        self.message.set_halign(Gtk.Align.START)
        right.pack_start(self.message, False, False, 0)
        self._refresh()

    def _date(self):
        year, month_zero, day = self.calendar.get_date()
        return dt.date(year, month_zero + 1, day).isoformat()

    def _refresh(self, *_args):
        date = self._date()
        selected = dt.date.fromisoformat(date)
        self.day_label.set_text(f"{selected.strftime('%A, %B')} {selected.day}, {selected.year}")
        for child in self.event_list.get_children():
            child.destroy()
        events = self.store.for_day(date)
        for event in events:
            row = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
            label = Gtk.Label(label=(event.get("time", "") + "  " + event["title"]).strip())
            label.set_halign(Gtk.Align.START)
            label.set_ellipsize(Pango.EllipsizeMode.END)
            row.pack_start(label, True, True, 0)
            edit = TahoeButton(label="Edit")
            edit.connect("clicked", self._edit, event)
            row.pack_start(edit, False, False, 0)
            remove = TahoeButton(label="Remove")
            remove.connect("clicked", self._remove, event["id"])
            row.pack_start(remove, False, False, 0)
            self.event_list.add(row)
        if not events:
            empty = Gtk.Label(label="No events for this day")
            empty.get_style_context().add_class("dim-label")
            self.event_list.add(empty)
        self.event_list.show_all()

    def _date_changed(self, *_args):
        self._clear_form()
        self.message.set_text("")
        self._refresh()

    def _edit(self, _button, event):
        self.editing_id = event["id"]
        self.title_entry.set_text(event["title"])
        self.time_entry.set_text(event.get("time", ""))
        self.save_button.set_label("Save")
        self.title_entry.grab_focus()

    def _remove(self, _button, event_id):
        self.store.remove_event(self._date(), event_id)
        if self.editing_id == event_id:
            self._clear_form()
        self.message.set_text("")
        self._refresh()

    def _save(self, *_args):
        try:
            self.store.save_event(self._date(), self.title_entry.get_text(),
                                  self.time_entry.get_text(), self.editing_id)
        except (OSError, ValueError) as error:
            self.message.set_text(str(error))
            return
        self._clear_form()
        self.message.set_text("")
        self._refresh()

    def _clear_form(self):
        self.editing_id = None
        self.title_entry.set_text("")
        self.time_entry.set_text("")
        self.save_button.set_label("Add")
