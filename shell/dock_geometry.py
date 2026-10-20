"""Medidas, layout de repouso e hit testing do Dock; unidades lógicas GTK."""

from dataclasses import dataclass
import ctypes
from pathlib import Path


@dataclass(frozen=True)
class DockMetrics:
    icon: int
    pad_top: int
    pad_side: int
    gap: int
    h: int
    radius: float
    dot: int
    dot_gap: int
    sep_col: int
    sep_h: int
    bottom: int

    @classmethod
    def from_icon(cls, icon=46):
        scale = icon / 36
        # DCK-05: tahoe-dark.jpeg (2560x1656), Finder em x=150:
        # ponto ocupa y=1630..1637 (~8 pixels), ícone visível ~80 pixels.
        # 4 unidades GTK é a aproximação escolhida; escala da captura não confirmada.
        # Gap lógico de 4 segue a meta do usuário, não uma medição Apple.
        return cls(round(36 * scale), round(11 * scale), round(8 * scale),
                   round(9 * scale), round(58 * scale), 15 * scale,
                   4, 4,
                   round(11 * scale), round(41 * scale), round(4 * scale))

    @staticmethod
    def magnification_shifts(growths):
        """Desloca centros, preservando o gap e centralizando a largura ampliada."""
        consumed = 0.0
        half_growth = sum(growths) / 2
        shifts = []
        for growth in growths:
            shifts.append(consumed + growth / 2 - half_growth)
            consumed += growth
        return shifts

    def layout(self, items):
        x = self.pad_side
        for item in items:
            item["x"] = x
            x += (self.sep_col if item["kind"] == "sep" else self.icon) + self.gap
        return x - self.gap + self.pad_side

    def index_at(self, items, drawn, x, y, origin_x, origin_y):
        if not (origin_y - self.icon <= y <= origin_y + self.h):
            return None
        for index, (ix, iy, size) in drawn.items():
            if ix <= x < ix + size and iy <= y < iy + size:
                return index
        if drawn:
            for index, (ix, _iy, size) in drawn.items():
                if ix - self.gap / 2 <= x < ix + size + self.gap / 2:
                    return index
            return None
        for index, item in enumerate(items):
            span = self.sep_col if item["kind"] == "sep" else self.icon
            if origin_x + item["x"] - self.gap / 2 <= x < origin_x + item["x"] + span + self.gap / 2:
                return index
        return None


# O módulo segue sendo a interface da view GTK; a geometria executa em Rust.
# O cálculo original acima atende checkouts ainda não compilados.
class _RawMetrics(ctypes.Structure):
    _fields_ = [("icon", ctypes.c_int32), ("pad_top", ctypes.c_int32),
                ("pad_side", ctypes.c_int32), ("gap", ctypes.c_int32),
                ("h", ctypes.c_int32), ("radius", ctypes.c_double),
                ("dot", ctypes.c_int32), ("dot_gap", ctypes.c_int32),
                ("sep_col", ctypes.c_int32), ("sep_h", ctypes.c_int32),
                ("bottom", ctypes.c_int32)]


class _RawDrawn(ctypes.Structure):
    _fields_ = [("index", ctypes.c_int64), ("x", ctypes.c_double),
                ("y", ctypes.c_double), ("size", ctypes.c_double)]


_LIB = (Path(__file__).resolve().parents[1]
        / "core/dock-geometry/target/release/libhyprmac_dock_geometry.so")
try:
    _rust = ctypes.CDLL(str(_LIB))
    _rust.hyprmac_dock_metrics.argtypes = [ctypes.c_int32]
    _rust.hyprmac_dock_metrics.restype = _RawMetrics
    _rust.hyprmac_dock_shifts.argtypes = [ctypes.POINTER(ctypes.c_double), ctypes.c_size_t,
                                          ctypes.POINTER(ctypes.c_double)]
    _rust.hyprmac_dock_shifts.restype = None
    _rust.hyprmac_dock_layout.argtypes = [_RawMetrics, ctypes.POINTER(ctypes.c_uint8),
                                          ctypes.c_size_t, ctypes.POINTER(ctypes.c_double)]
    _rust.hyprmac_dock_layout.restype = ctypes.c_double
    _rust.hyprmac_dock_index_at.argtypes = [_RawMetrics, ctypes.POINTER(ctypes.c_uint8),
                                            ctypes.POINTER(ctypes.c_double), ctypes.c_size_t,
                                            ctypes.POINTER(_RawDrawn), ctypes.c_size_t,
                                            ctypes.c_double, ctypes.c_double,
                                            ctypes.c_double, ctypes.c_double]
    _rust.hyprmac_dock_index_at.restype = ctypes.c_int64
except OSError:
    _rust = None

RUST_GEOMETRY_ACTIVE = _rust is not None
_python_from_icon = DockMetrics.from_icon
_python_shifts = DockMetrics.magnification_shifts
_python_layout = DockMetrics.layout
_python_index_at = DockMetrics.index_at


def _raw(self):
    return _RawMetrics(self.icon, self.pad_top, self.pad_side, self.gap, self.h,
                       self.radius, self.dot, self.dot_gap, self.sep_col,
                       self.sep_h, self.bottom)


def _from_icon(cls, icon=46):
    if _rust is None:
        return _python_from_icon(icon)
    raw = _rust.hyprmac_dock_metrics(icon)
    return cls(*(getattr(raw, name) for name, _ in _RawMetrics._fields_))


def _shifts(growths):
    if _rust is None:
        return _python_shifts(growths)
    size = len(growths)
    if not size:
        return []
    values = (ctypes.c_double * size)(*growths)
    result = (ctypes.c_double * size)()
    _rust.hyprmac_dock_shifts(values, size, result)
    return list(result)


def _layout(self, items):
    if _rust is None:
        return _python_layout(self, items)
    size = len(items)
    separators = (ctypes.c_uint8 * size)(*(item["kind"] == "sep" for item in items))
    positions = (ctypes.c_double * size)()
    width = _rust.hyprmac_dock_layout(_raw(self), separators, size, positions)
    for item, x in zip(items, positions):
        item["x"] = int(x)
    return int(width)


def _index_at(self, items, drawn, x, y, origin_x, origin_y):
    if _rust is None:
        return _python_index_at(self, items, drawn, x, y, origin_x, origin_y)
    size = len(items)
    separators = (ctypes.c_uint8 * size)(*(item["kind"] == "sep" for item in items))
    positions = (ctypes.c_double * size)(*(item.get("x", 0) for item in items))
    ordered = (_RawDrawn * len(drawn))(*(_RawDrawn(index, *box)
                                          for index, box in drawn.items()))
    result = _rust.hyprmac_dock_index_at(_raw(self), separators, positions, size,
                                         ordered, len(drawn), x, y, origin_x, origin_y)
    return None if result == -1 else result


DockMetrics.from_icon = classmethod(_from_icon)
DockMetrics.magnification_shifts = staticmethod(_shifts)
DockMetrics.layout = _layout
DockMetrics.index_at = _index_at
