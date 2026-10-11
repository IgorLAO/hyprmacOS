"""Local Clock pilot: stopwatch, timer and alarms while its window is open."""

import datetime as dt
import json
import time
from pathlib import Path

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gtk

import sys
from pathlib import Path
TAHOE_CONTROLS_PATH = Path(__file__).parent.parent / "tahoe" / "controls"
sys.path.insert(0, str(TAHOE_CONTROLS_PATH))
from button import TahoeButton



PREFS = Path.home() / ".config/hyprmac/app-factory/clock.json"


class ClockPanel(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=18)
        self.stopwatch_start = None
        self.stopwatch_elapsed = 0.0
        self.timer_end = None
        self.timer_remaining = 0.0
        self.alarms = self._read_alarms()
        self.last_alarm_date = {}

        grid = Gtk.Grid(column_spacing=24, row_spacing=18)
        self.pack_start(grid, False, False, 0)
        self.stopwatch_label = Gtk.Label(label="00:00.0")
        self.stopwatch_label.get_style_context().add_class("title")
        grid.attach(Gtk.Label(label="Stopwatch"), 0, 0, 2, 1)
        grid.attach(self.stopwatch_label, 0, 1, 2, 1)
        start = TahoeButton(label="Start / Pause")
        start.connect("clicked", self._toggle_stopwatch)
        grid.attach(start, 0, 2, 1, 1)
        reset = TahoeButton(label="Reset")
        reset.connect("clicked", self._reset_stopwatch)
        grid.attach(reset, 1, 2, 1, 1)

        grid.attach(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL), 2, 0, 1, 4)
        grid.attach(Gtk.Label(label="Timer"), 3, 0, 2, 1)
        self.timer_label = Gtk.Label(label="00:00")
        self.timer_label.get_style_context().add_class("title")
        grid.attach(self.timer_label, 3, 1, 2, 1)
        self.minutes = Gtk.SpinButton.new_with_range(0, 999, 1)
        self.seconds = Gtk.SpinButton.new_with_range(0, 59, 1)
        self.minutes.set_value(5)
        grid.attach(self.minutes, 3, 2, 1, 1)
        grid.attach(self.seconds, 4, 2, 1, 1)
        timer_start = TahoeButton(label="Start / Pause")
        timer_start.connect("clicked", self._toggle_timer)
        grid.attach(timer_start, 3, 3, 1, 1)
        timer_reset = TahoeButton(label="Reset")
        timer_reset.connect("clicked", self._reset_timer)
        grid.attach(timer_reset, 4, 3, 1, 1)

        alarms_title = Gtk.Label(label="Alarms (while Clock is open)")
        alarms_title.set_halign(Gtk.Align.START)
        self.pack_start(alarms_title, False, False, 0)
        row = Gtk.Box(spacing=8)
        self.hour = Gtk.SpinButton.new_with_range(0, 23, 1)
        self.minute = Gtk.SpinButton.new_with_range(0, 59, 1)
        now = dt.datetime.now()
        self.hour.set_value(now.hour)
        self.minute.set_value(now.minute)
        row.pack_start(self.hour, False, False, 0)
        row.pack_start(Gtk.Label(label=":"), False, False, 0)
        row.pack_start(self.minute, False, False, 0)
        add = TahoeButton(label="Add alarm")
        add.connect("clicked", self._add_alarm)
        row.pack_start(add, False, False, 0)
        self.pack_start(row, False, False, 0)
        self.alarm_list = Gtk.ListBox()
        self.pack_start(self.alarm_list, False, False, 0)
        self._refresh_alarms()
        self._source = GLib.timeout_add(250, self._tick)
        self.connect("destroy", self._destroy)

    def _toggle_stopwatch(self, *_args):
        if self.stopwatch_start is None:
            self.stopwatch_start = time.monotonic()
        else:
            self.stopwatch_elapsed += time.monotonic() - self.stopwatch_start
            self.stopwatch_start = None

    def _reset_stopwatch(self, *_args):
        self.stopwatch_start = None
        self.stopwatch_elapsed = 0.0
        self.stopwatch_label.set_text("00:00.0")

    def _toggle_timer(self, *_args):
        if self.timer_end is not None:
            self.timer_remaining = max(0.0, self.timer_end - time.monotonic())
            self.timer_end = None
        else:
            if self.timer_remaining <= 0:
                self.timer_remaining = self.minutes.get_value_as_int() * 60 + self.seconds.get_value_as_int()
            if self.timer_remaining > 0:
                self.timer_end = time.monotonic() + self.timer_remaining

    def _reset_timer(self, *_args):
        self.timer_end = None
        self.timer_remaining = 0.0
        self.timer_label.set_text("00:00")

    def _add_alarm(self, *_args):
        value = f"{self.hour.get_value_as_int():02d}:{self.minute.get_value_as_int():02d}"
        if value not in self.alarms:
            self.alarms.append(value)
            self.alarms.sort()
            self._write_alarms()
            self._refresh_alarms()

    def _remove_alarm(self, _button, value):
        self.alarms.remove(value)
        self._write_alarms()
        self._refresh_alarms()

    def _refresh_alarms(self):
        for child in self.alarm_list.get_children():
            child.destroy()
        for value in self.alarms:
            row = Gtk.Box(spacing=12)
            row.pack_start(Gtk.Label(label=value), True, True, 0)
            remove = TahoeButton(label="Remove")
            remove.connect("clicked", self._remove_alarm, value)
            row.pack_end(remove, False, False, 0)
            self.alarm_list.add(row)
        self.alarm_list.show_all()

    def _tick(self):
        now_mono = time.monotonic()
        elapsed = self.stopwatch_elapsed
        if self.stopwatch_start is not None:
            elapsed += now_mono - self.stopwatch_start
        self.stopwatch_label.set_text(f"{int(elapsed // 60):02d}:{int(elapsed % 60):02d}.{int(elapsed * 10) % 10}")
        if self.timer_end is not None:
            self.timer_remaining = max(0.0, self.timer_end - now_mono)
            if self.timer_remaining == 0:
                self.timer_end = None
                self._alert("Timer finished")
        seconds = int(self.timer_remaining + 0.999)
        self.timer_label.set_text(f"{seconds // 60:02d}:{seconds % 60:02d}")
        current = dt.datetime.now()
        key = current.strftime("%H:%M")
        date = current.date().isoformat()
        if current.second == 0 and key in self.alarms and self.last_alarm_date.get(key) != date:
            self.last_alarm_date[key] = date
            self._alert("Alarm " + key)
        return True

    def _alert(self, message):
        dialog = Gtk.MessageDialog(transient_for=self.get_toplevel(), modal=True,
                                   message_type=Gtk.MessageType.INFO,
                                   buttons=Gtk.ButtonsType.OK, text=message)
        dialog.connect("response", lambda widget, *_: widget.destroy())
        dialog.show()

    @staticmethod
    def _read_alarms():
        try:
            data = json.loads(PREFS.read_text())
            return sorted({v for v in data.get("alarms", [])
                           if isinstance(v, str) and len(v) == 5 and v[2] == ":"})
        except (OSError, ValueError, TypeError):
            return []

    def _write_alarms(self):
        PREFS.parent.mkdir(parents=True, exist_ok=True)
        PREFS.write_text(json.dumps({"alarms": self.alarms}))

    def _destroy(self, *_args):
        GLib.source_remove(self._source)
