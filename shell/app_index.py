"""Índice compartilhado de aplicativos instalados para os componentes do shell."""

import os

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gio, GLib, Gtk


class AppIndex:
    """Resolve classe de janela em nome e ícone a partir dos arquivos .desktop.

    Os fallbacks pertencem ao shell porque também conhecem seus ícones internos.
    O índice é construído sob demanda uma única vez e compartilhado por Dock,
    Spotlight, alternador e janela de encerramento forçado.
    """

    def __init__(self, fallback_name, fallback_icon, icon_size=72):
        self.fallback_name = fallback_name
        self.fallback_icon = fallback_icon
        self.icon_size = icon_size
        self.ready = False

    def _build(self):
        """Cria índices por desktop id, StartupWMClass e executável."""
        self.by_id, self.by_wm, self.by_exec = {}, {}, {}
        for info in Gio.AppInfo.get_all():
            if not isinstance(info, Gio.DesktopAppInfo):
                continue
            app_id = (info.get_id() or "").removesuffix(".desktop").lower()
            if app_id:
                self.by_id.setdefault(app_id, info)
            wm = (info.get_startup_wm_class() or "").lower()
            if wm:
                self.by_wm.setdefault(wm, info)
            args = [part for part in (info.get_commandline() or "").split()
                    if not part.startswith("%")]
            executable = os.path.basename(info.get_executable() or "").lower()
            # Atalhos web e jogos Steam compartilham o executável do processo pai.
            if executable and len(args) <= 1:
                self.by_exec.setdefault(executable, info)
        self.ready = True

    def _info(self, window_class):
        if not self.ready:
            self._build()
        name = (window_class or "").lower()
        short = name.split(".")[-1]
        return (self.by_id.get(name) or self.by_wm.get(name) or self.by_exec.get(name)
                or self.by_id.get(short) or self.by_wm.get(short))

    def name(self, window_class):
        info = self._info(window_class)
        return info.get_name() if info else None

    def lookup(self, window_class):
        name = (window_class or "").lower()
        info = self._info(window_class)
        display_name = info.get_name() if info else self.fallback_name(window_class)
        pixbuf = None
        if info and info.get_icon():
            icon = Gtk.IconTheme.get_default().lookup_by_gicon(
                info.get_icon(), self.icon_size * 2, Gtk.IconLookupFlags.FORCE_SIZE)
            try:
                pixbuf = icon.load_icon() if icon else None
            except GLib.Error:
                pass
        return display_name, pixbuf or self.fallback_icon(name, self.icon_size * 2)
