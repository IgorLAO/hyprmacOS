"""Spotlight GTK view and transitions, using the shared search/control modules."""
import json
import os
import re
import subprocess
import sys
import time
import urllib.parse

import cairo
import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
gi.require_version("GdkPixbuf", "2.0")
gi.require_version("GtkLayerShell", "0.1")
from gi.repository import Gdk, GdkPixbuf, Gio, GLib, Gtk, Pango
from gi.repository import GtkLayerShell as LS

from cocoa_entry import CocoaEntryKeys, is_modified_arrow
from spotlight_controls import SPOT_FIELD, SpotControls, draw_appstore_a
import spotlight_quickkeys as quickkeys
from spotlight_search import SPOT_APP_CATS, SPOT_MODES, SPOT_WEIGHT, spot_app_category, spot_calc, spot_filter_command, spot_fold, spot_score

E = LS.Edge


def create_spotlight_class(*, CACHE, G, MAX_QK_CHARS, POP_MS, ROOT,
                           SPOT_ARG_ACTIONS, add_class, close_other_panels,
                           dispatch, gdk_monitors, hypr_json, in_thread,
                           label, layer_window, reduce_motion, register_panel,
                           run_arg_action, set_class, spawn, spot_shift):
    """Bind the shell's panel, compositor and action services once."""
    SPOT_W, SPOT_TOP, SPOT_ROW, SPOT_VISIBLE = 500, 128, 53, 8
    # Modo Arquivos vazio (referencias/telas/spotlight-clique-modo-5, 0,83 px/pt): painel de ≈ 500,
    # filtros em cápsulas de 22, seções "Suggestions"/"Recents" em grade de 5 colunas de 112 com
    # miniatura de 65 e nome em 2 linhas, passo vertical de 121
    SPOT_PANEL_H, SPOT_CELL_W, SPOT_THUMB, SPOT_COLS = 500, 112, 65, 5
    # Modo Apps vazio (spotlight-modo-apps-6…9, painel = 588 pt): cápsulas de categoria do tamanho
    # do texto (cortadas à direita, rolam), linha dos apps usados por último, filete a ~201 do topo,
    # depois todos os apps em ordem alfabética; ícone 58, nome em 1 linha a 11 dele, passo de 103
    SPOT_APP_ICON = 58


    def _spot_items_module():
        from importlib.machinery import SourceFileLoader
        return SourceFileLoader("spotlight_itens",
                                os.path.join(ROOT, "scripts", "spotlight-itens")).load_module()


    class Spotlight:
        def __init__(self, clipboard):
            self.open = False
            self.mode = "all"
            self.clipboard = clipboard
            self.mod = None                 # scripts/spotlight-itens (carregado no 1º uso)
            self.apps = self.settings = self.actions = None
            self.files = []
            self.results = []
            self._pb = {}                   # caminho → pixbuf 28 (miniaturas/ícones de arquivo)
            self._debounce = None
            self.pending = None             # ação que pede confirmação (Restart…)
            register_panel(self)
            # app instalado/removido: refaz a lista de apps na próxima abertura
            self._app_mon = Gio.AppInfoMonitor.get()
            self._app_mon.connect("changed", lambda *_: setattr(self, "apps", None))
            self.win = layer_window("hyprmac-spotlight", LS.Layer.OVERLAY,
                                    anchors=(E.TOP, E.BOTTOM, E.LEFT, E.RIGHT), exclusive=-1,
                                    keyboard=LS.KeyboardMode.EXCLUSIVE)
            add_class(self.win, "spot-backdrop")
            self.win.add_events(Gdk.EventMask.BUTTON_PRESS_MASK)
            self.win.connect("button-press-event", lambda *_: self.hide() or True)
            self.win.connect("key-press-event", self._on_key)

            self.panel = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            add_class(self.panel, "spot-panel")
            self.panel.set_size_request(SPOT_W + 2 * 48, -1)   # + margens da sombra (.spot-panel)

            # campo: lupa · [modo] · texto + conclusão em linha · ícone do melhor resultado
            field = Gtk.Box(spacing=0)
            self.field = field
            add_class(field, "spot-field")
            field.set_size_request(-1, SPOT_FIELD)
            self.glass_icon = label(G("f0349"), "icon spot-glass", 0.5)     # lupa (ou o ícone do modo)
            field.pack_start(self.glass_icon, False, False, 0)
            # modo Apps: o "A" da App Store no lugar da lupa (spotlight-modo-apps-9; a fonte não tem)
            self.glass_a = Gtk.DrawingArea()
            add_class(self.glass_a, "spot-glass")
            self.glass_a.set_size_request(26, -1)
            self.glass_a.set_margin_end(10)       # o CSS da lupa não dá margem a um DrawingArea
            self.glass_a.set_no_show_all(True)

            def _draw_a(w, cr):
                c = w.get_style_context().get_color(w.get_state_flags())
                cr.set_source_rgba(c.red, c.green, c.blue, c.alpha)
                draw_appstore_a(cr, w.get_allocated_width() / 2, w.get_allocated_height() / 2, 12, 2.4)
                return False
            self.glass_a.connect("draw", _draw_a)
            field.pack_start(self.glass_a, False, False, 0)
            self.mode_pill = label("", "spot-mode", 0.5)
            self.mode_pill.set_no_show_all(True)
            field.pack_start(self.mode_pill, False, False, 0)
            # Tahoe (referencias/desejos/spotlight-busca-filtro-folders): o filtro escolhido vira um
            # "token" no campo, antes do texto — ícone + nome numa cápsula de canto 8
            self.scope = None                # {"key", "label", "path"?} — filtro ou pasta (tab)
            self.token = Gtk.Box(spacing=5)
            add_class(self.token, "spot-token")
            self.token.set_valign(Gtk.Align.CENTER)
            self.token_img = Gtk.Image()
            self.token_img.set_pixel_size(22)
            self.token_lbl = label("", "spot-token-lbl")
            self.token.pack_start(self.token_img, False, False, 0)
            self.token.pack_start(self.token_lbl, False, False, 0)
            self.token.set_no_show_all(True)
            self.token_img.show()
            self.token_lbl.show()
            field.pack_start(self.token, False, False, 0)
            self.entry = Gtk.Entry()
            add_class(self.entry, "spot-entry")
            self._cocoa_keys = CocoaEntryKeys(self.entry)
            self.entry.set_has_frame(False)
            self.entry.set_width_chars(1)        # a largura segue o texto (_update_hint)
            self.entry.connect("changed", lambda _e: self._search_soon())
            self.entry.connect("activate", lambda _e: self._activate())
            field.pack_start(self.entry, False, False, 0)
            self.placeholder = label(SPOT_MODES["all"], "spot-placeholder")
            self.placeholder.set_valign(Gtk.Align.CENTER)
            field.pack_start(self.placeholder, False, False, 0)
            self.hint = label("", "spot-hint", markup=True)
            self.hint.set_no_show_all(True)
            self.hint.set_valign(Gtk.Align.CENTER)
            self.hint.set_ellipsize(Pango.EllipsizeMode.END)
            self.hint.set_max_width_chars(1)     # o painel não cresce com nomes longos
            field.pack_start(self.hint, False, False, 0)
            # Tahoe: num modo, o atalho aparece à direita do campo em duas teclinhas ("⌘ 2")
            self.keys = Gtk.Box(spacing=3)
            self.keys.set_valign(Gtk.Align.CENTER)
            self.key_num = label("", "spot-key", 0.5)
            self.keys.pack_start(label("⌘", "spot-key", 0.5), False, False, 0)
            self.keys.pack_start(self.key_num, False, False, 0)
            self.keys.set_no_show_all(True)
            for ch in self.keys.get_children():
                ch.show()
            field.pack_end(self.keys, False, False, 0)
            # Tahoe, modo Arquivos aberto: "⋯" num círculo de ≈ 20 no lugar das teclinhas
            self.more = label("⋯", "spot-more", 0.5)
            self.more.set_valign(Gtk.Align.CENTER)
            self.more.set_no_show_all(True)
            field.pack_end(self.more, False, False, 0)
            self.top_icon = Gtk.Image()
            add_class(self.top_icon, "spot-top-icon")
            self.top_icon.set_pixel_size(28)
            field.pack_end(self.top_icon, False, False, 0)

            self.sep = Gtk.Box()
            add_class(self.sep, "spot-sep")
            self.list = Gtk.ListBox()
            add_class(self.list, "spot-list")
            self.list.set_selection_mode(Gtk.SelectionMode.BROWSE)
            self.list.set_activate_on_single_click(True)
            self.list.connect("row-activated", lambda _l, row: self._run(row.item))
            self.list.connect("row-selected", lambda _l, r: (
                r is not None and self.calc_sel and self._set_calc_sel(False),
                self._update_hint(), self._tab_hints()))
            self.scroll = Gtk.ScrolledWindow()
            self.scroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
            self.scroll.set_propagate_natural_height(True)
            self.scroll.set_max_content_height(SPOT_VISIBLE * SPOT_ROW + 10)
            self.scroll.add(self.list)
            self.foot = label("", "spot-foot")
            # grade do modo Arquivos (vazio): filtros + Suggestions + Recents
            self.gbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            add_class(self.gbox, "spot-grid")
            self.gscroll = Gtk.ScrolledWindow()
            self.gscroll.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
            self.gscroll.set_size_request(-1, SPOT_PANEL_H - SPOT_FIELD - 1)
            self.gscroll.add(self.gbox)
            self.cells, self.cell_sel, self.file_filter, self.app_filter = [], -1, None, None

            # filtros da busca (spotlight-busca-filtros-tab): cápsulas do tamanho do texto com os
            # tipos e os apps dos resultados; a fileira é cortada à direita e rola
            self.qfilters = Gtk.Box(spacing=8)
            self.qf_sc = Gtk.ScrolledWindow()
            self.qf_sc.set_policy(Gtk.PolicyType.EXTERNAL, Gtk.PolicyType.NEVER)
            self.qf_sc.add(self.qfilters)
            add_class(self.qf_sc, "spot-filters", "spot-cats", "spot-qfilters")
            self.qf_sc.connect("scroll-event", self._cats_scroll)

            # conta digitada (video/frames-ui/ui_0156, 2,395 px/pt): cartão de 554×55 recuado 17,
            # 2 abaixo do campo e 9 acima do filete; "5+5 =" 12 em cima, "10" 19 embaixo, botão
            # de copiar redondo de 23 a 15 da borda. Selecionado por padrão; ↩ copia.
            self.calc_card = Gtk.EventBox()
            self.calc_card.set_visible_window(False)
            cbox = Gtk.Box(spacing=8)
            add_class(cbox, "spot-calc")
            self.calc_box = cbox
            ctexts = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
            ctexts.set_valign(Gtk.Align.CENTER)
            self.calc_expr = label("", "spot-calc-expr")
            self.calc_val = label("", "spot-calc-val")
            self.calc_val.set_ellipsize(Pango.EllipsizeMode.END)
            ctexts.pack_start(self.calc_expr, False, False, 0)
            ctexts.pack_start(self.calc_val, False, False, 0)
            cbox.pack_start(ctexts, True, True, 0)
            ccopy = Gtk.Button()
            add_class(ccopy, "spot-calc-copy")
            ccopy.add(label(G("f018f"), "icon", 0.5))          # documentos (copiar)
            ccopy.set_valign(Gtk.Align.CENTER)
            ccopy.set_can_focus(False)
            ccopy.set_tooltip_text("Copy")
            ccopy.connect("clicked", lambda _b: self.calc_item and self._run(self.calc_item))
            cbox.pack_end(ccopy, False, False, 0)
            self.calc_card.add(cbox)
            self.calc_card.connect("button-press-event",
                                   lambda *_: (self.calc_item and self._run(self.calc_item), True)[1])
            self.calc_card.set_no_show_all(True)
            cbox.show_all()
            self.calc_item, self.calc_sel = None, False

            self.panel.pack_start(field, False, False, 0)
            self.panel.pack_start(self.calc_card, False, False, 0)
            self.panel.pack_start(self.sep, False, False, 0)
            self.panel.pack_start(self.qf_sc, False, False, 0)
            self.panel.pack_start(self.scroll, False, False, 0)
            self.panel.pack_start(self.foot, False, False, 0)
            self.panel.pack_start(self.gscroll, False, False, 0)
            ev = Gtk.EventBox()
            ev.set_visible_window(False)
            ev.add(self.panel)
            ev.set_halign(Gtk.Align.CENTER)
            ev.set_valign(Gtk.Align.START)
            ev.set_margin_top(SPOT_TOP)
            ev.connect("button-press-event", lambda *_: True)
            self._spot_ev, self._spot_shift = ev, 0
            # controles de modo ao lado da cápsula (sobrepostos: não tiram a cápsula do centro)
            self.ctl = SpotControls(self, reduce_motion)
            ov = Gtk.Overlay()
            ov.add(ev)
            ov.add_overlay(self.ctl)
            self.win.add(ov)
            self.win.add_events(Gdk.EventMask.POINTER_MOTION_MASK)
            self.win.connect("motion-notify-event", self._win_motion)
            ov.connect("get-child-position", self._place_ctl)
            self._near_timer = None
            ov.show_all()
            for w in (self.sep, self.scroll, self.foot, self.gscroll, self.qf_sc):
                w.hide()

        # ── comando do D-Bus: "spotlight", "spotlight files", "spotlight mode actions" ──
        def command(self, arg=""):
            words = arg.split()
            if words and words[0] == "preview":     # testes: sem capturar o teclado
                return self.preview(" ".join(words[1:]))
            if words and words[0] == "mode":
                mode = self._norm(words[1] if len(words) > 1 else "")
                if mode == "clipboard":          # ⌘4: o histórico é o painel da Área de Transferência
                    self.hide()
                    return self.clipboard.show()
                return self._set_mode(mode) if self.open else self.show(mode)
            if self.open:
                return self.hide()
            mode = self._norm(words[0]) if words else "all"
            return self.clipboard.show() if mode == "clipboard" else self.show(mode)

        @staticmethod
        def _norm(m):
            return {"apps": "apps", "1": "apps", "files": "files", "arquivos": "files", "2": "files",
                    "actions": "actions", "acoes": "actions", "ações": "actions", "3": "actions",
                    "clipboard": "clipboard", "area": "clipboard", "4": "clipboard"}.get(m, "all")

        def show(self, mode="all"):
            close_other_panels(self)
            mons = hypr_json("monitors")
            mon = next((m for m in mons if m.get("focused")), None)
            gmon = gdk_monitors()[0].get(mon["name"]) if mon else None
            if gmon:
                LS.set_monitor(self.win, gmon)
            self.open = True
            self.pending = None
            self._hist_i, self._hist_text = -1, None
            self._set_scope(None, search=False)
            self._load()
            self.entry.set_text("")
            self._set_mode(mode)
            self._stretch_in()
            self.win.show()
            self.ctl.show_controls(True)
            self.entry.grab_focus()
            dispatch('hl.dsp.submap("spotlight")')     # Super+1…4 trocam o modo

        def _stretch_in(self):
            """Entrada do Tahoe (referencias/telas/spotlight-abrir-1…2): a cápsula nasce ~5 %
            mais larga e um pouco mais baixa e volta ao tamanho, devagar e sem quicar."""
            if getattr(self, "_stretch_tick", None):
                self.panel.remove_tick_callback(self._stretch_tick)
                self._stretch_tick = None
            if reduce_motion():                          # sem elasticidade (WWDC25 219)
                self.panel.set_size_request(SPOT_W + 2 * 48, -1)
                self.field.set_size_request(-1, SPOT_FIELD)
                return
            t0 = [None]

            def frame(_w, clock):
                now = clock.get_frame_time() / 1e6
                if t0[0] is None:
                    t0[0] = now
                u = min(1.0, (now - t0[0]) / 0.55)
                e = 1 - (1 - u) ** 4                     # sai rápido, assenta bem suave
                sx, sy = 1 + 0.05 * (1 - e), 1 - 0.04 * (1 - e)
                self.panel.set_size_request(int(SPOT_W * sx) + 2 * 48, -1)
                self.field.set_size_request(-1, int(round(SPOT_FIELD * sy)))
                if u >= 1:
                    self._stretch_tick = None
                    return False
                return True
            self.panel.set_size_request(int(SPOT_W * 1.05) + 2 * 48, -1)     # 1º quadro já esticado
            self.field.set_size_request(-1, int(round(SPOT_FIELD * 0.96)))
            self._stretch_tick = self.panel.add_tick_callback(frame)

        def hide(self):
            if not self.open:
                return
            self.open = False
            self._grid_on = False
            self.ctl.reset()
            self.win.hide()
            if getattr(self, "_previewing", False):
                self._previewing = False
                LS.set_keyboard_mode(self.win, LS.KeyboardMode.EXCLUSIVE)
                return
            dispatch('hl.dsp.submap("reset")')

        def preview(self, text="", secs=1.5):
            """Mostra o painel com um texto, SEM pegar o teclado e sem submap, e fecha
            sozinho — para prints de teste enquanto alguém usa o computador."""
            if self.open:
                return
            self._previewing = True
            LS.set_keyboard_mode(self.win, LS.KeyboardMode.NONE)
            ctl = "+ctl" in text.split()           # testes: os botões de modo brotam sozinhos
            pick = next((w[1:] for w in text.split() if w.startswith("%")), None)   # "%folders"
            tab = "+tab" in text.split()           # testes: tab no 1º resultado (pasta)
            up = "+up" in text.split()             # testes: ↑ com o campo vazio (histórico)
            hover = next((w[7:] for w in text.split() if w.startswith("+hover=")), None)  # "+hover=files"
            text = " ".join(w for w in text.split()
                            if w not in ("+ctl", "+tab", "+up") and not w.startswith(("%", "+hover=")))
            if ctl:
                GLib.timeout_add(250, lambda: self.ctl.show_controls(True) and False)
            if hover in self.ctl.MODES:             # testes: ponteiro sobre um botão de modo
                GLib.timeout_add(700, lambda: self.ctl._set_hover(self.ctl.MODES.index(hover)) and False)
            mode = "all"
            if text.split()[:1] and text.split()[0].startswith("@"):     # "@files texto"
                mode, text = self._norm(text.split()[0][1:]), " ".join(text.split()[1:])
            self.open = True
            self._set_scope(None, search=False)
            self._load()
            self.entry.set_text(text)
            self._set_mode(mode)
            self._search()
            if up:
                ev = Gdk.Event.new(Gdk.EventType.KEY_PRESS)
                ev.keyval, ev.state = Gdk.KEY_Up, 0
                GLib.timeout_add(300, lambda: self._on_key(self.win, ev) and False)
            if pick:                                # testes: escolhe o filtro (vira token)
                def escolhe():                      # depois que os arquivos carregam
                    f = next((f for f in self.filters if f[0].startswith(pick)), None)
                    if f:
                        self._pick_filter(f)
                    if tab:
                        ev = Gdk.Event.new(Gdk.EventType.KEY_PRESS)
                        ev.keyval, ev.state = Gdk.KEY_Tab, 0
                        self._on_key(self.win, ev)
                    return False
                GLib.timeout_add(450, escolhe)
            self._stretch_in()
            self.win.show()
            GLib.timeout_add(int(secs * 1000), lambda: self.hide() and False)

        def _hover_mode(self, mode):
            """Ponteiro sobre um botão de modo: o campo vazio antecipa o nome e o atalho dele
            ("Actions ⌘3", referencias/telas/spotlight-controles-2…6) sem trocar de modo;
            ao sair, volta ao modo atual."""
            if self.scope or self.entry.get_text():
                return
            shown = mode or self.mode
            self.entry.set_placeholder_text(SPOT_MODES.get(shown, SPOT_MODES["all"]))
            self.placeholder.set_text(SPOT_MODES.get(shown, SPOT_MODES["all"]))
            num = {"apps": "1", "files": "2", "actions": "3", "clipboard": "4"}.get(mode) if mode else \
                {"apps": "1", "files": "2", "actions": "3"}.get(self.mode)
            self.key_num.set_text(num or "")
            self.keys.set_visible(bool(num))
            self._update_hint()

        def _set_mode(self, mode):
            self.mode = mode
            # Tahoe: o placeholder vira o nome do modo ("Files") e o atalho fica à direita
            self.entry.set_placeholder_text(SPOT_MODES.get(mode, SPOT_MODES["all"]))
            self.placeholder.set_text(SPOT_MODES.get(mode, SPOT_MODES["all"]))
            self.mode_pill.set_visible(False)
            num = {"apps": "1", "files": "2", "actions": "3"}.get(mode)
            self.key_num.set_text(num or "")
            self.keys.set_visible(bool(num))
            # Tahoe (referencias/telas/spotlight-clique-modo-*): no modo, a lupa vira o ícone dele
            self.glass_icon.set_text(G({"files": "f0256", "actions": "f0328"}.get(mode, "f0349")))
            self.glass_icon.set_visible(mode != "apps")
            self.glass_a.set_visible(mode == "apps")
            self.ctl.queue_draw()
            self._search()

        # ── controles de modo (os 4 círculos de vidro) ──
        def _place_ctl(self, ov, child, rect):
            """O Gtk.Overlay pergunta onde pôr os botões: logo após a ponta da cápsula."""
            if child is not self.ctl:
                return False
            w = ov.get_allocated_width()
            # tela estreita (escala grande): sem caber os 4 botões, o conjunto anda para a
            # esquerda o mínimo necessário, em vez de cortar o último botão na borda
            shift = spot_shift(w, SPOT_W, self.ctl.OVER, self.ctl.w,
                               center_group=self.open and not self.sep.get_visible())
            if shift != self._spot_shift:
                self._spot_shift = shift
                # fora da alocação em curso: dentro dela a margem nova não gera outro layout
                GLib.idle_add(lambda s=shift: self._spot_ev.set_margin_end(2 * s) or False)
            rect.x = int(w / 2 - shift + SPOT_W / 2 - self.ctl.OVER)
            rect.y = int(SPOT_TOP + SPOT_FIELD / 2 - self.ctl.h / 2)
            rect.width, rect.height = self.ctl.w, self.ctl.h
            return True

        def _win_motion(self, _w, ev):
            """Ponteiro na extremidade direita da cápsula (ou sobre os botões já abertos):
            eles brotam. Como no Tahoe, só na ponta — não no campo de texto."""
            a = self.win.get_allocation()
            x0 = a.width / 2 - getattr(self, "_spot_shift", 0) + SPOT_W / 2
            fim = x0 + (self.ctl.w if self.ctl.t > 0 else 8)
            near = (x0 - SPOT_FIELD <= ev.x <= fim and
                    SPOT_TOP - 6 <= ev.y <= SPOT_TOP + SPOT_FIELD + 6)
            self._pointer_near(near)
            return False

        def _pointer_near(self, near):
            if self.sep.get_visible():          # com resultados, a cápsula virou painel
                near = False
            if not near:
                self._ctl_block = False         # depois de um clique, só voltam ao sair e entrar
            elif getattr(self, "_ctl_block", False):
                return
            if near:
                if self._near_timer:
                    GLib.source_remove(self._near_timer)
                    self._near_timer = None
                self.ctl.show_controls(True)
            elif self.ctl.target > 0 and not self._near_timer:
                def recolhe():
                    self._near_timer = None
                    self.ctl.show_controls(False)
                    return False
                self._near_timer = GLib.timeout_add(700, recolhe)

        def _pick_mode(self, mode):
            if mode == "clipboard":              # ⌘4: o histórico é o painel da Área de Transferência
                self.hide()
                return self.clipboard.show()
            self._set_mode(mode)
            # os botões voltam para dentro da cápsula (a mesma fusão, ao contrário)
            self._ctl_block = True
            if self._near_timer:
                GLib.source_remove(self._near_timer)
                self._near_timer = None
            self.ctl.show_controls(False)
            if not getattr(self, "_previewing", False):
                self.entry.grab_focus()

        # ── fontes ──
        def _load(self):
            if self.mod is None:
                try:
                    self.mod = _spot_items_module()
                except Exception as e:
                    print("spotlight-itens:", e, file=sys.stderr)
            if self.apps is None:
                self._load_apps()
            try:      # ações: rápidas, leem os menus da barra na hora
                self.actions = self.mod.action_items() if self.mod else []
            except Exception:
                self.actions = []
            self.actions = self.actions + [a for a in SPOT_ARG_ACTIONS
                                           if a["id"] not in {x["id"] for x in self.actions}]
            self._qk = quickkeys.load()
            self._qk_keys = quickkeys.effective(self.actions, self._qk)
            self.hist = {m: set(self.mod.history_ids(m)) if self.mod else set()
                         for m in ("apps", "files", "actions")}
            in_thread(self._load_files)

        def _load_apps(self):
            self.apps, self.settings = [], []
            # painéis dos Ajustes do hyprmac (a lista da barra lateral dele)
            try:
                src = open(os.path.join(ROOT, "shell", "hyprmac-ajustes")).read()
                panes = re.findall(r'\("([a-z-]+)", "([^"]+)", "([a-z0-9]+)", "#[0-9A-Fa-f]{6}", "([^"]*)"\)', src)
            except OSError:
                panes = []
            cog = Gio.ThemedIcon.new("preferences-system")
            for key, title, _glyph, words in panes:
                self.settings.append({
                    "kind": "setting", "name": title, "gicon": cog, "sub": "System Settings",
                    "extra": words, "id": "ajustes:" + key,
                    "cmd": os.path.join(ROOT, "shell", "hyprmac-ajustes") + " " + key})
            for info in Gio.AppInfo.get_all():
                if not isinstance(info, Gio.DesktopAppInfo):
                    continue
                if re.fullmatch(r"gnome-.+-panel\.desktop", os.path.basename(info.get_filename() or "")):
                    continue
                if info.should_show():
                    self.apps.append({
                        "kind": "app", "name": info.get_name(), "gicon": info.get_icon(),
                        "sub": "", "id": info.get_filename(),
                        "wm_class": info.get_startup_wm_class() or "",
                        "executable": os.path.basename(info.get_executable() or ""),
                        "cat": spot_app_category(info.get_categories()),
                        "extra": " ".join([info.get_generic_name() or "",
                                           *(info.get_keywords() or []),
                                           info.get_executable() or ""])})
            self.apps.sort(key=lambda a: spot_fold(a["name"]))

        def _load_files(self):
            try:
                items = self.mod.file_items() if self.mod else []
            except Exception:
                items = []
            files = []
            for it in items:
                files.append(self._file_entry(it["id"], it.get("source", "")))
            GLib.idle_add(self._files_ready, files)

        def _file_entry(self, p, source=""):
            """Arquivo/pasta como item; subtítulo do Tahoe "5/7/25, 6:43 PM · Documents"
            (data de modificação · pasta onde está), aqui no formato do Brasil."""
            try:
                st = os.stat(p)
                when = time.strftime("%d/%m/%y, %H:%M", time.localtime(st.st_mtime))
                is_dir = os.path.isdir(p)
            except OSError:
                when, is_dir = "", False
            parent = os.path.dirname(p)
            where = os.path.basename(parent) or parent
            mime = "inode/directory" if is_dir else Gio.content_type_get_mime_type(
                Gio.content_type_guess(p, None)[0])
            return {"kind": "file", "name": os.path.basename(p) or p, "path": p, "id": p,
                    "dir": self.mod.tilde(parent) if self.mod else parent, "is_dir": is_dir,
                    "mime": mime,
                    "sub": f"{when} · {where}" if when else where, "extra": "", "source": source}

        def _files_ready(self, files):
            self.files = files
            if self.open and (self.entry.get_text().strip() or self.mode == "files"):
                self._search()
            # ícones/miniaturas prontos antes de alguém digitar — na thread do GTK, aos
            # poucos: o tema de ícones e o librsvg não podem ser usados de outra thread
            # (carregar SVG fora dela derrubou o shell com SIGSEGV)
            todo = [f["path"] for f in files if f["path"] not in self._pb]

            def batch():
                for path in todo[:25]:
                    self._file_pb(path)
                del todo[:25]
                return bool(todo)
            GLib.idle_add(batch, priority=GLib.PRIORITY_LOW)
            return False

        def _file_pb(self, path, size=28):
            key = path if size == 28 else (path, size)
            pb = self._pb.get(key, False)
            if pb is False:
                try:
                    pb = GdkPixbuf.Pixbuf.new_from_file_at_scale(
                        self.mod.file_icon(path), size, size, True)
                except Exception:
                    pb = None
                self._pb[key] = pb
            return pb

        def _arg_action(self, text):
            """"<quick key> <texto>" de uma ação que recebe texto → resultado pronto para rodar."""
            words = text.strip().split(None, 1)
            if len(words) != 2:
                return None
            for raw in self.actions or []:
                if raw.get("arg") and self._qk_keys.get(raw["id"]) == spot_fold(words[0]):
                    entry = self._action_entry(raw)
                    entry.update(name=f"{raw['label']} “{words[1]}”", argtext=words[1],
                                 id=f"{raw['id']}:{words[1]}")
                    return entry
            return None

        def _action_entry(self, a):
            key = getattr(self, "_qk_keys", {}).get(a["id"], a.get("key") or "")
            if a.get("menu"):
                sub = f"{a['menu']} ▸ menu" + (f"  ·  {a['shortcut']}" if a.get("shortcut") else "")
            else:
                sub = "Action"
            return {"kind": "action", "name": a["label"], "sub": sub, "id": a["id"],
                    "extra": key, "key": key, "raw": a,
                    "icons": a.get("icons") or self.mod.MENU_ICONS.get(a.get("menu"), [])}

        # ── busca ──
        def _search_soon(self):
            """Espera a pessoa parar de digitar por 40 ms (cada busca refaz a lista)."""
            if self._debounce:
                GLib.source_remove(self._debounce)
            self._debounce = GLib.timeout_add(40, self._search_now)

        def _search_now(self):
            self._debounce = None
            self._search()
            return False

        def _search(self):
            from spotlight_search import (spot_filter_results, spot_app_results,
                                          spot_file_query, spot_file_matches)
            q = spot_fold(self.entry.get_text().strip())
            self.pending = None
            mode = self.mode
            out = []
            selector = spot_filter_results(self.entry.get_text(),
                        include_sources=getattr(self, "clipboard", None) is not None) if not self.scope else None
            if selector is not None:
                self.results, self.filters = selector, []
                return self._fill()
            if self.scope and self.scope.get("target"):
                sc = self.scope
                self.results = spot_app_results(
                    sc, self.entry.get_text(),
                    clients=(hypr_json("clients") or []) if sc["target"] == "windows" else [],
                    actions=sc.get("app_actions", []), files=self.files, settings=self.settings)
                self.filters = []
                return self._fill()
            if mode == "all" and q:
                v = spot_calc(self.entry.get_text())
                if v is not None:
                    out.append((1000, {"kind": "calc", "name": v, "sub": "Calculator  ·  ↩ Copy",
                                       "id": "calc"}))
            sc = self.scope
            file_query, file_kinds = spot_file_query(self.entry.get_text())
            file_q = spot_fold(file_query)
            if file_kinds and mode == "all" and (not sc or sc["key"] in ("files", "folders")):
                mode = "files"
            if sc and sc.get("path"):            # tab numa pasta: busca dentro dela
                for f in self._folder_items(sc["path"]):
                    if not spot_file_matches(f, file_kinds):
                        continue
                    s_ = spot_score(file_q, f["name"]) if file_q else 1
                    if s_:
                        out.append((s_, f))
                if q:
                    out.sort(key=lambda t: -t[0])
                self.results, self.filters = [it for _s, it in out[:200]], []
                return self._fill()
            if mode == "all" and not q and not sc:   # Tahoe: aberto e vazio, é só a cápsula
                self.results, self.filters = [], []
                return self._fill()
            if mode in ("all", "apps"):
                for a in self.apps:
                    s = spot_score(q, a["name"], a["extra"])
                    if s:
                        out.append((s + SPOT_WEIGHT["app"] + (10 if a["id"] in self.hist["apps"] else 0), a))
            if mode == "all":
                for a in self.settings:
                    s = spot_score(q, a["name"], a["extra"]) if q or sc else 0
                    if s:
                        out.append((s + SPOT_WEIGHT["setting"], a))
            arg_hit = self._arg_action(self.entry.get_text()) if mode in ("all", "actions") and not sc else None
            if arg_hit:                          # "ar buy milk": a ação com o texto, em primeiro
                out.append((2000, arg_hit))
            if mode in ("all", "actions") and (q or sc or mode == "actions"):
                for raw in self.actions:
                    a = self._action_entry(raw)
                    s = 98 if q and a["key"] == q else spot_score(q, a["name"], a["sub"])
                    if s:
                        out.append((s + SPOT_WEIGHT["action"] + (10 if a["id"] in self.hist["actions"] else 0), a))
            if mode in ("all", "files") and (q or sc or mode == "files"):
                for i, f in enumerate(self.files):
                    if not spot_file_matches(f, file_kinds):
                        continue
                    s = spot_score(file_q, f["name"]) if file_q else 50 - i * 0.01
                    if s:
                        out.append((s + (SPOT_WEIGHT["file"] if mode == "all" else 0)
                                    + (10 if f["id"] in self.hist["files"] else 0), f))
            if q:
                out.sort(key=lambda t: -t[0])
            if sc:                               # filtro escolhido (token): só esse tipo/app
                out = [t for t in out if (t[1]["kind"] == "file" if sc["key"] == "files"
                                         else self._filter_of(t[1])[0] == sc["key"])]
            self.results = [it for _s, it in out[:40 if q or sc else 250]]
            # cápsulas: os tipos/apps dos melhores resultados, na ordem em que aparecem
            self.filters = []
            if mode == "all" and q and not sc:
                seen = set()
                for _s, it in out[:60]:
                    f = self._filter_of(it)
                    if f[0] and f[0] not in seen:
                        seen.add(f[0])
                        self.filters.append(f)
            self._fill()

        def _filter_of(self, it):
            """(chave, rótulo, gicon) do filtro do resultado — Folders, Applications, System
            Settings, Actions ou o app que abre o arquivo (TextEdit, Preview…), como no Tahoe."""
            kind = it["kind"]
            if kind == "app":
                return ("apps", "Applications", Gio.ThemedIcon.new("system-software-install"))
            if kind == "setting":
                return ("settings", "System Settings", Gio.ThemedIcon.new("preferences-system"))
            if kind == "action":
                return ("actions", "Actions", Gio.ThemedIcon.new("system-run-symbolic"))
            if kind == "file":
                if it.get("is_dir"):
                    return ("folders", "Folders", Gio.ThemedIcon.new("folder"))
                app = self._file_app(it)
                if app:
                    info = Gio.DesktopAppInfo.new(app[0]) if app[0] else None
                    return ("app:" + app[0], app[1], info.get_icon() if info else None)
            return (None, None, None)

        def _folder_items(self, root):
            """Conteúdo da pasta (até 2 níveis, sem ocultos), mais recentes primeiro."""
            found = []
            base = root.rstrip("/").count("/")
            for cur, dirs, files in os.walk(root):
                dirs[:] = [d for d in dirs if not d.startswith(".")]
                if cur.rstrip("/").count("/") - base >= 1:
                    dirs[:] = []
                for n in dirs + [f for f in files if not f.startswith(".")]:
                    p = os.path.join(cur, n)
                    try:
                        found.append((os.lstat(p).st_mtime, p))
                    except OSError:
                        pass
                if len(found) > 600:
                    break
            found.sort(reverse=True)
            return [self._file_entry(p) for _m, p in found[:400]]

        def _set_scope(self, scope, search=True):
            """Filtro (token no campo) ligado/desligado."""
            self.scope = scope
            if scope:
                self.token_lbl.set_text(scope["label"])
                if (scope.get("path") or scope["key"] == "folders") and self.mod:
                    # a pasta azul colorida, como no resultado (não o símbolo do tema)
                    pb = self._file_pb(scope.get("path") or os.path.expanduser("~"), 22)
                    if pb:
                        self.token_img.set_from_pixbuf(pb)
                        self.token_img.show()
                    else:
                        self.token_img.hide()
                elif scope.get("gicon"):
                    self.token_img.set_from_gicon(scope["gicon"], Gtk.IconSize.DIALOG)
                    self.token_img.set_pixel_size(22)
                    self.token_img.show()
                else:
                    self.token_img.hide()
            self.token.set_visible(bool(scope))
            # com o token o campo não mostra placeholder (spotlight-busca-filtro-folders)
            self.entry.set_placeholder_text("" if scope else SPOT_MODES.get(self.mode, SPOT_MODES["all"]))
            self.placeholder.set_text("" if scope else SPOT_MODES.get(self.mode, SPOT_MODES["all"]))
            if search:
                self._search()

        def _pick_filter(self, f):
            self._set_scope({"key": f[0], "label": f[1], "gicon": f[2]})
            self.entry.grab_focus_without_selecting()

        def _files_view(self):
            """Modo Arquivos ou Apps sem texto: o painel vira a grade (filtros + ícones)."""
            return (not self.scope and self.mode in ("files", "apps")
                    and not self.entry.get_text().strip())

        def _fill(self):
            grid = self._files_view()
            self.gscroll.set_visible(grid)
            self.more.set_visible(grid)
            self.keys.set_visible(not grid and self.mode in ("apps", "files", "actions"))
            if grid:
                for row in self.list.get_children():
                    row.destroy()
                self.qf_sc.hide()
                self.sep.show()
                self.scroll.hide()
                self.foot.hide()
                set_class(self.panel, "spot-open", True)
                self._build_grid()
                self._update_hint()
                if not getattr(self, "_grid_on", False):
                    self._grid_on = True
                    self._grow_grid()
                elif getattr(self, "_grid_mode", None) != self.mode:
                    self.gbox.set_opacity(0)
                    self._fade_grid()
                self._grid_mode = self.mode
                return
            self._grid_on = False
            for ch in self.qfilters.get_children():
                ch.destroy()
            for f in getattr(self, "filters", []):
                b = Gtk.Button(label=f[1])
                add_class(b, "spot-filter", "spot-cat")
                b.set_can_focus(False)
                b.connect("clicked", lambda _b, f_=f: self._pick_filter(f_))
                self.qfilters.pack_start(b, False, False, 0)
            self.qfilters.show_all()
            self.qf_sc.set_visible(bool(getattr(self, "filters", [])))
            self.qf_sc.get_hadjustment().set_value(0)
            for row in self.list.get_children():
                row.destroy()
            calc = next((it for it in self.results if it["kind"] == "calc"), None)
            self.calc_item = calc
            self.calc_card.set_visible(bool(calc))
            if calc:
                self.calc_expr.set_text(self.entry.get_text().strip() + " =")
                self.calc_val.set_text(calc["name"])
            self.calc_sel = bool(calc)
            set_class(self.calc_box, "selected", self.calc_sel)
            for it in self.results:
                if it["kind"] != "calc":
                    self.list.add(self._row(it))
            has = any(it["kind"] != "calc" for it in self.results)
            typed = bool(self.entry.get_text().strip())
            self.sep.set_visible(has or typed or self.mode != "all" or bool(self.scope))
            self.scroll.set_visible(has)
            self.foot.set_visible(not has and not calc and (typed or self.mode != "all" or bool(self.scope)))
            self.foot.set_text("No results" if typed or self.scope else "")
            set_class(self.panel, "spot-open", has or typed or self.mode != "all" or bool(self.scope))
            self.list.show_all()
            first = self.list.get_row_at_index(0)
            if first and not self.calc_sel:
                self.list.select_row(first)
            elif self.calc_sel:
                self.list.unselect_all()
            self.scroll.get_vadjustment().set_value(0)      # abria rolado, com a 1ª linha cortada
            self._update_hint()

        def _grow_grid(self):
            """Tahoe (spotlight-clique-modo-3…5): o painel cresce vazio a partir da cápsula e só
            depois o conteúdo aparece. Os quadros não dão o tempo: usa os 320 ms da mola do shell."""
            if getattr(self, "_grow_tick", None):
                self.gscroll.remove_tick_callback(self._grow_tick)
            full = SPOT_PANEL_H - SPOT_FIELD - 1
            self.gbox.set_opacity(0)
            if reduce_motion():                          # sem crescer; o conteúdo só esmaece
                self._grow_tick = None
                self.gscroll.set_size_request(-1, full)
                self._fade_grid()
                return
            t0 = [None]
            self.gscroll.set_size_request(-1, 1)

            def frame(_w, clock):
                now = clock.get_frame_time() / 1e6
                if t0[0] is None:
                    t0[0] = now
                u = min(1.0, (now - t0[0]) / (POP_MS / 1000))
                e = 1 - (1 - u) ** 3
                self.gscroll.set_size_request(-1, max(1, int(full * e)))
                if u >= 1:
                    self._grow_tick = None
                    self._fade_grid()
                    return False
                return True
            self._grow_tick = self.gscroll.add_tick_callback(frame)

        def _fade_grid(self):
            t0 = [None]

            def frame(_w, clock):
                now = clock.get_frame_time() / 1e6
                if t0[0] is None:
                    t0[0] = now
                u = min(1.0, (now - t0[0]) / 0.15)
                self.gbox.set_opacity(u)
                return u < 1
            self.gbox.add_tick_callback(frame)

        # ── modo Arquivos: grade ──
        def _file_app(self, f):
            """App padrão para o tipo do arquivo (para as cápsulas de filtro)."""
            if "app" not in f:
                app = None
                try:
                    ctype, _ = Gio.content_type_guess(f["name"], None)
                    info = Gio.AppInfo.get_default_for_type(ctype, False)
                    app = (info.get_id(), info.get_name()) if info else None
                except Exception:
                    app = None
                f["app"] = app
            return f["app"]

        def _build_grid(self):
            for ch in self.gbox.get_children():
                ch.destroy()
            self.cells, self.cell_sel = [], -1
            if self.mode == "apps":
                return self._build_apps_grid()
            files = self.files
            # filtros: os apps que abrem os arquivos recentes, os mais frequentes primeiro (até 5)
            count = {}
            for f in files[:80]:
                app = self._file_app(f)
                if app:
                    count[app] = count.get(app, 0) + 1
            apps = [a for a, _n in sorted(count.items(), key=lambda t: -t[1])][:5]
            if self.file_filter and self.file_filter not in {a[0] for a in apps}:
                self.file_filter = None
            if apps:
                row = Gtk.Box(spacing=8, homogeneous=False)
                add_class(row, "spot-filters")
                for app_id, name in apps:
                    b = Gtk.Button(label=name)
                    add_class(b, "spot-filter")
                    if app_id == self.file_filter:
                        add_class(b, "active")
                    b.set_can_focus(False)
                    b.connect("clicked", lambda _b, a=app_id: self._toggle_filter(a))
                    row.pack_start(b, True, True, 0)
                self.gbox.pack_start(row, False, False, 0)
            if self.file_filter:
                files = [f for f in files if (self._file_app(f) or ("",))[0] == self.file_filter]
            sugg = [f for f in files if f.get("source") == "history"][:SPOT_COLS]
            rest = [f for f in files if f not in sugg][:60]
            first = True
            for title, items in (("Suggestions", sugg), ("Recents", rest)):
                if not items:
                    continue
                if not first:
                    sep = Gtk.Box()
                    add_class(sep, "spot-grid-sep")
                    self.gbox.pack_start(sep, False, False, 0)
                hdr = label(title, "spot-grid-hdr")
                if first:
                    add_class(hdr, "first")
                self.gbox.pack_start(hdr, False, False, 0)
                grid = Gtk.Grid()
                add_class(grid, "spot-cells")
                grid.set_column_homogeneous(True)
                for i, f in enumerate(items):
                    grid.attach(self._cell(f), i % SPOT_COLS, i // SPOT_COLS, 1, 1)
                for i in range(len(items), SPOT_COLS):       # colunas vazias mantêm a largura
                    ph = Gtk.Box()
                    ph.set_size_request(SPOT_CELL_W, -1)
                    grid.attach(ph, i, 0, 1, 1)
                self.gbox.pack_start(grid, False, False, 0)
                first = False
            if not self.cells:
                self.gbox.pack_start(label("No Recent Files", "spot-foot"), False, False, 0)
            self.gbox.show_all()
            self.gscroll.get_vadjustment().set_value(0)

        def _cell(self, f):
            b = Gtk.Button()
            add_class(b, "spot-cell")
            b.set_relief(Gtk.ReliefStyle.NONE)
            b.set_can_focus(False)
            b.set_size_request(SPOT_CELL_W, -1)
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
            img = Gtk.Image()
            pb = self._file_pb(f["path"], 2 * SPOT_THUMB)
            if pb:
                k = SPOT_THUMB / max(pb.get_width(), pb.get_height())
                pb = pb.scale_simple(max(1, round(pb.get_width() * k)), max(1, round(pb.get_height() * k)),
                                     GdkPixbuf.InterpType.HYPER)
                img.set_from_pixbuf(pb)
            else:
                img.set_from_icon_name("text-x-generic", Gtk.IconSize.DIALOG)
                img.set_pixel_size(SPOT_THUMB)
            img.set_size_request(SPOT_THUMB, SPOT_THUMB)
            add_class(img, "spot-thumb")
            box.pack_start(img, False, False, 0)
            name = Gtk.Label(label=f["name"])
            add_class(name, "spot-cell-name")
            name.set_line_wrap(True)
            name.set_line_wrap_mode(Pango.WrapMode.WORD_CHAR)
            name.set_lines(2)
            name.set_ellipsize(Pango.EllipsizeMode.END)
            name.set_justify(Gtk.Justification.CENTER)
            name.set_max_width_chars(12)
            name.set_size_request(SPOT_CELL_W - 12, -1)
            box.pack_start(name, False, False, 0)
            b.add(box)
            b.item = f
            b.set_tooltip_text(f["dir"] + "/" + f["name"] if f.get("dir") else f["name"])
            b.connect("clicked", lambda _b, it=f: self._run(it))
            self.cells.append(b)
            return b

        def _build_apps_grid(self):
            """Modo Apps (spotlight-modo-apps-9): categorias · usados por último · filete · todos."""
            apps = self.apps or []
            present = {a["cat"] for a in apps if a.get("cat")}
            cats = [c for c, _k in SPOT_APP_CATS if c in present]
            if self.app_filter not in cats:
                self.app_filter = None
            if cats:
                row = Gtk.Box(spacing=8)
                for cat in cats:
                    b = Gtk.Button(label=cat)
                    add_class(b, "spot-filter", "spot-cat")
                    if cat == self.app_filter:
                        add_class(b, "active")
                    b.set_can_focus(False)
                    b.connect("clicked", lambda _b, c=cat: self._toggle_app_filter(c))
                    row.pack_start(b, False, False, 0)
                # as cápsulas têm o tamanho do texto e a fileira é cortada à direita (rola)
                sc = Gtk.ScrolledWindow()
                sc.set_policy(Gtk.PolicyType.EXTERNAL, Gtk.PolicyType.NEVER)
                sc.add(row)
                add_class(sc, "spot-filters", "spot-cats")
                sc.connect("scroll-event", self._cats_scroll)
                self.gbox.pack_start(sc, False, False, 0)
            if self.app_filter:
                apps = [a for a in apps if a.get("cat") == self.app_filter]
            by_id = {a["id"]: a for a in apps}
            recent = [by_id[i] for i in (self.mod.history_ids("apps") if self.mod else []) if i in by_id]
            seen, sugg = set(), []
            for a in recent:
                if a["id"] not in seen:
                    seen.add(a["id"])
                    sugg.append(a)
            sugg = sugg[:SPOT_COLS]
            first = True
            for items in (sugg, apps):
                if not items:
                    continue
                if not first:
                    sep = Gtk.Box()
                    add_class(sep, "spot-grid-sep", "apps")
                    self.gbox.pack_start(sep, False, False, 0)
                grid = Gtk.Grid(row_spacing=9)
                add_class(grid, "spot-cells", "apps")
                if first:
                    add_class(grid, "first")
                grid.set_column_homogeneous(True)
                for i, a in enumerate(items):
                    grid.attach(self._app_cell(a), i % SPOT_COLS, i // SPOT_COLS, 1, 1)
                for i in range(len(items), SPOT_COLS):       # colunas vazias mantêm a largura
                    ph = Gtk.Box()
                    ph.set_size_request(SPOT_CELL_W, -1)
                    grid.attach(ph, i, 0, 1, 1)
                self.gbox.pack_start(grid, False, False, 0)
                first = False
            if not self.cells:
                self.gbox.pack_start(label("No Apps", "spot-foot"), False, False, 0)
            self.gbox.show_all()
            self.gscroll.get_vadjustment().set_value(0)

        def _cats_scroll(self, sc, ev):
            """Roda do mouse na fileira de categorias: rola para o lado."""
            adj = sc.get_hadjustment()
            ok, dx, dy = ev.get_scroll_deltas()
            if not ok:
                dy = {Gdk.ScrollDirection.UP: -1, Gdk.ScrollDirection.DOWN: 1,
                      Gdk.ScrollDirection.LEFT: -1, Gdk.ScrollDirection.RIGHT: 1}.get(ev.direction, 0)
                dx = 0
            adj.set_value(adj.get_value() + (dx or dy) * 40)
            return True

        def _app_cell(self, a):
            b = Gtk.Button()
            add_class(b, "spot-cell", "app")
            b.set_relief(Gtk.ReliefStyle.NONE)
            b.set_can_focus(False)
            b.set_size_request(SPOT_CELL_W, -1)
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
            img = Gtk.Image()
            img.set_pixel_size(SPOT_APP_ICON)
            if a.get("gicon"):
                img.set_from_gicon(a["gicon"], Gtk.IconSize.DIALOG)
            else:
                img.set_from_icon_name("application-x-executable", Gtk.IconSize.DIALOG)
            img.set_size_request(SPOT_APP_ICON, SPOT_APP_ICON)
            add_class(img, "spot-thumb", "app")
            box.pack_start(img, False, False, 0)
            name = Gtk.Label(label=a["name"])
            add_class(name, "spot-cell-name", "app")
            name.set_ellipsize(Pango.EllipsizeMode.END)
            name.set_max_width_chars(10)          # ~92 pt, como "Adobe Premiere…" na referência
            name.set_size_request(SPOT_CELL_W - 20, -1)
            name.set_halign(Gtk.Align.CENTER)     # senão estica até a célula e não corta
            box.pack_start(name, False, False, 0)
            b.add(box)
            b.item = a
            b.set_tooltip_text(a["name"])
            if a.get("id") and os.path.isfile(a["id"]):
                b.drag_source_set(Gdk.ModifierType.BUTTON1_MASK,
                                  [Gtk.TargetEntry.new("text/uri-list", 0, 0)],
                                  Gdk.DragAction.COPY)
                b.connect("drag-data-get", lambda _w, _context, data, _info, _time, path=a["id"]:
                          data.set_uris([Gio.File.new_for_path(path).get_uri()]))
                # O Spotlight ocupa a tela; durante o gesto deixa o Dock receber o drop.
                b.connect("drag-begin", lambda *_: self.win.get_window().set_pass_through(True))
                b.connect("drag-end", lambda *_: self.win.get_window().set_pass_through(False))
            b.connect("clicked", lambda _b, it=a: self._run(it))
            self.cells.append(b)
            return b

        def _toggle_app_filter(self, cat):
            self.app_filter = None if self.app_filter == cat else cat
            self._build_grid()

        def _toggle_filter(self, app_id):
            self.file_filter = None if self.file_filter == app_id else app_id
            self._build_grid()

        def _move_cell(self, dx, dy):
            n = len(self.cells)
            if not n:
                return
            i = self.cell_sel
            if i < 0:
                i = 0
            else:
                i = max(0, min(n - 1, i + dx + dy * SPOT_COLS))
            if 0 <= self.cell_sel < n:
                self.cells[self.cell_sel].get_style_context().remove_class("selected")
            self.cell_sel = i
            cell = self.cells[i]
            cell.get_style_context().add_class("selected")
            a = cell.get_allocation()
            adj = self.gscroll.get_vadjustment()
            ok, _x, y = cell.translate_coordinates(self.gbox, 0, 0) or (False, 0, 0)
            if ok:
                if y < adj.get_value():
                    adj.set_value(max(0, y - 30))
                elif y + a.height > adj.get_value() + adj.get_page_size():
                    adj.set_value(y + a.height - adj.get_page_size() + 10)

        def _icon(self, it, size=28):
            img = Gtk.Image()
            img.set_pixel_size(size)
            kind = it["kind"]
            if kind in ("app", "setting", "window", "app_action") and it.get("gicon"):
                img.set_from_gicon(it["gicon"], Gtk.IconSize.DIALOG)
            elif kind == "file":
                pb = self._file_pb(it["path"], size)
                if pb:
                    img.set_from_pixbuf(pb)
                else:
                    img.set_from_icon_name("text-x-generic", Gtk.IconSize.DIALOG)
            elif kind == "calc":
                img.set_from_icon_name("accessories-calculator", Gtk.IconSize.DIALOG)
            else:
                theme = Gtk.IconTheme.get_default()
                name = next((n for n in it.get("icons", []) if theme.has_icon(n)), "system-run")
                img.set_from_icon_name(name, Gtk.IconSize.DIALOG)
            img.set_pixel_size(size)
            return img

        def _row(self, it):
            row = Gtk.ListBoxRow()
            row.item = it
            box = Gtk.Box(spacing=0)
            add_class(box, "spot-row")
            box.set_size_request(-1, SPOT_ROW - 2)
            icon = self._icon(it)
            add_class(icon, "spot-icon")
            box.pack_start(icon, False, False, 0)
            texts = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
            texts.set_valign(Gtk.Align.CENTER)
            title = label(it["name"], "spot-title")
            title.set_ellipsize(Pango.EllipsizeMode.END)
            title.set_max_width_chars(1)
            texts.pack_start(title, False, False, 0)
            if it.get("sub"):
                sub = label(it["sub"], "spot-sub")
                sub.set_ellipsize(Pango.EllipsizeMode.END)
                sub.set_max_width_chars(1)
                texts.pack_start(sub, False, False, 0)
                row.sub_label = sub
            box.pack_start(texts, True, True, 0)
            if it["kind"] == "action" and (it.get("key") or self.mode == "actions"):
                box.pack_end(self._quick_key_widget(it), False, False, 0)
            if it["kind"] == "app" or (it["kind"] == "file" and it.get("is_dir")):
                # Tahoe: "Search ai app  tab" à direita do resultado selecionado
                tab = Gtk.Box(spacing=6)
                tab.set_valign(Gtk.Align.CENTER)
                hint = label(f"Search in {it['name']}", "spot-tab-hint")
                hint.set_ellipsize(Pango.EllipsizeMode.END)
                hint.set_max_width_chars(18)
                tab.pack_start(hint, False, False, 0)
                tab.pack_start(label("tab", "spot-key spot-tab-key", 0.5), False, False, 0)
                tab.set_no_show_all(True)
                for ch in tab.get_children():
                    ch.show()
                box.pack_end(tab, False, False, 0)
                row.tab_hint = tab
            row.add(box)
            return row

        # ── quick keys (Mac User Guide ▸ Take actions and shortcuts in Spotlight) ──
        def _quick_key_widget(self, it):
            """Tecla da ação à direita; no modo Ações, sem tecla, "Add quick keys". Clicar
            abre o campo no lugar: Return grava, Esc ou sair do campo cancela."""
            stack = Gtk.Stack()
            stack.set_valign(Gtk.Align.CENTER)
            button = Gtk.Button()
            add_class(button, "spot-qk", "spot-qk-add" if not it.get("key") else "spot-qk-key")
            button.set_relief(Gtk.ReliefStyle.NONE)
            button.set_can_focus(False)
            button.add(label(it.get("key") or "Add quick keys", "spot-qk-label", 0.5))
            entry = Gtk.Entry()
            add_class(entry, "spot-qk-entry")
            entry.set_width_chars(MAX_QK_CHARS)
            entry.set_max_length(quickkeys.MAX_LEN)
            stack.add_named(button, "show")
            stack.add_named(entry, "edit")

            def edit(_b):
                entry.set_text(it.get("key") or "")
                stack.set_visible_child_name("edit")
                entry.grab_focus()
                self._qk_editing = (entry, stack, it)

            def done(save):
                if getattr(self, "_qk_editing", None) is None or self._qk_editing[0] is not entry:
                    return
                self._qk_editing = None
                if save:
                    self._qk_save(quickkeys.assign(self._qk, it["id"], entry.get_text(), self._qk_keys))
                    self._search()
                else:
                    stack.set_visible_child_name("show")
                self.entry.grab_focus_without_selecting()
            button.connect("clicked", edit)
            entry.connect("activate", lambda _e: done(True))
            entry.connect("focus-out-event", lambda *_: done(False) or False)
            entry._qk_cancel = lambda: done(False)
            stack.show_all()
            return stack

        def _qk_save(self, overrides):
            self._qk = overrides
            self._qk_keys = quickkeys.effective(self.actions or [], overrides)
            in_thread(quickkeys.save, dict(overrides))

        def _tab_hints(self):
            sel = self.list.get_selected_row()
            for row in self.list.get_children():
                if hasattr(row, "tab_hint"):
                    row.tab_hint.set_visible(row is sel)

        def _selected(self):
            if self._files_view():
                return self.cells[self.cell_sel].item if 0 <= self.cell_sel < len(self.cells) else None
            if self.calc_sel and self.calc_item:
                return self.calc_item
            row = self.list.get_selected_row()
            return row.item if row else None

        def _set_calc_sel(self, on):
            self.calc_sel = bool(on and self.calc_item)
            set_class(self.calc_box, "selected", self.calc_sel)
            if self.calc_sel:
                self.list.unselect_all()
            self._update_hint()

        def _update_hint(self):
            """Conclusão em linha: o resto do nome do melhor resultado + o que o Enter faz."""
            text = self.entry.get_text()
            it = self._selected()
            layout = self.entry.create_pango_layout(text)
            # mede no tamanho do CSS (25): antes de a janela abrir o estilo ainda não chegou
            fd = self.entry.get_style_context().get_property("font", Gtk.StateFlags.NORMAL).copy()
            fd.set_absolute_size(30 * Pango.SCALE)
            layout.set_font_description(fd)
            text_w = layout.get_pixel_size()[0] + 6
            self.entry.set_size_request(text_w, -1)
            self.placeholder.set_visible(not text and not self.scope)
            if not it or not text.strip():
                self.hint.hide()
                self.top_icon.clear()
                return
            verb = {"app": "Open", "setting": "Open", "file": "Open", "action": "Run",
                    "calc": "Copy", "filter": "Filter", "window": "Show",
                    "app_action": "Run"}[it["kind"]]
            rest = ""
            if it["kind"] == "calc":
                rest = "  = " + it["name"]
            elif spot_fold(it["name"]).startswith(spot_fold(text)):
                rest = it["name"][len(text):]
            else:
                rest = "  " + it["name"]
            # como na referência: a conclusão no tamanho do texto, "— Open" menor e cinza
            markup = (f'<span>{GLib.markup_escape_text(rest)}</span>'
                      f'<span alpha="55%" size="80%">  —  {verb}</span>')
            if it["kind"] == "calc":     # ui_0156: só "= 10", menor e cinza, sem o verbo
                markup = f'<span alpha="55%" size="80%">= {GLib.markup_escape_text(it["name"])}</span>'

            self.hint.set_markup(markup)
            # só o espaço que sobra no campo (lupa 36, ícone 36, paddings 34, modo)
            pill = self.mode_pill.get_allocated_width() + 8 if self.mode_pill.get_visible() else 0
            if self.token.get_visible():
                pill += self.token.get_allocated_width() + 8
            room = SPOT_W - 36 - 36 - 34 - pill - text_w
            lay = self.hint.create_pango_layout(None)
            lay.set_markup(markup, -1)
            self.hint.set_size_request(max(40, min(room, lay.get_pixel_size()[0] + 14)), -1)
            self.hint.show()
            if it["kind"] in ("app", "setting") and it.get("gicon"):
                self.top_icon.set_from_gicon(it["gicon"], Gtk.IconSize.DIALOG)
                self.top_icon.set_pixel_size(28)
            elif it["kind"] == "calc":
                self.top_icon.set_from_icon_name("accessories-calculator", Gtk.IconSize.DIALOG)
                self.top_icon.set_pixel_size(28)
            else:
                self.top_icon.clear()

        # ── teclado ──
        def _on_key(self, _w, ev):
            if is_modified_arrow(ev):
                return False
            editing = getattr(self, "_qk_editing", None)
            if editing:                          # campo de quick key: as teclas são dele
                if ev.keyval == Gdk.KEY_Escape:
                    editing[0]._qk_cancel()
                    return True
                return False
            k, st = ev.keyval, ev.state
            ctrl = bool(st & (Gdk.ModifierType.CONTROL_MASK | Gdk.ModifierType.SUPER_MASK |
                              Gdk.ModifierType.MOD4_MASK))
            if k == Gdk.KEY_Escape:
                if self.entry.get_text():
                    self.entry.set_text("")
                elif self.scope:
                    self._set_scope(None)
                else:
                    self.hide()
                return True
            if k == Gdk.KEY_BackSpace and self.scope and not self.entry.get_text():
                self._set_scope(None)              # ⌫ com o campo vazio apaga o token
                return True
            if self._files_view() and k in (Gdk.KEY_Down, Gdk.KEY_Up, Gdk.KEY_Left, Gdk.KEY_Right):
                self._move_cell(*{Gdk.KEY_Left: (-1, 0), Gdk.KEY_Right: (1, 0),
                                  Gdk.KEY_Up: (0, -1), Gdk.KEY_Down: (0, 1)}[k])
                return True
            # ↑ com o campo vazio (ou mostrando uma busca do histórico): buscas anteriores
            text = self.entry.get_text()
            browsing = text and text == getattr(self, "_hist_text", None)
            if k == Gdk.KEY_Up and (not text or browsing) and not self.scope:
                if self._history_step(1):
                    return True
            if k in (Gdk.KEY_Down, Gdk.KEY_Up) and self.calc_item:
                rows = self.list.get_children()
                cur = self.list.get_selected_row()
                if k == Gdk.KEY_Down and self.calc_sel:
                    if rows:
                        self.calc_sel = False
                        set_class(self.calc_box, "selected", False)
                        self.list.select_row(rows[0])
                    return True
                if k == Gdk.KEY_Up and rows and cur is rows[0]:
                    self._set_calc_sel(True)
                    return True
            if k in (Gdk.KEY_Down, Gdk.KEY_Up):
                rows = self.list.get_children()
                if rows:
                    cur = self.list.get_selected_row()
                    i = rows.index(cur) if cur in rows else -1
                    i = min(len(rows) - 1, i + 1) if k == Gdk.KEY_Down else max(0, i - 1)
                    self.list.select_row(rows[i])
                    rows[i].grab_focus()
                    self.entry.grab_focus_without_selecting()
                return True
            if k == Gdk.KEY_Tab:
                from spotlight_search import spot_app_scope
                # O primeiro app é o alvo do Tab; a pasta selecionada mantém seu gesto.
                first = self.results[0] if self.results else None
                scope = spot_app_scope(first) if text.strip() and not self.scope else None
                if scope:
                    self._enter_app_scope(scope)
                    return True
                it = self._selected()
                if it and it["kind"] == "file" and it.get("is_dir"):
                    self.entry.set_text("")        # tab: buscar dentro da pasta (token = pasta)
                    self._set_scope({"key": "folder", "label": it["name"], "path": it["path"],
                                     "gicon": Gio.ThemedIcon.new("folder")})
                    return True
                if it and it["kind"] != "calc":
                    self.entry.set_text(it["name"])
                    self.entry.set_position(-1)
                return True
            if ctrl and k in (Gdk.KEY_r, Gdk.KEY_R):        # ⌘R: mostrar na pasta
                it = self._selected()
                if it and it["kind"] == "file":
                    self._run(it, reveal=True)
                return True
            if k in (Gdk.KEY_Return, Gdk.KEY_KP_Enter) and ctrl:
                it = self._selected()
                if it and it["kind"] == "file":
                    self._run(it, reveal=True)
                    return True
            return False

        def _activate(self):
            from spotlight_search import spot_filter_results
            if not self.scope and getattr(self, "clipboard", None) is not None:
                selector = spot_filter_results(self.entry.get_text(), include_sources=True)
                if selector is not None:
                    selected = self._selected()
                    it = next((it for it in selector if selected and it["id"] == selected["id"]),
                              selector[0] if selector else None)
                    if it:
                        self._run(it)
                    return
            key = spot_filter_command(self.entry.get_text())
            if key:
                kind = {"apps": "app", "folders": "file", "settings": "setting",
                        "actions": "action"}[key]
                f = self._filter_of({"kind": kind, "is_dir": key == "folders"})
                # O mesmo token das cápsulas; o modo geral contém todos os tipos.
                if self.mode != "all":
                    self._set_mode("all")
                self.entry.set_text("")
                self._pick_filter(f)
                return
            # Refaz o seletor para Return antes do debounce de 40 ms.
            from spotlight_search import spot_filter_results
            selector = spot_filter_results(self.entry.get_text()) if not self.scope else None
            if selector is not None and getattr(self, "results", None) is not None:
                selected = self._selected()
                it = next((it for it in selector if selected and it["id"] == selected["id"]),
                          selector[0] if selector else None)
                if it:
                    self._run(it)
                return
            it = self._selected()
            if it:
                self._run(it)

        def _enter_app_scope(self, scope):
            """Ações .desktop pertencem ao app, sem misturar menus de outro app."""
            app = scope["app"]
            if not scope.get("gicon"):
                scope["gicon"] = Gio.ThemedIcon.new("application-x-executable")
            info = Gio.DesktopAppInfo.new_from_filename(app["id"])
            scope["app_actions"] = []
            if info and scope["target"] == "windows":
                for action in info.list_actions():
                    scope["app_actions"].append({
                        "kind": "app_action", "name": info.get_action_name(action),
                        "sub": app["name"], "id": app["id"] + ":" + action,
                        "desktop": app["id"], "action": action, "gicon": app.get("gicon")})
            if self.mode != "all":
                self._set_mode("all")
            self.entry.set_text("")
            self._set_scope(scope)
            self.entry.grab_focus_without_selecting()

        # ── histórico das buscas (↑ com o campo vazio, como no Spotlight do Tahoe) ──
        QUERIES = os.path.join(CACHE, "spotlight-buscas.json")

        def _queries(self):
            try:
                with open(self.QUERIES) as f:
                    q = json.load(f)
                return [t for t in q if isinstance(t, str)]
            except (OSError, ValueError):
                return []

        def _remember_query(self):
            text = self.entry.get_text().strip()
            if not text:
                return
            q = [t for t in self._queries() if t != text]
            q.insert(0, text)
            try:
                os.makedirs(CACHE, exist_ok=True)
                with open(self.QUERIES, "w") as f:
                    json.dump(q[:30], f)
            except OSError:
                pass

        def _history_step(self, d):
            """↑ (d=+1) volta para buscas mais antigas, ↓ (d=-1) para as mais novas; passar
            da mais nova devolve o campo vazio."""
            q = self._queries()
            if not q:
                return False
            i = getattr(self, "_hist_i", -1) + d
            if i < 0:
                self._hist_i = -1
                self._hist_text = None
                self.entry.set_text("")
                return True
            i = min(i, len(q) - 1)
            self._hist_i = i
            self._hist_text = q[i]
            self.entry.set_text(q[i])
            self.entry.set_position(-1)
            return True

        # ── executar ──
        def _run(self, it, reveal=False):
            kind = it["kind"]
            if kind == "filter":
                from spotlight_search import spot_filter_scope
                scope = spot_filter_scope(it, include_sources=getattr(self, "clipboard", None) is not None)
                if scope:
                    if scope["key"] == "clipboard":
                        return self._pick_mode("clipboard")
                    if scope["key"] == "files":
                        self._set_scope(None, search=False)
                        self.entry.set_text("")
                        self._set_mode("files")
                        self.entry.grab_focus_without_selecting()
                        return
                    scope["gicon"] = Gio.ThemedIcon.new(scope.pop("icon"))
                    if self.mode != "all":
                        self._set_mode("all")
                    self.entry.set_text("")
                    self._set_scope(scope)
                    self.entry.grab_focus_without_selecting()
                return
            mod = self.mod
            if kind == "action" and it["raw"].get("arg") and not it.get("argtext"):
                # Tahoe: digitar a quick key "prompt you to enter" o texto no próprio campo
                self.entry.set_text((it.get("key") or it["name"]) + " ")
                self.entry.set_position(-1)
                return
            self._remember_query()
            if kind == "action" and it["raw"].get("arg"):
                self.hide()
                in_thread(run_arg_action, it["raw"]["arg"], it["argtext"])
                new = quickkeys.after_run(self._qk, it["raw"], self._qk_keys)
                if new is not self._qk:
                    self._qk_save(new)
                return
            if kind == "action" and it["raw"].get("confirm") and self.pending is not it:
                self.pending = it        # como o alerta do Mac: Enter de novo confirma
                row = self.list.get_selected_row()
                if row is not None and hasattr(row, "sub_label"):
                    row.sub_label.set_text(f"Press ↩ again to {it['name'].rstrip('…')}")
                return
            self.hide()
            if kind == "calc":
                subprocess.run(["wl-copy"], input=it["name"].replace(" ", "").encode())
            elif kind == "app":
                spawn(f"gio launch {GLib.shell_quote(it['id'])}")
                mod and in_thread(mod.cmd_record_app, it["id"])
            elif kind == "setting":
                spawn(it["cmd"])
            elif kind == "window":
                dispatch("focuswindow address:" + it["address"])
            elif kind == "app_action":
                info = Gio.DesktopAppInfo.new_from_filename(it["desktop"])
                if info:
                    info.launch_action(it["action"], None)
            elif kind == "action":
                spawn(it["raw"]["cmd"])
                mod and in_thread(mod.record, "actions", it["id"], it["name"])
                # "Suggested quick keys are automatically assigned after running an action once"
                new = quickkeys.after_run(self._qk, it["raw"], self._qk_keys)
                if new is not self._qk:
                    self._qk_save(new)
            elif kind == "file":
                path = it["path"]
                if reveal:
                    uri = "file://" + urllib.parse.quote(path)
                    spawn("gdbus call --session --dest org.freedesktop.FileManager1 "
                          "--object-path /org/freedesktop/FileManager1 "
                          "--method org.freedesktop.FileManager1.ShowItems "
                          f"{GLib.shell_quote(json.dumps([uri]))} '' >/dev/null 2>&1 || "
                          f"gio open {GLib.shell_quote(os.path.dirname(path))}")
                else:
                    spawn(f"gio open {GLib.shell_quote(path)}")
                mod and in_thread(mod.record, "files", path, it["name"])

    return Spotlight
