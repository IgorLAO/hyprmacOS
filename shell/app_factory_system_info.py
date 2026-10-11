"""Local Linux hardware summary for the System Information factory app.

The values describe the current Linux host; this is not an Apple system report.
"""

import os
from pathlib import Path
import socket

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk
from tahoe.compatibility.button import TahoeButton


def _read(path):
    try:
        return Path(path).read_text(encoding="utf-8", errors="replace").strip()
    except OSError:
        return ""


def _cpu_model():
    for line in _read("/proc/cpuinfo").splitlines():
        key, separator, value = line.partition(":")
        if separator and key.strip() in ("model name", "Hardware", "Processor"):
            return value.strip()
    return os.uname().machine


def _memory():
    for line in _read("/proc/meminfo").splitlines():
        if line.startswith("MemTotal:"):
            try:
                return f"{int(line.split()[1]) / 1048576:.1f} GiB"
            except (IndexError, ValueError):
                break
    return "Unavailable"


def collect_system_info():
    """Return a small, read-only snapshot without starting external services."""
    release = os.uname()
    return {
        "Host name": socket.gethostname(),
        "Kernel": f"Linux {release.release}",
        "Architecture": release.machine,
        "Processor": _cpu_model(),
        "Logical CPUs": str(os.cpu_count() or "Unavailable"),
        "Memory": _memory(),
    }


class SystemInfoPanel(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        intro = Gtk.Label(label="Hardware and system details from this Linux computer")
        intro.set_halign(Gtk.Align.START)
        intro.get_style_context().add_class("dim-label")
        self.pack_start(intro, False, False, 0)

        self.grid = Gtk.Grid(column_spacing=24, row_spacing=14)
        self.grid.set_halign(Gtk.Align.START)
        self.pack_start(self.grid, False, False, 0)

        refresh = TahoeButton(label="Refresh")
        refresh.set_halign(Gtk.Align.START)
        refresh.connect("clicked", self._refresh)
        self.pack_start(refresh, False, False, 0)
        self._refresh()

    def _refresh(self, *_args):
        for child in self.grid.get_children():
            self.grid.remove(child)
        for row, (key, value) in enumerate(collect_system_info().items()):
            name = Gtk.Label(label=key)
            name.set_halign(Gtk.Align.START)
            name.get_style_context().add_class("dim-label")
            detail = Gtk.Label(label=value)
            detail.set_halign(Gtk.Align.START)
            detail.set_selectable(True)
            detail.set_line_wrap(True)
            detail.set_max_width_chars(55)
            self.grid.attach(name, 0, row, 1, 1)
            self.grid.attach(detail, 1, row, 1, 1)
        self.grid.show_all()
