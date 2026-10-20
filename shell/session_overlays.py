"""Force Quit and app switcher overlays for the shell session."""
import os
import signal

import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
gi.require_version("GdkPixbuf", "2.0")
gi.require_version("GtkLayerShell", "0.1")
from gi.repository import Gdk, GdkPixbuf, GLib, Gtk
from gi.repository import GtkLayerShell as LS
from app_index import AppIndex

SW_ICON = 72


def create_session_overlays(*, add_class, app_name, dispatch, gdk_monitors,
                            hypr_json, label, layer_window, paint_cover,
                            rounded_rect, set_class):
    """Bind the shell UI/compositor callbacks; no second event connection."""
    class ForceQuit:
        """Janela "Force Quit Applications" (⌥⌘Esc no Mac, Super+Alt+Esc aqui):
        lista os apps com janela aberta (ícone + nome, em ordem alfabética), texto de
        instrução em cima, dica do atalho embaixo e o botão azul "Forçar Encerrar",
        que pede confirmação e manda SIGKILL aos processos do app (ATL-08)."""

        ICON = 20

        def __init__(self, apps):
            self.apps = apps
            self.win = None

        def toggle(self):
            if self.win:
                self.win.destroy()
                return
            self._build()

        def _apps(self):
            por_classe = {}
            for c in hypr_json("clients"):
                cl = c.get("class") or ""
                if not cl or cl == "hyprmac-shell" or c.get("pid", 0) <= 0:
                    continue
                por_classe.setdefault(cl, set()).add(c["pid"])
            itens = []
            for cl, pids in por_classe.items():
                nome, pb = self.apps.lookup(cl)
                if pb:
                    pb = pb.scale_simple(self.ICON * 2, self.ICON * 2, GdkPixbuf.InterpType.BILINEAR)
                itens.append((nome or app_name(cl), pb, pids))
            return sorted(itens, key=lambda i: i[0].lower())

        def _build(self):
            win = Gtk.Window(title="Force Quit Applications")
            win.set_resizable(False)
            win.set_keep_above(True)
            add_class(win, "hyprmac-forcequit")
            hb = Gtk.HeaderBar(title="Force Quit Applications", show_close_button=True)
            win.set_titlebar(hb)
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
            box.set_border_width(20)
            box.set_size_request(420, -1)
            texto = label("If an app doesn’t respond for a while, select its name "
                          "and click Force Quit.", "fq-text")
            texto.set_line_wrap(True)
            texto.set_max_width_chars(48)
            box.pack_start(texto, False, False, 0)
            lista = Gtk.ListBox()
            lista.set_selection_mode(Gtk.SelectionMode.SINGLE)
            add_class(lista, "fq-list")
            self.rows = []
            for nome, pb, pids in self._apps():
                row = Gtk.Box(spacing=8)
                img = Gtk.Image()
                if pb:
                    surf = Gdk.cairo_surface_create_from_pixbuf(pb, 2, None)
                    img.set_from_surface(surf)
                row.pack_start(img, False, False, 0)
                row.pack_start(label(nome, "fq-name"), True, True, 0)
                lista.add(row)
                self.rows.append((nome, pids))
            sc = Gtk.ScrolledWindow()
            sc.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
            sc.set_size_request(-1, 220)
            sc.add(lista)
            add_class(sc, "fq-frame")
            box.pack_start(sc, True, True, 0)
            rodape = Gtk.Box(spacing=12)
            rodape.pack_start(label("You can open this window by pressing Command-Option-Escape.", "fq-hint"),
                              True, True, 0)
            botao = Gtk.Button(label="Force Quit")
            add_class(botao, "suggested-action")
            botao.set_sensitive(False)
            rodape.pack_end(botao, False, False, 0)
            box.pack_start(rodape, False, False, 0)
            win.add(box)

            lista.connect("row-selected", lambda _l, r: botao.set_sensitive(r is not None))
            lista.connect("row-activated", lambda _l, r: self._confirm(r.get_index()))
            botao.connect("clicked", lambda _b: lista.get_selected_row()
                          and self._confirm(lista.get_selected_row().get_index()))
            win.connect("key-press-event", lambda _w, e: e.keyval == Gdk.KEY_Escape and win.destroy())
            win.connect("destroy", lambda *_: setattr(self, "win", None))
            self.win = win
            win.show_all()
            if self.rows:
                lista.select_row(lista.get_row_at_index(0))
                lista.get_row_at_index(0).grab_focus()

        def _confirm(self, i):
            nome, pids = self.rows[i]
            d = Gtk.MessageDialog(transient_for=self.win, modal=True,
                                  message_type=Gtk.MessageType.WARNING,
                                  buttons=Gtk.ButtonsType.NONE,
                                  text=f"Do you want to force “{nome}” to quit?")
            d.format_secondary_text("You will lose any unsaved changes.")
            d.add_button("Cancel", Gtk.ResponseType.CANCEL)
            ok = d.add_button("Force Quit", Gtk.ResponseType.OK)
            add_class(ok, "suggested-action")
            d.set_default_response(Gtk.ResponseType.OK)
            if d.run() == Gtk.ResponseType.OK:
                for pid in pids:
                    try:
                        os.kill(pid, signal.SIGKILL)
                    except OSError:
                        pass
                if self.win:
                    self.win.destroy()
            d.destroy()


    class AppSwitcher:
        """Alt+Tab como o ⌘Tab do macOS: um ícone por app, em ordem de uso recente.
        Tab/Shift+Tab (via bind do Hyprland) avançam/voltam; soltar o Alt ativa.
        Com o Alt ainda seguro, Q encerra o app selecionado e H o oculta (ATL-07)."""

        def __init__(self, apps=None):
            self.apps = apps or AppIndex()
            self.open = False
            self.items = []          # [(nome, pixbuf, endereço da janela mais recente, classe)]
            self.sel = 0
            self.win = layer_window("hyprmac-switcher", LS.Layer.OVERLAY,
                                    keyboard=LS.KeyboardMode.EXCLUSIVE)
            add_class(self.win, "switcher")
            self.win.add_events(Gdk.EventMask.KEY_PRESS_MASK | Gdk.EventMask.KEY_RELEASE_MASK)
            self.win.connect("key-press-event", self._key_press)
            self.win.connect("key-release-event", self._key_release)
            self.win.connect("focus-in-event", lambda *_: GLib.timeout_add(90, self._check_alt))
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=8)
            add_class(box, "switcher-panel")
            self.row = Gtk.Box(spacing=6)
            self.name = label("", "switcher-name", xalign=0.5)
            box.pack_start(self.row, False, False, 0)
            box.pack_start(self.name, False, False, 0)
            self.win.add(box)
            box.show_all()

        # ── comandos ──
        def next(self, held="alt"):
            self._step(+1, held)

        def prev(self, held="alt"):
            self._step(-1, held)

        def _step(self, d, held=None):
            if not self.open:
                if not self._collect():
                    return
                # ⌘Tab = Super+Tab (como o resto do mapeamento ⌘→Super); Alt+Tab continua.
                # Com Super segurado, o submap "switcher" (hypr/hyprmac.lua) desvia ⌘Q/⌘H do app
                # em foco para o app selecionado, como no Mac.
                self._held = "super" if held == "super" else "alt"
                if self._held == "super":
                    dispatch('hl.dsp.submap("switcher")')
                self.sel = 1 % len(self.items) if d > 0 else len(self.items) - 1
                self._build()
                self._show()
            else:
                self.sel = (self.sel + d) % len(self.items)
                self._highlight()

        def _collect(self):
            clients = [c for c in hypr_json("clients") if c.get("mapped") and not c.get("hidden")]
            clients.sort(key=lambda c: c.get("focusHistoryID", 99))
            seen, items = set(), []
            for c in clients:                         # um ícone por app, o mais recente
                cls = c.get("class") or c.get("initialClass") or ""
                if cls in seen or cls == "hyprmac-shell":
                    continue
                seen.add(cls)
                name, pb = self.apps.lookup(cls)
                items.append((name, pb, c["address"], cls))
            self.items = items
            return bool(items)

        def _build(self):
            for ch in self.row.get_children():
                ch.destroy()
            self.cells = []
            for i, (name, pb, _addr, _cls) in enumerate(self.items):
                ev = Gtk.EventBox()
                cell = Gtk.Box()
                add_class(cell, "switcher-cell")
                area = Gtk.DrawingArea()
                area.set_size_request(SW_ICON, SW_ICON)
                cache = {}
                area.connect("draw", lambda a, cr, p=pb, c=cache, n=name: self._draw_icon(a, cr, p, c, n))
                cell.pack_start(area, False, False, 0)
                ev.add(cell)
                ev.connect("button-press-event", lambda _w, _e, k=i: self._pick(k))
                ev.connect("enter-notify-event", lambda _w, _e, k=i: self._hover(k))
                self.row.pack_start(ev, False, False, 0)
                self.cells.append(cell)
            self.row.show_all()
            self._highlight()

        @staticmethod
        def _draw_icon(area, cr, pb, cache, name):
            w, h = area.get_allocated_width(), area.get_allocated_height()
            if pb:
                paint_cover(cr, pb, w, h, cache=cache)
                return
            rounded_rect(cr, 4, 4, w - 8, h - 8, 16)
            cr.set_source_rgba(1, 1, 1, 0.18)
            cr.fill()
            cr.set_source_rgb(1, 1, 1)
            cr.set_font_size(30)
            letter = (name or "?")[:1].upper()
            ext = cr.text_extents(letter)
            cr.move_to((w - ext.width) / 2 - ext.x_bearing, (h - ext.height) / 2 - ext.y_bearing)
            cr.show_text(letter)

        def _highlight(self):
            for i, cell in enumerate(self.cells):
                set_class(cell, "selected", i == self.sel)
            self.name.set_text(self.items[self.sel][0] if self.items else "")

        def _hover(self, k):
            self.sel = k
            self._highlight()

        def _pick(self, k):
            self.sel = k
            self.activate()

        # ── abrir/fechar ──
        def _show(self):
            mons = hypr_json("monitors")
            mon = next((m for m in mons if m.get("focused")), None)
            gmon = gdk_monitors()[0].get(mon["name"]) if mon else None
            if gmon:
                LS.set_monitor(self.win, gmon)
            self.open = True
            self.win.show()

        def _check_alt(self):
            """Toque rápido (Alt já solto quando o seletor ganhou o teclado): troca direto."""
            if not self.open:
                return False
            state = Gdk.Keymap.get_for_display(Gdk.Display.get_default()).get_modifier_state()
            mask = (Gdk.ModifierType.SUPER_MASK | Gdk.ModifierType.MOD4_MASK
                    if getattr(self, "_held", "alt") == "super" else Gdk.ModifierType.MOD1_MASK)
            if not state & mask:
                self.activate()
            return False

        def activate(self):
            if not self.open:
                return
            addr = self.items[self.sel][2] if self.items else None
            cls = self.items[self.sel][3] if self.items else None
            self.close()
            if cls:
                # app oculto (⌘H): como no Mac, escolher no ⌘Tab mostra as janelas de novo
                # na mesa atual (as minimizadas continuam no Dock)
                ws = (hypr_json("activeworkspace") or {}).get("id", 1)
                ocultas = [c for c in hypr_json("clients") if c.get("class") == cls
                           and c["workspace"]["name"] == "special:magic"]
                for c in ocultas:
                    dispatch(f'hl.dsp.window.move({{ workspace = {ws}, follow = false, '
                             f'window = "address:{c["address"]}" }})')
                if ocultas and addr not in {c["address"] for c in ocultas}:
                    addr = ocultas[0]["address"]
            if addr:
                dispatch(f'hl.dsp.focus({{ window = "address:{addr}" }})')

        def close(self):
            self.open = False
            self.win.hide()
            if getattr(self, "_held", "alt") == "super":
                self._held = "alt"
                dispatch('hl.dsp.submap("reset")')

        def _key_press(self, _w, ev):
            k = ev.keyval
            if k == Gdk.KEY_Escape:
                self.close()
            elif k in (Gdk.KEY_Return, Gdk.KEY_KP_Enter, Gdk.KEY_space):
                self.activate()
            elif k in (Gdk.KEY_Right, Gdk.KEY_Tab):
                self._step(+1)
            elif k in (Gdk.KEY_Left, Gdk.KEY_ISO_Left_Tab):
                self._step(-1)
            elif k in (Gdk.KEY_q, Gdk.KEY_Q):
                self._quit_selected()
            elif k in (Gdk.KEY_h, Gdk.KEY_H):
                self._hide_selected()
            return True

        def _quit_selected(self):
            """Q: encerra o app selecionado (fecha todas as janelas da classe, como o
            ⌘Q do hyprmac-janela) e o tira da fila; o seletor continua aberto."""
            if not self.items:
                return
            cls = self.items[self.sel][3]
            for c in hypr_json("clients"):
                if c.get("class") == cls:
                    dispatch(f'hl.dsp.window.close({{ window = "address:{c["address"]}" }})')
            del self.items[self.sel]
            if not self.items:
                self.close()
                return
            self.sel %= len(self.items)
            self._build()

        def _hide_selected(self):
            """H: oculta o app selecionado (vai para o scratchpad, como o ⌘H). Ele
            continua na fila — no macOS o app oculto segue no ⌘Tab, esmaecido."""
            if not self.items:
                return
            cls = self.items[self.sel][3]
            for c in hypr_json("clients"):
                if c.get("class") == cls and not c["workspace"]["name"].startswith("special"):
                    dispatch('hl.dsp.window.move({ workspace = "special:magic", follow = false, '
                             f'window = "address:{c["address"]}" }})')
            add_class(self.cells[self.sel], "hidden")

        def _key_release(self, _w, ev):
            keys = ((Gdk.KEY_Super_L, Gdk.KEY_Super_R) if getattr(self, "_held", "alt") == "super"
                    else (Gdk.KEY_Alt_L, Gdk.KEY_Alt_R, Gdk.KEY_Meta_L, Gdk.KEY_Meta_R))
            if ev.keyval in keys:
                self.activate()
            return True

    return ForceQuit, AppSwitcher
