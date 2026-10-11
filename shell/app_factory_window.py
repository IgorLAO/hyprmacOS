"""Shared GTK3 window for manifest based HyprMac apps.

The GTK theme supplies the existing Tahoe titlebar and traffic lights.  A
manifest supplies identity and structure; this module never claims that a
provisional layout is an Apple measurement.
"""

import importlib
import json
from pathlib import Path

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
gi.require_version("GdkPixbuf", "2.0")
from gi.repository import Gdk, GdkPixbuf, Gio, GLib, Gtk

from app_theme import bind_color_scheme
from tahoe.compatibility.button import TahoeButton, TahoeToggleButton, TahoeMenuButton


ROOT = Path(__file__).resolve().parent.parent


def _icon(manifest, size):
    name = manifest.get("icon", "application-x-executable")
    path = ROOT / name
    if path.is_file():
        pixbuf = GdkPixbuf.Pixbuf.new_from_file_at_scale(str(path), size, size, True)
        return Gtk.Image.new_from_pixbuf(pixbuf)
    return Gtk.Image.new_from_icon_name(name, Gtk.IconSize.DIALOG)


class FactoryWindow(Gtk.ApplicationWindow):
    def __init__(self, app, manifest):
        super().__init__(application=app, title=manifest["name"])
        self.manifest = manifest
        self.set_role(manifest["id"])
        self.set_default_size(*manifest.get("size", [760, 520]))
        self.set_position(Gtk.WindowPosition.CENTER)
        self.set_icon_name(manifest.get("icon_name", "application-x-executable"))
        self._settings_path = (Path.home() / ".config/hyprmac/app-factory" /
                               (manifest["id"] + ".json"))
        self._restore_size()
        self.connect("delete-event", self._save_size)
        bind_color_scheme(self)

        header = Gtk.HeaderBar()
        header.set_show_close_button(True)
        header.set_title(manifest["name"])
        self.set_titlebar(header)

        menu = TahoeMenuButton(icon_name="open-menu-symbolic")
        menu.set_tooltip_text("App menu")
        popup = Gtk.Menu()
        about = Gtk.MenuItem(label="About " + manifest["name"])
        about.connect("activate", self._about)
        quit_item = Gtk.MenuItem(label="Quit")
        quit_item.connect("activate", lambda *_: app.quit())
        popup.append(about)
        popup.append(quit_item)
        popup.show_all()
        menu.set_popup(popup)
        header.pack_end(menu)
        for item in manifest.get("toolbar_items", []):
            button = TahoeButton(label=item["label"])
            button.connect("clicked", self._toolbar_action, item["action"])
            header.pack_end(button)

        accel = Gtk.AccelGroup()
        self.add_accel_group(accel)
        quit_item.add_accelerator("activate", accel, Gdk.KEY_q,
                                  Gdk.ModifierType.CONTROL_MASK, Gtk.AccelFlags.VISIBLE)
        self.connect("key-press-event", self._keys)

        outer = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        self.add(outer)
        sidebar_items = manifest.get("sidebar_items", [])
        sidebar_groups = manifest.get("sidebar_groups", [])
        self._section = manifest.get("sidebar_default", manifest["name"])
        self._nav_buttons = []
        if manifest.get("layout") == "sidebar":
            sidebar = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=4)
            sidebar.set_size_request(manifest.get("sidebar_width", 210), -1)
            sidebar.set_border_width(12)
            sidebar.get_style_context().add_class("sidebar")
            outer.pack_start(sidebar, False, False, 0)
            if sidebar_groups or sidebar_items:
                groups = sidebar_groups or [{"title": "", "items": sidebar_items}]
                if self._section == manifest["name"]:
                    self._section = groups[0]["items"][0]
                for group in groups:
                    if group["title"]:
                        heading = Gtk.Label(label=group["title"])
                        heading.set_halign(Gtk.Align.START)
                        heading.set_margin_top(16)
                        heading.get_style_context().add_class("dim-label")
                        sidebar.pack_start(heading, False, False, 0)
                    for label in group["items"]:
                        button = TahoeToggleButton(label=label)
                        button.set_relief(Gtk.ReliefStyle.NONE)
                        button.set_halign(Gtk.Align.FILL)
                        button.set_active(label == self._section)
                        button.connect("clicked", self._select_sidebar, label)
                        self._nav_buttons.append(button)
                        sidebar.pack_start(button, False, False, 0)
            else:
                sidebar.pack_start(Gtk.Label(label=manifest["name"]), False, False, 0)
            outer.pack_start(Gtk.Separator(orientation=Gtk.Orientation.VERTICAL), False, False, 0)
        content = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=16)
        content.set_border_width(24)
        outer.pack_start(content, True, True, 0)
        self.content = content
        self._section_label = Gtk.Label(label=self._section)
        self._section_label.set_halign(Gtk.Align.START)
        self._section_label.get_style_context().add_class("title")
        content.pack_start(self._section_label, False, False, 0)

        backend = manifest.get("backend")
        if backend and backend["kind"] == "python_panel":
            panel_class = getattr(importlib.import_module(backend["module"]), backend["class"])
            self.panel = panel_class()
            content.pack_start(self.panel, True, True, 0)
        else:
            box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
            box.set_valign(Gtk.Align.CENTER)
            box.set_halign(Gtk.Align.CENTER)
            box.pack_start(_icon(manifest, 64), False, False, 0)
            title = Gtk.Label(label="COMING SOON")
            title.get_style_context().add_class("title")
            box.pack_start(title, False, False, 0)
            label = Gtk.Label(label="This app is being built for HyprMac.")
            label.get_style_context().add_class("dim-label")
            box.pack_start(label, False, False, 0)
            revealer = Gtk.Revealer()
            revealer.set_transition_type(Gtk.RevealerTransitionType.CROSSFADE)
            revealer.set_transition_duration(self._transition_duration())
            revealer.add(box)
            content.pack_start(revealer, True, True, 0)
            GLib.idle_add(self._reveal, revealer)
        self.show_all()

    def _transition_duration(self):
        try:
            config = json.loads((Path.home() / ".config/hyprmac/config.json").read_text())
            if config.get("reduce_motion"):
                return 0
        except (OSError, ValueError, TypeError):
            pass
        source = Gio.SettingsSchemaSource.get_default()
        schema = source.lookup("org.gnome.desktop.interface", True) if source else None
        if schema and schema.has_key("enable-animations"):
            settings = Gio.Settings.new_full(schema, None, None)
            if not settings.get_boolean("enable-animations"):
                return 0
        return self.manifest.get("transition_ms", 0)

    @staticmethod
    def _reveal(revealer):
        revealer.set_reveal_child(True)
        return False

    def _toolbar_action(self, _button, action):
        if action == "refresh" and hasattr(self, "panel") and hasattr(self.panel, "_refresh"):
            self.panel._refresh()

    def _select_sidebar(self, _button, label):
        self._section = label
        self._section_label.set_text(label)
        for button in self._nav_buttons:
            button.set_active(button.get_label() == label)

    def _keys(self, _widget, event):
        if event.state & Gdk.ModifierType.CONTROL_MASK and event.keyval == Gdk.KEY_w:
            self.close()
            return True
        return False

    def _about(self, *_args):
        dialog = Gtk.AboutDialog(transient_for=self, modal=True)
        dialog.set_program_name(self.manifest["name"])
        dialog.set_comments("HyprMac app factory · " + self.manifest["status"])
        dialog.run()
        dialog.destroy()

    def _restore_size(self):
        try:
            data = json.loads(self._settings_path.read_text())
            width, height = data["size"]
            if 320 <= width <= 4000 and 240 <= height <= 3000:
                self.set_default_size(width, height)
        except (OSError, ValueError, KeyError, TypeError):
            pass

    def _save_size(self, *_args):
        width, height = self.get_size()
        self._settings_path.parent.mkdir(parents=True, exist_ok=True)
        self._settings_path.write_text(json.dumps({"size": [width, height]}))
        return False


def run_app(manifest, smoke=False):
    GLib.set_prgname(manifest["id"])

    class FactoryApp(Gtk.Application):
        def __init__(self):
            super().__init__(application_id=manifest["id"],
                             flags=Gio.ApplicationFlags.FLAGS_NONE)

        def do_activate(self):
            window = self.get_active_window()
            if window is None:
                window = FactoryWindow(self, manifest)
            window.present()
            if smoke:
                GLib.timeout_add(700, self._smoke_close, window)

        @staticmethod
        def _smoke_close(window):
            app = window.get_application()
            window.destroy()
            app.quit()
            return False

    return FactoryApp().run([])
