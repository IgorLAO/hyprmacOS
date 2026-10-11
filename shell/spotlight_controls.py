"""Controles de modo do Spotlight: desenho e animação GTK3.

O painel permanece no processo do shell. Este módulo apenas desenha os
controles e entrega cliques ao Spotlight que o criou.
"""

import math
from glass_motion import spring_step

import cairo
import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
gi.require_version("PangoCairo", "1.0")
from gi.repository import Gdk, Gtk, Pango, PangoCairo

SPOT_FIELD = 52

def draw_appstore_a(cr, cx, cy, s_, lw):
    """O "A" da App Store em três traços (perna direita longa, esquerda curta, travessa)."""
    cr.set_line_width(lw)
    cr.set_line_cap(cairo.LINE_CAP_ROUND)
    cr.move_to(cx - s_ * 0.15, cy - s_)
    cr.line_to(cx - s_ * 0.95, cy + s_ * 0.55)
    cr.move_to(cx - s_ * 0.15, cy - s_ * 0.55)
    cr.line_to(cx + s_ * 0.95, cy + s_ * 0.95)
    cr.move_to(cx - s_ * 0.95, cy + s_ * 0.2)
    cr.line_to(cx + s_ * 0.55, cy + s_ * 0.2)
    cr.stroke()


class SpotControls(Gtk.DrawingArea):
    """Os 4 botões de modo do Spotlight do Tahoe (Apps, Arquivos, Ações, Área de
    Transferência) — referencias/telas/spotlight-controles-1…6.png. Saem da ponta direita
    da cápsula como uma gota de vidro: incha a ponta, estica, solta-se e divide-se em 4
    círculos ligados por "pescoços" que afinam até romper. O desenho é uma união suave
    (metaball, smooth-min de SDFs) calculada por pixel; o vidro (lente, aro) vem do
    hyprglass, que faz de cada mancha de alfa da camada uma peça própria — a fusão com a
    cápsula e a separação saem líquidas sozinhas."""

    R = SPOT_FIELD / 2            # círculos do mesmo diâmetro da cápsula (medido: ≈ altura)
    GAP = 10                      # vão entre a cápsula e os círculos e entre eles
    OVER = int(SPOT_FIELD / 2)    # a área começa no centro do arco da ponta da cápsula
    MODES = ("apps", "files", "actions", "clipboard")
    GLYPHS = {"files": "f0256", "actions": "f0328", "clipboard": "f014c"}

    def __init__(self, spot, reduced_motion=lambda: False):
        super().__init__()
        self.spot = spot
        self.t = 0.0                  # 0 = recolhido, 1 = 4 botões soltos
        self._position = self._velocity = 0.0
        self._reduced_motion = reduced_motion
        self.target = 0.0
        self.hover = -1
        self._tick = None
        self._last = None
        self.w = int(self.OVER + self.GAP + 4 * SPOT_FIELD + 3 * self.GAP + 8)
        self.h = SPOT_FIELD + 8
        self.set_size_request(self.w, self.h)
        self.set_halign(Gtk.Align.START)
        self.set_valign(Gtk.Align.START)
        self.add_events(Gdk.EventMask.BUTTON_PRESS_MASK | Gdk.EventMask.POINTER_MOTION_MASK |
                        Gdk.EventMask.LEAVE_NOTIFY_MASK)
        self.connect("draw", self._draw)
        self.connect("button-press-event", self._click)
        self.connect("motion-notify-event", self._motion)
        self.connect("leave-notify-event", lambda *_: self._set_hover(-1))

    # ── geometria ──
    def centers(self):
        cy = self.h / 2
        x0 = self.OVER                                  # borda direita da cápsula
        return [(x0 + self.GAP + self.R + i * (2 * self.R + self.GAP), cy) for i in range(4)]

    def _hit(self, x, y):
        if self.t < 0.9:
            return -1
        for i, (cx, cy) in enumerate(self.centers()):
            if (x - cx) ** 2 + (y - cy) ** 2 <= self.R ** 2:
                return i
        return -1

    # GlassContainer.TransitionSettings.default Tahoe 26.6.1; associação ao
    # controle Spotlight experimental. Metaball e geometria continuam locais.
    def reset(self):
        """Fecha o painel sem preservar velocidade/estado de uma sessão anterior."""
        if self._tick is not None:
            self.remove_tick_callback(self._tick)
            self._tick = None
        self._position = self._velocity = self.t = self.target = 0.0
        self._last = None
        self.queue_draw()

    def show_controls(self, on):
        self.target = 1.0 if on else 0.0
        if self._reduced_motion():
            if self._tick is not None:
                self.remove_tick_callback(self._tick)
                self._tick = None
            self._position = self.t = self.target
            self._velocity = 0.0
            self.queue_draw()
        elif self._tick is None and self._position != self.target:
            self._last = None
            self._tick = self.add_tick_callback(self._step)

    def _step(self, _w, clock):
        now = clock.get_frame_time() / 1e6
        dt = 0.0 if self._last is None else max(now - self._last, 0.0)
        self._last = now
        if self._reduced_motion():
            self._position, self._velocity = self.target, 0.0
        else:
            self._position, self._velocity = spring_step(
                self._position, self._velocity, self.target, dt)
        # A máscara de separação só admite 0..1; não cortar o estado da mola.
        self.t = min(1.0, max(0.0, self._position))
        settled = abs(self._position - self.target) < 0.001 and abs(self._velocity) < 0.01
        if settled:
            self._position = self.t = self.target
            self._velocity = 0.0
            self._tick = None
        self.queue_draw()
        return not settled

    def _set_hover(self, i):
        if i != self.hover:
            self.hover = i
            self.queue_draw()
            hover_mode = getattr(self.spot, "_hover_mode", None)
            if hover_mode:
                hover_mode(self.MODES[i] if 0 <= i < len(self.MODES) else None)

    def _motion(self, _w, ev):
        self._set_hover(self._hit(ev.x, ev.y))
        # recolhidos, só a ponta da cápsula (o começo desta área) os chama
        self.spot._pointer_near(self.t > 0 or ev.x <= self.OVER + 8)
        return True          # não chega à janela: lá as coordenadas seriam lidas como dela

    def _click(self, _w, ev):
        i = self._hit(ev.x, ev.y)
        if i < 0:
            self.spot.hide()            # fora dos botões = fora do Spotlight
            return True
        self.spot._pick_mode(self.MODES[i])
        return True

    # ── desenho ──
    @staticmethod
    def _ease(u):
        u = max(0.0, min(1.0, u))
        # saída com mola: passa um pouco do alvo e volta (como os painéis do Tahoe)
        return 1 - (1 - u) ** 3 + (0.05 * math.sin(math.pi * (u - 0.6) / 0.4) if u > 0.6 else 0)

    def _field(self):
        import numpy as np
        R, t, h, w = self.R, self.t, self.h, self.w
        ys, xs = np.mgrid[0:h, 0:w].astype(np.float32) + 0.5
        cy = h / 2
        x0 = self.OVER
        # cápsula: a ponta é um arco de raio R centrado em (x0 - R, cy); à esquerda, faixa
        dx = np.maximum(xs - (x0 - R), 0)
        cap = np.sqrt(dx * dx + (ys - cy) ** 2) - R
        # pescoços: k grande no começo (tudo uma gota), pequeno no fim (gotas soltas)
        k = 4 + 30 * (1 - t) ** 1.3
        d = cap.copy()
        start = x0 - R * 0.55
        r = R * (0.5 + 0.5 * min(1.0, t * 1.6))
        for i, (fx, fy) in enumerate(self.centers()):
            e = self._ease((t - i * 0.07) / 0.79)
            cx = start + (fx - start) * e
            ci = np.sqrt((xs - cx) ** 2 + (ys - fy) ** 2) - r
            hh = np.clip(0.5 + 0.5 * (ci - d) / k, 0, 1)            # smooth-min polinomial
            d = ci * (1 - hh) + d * hh - k * hh * (1 - hh)
        cov = np.clip(0.5 - d, 0, 1)
        cov_cap = np.clip(0.5 - cap, 0, 1)
        return np.clip(cov - cov_cap, 0, 1)        # a cápsula já é desenhada pelo painel

    def _fill(self):
        ctx = self.spot.panel.get_style_context()
        c = ctx.get_property("background-color", Gtk.StateFlags.NORMAL)
        # o MESMO véu da cápsula (o vidro vem do compositor); só garante o mínimo acima do
        # mask_threshold da camada (0.025), senão a gota não vira vidro
        return (c.red, c.green, c.blue, max(c.alpha, 0.03))

    def _draw(self, _w, cr):
        if self.t <= 0.001:
            return False
        import numpy as np
        a = self._field()
        r, g, b, alpha = self._fill()
        # tema pela cor do texto do campo (o véu branco do vidro não diz se é claro/escuro)
        tc = self.spot.entry.get_style_context().get_color(Gtk.StateFlags.NORMAL)
        dark = (tc.red + tc.green + tc.blue) / 3 > 0.5
        A = a * alpha
        img = np.zeros((self.h, self.w, 4), dtype=np.uint8)          # ARGB32 premultiplicado
        img[..., 0] = (b * A * 255).astype(np.uint8)
        img[..., 1] = (g * A * 255).astype(np.uint8)
        img[..., 2] = (r * A * 255).astype(np.uint8)
        img[..., 3] = (A * 255).astype(np.uint8)
        stride = cairo.ImageSurface.format_stride_for_width(cairo.FORMAT_ARGB32, self.w)
        if stride != self.w * 4:
            return False
        surf = cairo.ImageSurface.create_for_data(memoryview(img).cast("B"), cairo.FORMAT_ARGB32,
                                                  self.w, self.h, stride)
        cr.set_source_surface(surf, 0, 0)
        cr.paint()

        # ícones: aparecem no fim, quando as gotas já são círculos
        ia = max(0.0, min(1.0, (self.t - 0.72) / 0.28))
        if ia <= 0:
            return False
        fg = (1, 1, 1) if dark else (0.25, 0.25, 0.28)
        for i, (cx, cy) in enumerate(self.centers()):
            mode = self.MODES[i]
            if i == self.hover or mode == self.spot.mode:
                cr.set_source_rgba(*((1, 1, 1, 0.10 * ia) if dark else (1, 1, 1, 0.35 * ia)))
                cr.arc(cx, cy, self.R - 2, 0, 2 * math.pi)
                cr.fill()
            cr.set_source_rgba(*fg, 0.92 * ia)
            if mode == "apps":                     # o "A" da App Store, em três traços
                draw_appstore_a(cr, cx, cy, 9, 2.2)
                continue
            lay = PangoCairo.create_layout(cr)
            lay.set_font_description(Pango.FontDescription("Symbols Nerd Font 15"))
            lay.set_text(chr(int(self.GLYPHS[mode], 16)), -1)
            _ink, log = lay.get_pixel_extents()
            cr.move_to(cx - log.width / 2, cy - log.height / 2)
            PangoCairo.show_layout(cr, lay)
        return False
