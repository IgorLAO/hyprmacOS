"""Sincroniza classes claro/escuro dos apps GTK próprios com a preferência do desktop.

Cada app preserva seu CSS e sua geometria. Este módulo só acompanha a mudança
de org.gnome.desktop.interface color-scheme durante a vida da janela.
"""

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gio


def bind_color_scheme(widget, settings=None):
    """Aplica dark/light agora e em mudanças posteriores; desliga ao destruir.

    Retorna Gio.Settings para que o widget conserve a assinatura. Sem o schema
    do desktop, mantém o modo escuro usado historicamente como fallback.
    """
    if settings is None:
        source = Gio.SettingsSchemaSource.get_default()
        schema = source.lookup("org.gnome.desktop.interface", True) if source else None
        if schema and schema.has_key("color-scheme"):
            settings = Gio.Settings.new_full(schema, None, None)

    def update(*_args):
        dark = settings is None or "dark" in settings.get_string("color-scheme")
        style = widget.get_style_context()
        style.remove_class("dark")
        style.remove_class("light")
        style.add_class("dark" if dark else "light")

    if settings is not None:
        handler = settings.connect("changed::color-scheme", update)
        widget.connect("destroy", lambda *_: settings.disconnect(handler))
    update()
    return settings
