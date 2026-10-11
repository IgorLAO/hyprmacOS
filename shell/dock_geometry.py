"""Medidas, layout de repouso e hit testing do Dock; unidades lógicas GTK."""

from dataclasses import dataclass


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
