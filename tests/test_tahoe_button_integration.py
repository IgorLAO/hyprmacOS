#!/usr/bin/env python3
"""Integration test for Tahoe button components in a simple GTK application."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gtk, Gdk, GLib

from tahoe.controls.button import (
    TahoeButton, TahoeToggleButton, TahoeMenuButton, TahoeCheckButton
)


def on_standard_clicked(button):
    print(f"Standard button clicked: {button.get_label()}")


def on_toggle_toggled(toggle):
    state = "on" if toggle.get_active() else "off"
    print(f"Toggle button {state}: {toggle.get_label()}")


def on_menu_clicked(menu_button):
    print(f"Menu button clicked: {menu_button.get_label() if menu_button.get_label() else 'icon-only'}")


def on_check_toggled(check):
    state = "checked" if check.get_active() else "unchecked"
    print(f"Check button {state}: {check.get_label()}")


def create_test_application():
    """Create a simple test application showing Tahoe buttons."""

    # Create main window
    window = Gtk.Window(title="Tahoe Button Test")
    window.set_default_size(400, 300)
    window.connect("destroy", Gtk.main_quit)

    # Create vertical box to hold buttons
    vbox = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=12)
    vbox.set_margin_start(12)
    vbox.set_margin_end(12)
    vbox.set_margin_top(12)
    vbox.set_margin_bottom(12)
    window.add(vbox)

    # Add standard buttons
    standard_btn = TahoeButton("Standard Button")
    standard_btn.connect("clicked", on_standard_clicked)
    vbox.pack_start(standard_btn, False, False, 0)

    # Add toggle button
    toggle_btn = TahoeToggleButton("Toggle Button")
    toggle_btn.connect("toggled", on_toggle_toggled)
    vbox.pack_start(toggle_btn, False, False, 0)

    # Add menu button
    menu_btn = TahoeMenuButton(icon_name="open-menu-symbolic", label="Menu")
    menu_btn.connect("clicked", on_menu_clicked)
    vbox.pack_start(menu_btn, False, False, 0)

    # Add check button
    check_btn = TahoeCheckButton("Enable Feature")
    check_btn.connect("toggled", on_check_toggled)
    vbox.pack_start(check_btn, False, False, 0)

    # Add styled buttons
    suggested_btn = TahoeButton("Suggested Action", style_class="suggested-action")
    suggested_btn.connect("clicked", lambda b: print("Suggested action clicked"))
    vbox.pack_start(suggested_btn, False, False, 0)

    destructive_btn = TahoeButton("Destructive Action", style_class="destructive-action")
    destructive_btn.connect("clicked", lambda b: print("Destructive action clicked"))
    vbox.pack_start(destructive_btn, False, False, 0)

    return window


def main():
    """Run the test application."""
    app = create_test_application()
    app.show_all()

    # Start GTK main loop
    Gtk.main()

    return 0


if __name__ == "__main__":
    sys.exit(main())