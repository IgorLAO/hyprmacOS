#!/usr/bin/env python3
"""Test Tahoe compatibility layer button components."""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk

from tahoe.compatibility.button import (
    TahoeButton, TahoeToggleButton, TahoeMenuButton,
    TahoeCheckButton, create_tahoe_button, create_tahoe_toggle_button,
    create_tahoe_menu_button, create_tahoe_check_button
)


def test_tahoe_button_creation():
    """Test that Tahoe button components can be created."""
    # Test standard button
    button = TahoeButton("Test Button")
    assert button.get_label() == "Test Button"
    print("✓ TahoeButton creation successful")

    # Test toggle button
    toggle = TahoeToggleButton("Test Toggle")
    assert toggle.get_label() == "Test Toggle"
    print("✓ TahoeToggleButton creation successful")

    # Test menu button
    menu_button = TahoeMenuButton(icon_name="open-menu-symbolic")
    print("✓ TahoeMenuButton creation successful")

    # Test check button
    check = TahoeCheckButton("Test Check")
    assert check.get_label() == "Test Check"
    print("✓ TahoeCheckButton creation successful")


def test_tahoe_button_factories():
    """Test that factory functions work correctly."""
    # Test factory functions
    button = create_tahoe_button("Factory Button")
    assert button.get_label() == "Factory Button"
    print("✓ create_tahoe_button factory successful")

    toggle = create_tahoe_toggle_button("Factory Toggle")
    assert toggle.get_label() == "Factory Toggle"
    print("✓ create_tahoe_toggle_button factory successful")

    menu_button = create_tahoe_menu_button(icon_name="system-run-symbolic")
    print("✓ create_tahoe_menu_button factory successful")

    check = create_tahoe_check_button("Factory Check")
    assert check.get_label() == "Factory Check"
    print("✓ create_tahoe_check_button factory successful")


def test_tahoe_button_styling():
    """Test that Tahoe buttons get proper styling."""
    button = TahoeButton("Styled Button")
    context = button.get_style_context()
    classes = list(context.list_classes())
    assert "button" in classes
    print("✓ TahoeButton styling applied")

    check = TahoeCheckButton("Styled Check")
    context = check.get_style_context()
    classes = list(context.list_classes())
    assert "check" in classes
    print("✓ TahoeCheckButton styling applied")


def test_button_in_app_factories():
    """Test that app factories can use the compatibility layer."""
    # Test that we can replace direct Gtk usage with compatibility layer
    from tahoe.compatibility.button import TahoeButton as CompatTahoeButton
    from tahoe.compatibility.button import TahoeToggleButton as CompatTahoeToggle
    from tahoe.compatibility.button import TahoeMenuButton as CompatTahoeMenu

    # These should work identically to the direct Gtk versions
    compat_button = CompatTahoeButton("Compat Button")
    assert compat_button.get_label() == "Compat Button"

    compat_toggle = CompatTahoeToggle("Compat Toggle")
    assert compat_toggle.get_label() == "Compat Toggle"

    compat_menu = CompatTahoeMenu(icon_name="open-menu-symbolic")
    # Menu button test passes if no exception

    print("✓ App factories can use compatibility layer")


if __name__ == "__main__":
    print("Testing Tahoe compatibility layer button components...")
    test_tahoe_button_creation()
    test_tahoe_button_factories()
    test_tahoe_button_styling()
    test_button_in_app_factories()
    print("\n✅ All Tahoe compatibility layer button tests passed!")