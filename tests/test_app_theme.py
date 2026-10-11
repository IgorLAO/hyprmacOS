"""Tema compartilhado deve acompanhar GSettings sem alterar CSS de cada app."""

import sys
from pathlib import Path
import unittest

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "shell"))
from app_theme import bind_color_scheme


class FakeSettings:
    def __init__(self):
        self.value = "prefer-dark"
        self.callback = None
        self.disconnected = False

    def get_string(self, _key):
        return self.value

    def connect(self, signal, callback):
        assert signal == "changed::color-scheme"
        self.callback = callback
        return 7

    def disconnect(self, handler):
        assert handler == 7
        self.disconnected = True

    def change(self, value):
        self.value = value
        self.callback(self)


class AppThemeTests(unittest.TestCase):
    def test_classes_follow_theme_and_disconnect_on_destroy(self):
        Gtk.init([])
        widget = Gtk.Box()
        settings = FakeSettings()
        self.assertIs(bind_color_scheme(widget, settings), settings)
        style = widget.get_style_context()
        self.assertTrue(style.has_class("dark"))
        settings.change("prefer-light")
        self.assertTrue(style.has_class("light"))
        self.assertFalse(style.has_class("dark"))
        settings.change("prefer-dark")
        self.assertTrue(style.has_class("dark"))
        self.assertFalse(style.has_class("light"))
        widget.destroy()
        self.assertTrue(settings.disconnected)


if __name__ == "__main__":
    unittest.main()
