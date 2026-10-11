"""Read-only, on-demand Console panel backed by the local journal."""

from __future__ import annotations

import subprocess
import threading

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gtk
from tahoe.compatibility.button import TahoeButton


def read_journal(limit: int = 200, timeout: float = 4.0) -> tuple[list[str], str]:
    """Return recent readable entries and a short source label or error."""
    limit = max(1, min(int(limit), 1000))
    base = ["journalctl", "--no-pager", "--output=short-iso", "-n", str(limit)]
    errors = []
    for command, label in ((base + ["--user"], "User Journal"), (base, "System Journal")):
        try:
            result = subprocess.run(command, capture_output=True, text=True,
                                    errors="replace", timeout=timeout, check=False)
        except (FileNotFoundError, subprocess.TimeoutExpired, OSError) as exc:
            errors.append(str(exc))
            continue
        lines = [line for line in result.stdout.splitlines()
                 if line and not line.startswith("-- No entries --")]
        if result.returncode == 0 and lines:
            return lines[-limit:], label
        errors.append((result.stderr or result.stdout or f"exit {result.returncode}").strip()[:160])
    return [], "; ".join(error for error in errors if error) or "No readable journal entries"


class ConsolePanel(Gtk.Box):
    """A lightweight Console view; opening and Refresh perform one journal read."""

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self._lines: list[str] = []
        self._loading = False
        self._alive = True
        self.connect("destroy", self._destroy)

        toolbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.pack_start(toolbar, False, False, 0)
        self.refresh_button = TahoeButton(label="Refresh")
        self.refresh_button.connect("clicked", self.refresh)
        toolbar.pack_start(self.refresh_button, False, False, 0)
        self.search = Gtk.SearchEntry()
        self.search.set_placeholder_text("Search messages")
        self.search.connect("search-changed", self._render)
        toolbar.pack_start(self.search, True, True, 0)

        self.status = Gtk.Label(label="Loading…")
        self.status.set_xalign(0)
        self.pack_start(self.status, False, False, 0)

        scroller = Gtk.ScrolledWindow()
        scroller.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        self.pack_start(scroller, True, True, 0)
        self.view = Gtk.TextView()
        self.view.set_editable(False)
        self.view.set_cursor_visible(False)
        self.view.set_monospace(True)
        self.view.set_wrap_mode(Gtk.WrapMode.NONE)
        scroller.add(self.view)
        self.refresh()

    def refresh(self, *_args):
        if self._loading:
            return
        self._loading = True
        self.refresh_button.set_sensitive(False)
        self.status.set_text("Loading…")
        threading.Thread(target=self._fetch, daemon=True).start()

    def _fetch(self):
        lines, source = read_journal()
        GLib.idle_add(self._finish, lines, source)

    def _finish(self, lines, source):
        if not self._alive:
            return False
        self._loading = False
        self.refresh_button.set_sensitive(True)
        self._lines = lines
        self._source = source
        self._render()
        return False

    def _render(self, *_args):
        query = self.search.get_text().casefold().strip()
        visible = [line for line in self._lines if query in line.casefold()]
        self.view.get_buffer().set_text("\n".join(visible))
        source = getattr(self, "_source", "Journal")
        if self._lines:
            self.status.set_text(f"{source} · {len(visible)} of {len(self._lines)} entries")
        else:
            self.status.set_text(source)

    def _destroy(self, *_args):
        self._alive = False


__all__ = ["ConsolePanel", "read_journal"]
