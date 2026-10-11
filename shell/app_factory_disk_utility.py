"""Read-only disk and partition inventory for the App Factory."""

from __future__ import annotations

import threading

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

try:
    from shell.linux_storage_adapter import (
        read_udisks_devices, read_block_devices, format_capacity,
    )
except Exception:  # pragma: no cover - allow direct module execution
    from linux_storage_adapter import (
        read_udisks_devices, read_block_devices, format_capacity,
    )


class DiskUtilityPanel(Gtk.Box):
    """A disk overview with no mount, format, eject, or write operations."""

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self._loading = False
        self._alive = True
        self.connect("destroy", self._destroy)
        header = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.pack_start(header, False, False, 0)
        title = Gtk.Label(label="Devices")
        title.set_xalign(0)
        header.pack_start(title, True, True, 0)
        self.refresh_button = Gtk.Button(label="Refresh")
        self.refresh_button.connect("clicked", self.refresh)
        header.pack_start(self.refresh_button, False, False, 0)

        self.status = Gtk.Label(label="Loading…")
        self.status.set_xalign(0)
        self.pack_start(self.status, False, False, 0)

        self.store = Gtk.TreeStore(str, str, str, str, str)
        self.view = Gtk.TreeView(model=self.store)
        self.view.set_headers_visible(True)
        for index, label in enumerate(("Device", "Capacity", "Type", "Format", "Mount Point")):
            renderer = Gtk.CellRendererText()
            column = Gtk.TreeViewColumn(label, renderer, text=index)
            column.set_resizable(True)
            self.view.append_column(column)
        scroller = Gtk.ScrolledWindow()
        scroller.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scroller.add(self.view)
        self.pack_start(scroller, True, True, 0)
        self.refresh()

    def refresh(self, *_args):
        if self._loading:
            return
        self._loading = True
        self.refresh_button.set_sensitive(False)
        self.status.set_text("Loading devices…")
        threading.Thread(target=self._fetch, daemon=True).start()

    def _fetch(self):
        devices, error = read_block_devices()
        from gi.repository import GLib
        GLib.idle_add(self._finish, devices, error)

    def _finish(self, devices: list[dict], error: str):
        if not self._alive:
            return False
        self._loading = False
        self.refresh_button.set_sensitive(True)
        self.store.clear()
        count = 0

        def add(device, parent=None):
            nonlocal count
            if not isinstance(device, dict):
                return
            name = str(device.get("model") or device.get("name") or device.get("path") or "Unknown")
            path = device.get("path")
            if path and path != name:
                name = f"{name} ({path})"
            row = self.store.append(parent, [
                name, format_capacity(device.get("size")),
                str(device.get("type") or "—"), str(device.get("fstype") or "—"),
                str(device.get("mountpoint") or "—"),
            ])
            count += 1
            for child in device.get("children") or []:
                add(child, row)

        for device in devices:
            add(device)
        self.view.expand_all()
        self.status.set_text(error or f"{count} devices and partitions · Read only")
        return False

    def _destroy(self, *_args):
        self._alive = False


__all__ = ["DiskUtilityPanel", "read_block_devices", "format_capacity", "read_udisks_devices"]