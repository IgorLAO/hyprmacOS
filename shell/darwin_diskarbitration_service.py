"""Darwin-compatible DiskArbitration service for HyprMac.

Maps Apple's DiskArbitration framework (DASession / DADisk) semantics to the
Linux services already used by HyprMac: UDisks2 (preferred) with a read-only
``lsblk`` fallback. Only read-only enumeration and mount-state reporting are
implemented; no mount, format, eject or write operations are performed, matching
the current Disk Utility pilot.

This belongs to the Darwin Services Layer: lower-level service behaviour lives
here, while the visual reconstruction remains in the Tahoe UI Compatibility
Layer.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, List, Optional

__all__ = ["Volume", "DiskArbitrationService", "darwin_disk_list"]


@dataclass
class Volume:
    name: str
    device: str
    size_bytes: int
    kind: str                 # "disk" or "partition"
    filesystem: str
    mountpoint: str
    mounted: bool
    children: List["Volume"]

    def to_dict(self) -> dict:
        return asdict(self)


def _volume_from_udisks(row: dict) -> Volume:
    path = str(row.get("path") or "")
    mountpoint = str(row.get("mountpoint") or "")
    children = [_volume_from_udisks(c) for c in (row.get("children") or []) if isinstance(c, dict)]
    return Volume(
        name=str(row.get("model") or row.get("name") or path.rsplit("/", 1)[-1] or "Unknown"),
        device=path,
        size_bytes=int(row.get("size") or 0),
        kind=str(row.get("type") or "disk"),
        filesystem=str(row.get("fstype") or ""),
        mountpoint=mountpoint,
        mounted=bool(mountpoint),
        children=children,
    )


class DiskArbitrationService:
    """Read-only adapter exposing DiskArbitration-style volume discovery."""

    def __init__(self, backend: Optional[str] = None):
        self._backend = backend

    def list_volumes(self) -> List[Volume]:
        """Return currently visible volumes, read-only."""
        volumes: List[Volume] = []
        raw, error = self._read_backend()
        if error or not raw:
            return volumes
        for row in raw:
            if isinstance(row, dict):
                volumes.append(_volume_from_udisks(row))
        return volumes

    def _read_backend(self):
        # Imported lazily to avoid a hard dependency on GTK at import time.
        try:
            from shell.linux_storage_adapter import read_block_devices
        except Exception:
            try:
                from linux_storage_adapter import read_block_devices  # type: ignore
            except Exception:
                return [], "storage adapter unavailable"
        try:
            return read_block_devices()
        except Exception as exc:  # pragma: no cover - defensive
            return [], str(exc)

    @property
    def backend_name(self) -> str:
        return "udisks2-or-lsblk"


def darwin_disk_list() -> List[dict]:
    """Convenience helper returning plain dicts (for CLI / tests)."""
    service = DiskArbitrationService()
    return [v.to_dict() for v in service.list_volumes()]