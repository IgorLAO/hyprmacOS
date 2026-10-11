"""Tests for shell/hyprmac-preview theme-related code without importing gi/GTK.

Checks:
- CSS block contains '.light .preview-sidebar' and '.light .preview-area'
- build() binds the window to color-scheme (app_theme adds/removes 'light')
- ScrolledWindow gets 'preview-area' class via add_class
"""
import re
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "shell" / "hyprmac-preview"


class TestPreviewTheme(unittest.TestCase):
    def setUp(self):
        self.content = SCRIPT_PATH.read_text(encoding="utf-8")

    def test_css_contains_light_rules(self):
        # Extract the CSS block (triple-quoted bytes string)
        # Pattern: CSS = b"""(.*?)""" with re.DOTALL to capture across lines
        css_match = re.search(r'CSS = b"""(.*?)"""', self.content, re.DOTALL)
        self.assertIsNotNone(css_match, "CSS block not found")
        css_block = css_match.group(1)
        # Check for the two rules
        self.assertRegex(css_block, r'\.light \.preview-sidebar',
                         "Missing '.light .preview-sidebar' rule in CSS")
        self.assertRegex(css_block, r'\.light \.preview-area',
                         "Missing '.light .preview-area' rule in CSS")

    def test_build_binds_window_to_color_scheme(self):
        # .light é aplicado e retirado por app_theme.bind_color_scheme (testado em
        # test_app_theme), inclusive quando o tema muda com a janela aberta
        build = self.content[self.content.find("def build(self):"):]
        build = build[:build.find("\n    def ", 1)]
        self.assertIn("bind_color_scheme(self.window)", build)
        self.assertIn("from app_theme import bind_color_scheme", self.content)

    def test_scroll_gets_preview_area_class(self):
        # Look for the line where self.scroll gets the preview-area class
        pattern = r'self\.scroll\.get_style_context\(\)\.add_class\("preview-area"\)'
        self.assertRegex(self.content, pattern,
                         'add_class("preview-area") not found on self.scroll')


if __name__ == "__main__":
    unittest.main()