"""Native Linux storage adapter used by HyprMac.

Wraps UDisks2 (preferred) with a read-only lsblk fallback. This is the
single implementation of block-device enumeration shared by Disk Utility and
the Darwin DiskArbitration compatibility layer.
"""

from __future__ import annotations

import json
import subprocess

import gi

gi.require_version("Gio", "2.0")
gi.require_version("GLib", "2.0")
from gi.repository import Gio, GLib


def _property(interface, name, default=None):
    value = interface.get_cached_property(name) if interface else None
    return value.unpack() if value is not None else default


def _decode_device(value):
    if isinstance(value, (bytes, bytearray, list)):
        return bytes(value).split(b"\0", 1)[0].decode("utf-8", "replace")
    return ""


def read_udisks_devices() -> list[dict]:
    """Read UDisks2's object manager; no mount or write methods called."""
    manager = Gio.DBusObjectManagerClient.new_for_bus_sync(
        Gio.BusType.SYSTEM, Gio.DBusObjectManagerClientFlags.NONE,
        "org.freedesktop.UDisks2", "/org/freedesktop/UDisks2", None, None, None)
    objects = {obj.get_object_path(): obj for obj in manager.get_objects()}
    rows = {}
    parents = {}
    for object_path, obj in objects.items():
        block = obj.get_interface("org.freedesktop.UDisks2.Block")
        if block is None:
            continue
        path = _decode_device(_property(block, "Device", []))
        partition = obj.get_interface("org.freedesktop.UDisks2.Partition")
        filesystem = obj.get_interface("org.freedesktop.UDisks2.Filesystem")
        drive_path = _property(block, "Drive", "")
        drive = objects.get(drive_path)
        drive_interface = drive.get_interface("org.freedesktop.UDisks2.Drive") if drive else None
        model = _property(drive_interface, "Model", "") if partition is None else ""
        mountpoints = _property(filesystem, "MountPoints", [])
        mountpoint = _decode_device(mountpoints[0]) if mountpoints else ""
        rows[object_path] = {
            "name": model or path.rsplit("/", 1)[-1], "path": path,
            "size": _property(block, "Size", 0),
            "type": "part" if partition else "disk",
            "fstype": _property(block, "IdType", ""),
            "mountpoint": mountpoint, "children": [],
        }
        parents[object_path] = _property(partition, "Table", "")
    roots = []
    for object_path, row in rows.items():
        parent = rows.get(parents[object_path])
        if parent is None:
            roots.append(row)
        else:
            parent["children"].append(row)
    return sorted(roots, key=lambda item: item["path"])


def read_block_devices(timeout: float = 4.0) -> tuple[list[dict], str]:
    """Get UDisks2 data, with lsblk as a read-only fallback."""
    try:
        devices = read_udisks_devices()
        if devices:
            return devices, ""
    except (GLib.Error, OSError, TypeError, ValueError):
        pass
    command = ["lsblk", "--json", "--bytes", "--tree", "--output",
               "NAME,PATH,SIZE,TYPE,FSTYPE,MOUNTPOINT,MODEL,TRAN"]
    try:
        result = subprocess.run(command, capture_output=True, text=True,
                                errors="replace", timeout=timeout, check=False)
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError) as exc:
        return [], str(exc)
    if result.returncode:
        return [], (result.stderr or f"lsblk exited {result.returncode}").strip()[:240]
    try:
        devices = json.loads(result.stdout).get("blockdevices", [])
    except (ValueError, AttributeError) as exc:
        return [], f"Cannot read device list: {exc}"
    if not isinstance(devices, list):
        return [], "Invalid device list"
    return devices, ""


def format_capacity(value) -> str:
    try:
        count = float(value)
    except (TypeError, ValueError):
        return "—"
    for unit in ("B", "KB", "MB", "GB", "TB", "PB"):
        if count < 1000 or unit == "PB":
            return f"{count:.0f} {unit}" if unit == "B" else f"{count:.1f} {unit}"
        count /= 1000
    return "—"