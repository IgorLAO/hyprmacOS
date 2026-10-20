"""GTK view for the Dock. The shell supplies its shared UI and compositor services."""
import json
import math
import os
import shutil
import subprocess
import time

import cairo
import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
gi.require_version("GdkPixbuf", "2.0")
gi.require_version("GtkLayerShell", "0.1")
gi.require_version("PangoCairo", "1.0")
from gi.repository import Gdk, GdkPixbuf, Gio, GLib, Gtk, Pango, PangoCairo
from gi.repository import GtkLayerShell as LS

from dock_geometry import DockMetrics
from dock_model import build_items as dock_items, needs_refresh as dock_needs_refresh, reorder_pinned, pin_slot, insert_pin
from dock_motion import DockMotion
from dock_drop import supports_documents as dock_supports_documents, open_documents as dock_open_documents, desktop_file_from_uris
from glass_motion import spring_step
from folder_appearance import folder_pixbuf, folder_color

E = LS.Edge
DOCK_PATH = os.path.expanduser("~/.config/hyprmac/dock.json")
DOCK_ICONS = os.path.join(os.path.dirname(__file__), "icones")
DOCK_SIDE = 120
TRASH_DIR = os.path.expanduser("~/.local/share/Trash/files")


def desktop_id(info):
    return (info.get_id() or "").removesuffix(".desktop") if info else ""


def info_for_command(cmd):
    words = [w for w in cmd.split() if w != "env" and "=" not in w]
    exe = os.path.basename(words[0]) if words else ""
    for info in Gio.AppInfo.get_all():
        if isinstance(info, Gio.DesktopAppInfo) and \
                os.path.basename(info.get_executable() or "") == exe:
            return info
    return None


def app_info(app_id):
    try:
        if os.path.isabs(app_id):
            return Gio.DesktopAppInfo.new_from_filename(app_id) if os.path.isfile(app_id) else None
        return Gio.DesktopAppInfo.new(app_id + ".desktop")
    except TypeError:
        return None


