"""Tahoe-compatible button component for HyprMac Compatibility Layer.

Provides macOS Tahoe 26.6.1 button behavior and appearance that can be
reused across applications:
- Standard push buttons with appropriate sizing and styling
- Toggle buttons for selection states
- Menu buttons for app menus
- Consistent visual feedback (hover, pressed, disabled states)
- Proper keyboard navigation and activation

Based on investigation of original macOS behavior and defines contracts
for equivalent Linux implementation.
"""

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, Gdk


class TahoeButton(Gtk.Button):
    """Standard macOS Tahoe button.

    Provides the visual appearance and behavior of NSButton from AppKit.
    Automatically applies Tahoe styling from gtk3.css.
    """

    def __init__(self, label="", style_class=None, **kwargs):
        super().__init__(label=label, **kwargs)

        # Apply Tahoe button styling - always add base button class
        self.get_style_context().add_class("button")
        # Add additional style class if provided
        if style_class:
            self.get_style_context().add_class(style_class)

        # Set proper focus handling
        self.set_can_focus(True)
        self.set_focus_on_click(True)


class TahoeToggleButton(Gtk.ToggleButton):
    """Tahoe toggle button for selection states.

    Used for sidebar navigation, preferences, etc.
    """

    def __init__(self, label="", **kwargs):
        super().__init__(label=label, **kwargs)
        self.get_style_context().add_class("button")
        self.set_can_focus(True)
        self.set_focus_on_click(True)


class TahoeMenuButton(Gtk.MenuButton):
    """Tahoe menu button for app menus and contextual menus.

    Matches the appearance of NSButton with menu indicator.
    """

    def __init__(self, icon_name=None, label=None, **kwargs):
        super().__init__(**kwargs)

        if icon_name:
            self.set_image(Gtk.Image.new_from_icon_name(icon_name, Gtk.IconSize.BUTTON))
        elif label:
            self.set_label(label)

        self.get_style_context().add_class("button")
        self.set_can_focus(True)
        self.set_focus_on_click(True)


class TahoeCheckButton(Gtk.CheckButton):
    """Tahoe check button for binary options.

    Used for checkboxes in preferences and settings.
    """

    def __init__(self, label="", **kwargs):
        super().__init__(label=label, **kwargs)
        self.get_style_context().add_class("check")
        self.set_can_focus(True)
        self.set_focus_on_click(True)


def create_tahoe_button(label="", style_class=None, **kwargs):
    """Factory function to create a Tahoe button.

    Args:
        label: Button label text
        style_class: Additional CSS class(es) to apply
        **kwargs: Additional Gtk.Button properties

    Returns:
        Configured TahoeButton instance
    """
    return TahoeButton(label=label, style_class=style_class, **kwargs)


def create_tahoe_toggle_button(label="", **kwargs):
    """Factory function to create a Tahoe toggle button."""
    return TahoeToggleButton(label=label, **kwargs)


def create_tahoe_menu_button(icon_name=None, label=None, **kwargs):
    """Factory function to create a Tahoe menu button."""
    return TahoeMenuButton(icon_name=icon_name, label=label, **kwargs)


def create_tahoe_check_button(label="", **kwargs):
    """Factory function to create a Tahoe check button."""
    return TahoeCheckButton(label=label, **kwargs)