"""Wallpaper, desktop widgets and desktop icons in the shared shell process."""
import json
import math
import os
import random
import subprocess
import sys
import threading
import time
import urllib.parse
import urllib.request

import cairo
import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
gi.require_version("GdkPixbuf", "2.0")
gi.require_version("GtkLayerShell", "0.1")
gi.require_version("PangoCairo", "1.0")
from gi.repository import Gdk, GdkPixbuf, Gio, GLib, Gtk, Pango, PangoCairo
from gi.repository import GtkLayerShell as LS

E = LS.Edge


def create_desktop_classes(*, BAR_DARK_TEXT_L, BAR_STRIP, CACHE, CFG,
                           DEFAULTS, ICON_STYLES, I, MESES, ROOT, WIDGET_SETS,
                           accent_rgb, add_class, bar_text_mode, gdk_monitors,
                           hypr_events, hypr_json, icon_style, in_thread,
                           is_dark, label, layer_window, menu_check,
                           menu_check_column, menu_header, open_settings,
                           paint_cover, reduce_motion, rounded_rect,
                           set_class, spawn):
    """Bind the existing shell services to the desktop views."""
    class Wallpaper:
        """Papel de parede em todos os monitores.

        CFG["wallpaper"] pode ser um caminho de imagem ou "gnome": nesse caso segue
        org.gnome.desktop.background (picture-uri / picture-uri-dark conforme o
        color-scheme, e picture-options), e atualiza na hora quando o GNOME muda.
        """

        GNOME_BG = "org.gnome.desktop.background"
        GNOME_IFACE = "org.gnome.desktop.interface"

        def __init__(self, monitors):
            self.windows, self.areas = [], []
            self.pixbuf, self.mode, self.color = None, "zoom", (0.0, 0.0, 0.0)
            self.gnome = False
            self.bg = Gio.Settings.new(self.GNOME_BG)
            self.iface = Gio.Settings.new(self.GNOME_IFACE)
            for key in ("picture-uri", "picture-uri-dark", "picture-options", "primary-color"):
                self.bg.connect(f"changed::{key}", lambda *_: self.gnome and self.reload())
            self.iface.connect("changed::color-scheme", lambda *_: self.gnome and self.reload())
            self.reload(redraw=False)
            for mon in monitors:
                win = layer_window("hyprmac-wallpaper", LS.Layer.BACKGROUND, mon,
                                   anchors=(E.TOP, E.BOTTOM, E.LEFT, E.RIGHT), exclusive=-1)
                area = Gtk.DrawingArea()
                cache = {}
                area.connect("draw", lambda a, cr, c=cache: self._draw(a, cr, c))
                win.add(area)
                win.show_all()
                self.windows.append(win)
                self.areas.append((area, cache))

        # ── origem da imagem ──
        def _gnome_source(self):
            dark = self.iface.get_string("color-scheme") == "prefer-dark"
            uri = self.bg.get_string("picture-uri-dark" if dark else "picture-uri") \
                or self.bg.get_string("picture-uri")
            path = Gio.File.new_for_uri(uri).get_path() if uri else None
            if path and path.endswith(".xml"):
                path = self._xml_first_file(path)
            rgba = Gdk.RGBA()
            rgba.parse(self.bg.get_string("primary-color") or "#000000")
            return path, self.bg.get_string("picture-options"), (rgba.red, rgba.green, rgba.blue)

        @staticmethod
        def _xml_first_file(path):
            """Papéis de parede dinâmicos do GNOME (.xml): usa a primeira imagem."""
            import xml.etree.ElementTree as ET
            try:
                node = ET.parse(path).getroot().find(".//file")
                return node.text.strip() if node is not None and node.text else None
            except (OSError, ET.ParseError):
                return None

        def reload(self, redraw=True):
            self.gnome = str(CFG["wallpaper"]).lower() == "gnome"
            if self.gnome:
                path, self.mode, self.color = self._gnome_source()
            else:
                path, self.mode = os.path.expanduser(CFG["wallpaper"]), "zoom"
            try:
                self.pixbuf = self._load(path) if path else None
            except GLib.Error as e:
                print("papel de parede:", e, file=sys.stderr)
                self.pixbuf = None
            if self.pixbuf is None and self.mode != "none":
                try:
                    self.pixbuf = GdkPixbuf.Pixbuf.new_from_file(DEFAULTS["photo_fallback"])
                except GLib.Error as e:
                    # Checkouts sem os assets locais ainda precisam iniciar o desktop.
                    print("papel de parede padrão indisponível:", e, file=sys.stderr)
                    self.pixbuf = None
                self.mode = "zoom"
            if redraw:
                for area, cache in self.areas:
                    cache.clear()
                    area.queue_draw()
            GLib.idle_add(self._bar_contrast)

        def _bar_contrast(self):
            """macOS Tahoe: na barra transparente o conteúdo fica PRETO sobre papel de parede
            claro e BRANCO sobre escuro. Mede a luminância média (linear) da faixa da barra no
            papel de parede, como ele é desenhado, e troca para preto acima de BAR_DARK_TEXT_L.
            Grava waybar/contrast.css e recarrega o estilo do Waybar."""
            pb = self.pixbuf
            dark_text = False
            bar_mode = bar_text_mode()   # "auto" | "white" | "black"
            rgb_sum, rgb_n = [0.0, 0.0, 0.0], 0
            if bar_mode != "white" and pb is not None and self.mode != "none":
                display = Gdk.Display.get_default()
                lums, rgb_sum, rgb_n = [], [0.0, 0.0, 0.0], 0
                for i in range(display.get_n_monitors()):
                    g = display.get_monitor(i).get_geometry()
                    pw, ph = pb.get_width(), pb.get_height()
                    if self.mode in ("zoom", "spanned"):
                        k = max(g.width / pw, g.height / ph)
                        x0, y0 = (pw * k - g.width) / 2 / k, (ph * k - g.height) / 2 / k
                        sw, sh = g.width / k, BAR_STRIP / k
                    else:
                        x0, y0, sw, sh = 0, 0, pw, BAR_STRIP * ph / max(1, g.height)
                    x0, y0 = int(max(0, x0)), int(max(0, y0))
                    sw, sh = max(1, min(pw - x0, int(sw))), max(1, min(ph - y0, int(sh)))
                    strip = pb.new_subpixbuf(x0, y0, sw, sh).scale_simple(
                        max(1, min(256, sw)), max(1, min(16, sh)), GdkPixbuf.InterpType.BILINEAR)
                    data, n, rs = strip.get_pixels(), strip.get_n_channels(), strip.get_rowstride()
                    tot = cnt = 0.0
                    for y in range(strip.get_height()):
                        for x in range(strip.get_width()):
                            o = y * rs + x * n
                            px = data[o:o + 3]
                            for ch in range(3):
                                rgb_sum[ch] += px[ch]
                            r, gg, b = (((c / 255) / 12.92) if c <= 10 else ((c / 255 + 0.055) / 1.055) ** 2.4
                                        for c in px)
                            tot += 0.2126 * r + 0.7152 * gg + 0.0722 * b
                            cnt += 1
                    lums.append(tot / max(1, cnt))
                    rgb_n += cnt
                if lums:
                    lum = sum(lums) / len(lums)
                    dark_text = lum > BAR_DARK_TEXT_L
            if bar_mode != "auto":
                dark_text = bar_mode == "black"
            want = ""
            if dark_text:
                try:
                    want = open(os.path.join(ROOT, "waybar", "contrast-dark.css")).read()
                except OSError:
                    want = ""
                # o preto da Apple puxa o tom do fundo: kit "Labels/Light Vibrant Primary" #363636
                # em plus-darker = fundo − 201 por canal (Finder: (3,33,56) sobre (136,206,250))
                if want and rgb_n:
                    c = [max(0, round(v / rgb_n) - 201) for v in rgb_sum]
                    want = want.replace("rgba(0, 0, 0, 0.85)", f"rgb({c[0]}, {c[1]}, {c[2]})")
            out = os.path.join(ROOT, "waybar", "contrast.css")
            try:
                cur = open(out).read()
            except OSError:
                cur = None
            if cur != want:
                with open(out, "w") as f:
                    f.write(want)
                subprocess.run(["pkill", "-SIGUSR2", "-x", "waybar"], check=False)
            return False

        @staticmethod
        def _load(path):
            """Carrega no máximo ~2× o maior monitor: imagens enormes (ex.: um quadro de
            30000 px) ocupavam ~2 GB de RAM decodificadas. Em JPEG o GdkPixbuf já
            reduz durante a leitura, então também fica bem mais rápido."""
            display = Gdk.Display.get_default()
            mons = [display.get_monitor(i).get_geometry() for i in range(display.get_n_monitors())]
            lim_w = 2 * max((g.width for g in mons), default=1920)
            lim_h = 2 * max((g.height for g in mons), default=1080)
            _fmt, w, h = GdkPixbuf.Pixbuf.get_file_info(path)
            if not (w and h and (w > lim_w or h > lim_h)):
                return GdkPixbuf.Pixbuf.new_from_file(path)
            # versão reduzida guardada em cache: decodificar a original leva vários segundos
            import hashlib
            st = os.stat(path)
            chave = hashlib.sha1(f"{path}|{st.st_mtime}|{st.st_size}|{lim_w}x{lim_h}".encode()).hexdigest()[:16]
            cache = os.path.join(CACHE, "wallpaper", chave + ".png")
            if os.path.exists(cache):
                return GdkPixbuf.Pixbuf.new_from_file(cache)
            # mantém a proporção cobrindo o limite (o desenho recorta/ajusta depois)
            s = max(lim_w / w, lim_h / h)
            pb = GdkPixbuf.Pixbuf.new_from_file_at_scale(path, max(1, round(w * s)),
                                                         max(1, round(h * s)), True)
            try:
                os.makedirs(os.path.dirname(cache), exist_ok=True)
                for velho in os.listdir(os.path.dirname(cache)):   # só o atual fica
                    os.remove(os.path.join(os.path.dirname(cache), velho))
                pb.savev(cache, "png", [], [])
            except (OSError, GLib.Error):
                pass
            return pb

        # ── desenho (mesmos modos do GNOME) ──
        def _draw(self, area, cr, cache):
            w, h = area.get_allocated_width(), area.get_allocated_height()
            cr.set_source_rgb(*self.color)
            cr.paint()
            pb, mode = self.pixbuf, self.mode
            if pb is None or mode == "none":
                return
            pw, ph = pb.get_width(), pb.get_height()
            if mode in ("zoom", "spanned"):
                paint_cover(cr, pb, w, h, cache=cache)
                return
            if mode == "stretched":
                sw, sh = w, h
            elif mode == "scaled":
                k = min(w / pw, h / ph)
                sw, sh = round(pw * k), round(ph * k)
            else:                       # "centered" e "wallpaper" (lado a lado)
                sw, sh = pw, ph
            key = (id(pb), sw, sh)
            scaled = cache.get(key)
            if scaled is None:
                scaled = pb if (sw, sh) == (pw, ph) else pb.scale_simple(sw, sh, GdkPixbuf.InterpType.HYPER)
                cache.clear()
                cache[key] = scaled
            if mode == "wallpaper":
                Gdk.cairo_set_source_pixbuf(cr, scaled, 0, 0)
                cr.get_source().set_extend(cairo.EXTEND_REPEAT)
            else:
                Gdk.cairo_set_source_pixbuf(cr, scaled, (w - sw) / 2, (h - sh) / 2)
            cr.paint()


    # ───────────────────────────── widgets da mesa ─────────────────────────────

    WMO = {  # código WMO → (descrição, ícone dia, ícone noite)
        0: ("Clear", "sun", "moon"),
        1: ("Mostly Clear", "sun", "moon"),
        2: ("Partly Cloudy", "partly", "partly_n"),
        3: ("Cloudy", "cloudy", "cloudy"),
        45: ("Foggy", "fog", "fog"), 48: ("Foggy", "fog", "fog"),
        51: ("Drizzle", "drizzle", "drizzle"), 53: ("Drizzle", "drizzle", "drizzle"),
        55: ("Drizzle", "drizzle", "drizzle"), 56: ("Drizzle", "drizzle", "drizzle"),
        57: ("Drizzle", "drizzle", "drizzle"),
        61: ("Rain", "rain", "rain"), 63: ("Rain", "rain", "rain"),
        65: ("Heavy Rain", "pour", "pour"), 66: ("Rain", "rain", "rain"),
        67: ("Heavy Rain", "pour", "pour"),
        71: ("Snow", "snow", "snow"), 73: ("Snow", "snow", "snow"), 75: ("Snow", "snow", "snow"),
        77: ("Snow", "snow", "snow"),
        80: ("Showers", "rain", "rain"), 81: ("Showers", "rain", "rain"),
        82: ("Heavy Rain", "pour", "pour"),
        85: ("Snow", "snow", "snow"), 86: ("Snow", "snow", "snow"),
        95: ("Thunderstorms", "storm", "storm"), 96: ("Thunderstorms", "storm", "storm"),
        99: ("Thunderstorms", "storm", "storm"),
    }


    def weather_icon(code, is_day):
        _, d, n = WMO.get(code, ("", "cloudy", "cloudy"))
        name = d if is_day else n
        # no escuro o widget é vidro e os ícones são brancos (tahoe-dark.jpeg); no claro, sol amarelo
        color = "#ffd60a" if name == "sun" and not is_dark() else "#ffffff"
        return f'<span foreground="{color}">{I[name]}</span>'


    def fetch_json(url, timeout=8):
        req = urllib.request.Request(url, headers={"User-Agent": "hyprmac-shell"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.load(r)


    def locate():
        """Cidade + coordenadas: config > cache > geolocalização por IP."""
        if CFG.get("latitude") is not None and CFG.get("longitude") is not None:
            return CFG.get("city") or "", CFG["latitude"], CFG["longitude"]
        if CFG.get("city"):
            q = urllib.parse.quote(CFG["city"])
            res = fetch_json(f"https://geocoding-api.open-meteo.com/v1/search?name={q}&count=1&language=pt")
            r = res["results"][0]
            return r["name"], r["latitude"], r["longitude"]
        path = os.path.join(CACHE, "location.json")
        try:
            with open(path) as f:
                loc = json.load(f)
            if time.time() - loc["t"] < 86400:
                return loc["city"], loc["lat"], loc["lon"]
        except (OSError, ValueError, KeyError):
            pass
        loc = fetch_json("http://ip-api.com/json/?fields=status,city,lat,lon")
        os.makedirs(CACHE, exist_ok=True)
        with open(path, "w") as f:
            json.dump({"t": time.time(), "city": loc["city"], "lat": loc["lat"], "lon": loc["lon"]}, f)
        return loc["city"], loc["lat"], loc["lon"]


    class WeatherWidget(Gtk.Box):
        def __init__(self, size="medium"):
            super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=0)
            add_class(self, "card", "weather", "weather-" + size)
            self.small = size == "small"
            self.set_size_request(*WIDGET_SIZES[size])

            top = Gtk.Box(spacing=8)
            left = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            self.city = label("Clima", "city")
            self.temp = label("--°", "temp")
            left.pack_start(self.city, False, False, 0)
            left.pack_start(self.temp, False, False, 0)
            right = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
            self.icon = label("", "icon now-icon", xalign=1.0, markup=True)
            self.cond = label("", "cond", xalign=1.0)
            self.hilo = label("", "hilo", xalign=1.0)
            for w in (self.icon, self.cond, self.hilo):
                right.pack_start(w, False, False, 0)
            top.pack_start(left, True, True, 0)
            top.pack_end(right, False, False, 0)

            self.hours = Gtk.Box(spacing=0, homogeneous=True)
            self.slots = []
            for _ in range(6):
                col = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=5)
                h, ic, t = (label("", "hour", 0.5), label("", "icon hicon", 0.5, True),
                            label("", "htemp", 0.5))
                for w in (h, ic, t):
                    col.pack_start(w, False, False, 0)
                self.hours.pack_start(col, True, True, 0)
                self.slots.append((h, ic, t))

            if self.small:        # pequeno: cidade, temperatura e condição empilhadas
                top.remove(right)
                for w in (self.icon, self.cond, self.hilo):
                    right.remove(w)
                    w.set_xalign(0.0)
                left.pack_start(self.icon, False, False, 0)
                left.pack_start(self.cond, False, False, 0)
                left.pack_start(self.hilo, False, False, 0)
            self.pack_start(top, True, True, 0)
            if not self.small:
                self.pack_end(self.hours, False, False, 0)
            self.refresh()
            GLib.timeout_add_seconds(15 * 60, self.refresh)

        def refresh(self):
            in_thread(self._fetch)
            return True

        def _fetch(self):
            try:
                city, lat, lon = locate()
                d = fetch_json(
                    "https://api.open-meteo.com/v1/forecast"
                    f"?latitude={lat}&longitude={lon}"
                    "&current=temperature_2m,weather_code,is_day"
                    "&hourly=temperature_2m,weather_code,is_day"
                    "&daily=temperature_2m_max,temperature_2m_min"
                    "&timezone=auto&forecast_days=2")
            except Exception as e:  # sem rede, API fora etc.
                print("clima:", e, file=sys.stderr)
                GLib.timeout_add_seconds(120, lambda: self.refresh() and False)
                return
            GLib.idle_add(self._apply, city, d)

        def _apply(self, city, d):
            cur, hourly, daily = d["current"], d["hourly"], d["daily"]
            code = cur["weather_code"]
            self.city.set_text(city)
            self.temp.set_text(f"{round(cur['temperature_2m'])}°")
            self.icon.set_markup(weather_icon(code, cur["is_day"]))
            self.cond.set_text(WMO.get(code, ("",))[0])
            self.hilo.set_text(f"H:{round(daily['temperature_2m_max'][0])}° "
                               f"L:{round(daily['temperature_2m_min'][0])}°" if not self.small else
                               f"M:{round(daily['temperature_2m_max'][0])}° "
                               f"m:{round(daily['temperature_2m_min'][0])}°")
            now_hour = cur["time"][:13]
            try:
                start = next(i for i, t in enumerate(hourly["time"]) if t[:13] >= now_hour)
            except StopIteration:
                start = 0
            for k, (h, ic, t) in enumerate(self.slots):
                i = start + k
                if i >= len(hourly["time"]):
                    break
                h.set_text("Now" if k == 0 else f"{int(hourly['time'][i][11:13])}h")
                ic.set_markup(weather_icon(hourly["weather_code"][i], hourly["is_day"][i]))
                t.set_text(f"{round(hourly['temperature_2m'][i])}°")
            return False


    class ShortcutsWidget(Gtk.Grid):
        """Cartão branco com atalhos (no lugar do widget do ChatGPT)."""

        def __init__(self):
            super().__init__(row_spacing=0, column_spacing=0,
                             row_homogeneous=True, column_homogeneous=True)
            add_class(self, "card", "shortcuts")
            self.set_size_request(204, 204)
            for (col, row, icon, tip, cmd) in (
                    (0, 0, I["console"], "Terminal", CFG["terminal"]),
                    (0, 1, I["camera"], "Screenshot", CFG["screenshot"]),
                    (1, 1, I["wave"], "Sound", "pavucontrol")):
                b = Gtk.Button()
                b.add(label(icon, "icon", 0.5))
                b.set_tooltip_text(tip)
                b.connect("clicked", lambda _b, c=cmd: spawn(c))
                b.set_halign(Gtk.Align.CENTER)
                b.set_valign(Gtk.Align.CENTER)
                b.set_size_request(64, 64)
                self.attach(b, col, row, 1, 1)


    class PhotoWidget(Gtk.EventBox):
        def __init__(self, size="small"):
            super().__init__()
            self.set_size_request(*WIDGET_SIZES[size])
            self.area = Gtk.DrawingArea()
            self.add(self.area)
            self.cache = {}
            self.pixbuf = None
            self.path = None
            self.area.connect("draw", self._draw)
            self.connect("button-press-event", lambda _w, ev: ev.button == 1 and self.path
                         and spawn(f"xdg-open '{self.path}'"))
            self.next_photo()
            GLib.timeout_add_seconds(10 * 60, self.next_photo)

        def _candidates(self):
            base = os.path.expanduser(CFG["photos_dir"])
            found = []
            for dirpath, dirnames, files in os.walk(base):
                dirnames[:] = [d for d in dirnames
                               if not d.startswith(".") and "screenshot" not in d.lower()]
                found += [os.path.join(dirpath, f) for f in files
                          if f.lower().endswith((".jpg", ".jpeg", ".png", ".webp"))]
                if len(found) > 5000:
                    break
            return found

        def next_photo(self):
            photos = self._candidates()
            path = random.choice(photos) if photos else CFG["photo_fallback"]
            try:
                self.pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(path, 900, 900, True)
                self.path = path
            except GLib.Error:
                self.pixbuf = GdkPixbuf.Pixbuf.new_from_file(CFG["photo_fallback"])
                self.path = CFG["photo_fallback"]
            self.area.queue_draw()
            return True

        def _draw(self, area, cr):
            w, h = area.get_allocated_width(), area.get_allocated_height()
            paint_cover(cr, self.pixbuf, w, h, radius=24, cache=self.cache)


    class ClockWidget(Gtk.DrawingArea):
        """Relógio analógico pequeno (widget "Relógio" do macOS): mostrador branco,
        números pretos, ponteiros pretos e o dos segundos laranja."""

        def __init__(self, size="small"):
            super().__init__()
            self.set_size_request(*WIDGET_SIZES[size])
            self.connect("draw", self._draw)
            GLib.timeout_add(1000, lambda: self.queue_draw() or True)

        _iface = None

        def _escuro(self):
            if ClockWidget._iface is None:
                ClockWidget._iface = Gio.Settings.new("org.gnome.desktop.interface")
            return ClockWidget._iface.get_string("color-scheme") == "prefer-dark"

        def _draw(self, area, cr):
            """Relógio do Tahoe (tahoe-dark.jpeg): no escuro, cartão de vidro, mostrador de
            vidro um pouco mais claro com 60 tracinhos (maiores a cada 5), números brancos
            Semibold e ponteiros claros arredondados; no claro, mostrador branco e tinta
            preta. Os estilos Dark/Clear/Tinted mudam cartão e mostrador."""
            w, h = area.get_allocated_width(), area.get_allocated_height()
            style = icon_style()
            escuro = self._escuro()
            cartao = {"dark": (0.04, 0.04, 0.05, 0.86), "clear": (1, 1, 1, 0.10),
                      "tinted": (*accent_rgb(), 0.30)}.get(
                style, (0.16, 0.17, 0.22, 0.50) if escuro else (0.11, 0.11, 0.12, 0.62))
            rounded_rect(cr, 0, 0, w, h, 24)
            cr.set_source_rgba(*cartao)
            cr.fill()
            cx, cy, r = w / 2, h / 2, min(w, h) / 2 - 14
            vidro = style != "default" or escuro          # mostrador de vidro com tinta branca
            cr.arc(cx, cy, r, 0, 2 * math.pi)
            cr.set_source_rgba(*((1, 1, 1, 0.10) if vidro else (1, 1, 1, 1)))
            cr.fill()
            tinta = (1, 1, 1) if vidro else (0, 0, 0)
            cr.set_line_cap(cairo.LINE_CAP_ROUND)
            for i in range(60):                           # tracinhos dos minutos
                a = 2 * math.pi * i / 60
                maior = i % 5 == 0
                r1, r2 = r * 0.95, r * (0.86 if maior else 0.90)
                cr.move_to(cx + math.cos(a) * r1, cy + math.sin(a) * r1)
                cr.line_to(cx + math.cos(a) * r2, cy + math.sin(a) * r2)
                cr.set_line_width(r * (0.022 if maior else 0.011))
                cr.set_source_rgba(*tinta, 0.85 if maior else 0.5)
                cr.stroke()
            lay = PangoCairo.create_layout(cr)
            fd = Pango.FontDescription.from_string("SF Pro Semibold")
            fd.set_absolute_size(r * 0.2 * Pango.SCALE)
            lay.set_font_description(fd)
            cr.set_source_rgb(*tinta)
            for n in range(1, 13):
                a = math.pi / 6 * n - math.pi / 2
                lay.set_text(str(n), -1)
                tw, th = lay.get_pixel_size()
                cr.move_to(cx + math.cos(a) * r * 0.70 - tw / 2, cy + math.sin(a) * r * 0.70 - th / 2)
                PangoCairo.show_layout(cr, lay)
            t = time.localtime()
            ponteiro = (0.86, 0.86, 0.88) if vidro else (0, 0, 0)
            for ang, length, width, col in (
                    ((t.tm_hour % 12 + t.tm_min / 60) / 12, 0.5, r * 0.07, ponteiro),
                    ((t.tm_min + t.tm_sec / 60) / 60, 0.78, r * 0.05, ponteiro),
                    (t.tm_sec / 60, 0.82, r * 0.018, (1.0, 0.58, 0.0))):
                a = 2 * math.pi * ang - math.pi / 2
                cr.move_to(cx, cy)
                cr.line_to(cx + math.cos(a) * r * length, cy + math.sin(a) * r * length)
                cr.set_line_width(width)
                cr.set_source_rgb(*col)
                cr.stroke()
            cr.arc(cx, cy, r * 0.05, 0, 2 * math.pi)
            cr.set_source_rgb(1.0, 0.58, 0.0)
            cr.fill()


    class MonthWidget(Gtk.Box):
        """Calendário do mês (widget pequeno do Calendário): mês em vermelho, dias da
        semana em cinza e o dia de hoje num círculo vermelho."""

        def __init__(self, size="small"):
            super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=4)
            add_class(self, "card", "month-widget")
            self.set_size_request(*WIDGET_SIZES[size])
            self.day = None
            self.refresh()
            GLib.timeout_add_seconds(60, self.refresh)

        def refresh(self):
            import calendar
            today = time.localtime()
            if self.day == today.tm_yday:
                return True
            self.day = today.tm_yday
            for child in self.get_children():
                child.destroy()
            self.pack_start(label(MESES[today.tm_mon - 1].upper(), "cal-month"), False, False, 0)
            grid = Gtk.Grid(column_homogeneous=True, row_spacing=1)
            for col, d in enumerate("SMTWTFS"):
                grid.attach(label(d, "cal-head", xalign=0.5), col, 0, 1, 1)
            cal = calendar.Calendar(firstweekday=6)
            for row, week in enumerate(cal.monthdayscalendar(today.tm_year, today.tm_mon), start=1):
                for col, day in enumerate(week):
                    if day:
                        cls = "cal-day cal-today" if day == today.tm_mday else "cal-day"
                        grid.attach(label(str(day), cls, xalign=0.5), col, row, 1, 1)
            self.pack_start(grid, True, True, 0)
            self.show_all()
            return True


    # Tamanhos dos widgets (pequeno, médio, grande): célula de 204 com vão de 22
    CELL, CELL_GAP = 204, 22
    WIDGET_SIZES = {"small": (CELL, CELL), "medium": (2 * CELL + CELL_GAP, CELL),
                    "large": (2 * CELL + CELL_GAP, 2 * CELL + CELL_GAP)}
    WIDGET_SPAN = {"small": (1, 1), "medium": (2, 1), "large": (2, 2)}
    class BatteryWidget(Gtk.Box):
        """Four device rings, measured against widget-bateria-{1,2}.png.

        UPower supplies both local batteries and Bluetooth peripherals; BlueZ
        Battery1 fills in devices not exported by UPower. No invented percentages.
        """
        def __init__(self, size="medium"):
            super().__init__(orientation=Gtk.Orientation.VERTICAL)
            add_class(self, "card", "battery-widget")
            self.set_size_request(*WIDGET_SIZES[size])
            self.devices = []
            self.pending = False
            self.closed = False
            self.area = Gtk.DrawingArea()
            self.area.connect("draw", self._draw)
            self.pack_start(self.area, True, True, 0)
            self.connect("destroy", self._destroy)
            self.timer = GLib.timeout_add_seconds(30, self._refresh)
            self._refresh()

        def _destroy(self, *_):
            self.closed = True
            GLib.source_remove(self.timer)

        def _refresh(self):
            if self.closed:
                return False
            if self.pending:
                return True
            self.pending = True
            def read():
                devices, seen = [], set()
                try:
                    bus = Gio.bus_get_sync(Gio.BusType.SYSTEM, None)
                    def call(service, path, interface, method, args=None):
                        return bus.call_sync(service, path, interface, method, args, None,
                                             Gio.DBusCallFlags.NONE, 2500, None).unpack()[0]
                    try:
                        paths = call("org.freedesktop.UPower", "/org/freedesktop/UPower",
                                     "org.freedesktop.UPower", "EnumerateDevices")
                    except GLib.Error:
                        paths = []
                    for path in paths:
                        try:
                            props = call("org.freedesktop.UPower", path,
                                         "org.freedesktop.DBus.Properties", "GetAll",
                                         GLib.Variant("(s)", ("org.freedesktop.UPower.Device",)))
                        except GLib.Error:
                            continue
                        if not props.get("IsPresent", True) or props.get("Type") in (1, 0):
                            continue
                        name = props.get("Model") or props.get("NativePath") or "Battery"
                        ident = str(props.get("Serial", "")).lower()
                        if ident:
                            seen.add(ident)
                        devices.append({"name": name, "percent": props.get("Percentage", 0),
                                        "local": props.get("Type") == 2,
                                        "kind": "headphones" if props.get("Type") in (16, 17) else "case",
                                        "charging": props.get("State") == 1})
                    try:
                        managed = call("org.bluez", "/", "org.freedesktop.DBus.ObjectManager",
                                       "GetManagedObjects")
                        for path, interfaces in managed.items():
                            battery = interfaces.get("org.bluez.Battery1")
                            device = interfaces.get("org.bluez.Device1", {})
                            if battery is None or not device.get("Connected"):
                                continue
                            if device.get("Address", "").lower() in seen:
                                continue
                            name = device.get("Alias", "Bluetooth")
                            if any(d["name"].casefold() == name.casefold() for d in devices):
                                continue
                            devices.append({"name": name, "percent": battery["Percentage"],
                                            "local": False, "charging": False,
                                            "kind": "headphones" if device.get("Icon") in
                                                    ("audio-headset", "audio-headphones") else "case"})
                    except GLib.Error:
                        pass
                except GLib.Error:
                    pass
                devices.sort(key=lambda d: not d["local"])
                GLib.idle_add(self._received, devices)
            threading.Thread(target=read, daemon=True).start()
            return True

        def _received(self, devices):
            self.pending = False
            if not self.closed:
                self.devices = devices[:4]
                self.set_tooltip_text("\n".join(f'{d["name"]}: {d["percent"]:.0f}%'
                                               for d in self.devices) or "No battery devices connected")
                self.area.queue_draw()
            return False

        def _draw(self, area, cr):
            width, height = area.get_allocated_width(), area.get_allocated_height()
            slots = 4
            step = width / slots
            # Reference card: 234×111, rings 43 px with centers 55 px apart.
            # Preserve those ratios within the established medium widget footprint.
            radius = step * 43 / 110
            cy = height * 0.40
            fg = self.get_style_context().get_color(Gtk.StateFlags.NORMAL)
            for i in range(slots):
                cx = step * (i + 0.5)
                cr.set_line_width(radius * 0.18)
                cr.set_source_rgba(fg.red, fg.green, fg.blue, 0.16)
                cr.new_sub_path()
                cr.arc(cx, cy, radius, 0, math.tau)
                cr.stroke()
                if i >= len(self.devices):
                    continue
                d = self.devices[i]
                pct = max(0, min(100, d["percent"]))
                ctx = self.get_style_context()
                parent = self
                clear = False
                while parent is not None:
                    clear = clear or parent.get_style_context().has_class("estilo-clear")
                    parent = parent.get_parent()
                color_name = "battery_low" if pct <= 10 else "battery_full"
                found, color = ctx.lookup_color(color_name)
                if found and not clear:
                    cr.set_source_rgba(color.red, color.green, color.blue, color.alpha)
                else:
                    cr.set_source_rgba(fg.red, fg.green, fg.blue, fg.alpha)
                cr.set_line_cap(cairo.LINE_CAP_ROUND)
                if pct:
                    cr.new_sub_path()
                    cr.arc(cx, cy, radius, -math.pi / 2, -math.pi / 2 + math.tau * pct / 100)
                    cr.stroke()
                cr.set_source_rgba(fg.red, fg.green, fg.blue, fg.alpha)
                cr.set_line_width(1.5)
                if d["local"]:
                    cr.rectangle(cx-radius*.375, cy-radius*.24, radius*.75, radius*.48)
                    cr.move_to(cx-radius*.5, cy+radius*.29)
                    cr.line_to(cx+radius*.5, cy+radius*.29)
                    cr.stroke()
                elif d.get("kind") == "headphones":
                    # Two earbuds and stems, as in widget-bateria-{1,2}.png.
                    for sign in (-1, 1):
                        ex = cx + sign * radius * 0.22
                        cr.new_sub_path()
                        cr.arc(ex, cy-radius*.10, radius*.15, 0, math.tau)
                        cr.fill()
                        # Speaker grille inside each bud, visible in the reference.
                        cr.set_source_rgba(0, 0, 0, 0.35)
                        cr.arc(ex, cy-radius*.10, radius*.045, 0, math.tau)
                        cr.fill()
                        cr.set_source_rgba(fg.red, fg.green, fg.blue, fg.alpha)
                        rounded_rect(cr, ex-radius*.04, cy-radius*.03,
                                     radius*.08, radius*.37, radius*.04)
                        cr.fill()
                else:
                    rounded_rect(cr, cx-radius*.35, cy-radius*.27,
                                 radius*.7, radius*.64, radius*.16)
                    cr.fill()
                    cr.set_source_rgba(0, 0, 0, 0.25)
                    cr.move_to(cx-radius*.29, cy-radius*.07)
                    cr.line_to(cx+radius*.29, cy-radius*.07)
                    cr.stroke()
                cr.set_source_rgba(fg.red, fg.green, fg.blue, fg.alpha)
                if d["charging"]:
                    # Reference places the charging mark on the top of the ring.
                    cr.save()
                    if d["local"]:
                        # widget-bateria-1: orange power badge at the upper-left rim.
                        cr.translate(cx - radius*.37, cy - radius*.93)
                        found, badge = ctx.lookup_color("battery_charging")
                        if found:
                            cr.set_source_rgba(badge.red, badge.green, badge.blue, badge.alpha)
                            cr.new_sub_path()
                            cr.arc(0, 0, radius*.17, 0, math.tau)
                            cr.fill()
                            cr.set_source_rgba(fg.red, fg.green, fg.blue, fg.alpha)
                    else:
                        cr.translate(cx, cy - radius)
                    cr.move_to(2, -7)
                    cr.line_to(-4, 1)
                    cr.line_to(0, 1)
                    cr.line_to(-2, 7)
                    cr.line_to(4, -1)
                    cr.line_to(0, -1)
                    cr.close_path()
                    cr.fill()
                    cr.restore()
                layout = PangoCairo.create_layout(cr)
                layout.set_font_description(self.get_style_context().get_font(Gtk.StateFlags.NORMAL))
                layout.set_text(f"{pct:.0f}%", -1)
                tw, th = layout.get_pixel_size()
                cr.move_to(cx-tw/2, cy+radius+12)
                PangoCairo.show_layout(cr, layout)
            return False


    # tipo → (nome na galeria, tamanhos disponíveis, construtor)
    WIDGET_KINDS = {
        "battery":   ("Baterias", ("medium",), BatteryWidget),
        "weather":   ("Tempo", ("small", "medium"), WeatherWidget),
        "calendar":  ("Calendário", ("small",), MonthWidget),
        "clock":     ("Relógio", ("small",), ClockWidget),
        "photo":     ("Fotos", ("small", "medium", "large"), PhotoWidget),
        "shortcuts": ("Atalhos", ("small",), lambda size="small": ShortcutsWidget()),
    }
    SIZE_NAMES = {"small": "Small", "medium": "Medium", "large": "Large"}
    WIDGETS_PATH = os.path.expanduser("~/.config/hyprmac/widgets.json")
    WIDGETS_DEFAULT = [{"kind": "weather", "size": "medium"}, {"kind": "shortcuts", "size": "small"},
                       {"kind": "photo", "size": "small"}]


    class DesktopWidgets:
        """Widgets da mesa como no macOS: grade de 2 colunas no canto superior esquerdo,
        atrás das janelas; esmaecem quando há janela ativa nesta tela e voltam inteiros
        com a mesa vazia. Botão direito na mesa ou num widget: menu com tamanhos,
        "Remove Widget", "Edit Widgets…" (galeria com + e o "−" em cada widget) e
        "Change Wallpaper…". O arranjo fica em ~/.config/hyprmac/widgets.json."""

        DIM = 0.45

        def __init__(self, monitor, wallpaper=None):
            self.monitor = monitor
            self.items = self._load()
            self.editing = False
            self.gallery = None
            self.opacity, self._fade = 1.0, None
            self.win = layer_window("hyprmac-widgets", LS.Layer.BOTTOM, monitor,
                                    anchors=(E.TOP, E.LEFT), margins={E.TOP: 20, E.LEFT: 20})
            self.grid = Gtk.Grid(row_spacing=CELL_GAP, column_spacing=CELL_GAP)
            self.win.add(self.grid)
            self.grid.drag_dest_set(Gtk.DestDefaults.ALL,
                                    [Gtk.TargetEntry.new("application/x-hyprmac-widget", 0, 0)],
                                    Gdk.DragAction.MOVE | Gdk.DragAction.COPY)
            self.grid.connect("drag-data-received", self._drop_widget)
            self.style = None
            self.set_style(icon_style())
            WIDGET_SETS.append(self)
            self._build()
            self.win.show_all()
            for win in (wallpaper.windows if wallpaper else []):
                win.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
                win.connect("button-press-event", lambda _w, ev: self._desk_click(ev, None))
            hypr_events(self._event)
            GLib.idle_add(self._update_dim)

        def set_style(self, style):
            """Default / Dark / Clear (vidro) / Tinted (cor de destaque), como os ícones."""
            for st in ICON_STYLES:
                set_class(self.win, "estilo-" + st, st == style)
            if style != self.style:
                self.style = style
                self.grid.queue_draw()

        # ── arranjo ──
        def _load(self):
            try:
                with open(WIDGETS_PATH) as f:
                    items = [i for i in json.load(f) if i.get("kind") in WIDGET_KINDS]
                for i in items:
                    if i.get("size") not in WIDGET_KINDS[i["kind"]][1]:
                        i["size"] = WIDGET_KINDS[i["kind"]][1][0]
                return items
            except (OSError, ValueError, AttributeError, TypeError):
                return [dict(i) for i in WIDGETS_DEFAULT]

        def _save(self):
            try:
                os.makedirs(os.path.dirname(WIDGETS_PATH), exist_ok=True)
                with open(WIDGETS_PATH, "w") as f:
                    json.dump(self.items, f, indent=1)
            except OSError:
                pass

        def _build(self):
            for child in self.grid.get_children():
                child.destroy()
            rows = []                          # ocupação: rows[r] = [col0, col1]

            def free(r, c, w, h):
                return c + w <= 2 and all(r + dr >= len(rows) or not rows[r + dr][c + dc]
                                          for dr in range(h) for dc in range(w))
            for idx, it in enumerate(self.items):
                w, h = WIDGET_SPAN[it["size"]]
                r = 0
                while True:
                    c = next((c for c in range(2) if free(r, c, w, h)), None)
                    if c is not None:
                        break
                    r += 1
                while len(rows) < r + h:
                    rows.append([False, False])
                for dr in range(h):
                    for dc in range(w):
                        rows[r + dr][c + dc] = True
                self.grid.attach(self._wrap(idx, it), c, r, w, h)
            self.grid.show_all()

        def _wrap(self, idx, it):
            """Widget + o "−" do modo de edição (canto superior esquerdo, como no Mac)."""
            overlay = Gtk.Overlay()
            overlay.widget_index = idx
            box = Gtk.EventBox()
            box.add(WIDGET_KINDS[it["kind"]][2](it["size"]))
            box.connect("button-press-event", lambda _w, ev, i=idx: self._desk_click(ev, i))
            overlay.add(box)
            if self.editing:
                box.drag_source_set(Gdk.ModifierType.BUTTON1_MASK,
                                    [Gtk.TargetEntry.new("application/x-hyprmac-widget", 0, 0)],
                                    Gdk.DragAction.MOVE)
                box.connect("drag-data-get", lambda _w, _c, data, _i, _t:
                            data.set(data.get_target(), 8, f"move:{idx}".encode()))
                minus = Gtk.Button()
                add_class(minus, "widget-remove")
                minus.add(label("−", None, 0.5))
                minus.set_halign(Gtk.Align.START)
                minus.set_valign(Gtk.Align.START)
                minus.connect("clicked", lambda _b, i=idx: self.remove(i))
                overlay.add_overlay(minus)
            return overlay

        def _drop_widget(self, _w, context, x, y, data, _info, stamp):
            success = False
            try:
                payload = bytes(data.get_data()).decode().split(":")
                # Find the actual allocation under the pointer, including mixed sizes.
                target = len(self.items)
                for child in self.grid.get_children():
                    alloc = child.get_allocation()
                    if alloc.x <= x < alloc.x + alloc.width and alloc.y <= y < alloc.y + alloc.height:
                        target = child.widget_index
                        break
                if payload[0] == "move" and self.editing:
                    source = int(payload[1])
                    if 0 <= source < len(self.items):
                        item = self.items.pop(source)
                        self.items.insert(min(target, len(self.items)), item)
                        success = True
                elif payload[0] == "add" and self.editing:
                    kind, size = payload[1:]
                    if kind in WIDGET_KINDS and size in WIDGET_KINDS[kind][1]:
                        self.items.insert(target, {"kind": kind, "size": size})
                        success = True
                if success:
                    self._save()
                    GLib.idle_add(self._build)
            except (ValueError, IndexError, UnicodeError):
                pass
            Gtk.drag_finish(context, success, False, stamp)

        def add(self, kind, size):
            self.items.append({"kind": kind, "size": size})
            self._save()
            self._build()

        def remove(self, idx):
            if 0 <= idx < len(self.items):
                self.items.pop(idx)
                self._save()
                self._build()

        def resize(self, idx, size):
            self.items[idx]["size"] = size
            self._save()
            self._build()

        # ── menus ──
        def _desk_click(self, ev, idx):
            if ev.button != 3:
                return False
            m = Gtk.Menu()
            m.set_reserve_toggle_size(False)
            add_class(m, "hyprmac-menu")

            def item(text, action, sensitive=True, check=None):
                it = Gtk.MenuItem(label=text)
                it.set_sensitive(sensitive)
                if check is not None:
                    menu_check(it, check)
                it.connect("activate", lambda _i: action())
                m.append(it)
            # Tahoe (video/frames-ui/ui_0073): cabeçalho "Size", tamanhos com ✓, Remove Widget,
            # Edit Widgets…; no fundo vazio (ui_0183) Change Wallpaper… e Edit Widgets… juntos.
            if idx is not None:
                cur = self.items[idx]
                m.append(menu_header("Size"))
                for size in WIDGET_KINDS[cur["kind"]][1]:
                    item(SIZE_NAMES[size], lambda s=size: self.resize(idx, s), check=size == cur["size"])
                m.append(Gtk.SeparatorMenuItem())
                item("Remove Widget", lambda: self.remove(idx))
                m.append(Gtk.SeparatorMenuItem())
            else:
                item("Change Wallpaper…", lambda: open_settings("wallpaper"))
            item("Edit Widgets…", self.edit)
            m.show_all()
            menu_check_column(m)
            m.popup_at_pointer(ev)
            self._menu = m                     # mantém vivo até fechar
            return True

        # ── edição (galeria) ──
        def edit(self):
            if self.gallery:
                return
            self.editing = True
            self._set_opacity(1.0, animate=False)
            self._build()
            self.gallery = WidgetGallery(self, self.monitor)

        def done(self):
            self.editing = False
            if self.gallery:
                self.gallery.win.destroy()
                self.gallery = None
            self._build()
            self._update_dim()

        # ── esmaecer com janela ativa ──
        def _event(self, line):
            if line.split(">>", 1)[0] in ("activewindowv2", "openwindow", "closewindow", "workspacev2",
                                          "movewindowv2", "focusedmonv2", "changefloatingmode"):
                self._update_dim()
            return False

        def _update_dim(self):
            if self.editing:
                return False
            name = None
            for mname, g in gdk_monitors()[0].items():
                if g == self.monitor:
                    name = mname
            mon = next((m for m in hypr_json("monitors") if m["name"] == name), None)
            ativa = hypr_json("activewindow") or {}
            dim = bool(mon and ativa.get("address") and ativa.get("monitor") == mon["id"]
                       and not ativa.get("workspace", {}).get("name", "").startswith("special")
                       and ativa.get("workspace", {}).get("id") == mon["activeWorkspace"]["id"])
            self._set_opacity(self.DIM if dim else 1.0)
            return False

        def _set_opacity(self, target, animate=True):
            if self._fade:
                GLib.source_remove(self._fade)
                self._fade = None
            if not animate or reduce_motion():
                self.opacity = target
                self.win.set_opacity(target)
                return
            start, t0 = self.opacity, time.monotonic()

            def step():
                k = min(1.0, (time.monotonic() - t0) / 0.25)
                self.opacity = start + (target - start) * (1 - (1 - k) ** 3)
                self.win.set_opacity(self.opacity)
                if k >= 1.0:
                    self._fade = None
                    return False
                return True
            self._fade = GLib.timeout_add(16, step)


    class DesktopIcons:
        """Ícones da Mesa (~/Desktop) como no Finder: colunas a partir do canto superior
        direito, ícone de 64 com o nome embaixo (Regular 12, branco com sombra, até 2
        linhas). Clique seleciona (fundo cinza no ícone, nome numa cápsula na cor de
        destaque); duplo clique abre; botão direito: Open e Move to Trash. Atualiza
        sozinho quando a pasta muda."""

        CELL_W, CELL_H, ICON = 100, 104, 64

        def __init__(self, monitor, wallpaper=None):
            self.dir = GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_DESKTOP) \
                or os.path.expanduser("~/Desktop")
            self.sel = None
            self.win = layer_window("hyprmac-desktop-icons", LS.Layer.BOTTOM, monitor,
                                    anchors=(E.TOP, E.RIGHT), margins={E.TOP: 12, E.RIGHT: 10})
            add_class(self.win, "desktop-icons")
            self.grid = Gtk.Grid(row_spacing=0, column_spacing=0)
            self.win.add(self.grid)
            self.monitor = monitor
            self.refresh()
            self.win.show_all()
            for w in (wallpaper.windows if wallpaper else []):     # clique na mesa: tira a seleção
                w.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
                w.connect("button-press-event", lambda _w, ev: ev.button == 1 and self._deselect() and False)
            if os.path.isdir(self.dir):
                self.mon = Gio.File.new_for_path(self.dir).monitor_directory(Gio.FileMonitorFlags.NONE, None)
                self.mon.connect("changed", lambda *_: GLib.timeout_add(300, self.refresh))

        def _items(self):
            try:
                nomes = sorted(n for n in os.listdir(self.dir) if not n.startswith("."))
            except OSError:
                return []
            itens = []
            for n in nomes:
                path = os.path.join(self.dir, n)
                nome, pb = n, None
                size = self.ICON * max(1, self.win.get_scale_factor())
                if n.endswith(".desktop"):
                    try:
                        info = Gio.DesktopAppInfo.new_from_filename(path)
                    except TypeError:
                        info = None
                    if info:
                        nome = info.get_name() or n
                        icon = info.get_icon()
                        if icon:
                            look = Gtk.IconTheme.get_default().lookup_by_gicon(
                                icon, size, Gtk.IconLookupFlags.FORCE_SIZE)
                            try:
                                pb = look.load_icon() if look else None
                            except GLib.Error:
                                pb = None
                if pb is None:
                    try:
                        fi = Gio.File.new_for_path(path).query_info(
                            "standard::icon,thumbnail::path", Gio.FileQueryInfoFlags.NONE, None)
                        thumb = fi.get_attribute_byte_string("thumbnail::path")
                        if thumb:
                            pb = GdkPixbuf.Pixbuf.new_from_file_at_scale(thumb, size, size, True)
                        else:
                            look = Gtk.IconTheme.get_default().lookup_by_gicon(
                                fi.get_icon(), size, Gtk.IconLookupFlags.FORCE_SIZE)
                            pb = look.load_icon() if look else None
                    except GLib.Error:
                        pb = None
                itens.append((path, nome, pb))
            return itens

        def refresh(self):
            for child in self.grid.get_children():
                child.destroy()
            geo = self.monitor.get_geometry() if self.monitor else None
            rows = max(1, ((geo.height if geo else 1080) - 34 - 12 - 110) // self.CELL_H)
            itens = self._items()
            cols = (len(itens) + rows - 1) // rows
            for k, (path, nome, pb) in enumerate(itens):
                col, row = cols - 1 - k // rows, k % rows      # de cima para baixo, da direita
                self.grid.attach(self._cell(path, nome, pb), col, row, 1, 1)
            self.grid.show_all()
            return False

        def _cell(self, path, nome, pb):
            ev = Gtk.EventBox()
            ev.set_size_request(self.CELL_W, self.CELL_H)
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=3)
            box.set_halign(Gtk.Align.CENTER)
            frame = Gtk.Box()
            add_class(frame, "di-icon")
            frame.set_halign(Gtk.Align.CENTER)
            area = Gtk.DrawingArea()
            area.set_size_request(self.ICON, self.ICON)
            cache = {}
            area.connect("draw", lambda a, cr: pb and paint_cover(
                cr, pb, a.get_allocated_width(), a.get_allocated_height(), radius=0, cache=cache))
            frame.add(area)
            lb = label(nome, "di-label", 0.5)
            lb.set_justify(Gtk.Justification.CENTER)
            lb.set_line_wrap(True)
            lb.set_line_wrap_mode(2)
            lb.set_lines(2)
            lb.set_ellipsize(Pango.EllipsizeMode.END)
            lb.set_max_width_chars(14)
            lb.set_halign(Gtk.Align.CENTER)
            box.pack_start(frame, False, False, 0)
            box.pack_start(lb, False, False, 0)
            ev.add(box)
            if path.endswith(".desktop"):
                ev.drag_source_set(Gdk.ModifierType.BUTTON1_MASK,
                                   [Gtk.TargetEntry.new("text/uri-list", 0, 0)],
                                   Gdk.DragAction.COPY)
                ev.connect("drag-data-get", lambda _w, _context, data, _info, _time, p=path:
                           data.set_uris([Gio.File.new_for_path(p).get_uri()]))
            ev.connect("button-press-event", lambda _w, e, p=path, c=(frame, lb): self._click(e, p, c))
            return ev

        def _deselect(self):
            if self.sel:
                for w in self.sel[1]:
                    set_class(w, "selected", False)
            self.sel = None

        def _select(self, path, cell):
            if self.sel:
                for w in self.sel[1]:
                    set_class(w, "selected", False)
            self.sel = (path, cell)
            for w in cell:
                set_class(w, "selected", True)

        def _open(self, path):
            if path.endswith(".desktop"):
                spawn("gio launch " + GLib.shell_quote(path))
            else:
                spawn("xdg-open " + GLib.shell_quote(path))

        def _click(self, ev, path, cell):
            self._select(path, cell)
            if ev.button == 1 and ev.type == Gdk.EventType._2BUTTON_PRESS:
                self._open(path)
            elif ev.button == 3:
                m = Gtk.Menu()
                m.set_reserve_toggle_size(False)
                add_class(m, "hyprmac-menu")
                for texto, acao in (("Open", lambda: self._open(path)), (None, None),
                                    ("Move to Trash", lambda: spawn("gio trash " + GLib.shell_quote(path)))):
                    if texto is None:
                        m.append(Gtk.SeparatorMenuItem())
                        continue
                    it = Gtk.MenuItem(label=texto)
                    it.connect("activate", lambda _i, a=acao: a())
                    m.append(it)
                m.show_all()
                m.popup_at_pointer(ev)
                self._menu = m
            return True


    class WidgetGallery:
        """Galeria "Edit Widgets" (painel de vidro na parte de baixo da tela, como no
        macOS): categorias à esquerda, prévias nos tamanhos disponíveis com "+" e o
        botão azul Done. Clicar numa prévia (ou no +) adiciona o widget na mesa."""

        def __init__(self, desk, monitor):
            self.desk = desk
            self.win = layer_window("hyprmac-widget-gallery", LS.Layer.TOP, monitor,
                                    anchors=(E.BOTTOM,), margins={E.BOTTOM: 24},
                                    keyboard=LS.KeyboardMode.ON_DEMAND)
            add_class(self.win, "widget-gallery")
            self.win.connect("key-press-event",
                             lambda _w, ev: ev.keyval == Gdk.KEY_Escape and desk.done())
            outer = Gtk.Box(spacing=0)
            add_class(outer, "wg-panel")
            side = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
            add_class(side, "wg-side")
            side.pack_start(label("Widgets", "wg-title"), False, False, 0)
            self.right = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
            add_class(self.right, "wg-content")
            self.buttons = {}
            for kind, (nome, _sizes, _ctor) in WIDGET_KINDS.items():
                b = Gtk.Button()
                b.add(label(nome, None, 0.0))
                add_class(b, "wg-cat")
                b.connect("clicked", lambda _b, k=kind: self.show(k))
                side.pack_start(b, False, False, 0)
                self.buttons[kind] = b
            outer.pack_start(side, False, False, 0)
            outer.pack_start(self.right, True, True, 0)
            self.win.add(outer)
            self.show(next(iter(WIDGET_KINDS)))
            self.win.show_all()

        def show(self, kind):
            for k, b in self.buttons.items():
                set_class(b, "selected", k == kind)
            for child in self.right.get_children():
                child.destroy()
            nome, sizes, ctor = WIDGET_KINDS[kind]
            self.right.pack_start(label(nome, "wg-head"), False, False, 0)
            row = Gtk.Box(spacing=18)
            for size in sizes:
                col = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
                prev = Gtk.Overlay()
                frame = Gtk.EventBox()
                w = ctor(size)
                frame.add(w)
                frame.drag_source_set(Gdk.ModifierType.BUTTON1_MASK,
                                      [Gtk.TargetEntry.new("application/x-hyprmac-widget", 0, 0)],
                                      Gdk.DragAction.COPY)
                frame.connect("drag-data-get", lambda _w, _c, data, _i, _t, k=kind, s=size:
                              data.set(data.get_target(), 8, f"add:{k}:{s}".encode()))
                frame._was_drag = False
                frame.connect("button-press-event", lambda w, ev: setattr(w, "_was_drag", False) or False)
                frame.connect("drag-begin", lambda w, _c: setattr(w, "_was_drag", True))
                frame.connect("button-release-event", lambda w, ev, s=size:
                              ev.button == 1 and not w._was_drag and self.desk.add(kind, s))
                prev.add(frame)
                plus = Gtk.Button()
                add_class(plus, "widget-add")
                plus.add(label("+", None, 0.5))
                plus.set_halign(Gtk.Align.START)
                plus.set_valign(Gtk.Align.START)
                plus.connect("clicked", lambda _b, s=size: self.desk.add(kind, s))
                prev.add_overlay(plus)
                col.pack_start(prev, False, False, 0)
                col.pack_start(label(SIZE_NAMES[size], "wg-size", 0.5), False, False, 0)
                row.pack_start(col, False, False, 0)
            self.right.pack_start(row, False, False, 0)
            foot = Gtk.Box()
            done = Gtk.Button(label="Done")
            add_class(done, "suggested-action", "wg-done")
            done.connect("clicked", lambda _b: self.desk.done())
            foot.pack_end(done, False, False, 0)
            self.right.pack_end(foot, False, False, 0)
            self.right.show_all()

    return Wallpaper, DesktopWidgets, DesktopIcons
