"""Read-only Linux process panel for the HyprMac Activity Monitor pilot."""

import os
from pathlib import Path

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gtk


PROC = Path("/proc")
PAGE_SIZE = os.sysconf("SC_PAGE_SIZE")
CPU_COUNT = os.cpu_count() or 1


def sample_processes(previous=None):
    """Return (rows, counters) using one /proc snapshot, without changing processes.

    A row is (pid, name, CPU percent of one logical core, resident bytes).  The
    first snapshot has no CPU interval and therefore reports zero CPU usage.
    """
    previous = previous or {}
    with (PROC / "stat").open(encoding="ascii") as stream:
        total = sum(int(value) for value in stream.readline().split()[1:])
    old_total, old_ticks = previous.get("total", total), previous.get("ticks", {})
    elapsed = max(0, total - old_total)
    ticks = {}
    rows = []
    for entry in PROC.iterdir():
        if not entry.name.isdecimal():
            continue
        try:
            pid = int(entry.name)
            stat = (entry / "stat").read_text(encoding="utf-8", errors="replace")
            # comm is parenthesized and may itself contain spaces or ')'.
            start, end = stat.index("("), stat.rindex(")")
            name = stat[start + 1:end]
            fields = stat[end + 2:].split()
            process_ticks = int(fields[11]) + int(fields[12])  # utime + stime
            resident = int(fields[21]) * PAGE_SIZE            # rss, pages
        except (OSError, ValueError, IndexError):
            # A process can exit between directory enumeration and file read.
            continue
        ticks[pid] = process_ticks
        delta = max(0, process_ticks - old_ticks.get(pid, process_ticks))
        cpu = 100.0 * CPU_COUNT * delta / elapsed if elapsed else 0.0
        rows.append((pid, name, cpu, max(0, resident)))
    return rows, {"total": total, "ticks": ticks}


class ActivityPanel(Gtk.Box):
    """Process table refreshed only while its containing window is alive."""

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self._counters = None
        self._source = None

        self.summary = Gtk.Label(label="Processes")
        self.summary.set_halign(Gtk.Align.START)
        self.pack_start(self.summary, False, False, 0)

        self.model = Gtk.ListStore(int, str, float, int)
        tree = Gtk.TreeView(model=self.model)
        tree.set_headers_clickable(True)
        tree.set_enable_search(True)
        tree.set_search_column(1)
        for title, column, formatter in (
            ("Process Name", 1, None),
            ("PID", 0, None),
            ("% CPU", 2, lambda value: f"{value:.1f}"),
            ("Memory", 3, lambda value: f"{value / 1048576:.1f} MB"),
        ):
            renderer = Gtk.CellRendererText()
            view_column = Gtk.TreeViewColumn(title, renderer)
            if formatter is None:
                view_column.add_attribute(renderer, "text", column)
            else:
                view_column.set_cell_data_func(
                    renderer,
                    lambda _col, cell, model, iterator, _data, index=column, fmt=formatter:
                    cell.set_property("text", fmt(model.get_value(iterator, index))),
                )
            view_column.set_sort_column_id(column)
            view_column.set_resizable(True)
            tree.append_column(view_column)
        self.model.set_sort_column_id(2, Gtk.SortType.DESCENDING)

        scroll = Gtk.ScrolledWindow()
        scroll.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroll.add(tree)
        self.pack_start(scroll, True, True, 0)
        self._refresh()
        self._source = GLib.timeout_add_seconds(2, self._refresh)
        self.connect("destroy", self._destroy)

    def _refresh(self):
        try:
            rows, self._counters = sample_processes(self._counters)
        except OSError:
            self.summary.set_text("Process data unavailable")
            return True
        self.model.clear()
        for row in rows:
            self.model.append(row)
        self.summary.set_text(f"{len(rows)} Processes · CPU and resident memory")
        return True

    def _destroy(self, *_args):
        if self._source is not None:
            GLib.source_remove(self._source)
            self._source = None
