"""Small, GTK independent registry for HyprMac application manifests."""

from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MANIFESTS = ROOT / "app-manifests"
ID_RE = re.compile(r"^dev\.hyprmac\.[A-Za-z][A-Za-z0-9]*$")
STATUSES = {"coming_soon", "partial", "implemented"}
LAYOUTS = {"window", "sidebar"}


def validate_manifest(data: object) -> dict:
    if not isinstance(data, dict):
        raise ValueError("manifest must be an object")
    required = {"id", "name", "icon", "layout", "size", "sidebar_items", "status", "bundle_id", "evidence"}
    missing = required - data.keys()
    if missing:
        raise ValueError(f"missing fields: {', '.join(sorted(missing))}")
    if not isinstance(data["id"], str) or not ID_RE.fullmatch(data["id"]):
        raise ValueError("invalid HyprMac id")
    for key in ("name", "icon", "bundle_id"):
        if not isinstance(data[key], str) or not data[key].strip():
            raise ValueError(f"invalid {key}")
    if data["layout"] not in LAYOUTS or data["status"] not in STATUSES:
        raise ValueError("invalid layout or status")
    size = data["size"]
    if not isinstance(size, list) or len(size) != 2 or any(type(v) is not int or not 320 <= v <= 4096 for v in size):
        raise ValueError("size must be two pixel dimensions in 320..4096")
    items = data["sidebar_items"]
    if not isinstance(items, list) or any(not isinstance(item, str) or not item.strip() for item in items):
        raise ValueError("sidebar_items must be a list of names")
    groups = data.get("sidebar_groups", [])
    if not isinstance(groups, list) or any(
            not isinstance(group, dict) or
            not isinstance(group.get("title"), str) or
            not isinstance(group.get("items"), list) or
            any(not isinstance(item, str) or not item.strip() for item in group["items"])
            for group in groups):
        raise ValueError("invalid sidebar_groups")
    if data["layout"] == "window" and (items or groups):
        raise ValueError("window layout cannot have sidebar_items")
    default = data.get("sidebar_default")
    available = items + [item for group in groups for item in group["items"]]
    if default is not None and default not in available:
        raise ValueError("sidebar_default is not a sidebar item")
    if not isinstance(data["evidence"], dict) or not data["evidence"].get("inventory"):
        raise ValueError("missing inventory evidence")
    backend = data.get("backend")
    if backend is not None:
        if not isinstance(backend, dict) or backend.get("kind") not in {"python_panel", "external"}:
            raise ValueError("invalid backend")
        if backend["kind"] == "python_panel" and not all(
                isinstance(backend.get(key), str) and backend[key]
                for key in ("module", "class")):
            raise ValueError("invalid python panel backend")
        if backend["kind"] == "external" and (
                not isinstance(backend.get("argv"), list) or
                not backend["argv"] or
                any(not isinstance(v, str) or not v for v in backend["argv"])):
            raise ValueError("invalid external backend")
    toolbar = data.get("toolbar_items", [])
    if not isinstance(toolbar, list) or any(
            not isinstance(item, dict) or
            not isinstance(item.get("label"), str) or
            item.get("action") not in {"refresh"}
            for item in toolbar):
        raise ValueError("invalid toolbar_items")
    duration = data.get("transition_ms", 0)
    if type(duration) is not int or not 0 <= duration <= 500:
        raise ValueError("invalid transition_ms")
    icon = data["icon"]
    if "/" in icon:
        path = (ROOT.parent / icon).resolve()
        if not path.is_relative_to(ROOT.parent) or not path.is_file():
            raise ValueError(f"missing icon: {icon}")
    return data


def load_manifest(app_id: str) -> dict:
    if not ID_RE.fullmatch(app_id):
        raise ValueError("invalid HyprMac id")
    path = MANIFESTS / f"{app_id.removeprefix('dev.hyprmac.')}.json"
    data = validate_manifest(json.loads(path.read_text(encoding="utf-8")))
    if data["id"] != app_id:
        raise ValueError(f"id does not match filename: {path}")
    return data


def all_manifests() -> list[dict]:
    if not MANIFESTS.is_dir():
        return []
    return [load_manifest("dev.hyprmac." + p.stem) for p in sorted(MANIFESTS.glob("*.json"))]
