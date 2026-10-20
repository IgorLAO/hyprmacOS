"""Ponte GTK para a cor de pastas; transformação dos pixels em Rust."""

import ctypes
import json
from pathlib import Path

import gi

gi.require_version("GdkPixbuf", "2.0")
from gi.repository import GdkPixbuf, GLib

from accent_palette import accent_hex


_LIB = Path(__file__).resolve().parents[1] / "core/folder-color/target/release/libhyprmac_folder_color.so"
try:
    _rust = ctypes.CDLL(str(_LIB))
    _rust.hyprmac_tint_folder.argtypes = [ctypes.POINTER(ctypes.c_uint8), ctypes.c_size_t,
                                          ctypes.c_size_t, ctypes.c_size_t, ctypes.c_size_t,
                                          ctypes.c_uint8, ctypes.c_uint8, ctypes.c_uint8]
    _rust.hyprmac_tint_folder.restype = ctypes.c_bool
    _rust.hyprmac_folder_color.argtypes = [ctypes.POINTER(ctypes.c_uint8), ctypes.c_size_t,
                                          ctypes.POINTER(ctypes.c_uint8)]
    _rust.hyprmac_folder_color.restype = ctypes.c_bool
except OSError:
    _rust = None

RUST_ACTIVE = _rust is not None
_SETTINGS = Path.home() / ".config/hyprmac/ajustes.json"
_ICON = Path(__file__).resolve().parent / "icones/Folder_Icon.png"
_COLORS = frozenset(("red", "orange", "yellow", "green", "blue", "purple", "pink", "graphite"))


def folder_color():
    try:
        raw = _SETTINGS.read_bytes()
    except OSError:
        return None
    if _rust is not None:
        input_data = (ctypes.c_uint8 * len(raw)).from_buffer_copy(raw)
        rgb = (ctypes.c_uint8 * 3)()
        if _rust.hyprmac_folder_color(input_data, len(raw), rgb):
            return "#" + "".join(f"{part:02X}" for part in rgb)
        return None
    try:
        state = json.loads(raw)
    except ValueError:
        return None
    name = state.get("folder_color", "auto")
    if name == "auto":
        return None
    if name == "choose":
        value = state.get("folder_color_custom", "")
        return value if isinstance(value, str) and len(value) == 7 and value.startswith("#") \
            and all(c in "0123456789abcdefABCDEF" for c in value[1:]) else None
    return accent_hex("slate" if name == "graphite" else name, False) if name in _COLORS else None


def folder_pixbuf(size, color=None):
    """Carrega o asset base e recolore sua tinta em Rust quando há escolha válida."""
    pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(str(_ICON), size, size, True)
    color = folder_color() if color is None else color
    if not color or _rust is None or not pixbuf.get_has_alpha() or pixbuf.get_n_channels() != 4:
        return pixbuf
    data = bytearray(pixbuf.get_pixels())
    ptr = (ctypes.c_uint8 * len(data)).from_buffer(data)
    channels = tuple(int(color[i:i + 2], 16) for i in (1, 3, 5))
    ok = _rust.hyprmac_tint_folder(ptr, len(data), pixbuf.get_width(), pixbuf.get_height(),
                                   pixbuf.get_rowstride(), *channels)
    if not ok:
        return pixbuf
    return GdkPixbuf.Pixbuf.new_from_bytes(GLib.Bytes.new(bytes(data)), GdkPixbuf.Colorspace.RGB,
                                            True, 8, pixbuf.get_width(), pixbuf.get_height(),
                                            pixbuf.get_rowstride())