def create_dock_class(*, CFG, A11Y, DOCKS, ROOT, ShellMenu, add_class,
                      dispatch, display_name, hypr_events, hypr_json,
                      icon_style_effective, in_thread, layer_window,
                      menu_check, menu_check_column, open_settings,
                      reduce_motion, rounded_rect, run, spawn,
                      styled_icon, ui_sound):
    """Bind shell services once; Dock instances share the existing event bus."""
    class Dock:
        def __init__(self, monitor, apps):
            self.apps = apps
            self.metrics = DockMetrics.from_icon(CFG.get("dock_icon", 46))
            for name, value in vars(self.metrics).items():
                setattr(self, name, value)
            self.above = round(self.icon * 1.15)      # espaço acima: rótulo e quique

            self.pinned, self.autohide = self._load()
            self.notifs = None       # NotificationCenter: selos vermelhos de contagem
            self.style, self._style_cache = icon_style_effective(), {}
            self._thumbs = {}        # endereço → miniatura da janela minimizada
            self._thumb_tries = {}
            DOCKS.append(self)
            self.items = []          # dicts: key, kind, name, info, pb, windows, x
            self.hover = self.pressed = None
            self.motion = DockMotion(spring_step)
            self._motion_tick = None
            self._pointer_x = None    # x do ponteiro sobre o Dock, para a curva gaussiana de magnificação
            self.shown = 1.0         # 0 = escondido (ocultar automaticamente)
            self._slide_velocity = 0.0
            self._anim = self._hide_timer = self._refresh_id = None
            self._pb_cache = {}
            self.theme = Gio.Settings.new("org.gnome.desktop.interface")
            self.theme.connect("changed::color-scheme", lambda *_: self._retheme())
            self.light = self.theme.get_string("color-scheme") != "prefer-dark"

            fm = info_for_command(CFG.get("file_manager", "nautilus"))
            st = info_for_command(CFG.get("settings", "gnome-control-center"))
            self.special_ids = {"hyprmac:finder": desktop_id(fm), "hyprmac:settings": desktop_id(st)}
            self.special_info = {"hyprmac:finder": fm, "hyprmac:settings": st}

            self.win = layer_window("hyprmac-dock", LS.Layer.TOP, monitor, anchors=(E.BOTTOM,))
            self.area = Gtk.DrawingArea()
            self.area.add_events(Gdk.EventMask.POINTER_MOTION_MASK | Gdk.EventMask.BUTTON_PRESS_MASK |
                                 Gdk.EventMask.BUTTON_RELEASE_MASK | Gdk.EventMask.LEAVE_NOTIFY_MASK |
                                 Gdk.EventMask.ENTER_NOTIFY_MASK)
            self.area.connect("draw", self._draw)
            self.area.connect("unmap", self._stop_motion_frames)
            self.area.connect("motion-notify-event", self._motion)
            self.area.connect("leave-notify-event", self._leave)
            self.area.connect("enter-notify-event", lambda *_: self._cancel_hide())
            self.area.connect("button-press-event", self._press)
            self.area.connect("button-release-event", self._release)
            # Somente destino: o drag interno continua com o grab de ponteiro existente.
            self.area.drag_dest_set(Gtk.DestDefaults(0),
                                    [Gtk.TargetEntry.new("text/uri-list", 0, 0)], Gdk.DragAction.COPY)
            self.area.connect("drag-motion", self._document_drag_motion)
            self.area.connect("drag-leave", self._document_drag_leave)
            self.area.connect("drag-drop", self._document_drop)
            self.area.connect("drag-data-received", self._document_received)
            self.win.add(self.area)
            self.win.connect("key-press-event", self._key)
            self.win.connect("focus-out-event", lambda *_: self._end_keyboard())

            # faixa de 2 px na borda de baixo: mostra o Dock quando ele se esconde sozinho
            self.trigger = layer_window("hyprmac-dock-trigger", LS.Layer.TOP, monitor,
                                        anchors=(E.BOTTOM, E.LEFT, E.RIGHT), exclusive=0)
            self.trigger.set_size_request(-1, 2)
            self.trigger.add_events(Gdk.EventMask.ENTER_NOTIFY_MASK)
            self.trigger.connect("enter-notify-event", lambda *_: self._reveal())
            self.trigger.connect("draw", lambda _w, cr: (cr.set_operator(cairo.OPERATOR_CLEAR),
                                                        cr.paint()) and False)

            self.refresh()
            self._apply_autohide(initial=True)
            self.win.show_all()
            self._update_input_region(0)
            hypr_events(self._event)
            GLib.timeout_add_seconds(4, self._poll_trash)

        # ── estado salvo ──
        def _load(self):
            try:
                with open(DOCK_PATH) as f:
                    d = json.load(f)
                return list(d.get("pinned", [])), bool(d.get("autohide", False))
            except (OSError, ValueError, AttributeError):
                pass
            pinned = ["hyprmac:finder", "hyprmac:apps"]
            browser = run("xdg-settings get default-web-browser").removesuffix(".desktop")
            term = desktop_id(info_for_command(CFG.get("terminal", "")))
            for cand in (browser, term, "spotify-launcher", "spotify",
                         "code", "md.obsidian.Obsidian", "discord"):
                if cand and cand not in pinned and app_info(cand):
                    pinned.append(cand)
            return pinned + ["hyprmac:settings"], False

        def _save(self):
            try:
                os.makedirs(os.path.dirname(DOCK_PATH), exist_ok=True)
                with open(DOCK_PATH, "w") as f:
                    json.dump({"pinned": self.pinned, "autohide": self.autohide}, f, indent=1)
            except OSError:
                pass

        # ── conteúdo ──
        def _key_of_class(self, cls):
            info = self.apps._info(cls)
            return desktop_id(info).lower() if info else "class:" + (cls or "").lower()

        def _pixbuf(self, kind, info=None, cls=None):
            size = self.icon * max(1, self.win.get_scale_factor())
            kit = {"finder": "Finder", "apps": "Apps", "settings": "System_Settings",
                   "trash": "Trash_Full" if self._trash_full() else "Trash_Empty"}.get(kind)
            key = (kind, kit, desktop_id(info) or cls, self.light, size,
                   folder_color() if kind == "downloads" else None)
            if key in self._pb_cache:
                return self._pb_cache[key]
            pb = None
            try:
                if kit:
                    variant = "Default" if self.light else "Dark"
                    pb = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                        os.path.join(DOCK_ICONS, f"{kit}-{variant}.png"), size, size, True)
                elif kind == "downloads":
                    pb = folder_pixbuf(size)
                elif info and info.get_icon():
                    look = Gtk.IconTheme.get_default().lookup_by_gicon(
                        info.get_icon(), size, Gtk.IconLookupFlags.FORCE_SIZE)
                    pb = look.load_icon() if look else None
            except GLib.Error:
                pb = None
            if pb is None and cls:
                pb = self.apps.lookup(cls)[1]
            self._pb_cache[key] = pb
            return pb

        def _capture_thumb(self, c):
            """Captura a janela minimizada (grim -T, funciona mesmo fora da tela) uma vez."""
            addr, sid = c["address"], c.get("stableId")
            if not sid or addr in self._thumbs:
                return False
            self._thumbs[addr] = None

            def work():
                try:
                    out = subprocess.run(["grim", "-T", str(sid), "-"], capture_output=True,
                                         timeout=3).stdout
                    loader = GdkPixbuf.PixbufLoader()
                    loader.write(out)
                    loader.close()
                    pb = loader.get_pixbuf()
                    k = self.icon * 2 / max(pb.get_width(), pb.get_height())
                    pb = pb.scale_simple(max(1, round(pb.get_width() * k)),
                                         max(1, round(pb.get_height() * k)), GdkPixbuf.InterpType.BILINEAR)
                except Exception:
                    pb = None

                def done():
                    if pb is None:                 # janela ainda em transição: tenta de novo
                        tries = self._thumb_tries.get(addr, 0) + 1
                        self._thumb_tries[addr] = tries
                        self._thumbs.pop(addr, None)
                        if tries < 4:
                            GLib.timeout_add(600 * tries, lambda: self._capture_thumb(c) and False)
                    else:
                        self._thumbs[addr] = pb
                        self.area.queue_draw()
                    return False
                GLib.idle_add(done)
            in_thread(work)

        def refresh(self):
            self._refresh_id = None
            pinned_items = []
            for p in self.pinned:
                if p == "hyprmac:apps":
                    pinned_items.append(dict(key=p, pin=p, kind="apps", name="Apps", info=None, cls=None))
                    continue
                if p in self.special_ids:
                    info, kind = self.special_info[p], p.split(":")[1]
                    key = self.special_ids[p].lower()
                else:
                    info, kind = app_info(p), "app"
                    if info is None:
                        continue
                    key = (desktop_id(info) or p).lower() if os.path.isabs(p) else p.lower()
                pinned_items.append(dict(key=key, pin=p, kind=kind, info=info, cls=None,
                                         name=info.get_name() if info else p))
            items = dock_items(hypr_json("clients"), pinned_items, self._key_of_class,
                               self.apps._info, display_name)
            minimized = {it["win"]["address"] for it in items if it["kind"] == "minimized"}
            for addr in [a for a in self._thumbs if a not in minimized]:
                del self._thumbs[addr]
            for it in items:
                if it["kind"] == "sep":
                    continue
                kind = "app" if it["kind"] == "minimized" else it["kind"]
                it["pb"] = self._pixbuf(kind, it.get("info"), it.get("cls") or
                                        (it["windows"][0].get("class") if it["windows"] else None))
                if it["windows"]:
                    self.motion.bounces.pop(it["key"], None)
                if it["kind"] == "minimized":
                    self._capture_thumb(it["win"])
            # Snapshots podem chegar durante o gesto: o índice muda, a identidade não.
            pressed_key = getattr(self, "_pressed_key", None)
            self.items = items
            if pressed_key is not None:
                self.pressed = next((i for i, it in enumerate(items) if it["key"] == pressed_key), None)
                if self.pressed is None:
                    self.dragging = False
                    self._pressed_key = None
                    self._drag_remove = False
            self._layout()
            return False

        def _layout(self):
            self.motion.retain_positions(self.items)
            self.w = self.metrics.layout(self.items)
            style = self._label_style()
            state = Gtk.StateFlags.NORMAL
            padding = style.get_padding(state)
            layout = self.area.create_pango_layout("Ag")
            layout.set_font_description(style.get_font(state))
            label_h = max(style.get_property("min-height", state),
                          layout.get_pixel_size()[1] + padding.top + padding.bottom)
            # A layer surface intercepta cliques mesmo onde é transparente em alguns
            # compositores. Mantenha só a faixa necessária aos ícones ampliados.
            self.above = math.ceil(max(self.icon * 0.7, label_h + 2))
            W, H = self.w + 2 * DOCK_SIDE, self.above + self.h + self.bottom
            self.area.set_size_request(W, H)
            self.win.resize(W, H)
            self._draw_geom = {}
            self._update_input_region(0)
            self.area.queue_draw()

        def _update_input_region(self, growth):
            # A região acompanha o vidro e os ícones ampliados, mas não o tooltip:
            # mover para a parte alta do ícone não pode disparar leave/collapse.
            left = math.floor(DOCK_SIDE - growth / 2)
            right = math.ceil(DOCK_SIDE + self.w + growth / 2)
            region = cairo.Region(cairo.RectangleInt(left, self.above, right - left, self.h))
            for x, y, size in self._draw_geom.values():
                x1, y1 = math.floor(x), math.floor(y)
                region.union(cairo.RectangleInt(x1, y1, math.ceil(x + size) - x1,
                                               math.ceil(y + size) - y1))
            rectangles = tuple((r.x, r.y, r.width, r.height)
                               for r in (region.get_rectangle(i) for i in range(region.num_rectangles())))
            if rectangles != getattr(self, "_input_rectangles", None):
                self.area.input_shape_combine_region(region)
                self._input_rectangles = rectangles
            # O compositor faz hit testing na layer surface (GtkWindow). A primeira
            # chamada ocorre antes de show_all(), então aplique quando ela realizar.
            if self.win.get_realized() and rectangles != getattr(self, "_window_input_rectangles", None):
                self.win.input_shape_combine_region(region)
                self._window_input_rectangles = rectangles

        def _schedule_refresh(self, ms=120):
            if self._refresh_id is None:
                self._refresh_id = GLib.timeout_add(ms, self.refresh)

        def _event(self, line):
            kind, _, data = line.partition(">>")
            if kind == "minimized" and DOCKS and self is DOCKS[0]:
                # botão amarelo/pedido xdg de minimizar dos apps: o Hyprland só avisa;
                # o Dock faz o mesmo que ⌘M (Genie) ou devolve a janela
                addr, _, state = data.partition(",")
                self._minimize_request(addr if addr.startswith("0x") else "0x" + addr, state == "1")
            if dock_needs_refresh(line):
                self._schedule_refresh()
            return False

        def _minimize_request(self, addr, on):
            client = next((c for c in hypr_json("clients") or [] if c["address"] == addr), None)
            if client is None:
                return
            parked = client["workspace"]["name"] == "special:minimized"
            if on and not parked:
                self.minimize(addr)
            elif not on and parked:
                it = next((i for i in self.items if i["kind"] == "minimized"
                           and i["win"]["address"] == addr), None)
                self._restore_minimized(it or {"win": client})

        def _trash_full(self):
            try:
                return bool(os.listdir(TRASH_DIR))
            except OSError:
                return False

        def _poll_trash(self):
            full = self._trash_full()
            if getattr(self, "_was_full", None) != full:
                self._was_full = full
                for it in self.items:
                    if it["kind"] == "trash":
                        it["pb"] = self._pixbuf("trash")
                self.area.queue_draw()
            return True

        def _retheme(self):
            self.light = self.theme.get_string("color-scheme") != "prefer-dark"
            self.style, self._style_cache = icon_style_effective(), {}   # Dark/Clear em "Auto"
            self.refresh()

        # ── desenho ──
        def _dock_rect(self):
            return DOCK_SIDE, self.above, self.w, self.h

        def _stop_motion_frames(self, *_):
            if self._motion_tick is not None:
                self.area.remove_tick_callback(self._motion_tick)
                self._motion_tick = None
            self.motion.reset_clock()

        def _queue_motion_frame(self, area, _clock):
            area.queue_draw()
            return True

        def _draw(self, area, cr):
            cr.set_operator(cairo.OPERATOR_CLEAR)
            cr.paint()
            cr.set_operator(cairo.OPERATOR_OVER)
            x0, y0, w, h = self._dock_rect()
            now = time.monotonic()
            animating = False
            # Preserve a geometria sob o clique e a âncora do menu: recolher a
            # ampliação durante a pressão desloca o alvo antes de soltar o botão.
            hold_magnification = ((self.pressed is not None or getattr(self, "menu_open", False))
                                  and not getattr(self, "dragging", False))
            mag_on = (CFG.get("dock_magnification", False) and self._pointer_x is not None and
                     not getattr(self, "dragging", False))
            rm = reduce_motion()
            hov_extra_lift = 0.0
            # Resolve todas as escalas antes de desenhar. O Dock Tahoe desloca os
            # vizinhos para abrir espaço; centros fixos fazem ícones ampliados colidirem.
            growths, animating, dt = self.motion.scales_for_frame(
                self.items, self.icon, self.gap, x0, self._pointer_x, mag_on,
                hold_magnification, rm, now)
            total_growth = sum(growths)
            x0 -= total_growth / 2
            w += total_growth
            r = self.radius
            # vidro: preenchimento (kit: luminosity #454545/0.50 escuro, #4D4D4D/0.30 claro,
            # + plus-darker #1A1A1A/0.10 + lighten #FFF/0.08)
            rounded_rect(cr, x0, y0, w, h, r)
            if A11Y["reduce_transparency"]:         # Reduzir Transparência: Dock sólido
                cr.set_source_rgba(*((0.90, 0.90, 0.91, 1) if self.light else (0.17, 0.17, 0.18, 1)))
            elif self.light:
                cr.set_source_rgba(0.12, 0.12, 0.14, 0.10)
                cr.fill_preserve()
                cr.set_source_rgba(1, 1, 1, 0.20)
            else:
                cr.set_source_rgba(0.16, 0.16, 0.17, 0.42)
                cr.fill_preserve()
                cr.set_source_rgba(1, 1, 1, 0.06)
            cr.fill()
            # sombra interna de baixo (kit: 0 -12 12 -12 #161616/0.70), bem sutil
            rounded_rect(cr, x0, y0, w, h, r)
            g = cairo.LinearGradient(0, y0 + h - 14, 0, y0 + h)
            g.add_color_stop_rgba(0, 0.09, 0.09, 0.09, 0)
            g.add_color_stop_rgba(1, 0.09, 0.09, 0.09, 0.10 if self.light else 0.22)
            cr.set_source(g)
            cr.fill()
            # filete escuro 0.5 por fora + realces brancos finos em cima e embaixo
            cr.set_line_width(1)
            rounded_rect(cr, x0 - 0.5, y0 - 0.5, w + 1, h + 1, r + 0.5)
            cr.set_source_rgba(0, 0, 0, 0.25 if not self.light else 0.12)
            # [TAHOE] Dock observa AXIncreaseContrast. Compartilha a variante de
            # contorno do shell; o Cairo não recebe border-color automaticamente.
            if A11Y["increase_contrast"]:
                found, border = self.area.get_style_context().lookup_color("shell_contrast_border")
                if found:
                    cr.set_source_rgba(border.red, border.green, border.blue, border.alpha)
            cr.stroke()
            rounded_rect(cr, x0 + 0.5, y0 + 0.5, w - 1, h - 1, r - 0.5)
            g = cairo.LinearGradient(0, y0, 0, y0 + h)
            top, mid, bot = (0.75, 0.12, 0.45) if self.light else (0.38, 0.06, 0.20)
            g.add_color_stop_rgba(0, 1, 1, 1, top)
            g.add_color_stop_rgba(0.35, 1, 1, 1, mid)
            g.add_color_stop_rgba(0.75, 1, 1, 1, mid)
            g.add_color_stop_rgba(1, 1, 1, 1, bot)
            cr.set_source(g)
            cr.stroke()

            # Ícones usam as posições de repouso; só a base se alarga para acomodá-los.
            x0 = DOCK_SIDE
            shifts = self.metrics.magnification_shifts(growths)
            self._draw_geom = {}
            dragged = None
            for i, it in enumerate(self.items):
                grow = growths[i]
                shift = shifts[i]
                is_dragged = getattr(self, "dragging", False) and i == self.pressed
                dragged_position = None
                if is_dragged:
                    # O item acompanha a mão; só os vizinhos/encaixe usam a mola.
                    dragged_position = self._drag_x - self._drag_offset - x0 - self.icon / 2 - shift
                position, moving = self.motion.position(it, dt, rm, dragged_position, shift)
                animating |= moving
                ix, iy = x0 + position, y0 + self.pad_top
                if it["kind"] == "sep":
                    cx = ix + self.sep_col / 2 + shift
                    cy = iy + self.icon / 2
                    cr.rectangle(round(cx) - 0.5, cy - self.sep_h / 2, 1, self.sep_h)
                    cr.set_source_rgba(1, 1, 1, 0.45) if self.light else cr.set_source_rgba(1, 1, 1, 0.22)
                    cr.fill()
                    self.motion.scales.pop(it["key"], None)
                    self.motion.velocities.pop(it["key"], None)
                    continue
                lift, bouncing = self.motion.bounce(it["key"], now, self.icon, rm)
                animating |= bouncing
                cur = self.motion.scales.get(it["key"], 1.0)
                lx, ly = ix + shift - grow / 2, iy - lift - grow
                size = self.icon * cur
                self._draw_geom[i] = (lx, ly, size)
                if is_dragged:
                    dragged = it, lx, ly, size
                else:
                    self._draw_icon(cr, it, lx, ly, pressed=(i == self.pressed), size=size)
                    self._draw_badge(cr, it, lx, ly, size=size)
                if i == self.hover:
                    hov_extra_lift = grow
                if it.get("windows"):
                    cr.arc(ix + shift + self.icon / 2,
                           iy + self.icon + self.dot_gap + self.dot / 2,
                           self.dot / 2, 0, 2 * math.pi)
                    cr.set_source_rgba(0.18, 0.18, 0.20, 0.85) if self.light else cr.set_source_rgba(0.78, 0.78, 0.80, 0.85)
                    cr.fill()
            if dragged:
                it, lx, ly, size = dragged
                self._draw_icon(cr, it, lx, ly, pressed=True, size=size)
                self._draw_badge(cr, it, lx, ly, size=size)
                if getattr(self, "_drag_remove", False):
                    self._draw_label(cr, it, x0, y0, text="Remove")
            self._update_input_region(total_growth)
            if self.hover is not None and self.pressed is None and self.hover < len(self.items):
                self._draw_label(cr, self.items[self.hover], x0, y0, hov_extra_lift)
            if animating:
                if self._motion_tick is None:
                    self._motion_tick = self.area.add_tick_callback(self._queue_motion_frame)
            else:
                self._stop_motion_frames()
            return True

        def _draw_minimized(self, cr, it, x, y, size=None):
            """Janela minimizada: miniatura dentro da caixa do ícone (proporção mantida,
            cantos de 4) com o ícone do app pequeno no canto de baixo à direita."""
            size = self.icon if size is None else size
            thumb = self._thumbs.get(it["win"]["address"])
            if thumb is not None:
                tw, th = thumb.get_width(), thumb.get_height()
                k = size * 0.92 / max(tw, th)
                w, h = tw * k, th * k
                tx, ty = x + (size - w) / 2, y + (size - h) / 2
                cr.save()
                rounded_rect(cr, tx, ty, w, h, 4)
                cr.clip()
                cr.translate(tx, ty)
                cr.scale(k, k)
                Gdk.cairo_set_source_pixbuf(cr, thumb, 0, 0)
                cr.get_source().set_filter(cairo.FILTER_GOOD)
                cr.paint()
                cr.restore()
            pb = it.get("pb")
            if pb:
                s = size * 0.42
                cr.save()
                cr.translate(x + size - s * 0.9, y + size - s * 0.9)
                cr.scale(s / pb.get_width(), s / pb.get_width())
                Gdk.cairo_set_source_pixbuf(cr, pb, 0, 0)
                cr.get_source().set_filter(cairo.FILTER_GOOD)
                cr.paint()
                cr.restore()

        def _draw_icon(self, cr, it, x, y, pressed=False, size=None):
            size = self.icon if size is None else size
            if it["kind"] == "minimized":
                self._draw_minimized(cr, it, x, y, size)
                return
            pb = it.get("pb")
            cr.push_group()
            if pb:
                cr.save()
                sc = size / pb.get_width()
                cr.translate(x, y)
                cr.scale(sc, sc)
                style = self.style
                if style == "default":
                    Gdk.cairo_set_source_pixbuf(cr, pb, 0, 0)
                else:
                    key = (id(pb), style)
                    if key not in self._style_cache:
                        self._style_cache[key] = styled_icon(pb, style)
                    cr.set_source_surface(self._style_cache[key], 0, 0)
                cr.get_source().set_filter(cairo.FILTER_GOOD)
                cr.paint_with_alpha(0.86 if style in ("clear", "clear-dark") else 1.0)
                cr.restore()
            else:
                rounded_rect(cr, x + 3, y + 3, size - 6, size - 6, size * 0.22)
                cr.set_source_rgba(0.55, 0.55, 0.6, 1)
                cr.fill()
            if it["kind"] == "downloads":
                self._draw_download_glyph(cr, x, y, size)
            if pressed:      # ícone escurece enquanto o botão está apertado
                cr.set_operator(cairo.OPERATOR_ATOP)
                cr.set_source_rgba(0, 0, 0, 0.35)
                cr.paint()
                cr.set_operator(cairo.OPERATOR_OVER)
            cr.pop_group_to_source()
            cr.paint()

        def _draw_badge(self, cr, it, x, y, size=None):
            """Selo vermelho de contagem no canto do ícone. Medido no Dock do Tahoe
            (referencias/telas/tahoe-dark.jpeg): diâmetro 0,47 do ícone, centro 0,16
            para dentro da borda direita e 0,12 abaixo do topo; vermelho do sistema;
            número branco com ~0,37 do diâmetro de altura. Com 2+ dígitos vira cápsula."""
            if not self.notifs or it["kind"] != "app":
                return
            n = self.notifs.count_for(it.get("key"), it.get("name"), it.get("cls"),
                                      *[w.get("class") for w in it.get("windows") or []])
            if not n:
                return
            size = self.icon if size is None else size
            d = size * 0.47
            cx, cy = x + size * 0.84, y + size * 0.12
            layout = PangoCairo.create_layout(cr)
            fd = Pango.FontDescription.from_string("SF Pro Medium")
            fd.set_absolute_size(d * 0.52 * Pango.SCALE)
            layout.set_font_description(fd)
            layout.set_text(str(n) if n < 1000 else "999+", -1)
            _ink, log = layout.get_pixel_extents()
            w = max(d, log.width + d * 0.5)
            right = cx + d / 2                     # com mais dígitos cresce para a esquerda
            rounded_rect(cr, right - w, cy - d / 2, w, d, d / 2)
            cr.set_source_rgba(1.0, 0.22, 0.24, 1) if self.light else cr.set_source_rgba(1.0, 0.26, 0.27, 1)
            cr.fill()
            cr.move_to(right - w / 2 - log.width / 2 - log.x, cy - log.height / 2 - log.y)
            cr.set_source_rgba(1, 1, 1, 1)
            PangoCairo.show_layout(cr, layout)

        def _draw_download_glyph(self, cr, x, y, size=None):
            """Pasta Downloads do Finder: "arrow.down.circle" gravado em azul escuro no corpo."""
            size = self.icon if size is None else size
            cx, cy, rad = x + size * 0.5, y + size * 0.58, size * 0.16
            cr.save()
            cr.set_source_rgba(0.10, 0.42, 0.72, 0.85)
            cr.set_line_width(max(1.4, size * 0.04))
            cr.set_line_cap(cairo.LINE_CAP_ROUND)
            cr.set_line_join(cairo.LINE_JOIN_ROUND)
            cr.arc(cx, cy, rad, 0, 2 * math.pi)
            cr.stroke()
            a = rad * 0.55
            cr.move_to(cx, cy - a)
            cr.line_to(cx, cy + a)
            cr.move_to(cx - a * 0.75, cy + a * 0.2)
            cr.line_to(cx, cy + a)
            cr.line_to(cx + a * 0.75, cy + a * 0.2)
            cr.stroke()
            cr.restore()

        def _label_style(self):
            if not hasattr(self, "label_style"):
                self.label_style = Gtk.StyleContext()
                path = Gtk.WidgetPath()
                path.append_type(Gtk.DrawingArea)
                self.label_style.set_path(path)
                self.label_style.set_screen(self.win.get_screen())
                self.label_style.add_class("dock-tooltip")
            return self.label_style

        def _draw_label(self, cr, it, x0, y0, extra_lift=0.0, text=None):
            """Nome do app acima do ícone, numa cápsula de vidro (como os menus).
            extra_lift: quanto o ícone cresceu por magnificação (sobe junto, mesma base)."""
            style = self._label_style()
            (style.add_class if self.light else style.remove_class)("light")
            state = Gtk.StateFlags.NORMAL
            padding = style.get_padding(state)
            layout = PangoCairo.create_layout(cr)
            layout.set_font_description(style.get_font(state))
            layout.set_text(text if text is not None else (it.get("name") or ""), -1)
            tw, th = layout.get_pixel_size()
            ph = max(style.get_property("min-height", state), th + padding.top + padding.bottom)
            pw = max(tw + padding.left + padding.right, ph + 18)
            idx = self.items.index(it)
            geom = getattr(self, "_draw_geom", {}).get(idx)
            cx = geom[0] + geom[2] / 2 if geom else (
                x0 + it["x"] + (self.sep_col if it["kind"] == "sep" else self.icon) / 2)
            lx = max(2, min(cx - pw / 2, self.w + 2 * DOCK_SIDE - pw - 2))
            ly = max(1, y0 - ph - 10 - extra_lift)
            # dock-rotulo-nome-app.png: 126×35 body, 12×7 curved pointer.
            # Build one outline so the border does not run across the pointer base.
            r = ph / 2
            tip = max(lx + r + 6, min(cx, lx + pw - r - 6))
            cr.new_sub_path()
            cr.arc(lx + pw - r, ly + r, r, -math.pi/2, math.pi/2)
            cr.line_to(tip + 9, ly + ph)
            cr.curve_to(tip + 4, ly + ph, tip + 3, ly + ph + 6, tip, ly + ph + 6)
            cr.curve_to(tip - 3, ly + ph + 6, tip - 4, ly + ph, tip - 9, ly + ph)
            cr.arc(lx + r, ly + r, r, math.pi/2, 3*math.pi/2)
            cr.close_path()
            tint = style.get_background_color(state)
            cr.set_source_rgba(tint.red, tint.green, tint.blue, tint.alpha)
            cr.fill_preserve()
            border = style.get_border_color(state)
            cr.set_line_width(1)
            cr.set_source_rgba(border.red, border.green, border.blue, border.alpha)
            cr.stroke()
            # Center actual glyph ink; SF Pro's logical box leaves asymmetric leading.
            ink, _logical = layout.get_pixel_extents()
            cr.move_to(lx + (pw - ink.width) / 2 - ink.x,
                       ly + (ph - ink.height) / 2 - ink.y)
            fg = style.get_color(state)
            cr.set_source_rgba(fg.red, fg.green, fg.blue, fg.alpha)
            PangoCairo.show_layout(cr, layout)

        # ── ponteiro ──
        def _index_at(self, x, y):
            return self.metrics.index_at(self.items, getattr(self, "_draw_geom", {}),
                                         x, y, DOCK_SIDE, self.above)

        def _motion(self, _w, ev):
            self._pointer_x = ev.x     # para a curva gaussiana de magnificação (_draw)
            if self._drag_motion(ev):
                return
            i = self._index_at(ev.x, ev.y)
            if i is not None and self.items[i]["kind"] == "sep":
                i = None
            if i != self.hover:
                self.hover = i
                self.area.queue_draw()
            elif CFG.get("dock_magnification", False):
                self.area.queue_draw()   # mesmo índice: a curva ainda segue o x do ponteiro
            self._cancel_hide()

        def _leave(self, _w, ev):
            if ev.detail == Gdk.NotifyType.INFERIOR:
                return
            if (getattr(self, "dragging", False) or
                    (self.pressed is not None and getattr(ev, "state", 0) & Gdk.ModifierType.BUTTON1_MASK)):
                return   # o grab entrega o release; sair da superfície não cancela o gesto
            self.hover = self.pressed = None
            self._pressed_key = None
            self._pointer_x = None    # sem ponteiro sobre o Dock: alvo de magnificação volta a 1.0
            self.area.queue_draw()
            if self.autohide and not getattr(self, "menu_open", False):
                self._hide_timer = GLib.timeout_add(450, self._conceal)

        def _press(self, _w, ev):
            i = self._index_at(ev.x, ev.y)
            control = bool(getattr(ev, "state", 0) & Gdk.ModifierType.CONTROL_MASK)
            if ev.button == 3 or (ev.button == 1 and control):
                self.pressed = None
                self._pressed_key = None
                self.dragging = self._drag_remove = False
                self._cancel_hide()
                self._menu(i, ev)
            elif ev.button == 1 and i is not None and self.items[i]["kind"] != "sep":
                self._cancel_hide()
                self.pressed = i
                self._pressed_key = self.items[i]["key"]
                self.drag_from, self.dragging = ev.x, False
                self._drag_from_y = ev.y
                self._drag_remove = False
                x, _y, size = self._draw_geom.get(i, (DOCK_SIDE + self.items[i]["x"], 0, self.icon))
                self._drag_offset = ev.x - (x + size / 2)
                self._drag_x = ev.x
                self.area.queue_draw()
            return True

        def _removable(self, it):
            return bool(it.get("pin") in self.pinned and it.get("pin") != "hyprmac:finder")

        def _outside_for_removal(self, x, y):
            # Política local de tolerância (1 ícone), não uma medida publicada Apple.
            x0, y0, w, h = self._dock_rect()
            return x < x0 - self.icon or x > x0 + w + self.icon or y < y0 - self.icon or y > y0 + h + self.icon

        def _drag_motion(self, ev):
            """Arrastar um ícone fixo reordena o Dock ao vivo: os vizinhos abrem espaço
            enquanto ele passa, como no Mac. Só entre os fixos (os abertos e não fixos
            ficam à direita deles)."""
            i = self.pressed
            movel = self._removable  # o Finder fica sempre na ponta
            if i is None or i >= len(self.items) or not movel(self.items[i]):
                return False
            self._drag_x = ev.x
            y = getattr(ev, "y", getattr(self, "_drag_from_y", self.above))
            if not getattr(self, "dragging", False):
                if math.hypot(ev.x - getattr(self, "drag_from", ev.x),
                              y - getattr(self, "_drag_from_y", y)) < 8:
                    return False
                self.dragging = True
                self.hover = None
            self._cancel_hide()
            self._drag_remove = self._outside_for_removal(ev.x, y)
            if self._drag_remove:
                self._track_drag_position(ev.x)
                self.area.queue_draw()
                return True
            x0 = self._dock_rect()[0]
            fixos = [n for n, it in enumerate(self.items) if movel(it)]
            # vaga cujo centro está mais perto do ponteiro
            alvo = min(fixos, key=lambda n: abs(x0 + self.items[n]["x"] + self.icon / 2 - ev.x))
            if alvo != i:
                # Os mesmos widgets/dados bastam para mudar a ordem. Consultar o
                # compositor e recarregar ícones aqui bloqueava cada troca de vaga.
                reorder_pinned(self.items, self.pinned, i, alvo)
                self.pressed = alvo
                self._layout()
            self._track_drag_position(ev.x)
            self.area.queue_draw()
            return True

        def _track_drag_position(self, x):
            # Eventos podem chegar e terminar antes do próximo draw. O retorno deve
            # partir da mão, nunca da posição de repouso guardada no quadro anterior.
            item = self.items[self.pressed]
            growths = [(self.motion.scales.get(it["key"], 1.0) - 1) * self.icon
                       if it["kind"] != "sep" else 0.0 for it in self.items]
            shift = self.metrics.magnification_shifts(growths)[self.pressed]
            position = x - self._drag_offset - DOCK_SIDE - self.icon / 2 - shift
            self.motion.position(item, 0.0, False, position, shift)

        def _release(self, _w, ev):
            if ev.button != 1 and getattr(self, "dragging", False):
                return True
            if getattr(self, "dragging", False) and self.pressed is not None:
                self._track_drag_position(ev.x)
            i, self.pressed = self.pressed, None
            self._pressed_key = None
            self.area.queue_draw()
            if getattr(self, "dragging", False):
                self.dragging = False
                remove = (i is not None and i < len(self.items) and self._removable(self.items[i])
                          and self._outside_for_removal(ev.x, ev.y))
                self._drag_remove = False
                if remove:
                    self.pinned.remove(self.items[i]["pin"])
                    self.hover = self._pointer_x = None
                self._save()
                if remove:
                    self.refresh()  # O app em execução continua na seção de abertos.
                if self.autohide and self._index_at(ev.x, ev.y) is None:
                    self._hide_timer = GLib.timeout_add(450, self._conceal)
                return True
            if ev.button == 1 and i is not None and i == self._index_at(ev.x, ev.y):
                self._activate(self.items[i])
            elif ev.button == 2:
                j = self._index_at(ev.x, ev.y)
                if j is not None and self.items[j]["kind"] == "app":
                    self._launch(self.items[j])
            return True

        # ── teclado: ⌃F3 (HIG ▸ Keyboards, "Move focus to the Dock") ──
        def focus_keyboard(self, arg=""):
            """O Dock recebe o foco do teclado com o primeiro ícone destacado e o nome
            visível; ←/→ percorrem os ícones, Return ou Espaço abrem, Esc devolve o foco.
            "preview [n]": mesmo destaque, n passos à direita, sem pegar o teclado (2 s)."""
            usable = [i for i, it in enumerate(self.items) if it["kind"] != "sep"]
            if not usable:
                return
            self._kb = True
            self._reveal()
            self.hover = usable[0]
            words = arg.split()
            if words[:1] == ["preview"]:
                self._kb_move(int(words[1]) if len(words) > 1 and words[1].isdigit() else 0)
                GLib.timeout_add(2000, lambda: self._end_keyboard() and False)
                return
            self.area.queue_draw()
            LS.set_keyboard_mode(self.win, LS.KeyboardMode.EXCLUSIVE)
            self.win.present()

        def _end_keyboard(self):
            if not getattr(self, "_kb", False):
                return
            self._kb = False
            LS.set_keyboard_mode(self.win, LS.KeyboardMode.NONE)
            self.hover = None
            self.area.queue_draw()
            if self.autohide and not getattr(self, "menu_open", False):
                self._hide_timer = GLib.timeout_add(450, self._conceal)

        def _kb_move(self, step):
            usable = [i for i, it in enumerate(self.items) if it["kind"] != "sep"]
            if not usable:
                return
            at = usable.index(self.hover) if self.hover in usable else 0
            self.hover = usable[min(max(at + step, 0), len(usable) - 1)]
            self.area.queue_draw()

        def _key(self, _w, ev):
            if not getattr(self, "_kb", False):
                return False
            key = ev.keyval
            if key in (Gdk.KEY_Left, Gdk.KEY_Right):
                self._kb_move(-1 if key == Gdk.KEY_Left else 1)
            elif key in (Gdk.KEY_Home, Gdk.KEY_End):
                self._kb_move(-len(self.items) if key == Gdk.KEY_Home else len(self.items))
            elif key in (Gdk.KEY_Return, Gdk.KEY_KP_Enter, Gdk.KEY_space):
                i = self.hover
                self._end_keyboard()
                if i is not None and i < len(self.items):
                    self._activate(self.items[i])
            elif key == Gdk.KEY_Escape:
                self._end_keyboard()
            return True

        # ── documentos externos sobre aplicativos ──
        def _document_app_at(self, x, y):
            if getattr(self, "dragging", False) or getattr(self, "menu_open", False):
                return None
            i = self._index_at(x, y)
            if i is None:
                return None
            it = self.items[i]
            return i if it["kind"] == "app" and dock_supports_documents(it.get("info")) else None

        def _document_drag_motion(self, area, context, x, y, timestamp):
            self._cancel_hide()
            target = area.drag_dest_find_target(context, None)
            i = self._document_app_at(x, y) if target and target.name() == "text/uri-list" else None
            x0, y0, w, h = self._dock_rect()
            on_dock = x0 <= x <= x0 + w and y0 <= y <= y0 + h
            accepted = bool(target and target.name() == "text/uri-list" and
                            context.get_actions() & Gdk.DragAction.COPY and (i is not None or on_dock))
            Gdk.drag_status(context, Gdk.DragAction.COPY if accepted else Gdk.DragAction(0), timestamp)
            self.hover = i if accepted else None
            self._pointer_x = x if accepted else None
            area.queue_draw()
            return True

        def _document_drag_leave(self, area, _context, _timestamp):
            self.hover = self._pointer_x = None
            area.queue_draw()
            # GTK pode emitir leave antes de data-received; preserve o destino pendente.
            if self.autohide and not getattr(self, "menu_open", False):
                self._cancel_hide()
                self._hide_timer = GLib.timeout_add(450, self._conceal)

        def _document_drop(self, area, context, x, y, timestamp):
            target = area.drag_dest_find_target(context, None)
            i = self._document_app_at(x, y) if target and target.name() == "text/uri-list" else None
            x0, y0, w, h = self._dock_rect()
            on_dock = x0 <= x <= x0 + w and y0 <= y <= y0 + h
            if not target or target.name() != "text/uri-list" or not (i is not None or on_dock) or \
                    not context.get_actions() & Gdk.DragAction.COPY:
                return False
            self._cancel_hide()
            # Vincula destino e posição antes da seleção: leave/refresh não os alteram.
            app = self.items[i] if i is not None else None
            slot = pin_slot(self.items, self.pinned, x, x0, self.icon)
            self._document_pending = (context, app["key"] if app else None,
                                      app["info"] if app else None, slot)
            area.drag_get_data(context, target, timestamp)
            return True

        def _document_received(self, area, context, _x, _y, data, _info, timestamp):
            pending = getattr(self, "_document_pending", None)
            success = False
            if pending is not None and pending[0] == context:
                self._document_pending = None
                if data.get_target().name() == "text/uri-list" and data.get_length() > 0:
                    uris = data.get_uris()
                    launcher = desktop_file_from_uris(uris, Gio.File.new_for_uri)
                    if launcher:
                        info = Gio.DesktopAppInfo.new_from_filename(launcher)
                        if info:
                            app_id = desktop_id(info)
                            pin = app_id if app_id and Gio.DesktopAppInfo.new(app_id + ".desktop") else launcher
                            if insert_pin(self.pinned, pin, pending[3]):
                                self._save()
                                self.refresh()
                            success = True
                    elif pending[2] is not None:
                        launch_context = area.get_display().get_app_launch_context()
                        launch_context.set_timestamp(timestamp)
                        success = dock_open_documents(pending[2], uris,
                                                      Gio.File.new_for_uri, launch_context)
            # COPY informa que o original deve ficar na origem; só abrimos no app.
            Gtk.drag_finish(context, success, False, timestamp)
            self._document_drag_leave(area, context, timestamp)

        # ── ações ──
        def _launch(self, it):
            kind = it["kind"]
            if kind == "apps":
                spawn(os.path.join(ROOT, "scripts", "spotlight") + " mode apps")
                return
            if kind in ("finder", "settings"):
                spawn(CFG["file_manager"] if kind == "finder" else CFG["settings"])
            elif it.get("info"):
                if os.path.isabs(it.get("pin") or ""):
                    it["info"].launch([], None)
                else:
                    spawn("gtk-launch " + GLib.shell_quote(desktop_id(it["info"])))
            else:
                return
            if not reduce_motion():
                self.motion.bounces[it["key"]] = time.monotonic()
                self.area.queue_draw()

        def _activate(self, it):
            kind = it["kind"]
            if kind == "minimized":           # volta para a mesa atual, em foco
                self._restore_minimized(it)
                return
            if kind == "downloads":
                spawn(f'{CFG["file_manager"]} {GLib.shell_quote(GLib.get_user_special_dir(GLib.UserDirectory.DIRECTORY_DOWNLOAD) or os.path.expanduser("~/Downloads"))}')
                return
            if kind == "trash":
                spawn(f'{CFG["file_manager"]} trash:/')
                return
            wins = it.get("windows") or []
            if not wins:
                self._launch(it)
                return
            visible = [c for c in wins if not c["workspace"]["name"].startswith("special")]
            if not visible:                # app oculto (⌘H): volta para a mesa atual
                ws = hypr_json("activeworkspace").get("id", 1)
                for c in wins:
                    dispatch(f'hl.dsp.window.move({{ workspace = {ws}, follow = false, '
                             f'window = "address:{c["address"]}" }})')
                visible = wins
            dispatch(f'hl.dsp.focus({{ window = "address:{visible[0]["address"]}" }})')

        def _focus_window(self, c):
            if c["workspace"]["name"].startswith("special"):
                ws = hypr_json("activeworkspace").get("id", 1)
                dispatch(f'hl.dsp.window.move({{ workspace = {ws}, follow = false, '
                         f'window = "address:{c["address"]}" }})')
            dispatch(f'hl.dsp.focus({{ window = "address:{c["address"]}" }})')

        def _dock_layer(self):
            try:      # hypr_json só aceita listas e alguns dicionários; "layers" é um dicionário
                layers = json.loads(run("hyprctl layers -j"))
            except ValueError:
                return None
            for mon in (layers if isinstance(layers, dict) else {}).values():
                for level in mon.get("levels", {}).values():
                    for layer in level:
                        if layer.get("namespace") == "hyprmac-dock":
                            return layer
            return None

        def _genie_rect(self, it=None):
            """Retângulo global do ícone para o Genie (hyprglass + hypr/hyprglass/genie.patch).
            Sem `it`: a vaga que a janela minimizada vai ocupar — a de Downloads, com o Dock
            já recentrado pelo ícone a mais."""
            layer = self._dock_layer()
            slot = it or next((i for i in self.items if i["kind"] == "downloads"), None)
            if layer is None or slot is None or "x" not in slot:
                return None
            x = layer["x"] + DOCK_SIDE + slot["x"]
            if it is None:
                x -= (self.icon + self.gap) / 2
            return [round(x), round(layer["y"] + self.above + self.pad_top), self.icon, self.icon]

        @staticmethod
        def _genie(*args):
            if reduce_motion() or CFG.get("dock_minimize_effect", "genie") != "genie":
                return False
            try:
                out = subprocess.run(["hyprctl", "hyprglass", *map(str, args)], capture_output=True,
                                     text=True, timeout=2).stdout
            except (OSError, subprocess.TimeoutExpired):
                return False
            return out.strip() == "ok"

        def minimize(self, address=None):
            """⌘M: a janela escoa até o Dock (Genie) e vai para special:minimized. Sem o
            plugin, com Reduzir Movimento ou fora do monitor do Dock, só se move."""
            win = (hypr_json("activewindow") or {}) if not address else {"address": address}
            addr = win.get("address")
            if not addr:
                return
            layer = self._dock_layer()
            client = next((c for c in hypr_json("clients") or [] if c["address"] == addr), {})
            same_monitor = layer is not None and client.get("monitor") == next(
                (m["id"] for m in hypr_json("monitors") or []
                 if m["x"] <= layer["x"] < m["x"] + m["width"]), None)
            rect = self._genie_rect() if same_monitor else []
            if rect is not None and self._genie("minimize", f"address:{addr}", *rect):
                return
            dispatch(f'hl.dsp.window.move({{ workspace = "special:minimized", follow = false, '
                     f'window = "address:{addr}" }})')

        def _restore_minimized(self, it):
            rect = (self._genie_rect(it) if "x" in it else None) or []
            if not self._genie("restore", f"address:{it['win']['address']}", *rect):
                self._focus_window(it["win"])

        def _show_all_windows(self, wins):
            """Foca uma janela visível do app e só então abre o Exposé dele (o overview
            lê a janela ativa); em sequência, num só processo, para não correr."""
            c = next(c for c in wins if not c["workspace"]["name"].startswith("special"))
            lua = f'hl.dsp.focus({{ window = "address:{c["address"]}" }})'
            overview = os.path.join(ROOT, "shell", "hyprmac-overview")
            spawn(f"hyprctl dispatch {GLib.shell_quote(lua)} >/dev/null && "
                  f"{GLib.shell_quote(overview)} app")

        def _toggle_pin(self, it):
            pin = it.get("pin")
            if pin in self.pinned:
                self.pinned.remove(pin)
            else:
                self.pinned.insert(len(self.pinned), desktop_id(it["info"]) if it.get("info")
                                   else it["key"])
            self._save()
            self.refresh()

        def _hide_app(self, it, hide):
            for c in it.get("windows") or []:
                special = c["workspace"]["name"].startswith("special")
                if hide and not special:
                    dispatch('hl.dsp.window.move({ workspace = "special:magic", follow = false, '
                             f'window = "address:{c["address"]}" }})')
                elif not hide and special:
                    self._focus_window(c)

        def _quit_app(self, it):
            for c in it.get("windows") or []:
                dispatch(f'hl.dsp.window.close({{ window = "address:{c["address"]}" }})')

        # ── menu do Dock (HIG "Dock menus": janelas abertas, Options, Show/Hide, Quit) ──
        def _menu(self, i, ev):
            m = Gtk.Menu()
            m.set_reserve_toggle_size(False)
            add_class(m, "hyprmac-menu")

            def item(menu, text, action=None, sensitive=True, submenu=None, check=None):
                mi = Gtk.MenuItem(label=text)
                mi.set_sensitive(sensitive)
                if check is not None:
                    menu_check(mi, check)
                if submenu is not None:
                    ShellMenu._attach_submenu(mi, submenu)
                elif action:
                    mi.connect("activate", lambda _m: action())
                menu.append(mi)

            sep = lambda menu: menu.append(Gtk.SeparatorMenuItem())   # noqa: E731
            it = self.items[i] if i is not None else None
            # Estrutura e títulos do DockMenus.plist do macOS 26.6.1 (25G76)
            if it is None or it["kind"] == "sep":
                item(m, "Turn Hiding Off" if self.autohide else "Turn Hiding On", self.toggle_autohide)
                item(m, "Turn Magnification Off" if CFG.get("dock_magnification") else
                     "Turn Magnification On", self._toggle_magnification)
                pos = Gtk.Menu()
                pos.set_reserve_toggle_size(False)
                for label in ("Left", "Bottom", "Right"):      # o hyprmac só tem o Dock embaixo
                    item(pos, label, sensitive=label == "Bottom", check=label == "Bottom")
                menu_check_column(pos)
                item(m, "Position on Screen", submenu=pos)
                eff = Gtk.Menu()
                eff.set_reserve_toggle_size(False)
                current = CFG.get("dock_minimize_effect", "genie")
                for key, label in (("genie", "Genie Effect"), ("scale", "Scale Effect")):
                    item(eff, label, lambda key=key: self._set_minimize_effect(key), check=key == current)
                menu_check_column(eff)
                item(m, "Minimize Using", submenu=eff)
                sep(m)
                item(m, "Dock Settings…", lambda: open_settings("desktop"))
            elif it["kind"] == "trash":
                item(m, "Open", lambda: self._activate(it))
                sep(m)
                item(m, "Empty Trash", lambda: (spawn("gio trash --empty"), ui_sound("trash-empty")),
                     sensitive=self._trash_full())
            elif it["kind"] in ("downloads", "apps"):
                item(m, "Open", lambda: self._activate(it))
            elif it["kind"] == "minimized":     # janela minimizada: só Open "nome" (sem Close)
                title = (it.get("name") or "").strip()
                title = title if len(title) <= 50 else title[:47] + "…"
                item(m, f"Open “{title}”", lambda: self._activate(it))
            else:
                wins = it.get("windows") or []
                for c in wins:
                    title = (c.get("title") or it["name"]).strip()
                    item(m, title if len(title) <= 60 else title[:57] + "…", lambda c=c: self._focus_window(c))
                if wins:
                    sep(m)
                opts = Gtk.Menu()
                opts.set_reserve_toggle_size(False)
                pinned = it.get("pin") in self.pinned
                item(opts, "Remove from Dock" if pinned else "Keep in Dock", lambda: self._toggle_pin(it),
                     sensitive=self._removable(it) if pinned else it["kind"] in ("app", "settings"))
                desktop = self._desktop_file(it)
                item(opts, "Open at Login", lambda: self._toggle_login_item(desktop),
                     sensitive=desktop is not None, check=self._is_login_item(desktop))
                item(opts, "Show in Finder", lambda: self._show_in_finder(desktop), sensitive=desktop is not None)
                menu_check_column(opts)
                item(m, "Options", submenu=opts)
                sep(m)
                if wins:
                    hidden = all(c["workspace"]["name"].startswith("special") for c in wins)
                    if not hidden:
                        # macOS: "Show All Windows" = Exposé do app (o mesmo do canto ativo)
                        item(m, "Show All Windows", lambda: self._show_all_windows(wins))
                    item(m, "Show" if hidden else "Hide", lambda: self._hide_app(it, not hidden))
                    others = [o for o in self.items if o is not it and o.get("windows")
                              and o["kind"] not in ("minimized",)]
                    item(m, "Hide Others", lambda: [self._hide_app(o, True) for o in others],
                         sensitive=bool(others))
                    item(m, "Quit", lambda: self._quit_app(it))
                else:
                    item(m, "Open", lambda: self._launch(it))
            m.show_all()
            menu_check_column(m)

            self.menu_open = True
            self.hover = None
            self.area.queue_draw()

            def closed(_m):
                self.menu_open = False
                self._dock_menu = None
                self.area.queue_draw()
                if self.autohide:
                    self._cancel_hide()
                    self._hide_timer = GLib.timeout_add(450, self._conceal)
            m.connect("deactivate", closed)
            self._dock_menu = m       # sem referência o menu é coletado antes de abrir
            x0, y0, _w, _h = self._dock_rect()
            rect = Gdk.Rectangle()
            if it is not None:
                geom = getattr(self, "_draw_geom", {}).get(i)
                if geom:
                    x, y, size = geom
                    rect.x, rect.y, rect.width = round(x), round(min(y0, y)), round(size)
                else:
                    rect.x, rect.y = int(x0 + it["x"]), int(y0)
                    rect.width = self.sep_col if it["kind"] == "sep" else self.icon
            else:
                rect.x, rect.y, rect.width = int(ev.x), int(y0), 1
            rect.height = 1
            m.popup_at_rect(self.area.get_window(), rect, Gdk.Gravity.NORTH, Gdk.Gravity.SOUTH, ev)

        # ── ocultar automaticamente (⌥⌘D) ──
        def _toggle_magnification(self):
            CFG["dock_magnification"] = not CFG.get("dock_magnification", False)
            self._save_shell_conf("dock_magnification", CFG["dock_magnification"])
            self.area.queue_draw()

        def _set_minimize_effect(self, key):
            CFG["dock_minimize_effect"] = key
            self._save_shell_conf("dock_minimize_effect", key)

        @staticmethod
        def _save_shell_conf(key, value):
            path = os.path.expanduser("~/.config/hyprmac/config.json")
            try:
                with open(path) as f:
                    conf = json.load(f)
            except (OSError, ValueError):
                conf = {}
            conf[key] = value
            tmp = path + ".tmp"
            with open(tmp, "w") as f:
                json.dump(conf, f, indent=2, ensure_ascii=False)
            os.replace(tmp, path)

        @staticmethod
        def _desktop_file(it):
            info = it.get("info")
            path = info.get_filename() if info is not None and hasattr(info, "get_filename") else None
            return path if path and os.path.exists(path) else None

        @staticmethod
        def _login_path(desktop):
            return os.path.join(GLib.get_user_config_dir(), "autostart", os.path.basename(desktop))

        def _is_login_item(self, desktop):
            return bool(desktop) and os.path.exists(self._login_path(desktop))

        def _toggle_login_item(self, desktop):
            """Options ▸ Open at Login = ~/.config/autostart (padrão XDG)."""
            target = self._login_path(desktop)
            if os.path.exists(target):
                os.remove(target)
            else:
                os.makedirs(os.path.dirname(target), exist_ok=True)
                shutil.copyfile(desktop, target)

        @staticmethod
        def _show_in_finder(desktop):
            fm = CFG.get("file_manager", "nautilus")
            flag = "--select" if os.path.basename(fm.split()[0]) in ("dolphin", "nautilus") else ""
            spawn(f"{fm} {flag} {GLib.shell_quote(desktop)}".replace("  ", " "))

        def toggle_autohide(self, *_):
            self.autohide = not self.autohide
            self._save()
            self._apply_autohide()

        def _apply_autohide(self, initial=False):
            zone = 0 if self.autohide else self.h + self.bottom
            LS.set_exclusive_zone(self.win, zone)
            if self.autohide:
                self.trigger.show_all()
                if initial:
                    self.shown = 0.0
                    self._set_offset()
                else:
                    self._conceal()
            else:
                self.trigger.hide()
                self._slide_to(1.0)

        def _cancel_hide(self):
            if self._hide_timer:
                GLib.source_remove(self._hide_timer)
                self._hide_timer = None

        def _reveal(self):
            self._cancel_hide()
            self._slide_to(1.0)
            return False

        def _conceal(self):
            self._hide_timer = None
            if self.autohide and not getattr(self, "menu_open", False):
                self._slide_to(0.0)
            return False

        def _set_offset(self):
            hidden_by = (1 - self.shown) * (self.h + self.bottom + self.above)
            margin = -round(hidden_by)
            if margin != getattr(self, "_offset_margin", None):
                LS.set_margin(self.win, E.BOTTOM, margin)
                self._offset_margin = margin

        def _slide_to(self, target):
            """Inverte a mola existente sem descartar a velocidade do gesto anterior.

            Mantém timer: uma camada inteiramente fora da tela pode ficar sem frames
            do compositor, mas ainda precisa responder ao gatilho de reabertura.
            A mola é uma aproximação local; não há gravação Tahoe equivalente.
            """
            if (self._anim is not None and getattr(self, "_slide_target", None) == target
                    and not reduce_motion()):
                return
            if self._anim:
                GLib.source_remove(self._anim)
                self._anim = None
            self._slide_target = target
            self._slide_velocity = getattr(self, "_slide_velocity", 0.0)
            if reduce_motion() or (self.shown == target and abs(self._slide_velocity) < 0.01):
                self.shown = target
                self._slide_velocity = 0.0
                self._set_offset()
                return
            previous = time.monotonic()

            def step():
                nonlocal previous
                now = time.monotonic()
                if reduce_motion():
                    self.shown, self._slide_velocity = target, 0.0
                else:
                    self.shown, self._slide_velocity = spring_step(
                        self.shown, self._slide_velocity, target, now - previous)
                    # Limites físicos da borda: não ultrapassar a posição de repouso.
                    if not 0 <= self.shown <= 1:
                        self.shown, self._slide_velocity = max(0, min(1, self.shown)), 0.0
                previous = now
                self._set_offset()
                if self.shown == target and self._slide_velocity == 0:
                    self._anim = None
                    return False
                return True
            self._anim = GLib.timeout_add(16, step)

    return Dock
