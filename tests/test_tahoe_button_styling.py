#!/usr/bin/env python3
"""Test Tahoe button styling against GTK theme."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from tahoe.controls.button import (
    TahoeButton, TahoeToggleButton, TahoeMenuButton, TahoeCheckButton
)


def test_tahoe_button_inherits_gtk_styling():
    """Test that TahoeButton properly inherits GTK styling."""
    button = TahoeButton("Test")

    # Check that the button has the "button" style class applied
    style_context = button.get_style_context()
    classes = list(style_context.list_classes())

    assert "button" in classes, f"Expected 'button' class in {classes}"
    print("✓ TahoeButton correctly applies 'button' style class")


def test_tahoe_button_has_proper_properties():
    """Test that TahoeButton has proper focus and click properties."""
    button = TahoeButton("Test")

    # These should be True based on our implementation
    assert button.get_can_focus() == True, "Button should be able to receive focus"
    assert button.get_focus_on_click() == True, "Button should focus on click"
    print("✓ TahoeButton has proper focus properties")


def test_tahoe_button_can_be_styled():
    """Test that TahoeButton accepts additional style classes."""
    button = TahoeButton("Test", style_class="suggested-action")

    style_context = button.get_style_context()
    classes = list(style_context.list_classes())

    assert "button" in classes, "Should have base button class"
    assert "suggested-action" in classes, "Should have additional style class"
    print("✓ TahoeButton accepts additional style classes")


def test_tahoe_toggle_button_styling():
    """Test that TahoeToggleButton gets proper styling."""
    toggle = TahoeToggleButton("Test")

    style_context = toggle.get_style_context()
    classes = list(style_context.list_classes())

    assert "button" in classes, f"Expected 'button' class in {classes}"
    assert toggle.get_can_focus() == True, "Toggle should be able to receive focus"
    assert toggle.get_focus_on_click() == True, "Toggle should focus on click"
    print("✓ TahoeToggleButton styling correct")


def test_tahoe_menu_button_styling():
    """Test that TahoeMenuButton gets proper styling."""
    menu_btn = TahoeMenuButton(icon_name="open-menu-symbolic")

    style_context = menu_btn.get_style_context()
    classes = list(style_context.list_classes())

    assert "button" in classes, f"Expected 'button' class in {classes}"
    assert menu_btn.get_can_focus() == True, "Menu button should be able to receive focus"
    assert menu_btn.get_focus_on_click() == True, "Menu button should focus on click"
    print("✓ TahoeMenuButton styling correct")


def test_tahoe_check_button_styling():
    """Test that TahoeCheckButton gets proper styling."""
    check = TahoeCheckButton("Test")

    style_context = check.get_style_context()
    classes = list(style_context.list_classes())

    assert "check" in classes, f"Expected 'check' class in {classes}"
    assert check.get_can_focus() == True, "Check button should be able to receive focus"
    assert check.get_focus_on_click() == True, "Check button should focus on click"
    print("✓ TahoeCheckButton styling correct")


if __name__ == "__main__":
    print("Testing Tahoe button styling...")
    test_tahoe_button_inherits_gtk_styling()
    test_tahoe_button_has_proper_properties()
    test_tahoe_button_can_be_styled()
    test_tahoe_toggle_button_styling()
    test_tahoe_menu_button_styling()
    test_tahoe_check_button_styling()
    print("\n✅ All Tahoe button styling tests passed!")