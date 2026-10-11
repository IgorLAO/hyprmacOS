"""Tests for shell/hyprmac-preview theme-related code without importing gi/GTK.

Checks:
- CSS block contains '.light .preview-sidebar' and '.light .preview-area'
- build() adds 'light' class when color-scheme is not 'prefer-dark'
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

    def test_build_adds_light_when_not_dark(self):
        # Find the line with 'escuro = ... == \"prefer-dark\"'
        prefer_dark_pattern = r'escuro = Gio\.Settings\.new\("org\.gnome\.desktop\.interface"\)\.get_string\("color-scheme"\) == "prefer-dark"'
        self.assertRegex(self.content, prefer_dark_pattern,
                         "prefer-dark condition not found in build()")
        # Find the build method (simplistic: look for 'def build(self):')
        build_def_idx = self.content.find('def build(self):')
        self.assertNotEqual(build_def_idx, -1, "build method not found")
        # From that point, find the line with 'if not escuro:'
        after_build = self.content[build_def_idx:]
        if_not_escuro_match = re.search(r'^\s*if not escuro:$', after_build, re.MULTILINE)
        self.assertIsNotNone(if_not_escuro_match, "if not escuro: block not found in build()")
        # Get the line number of that if statement within the whole content
        # We'll compute the index of the match
        if_not_escuro_idx = after_build.index(if_not_escuro_match.group(0)) + build_def_idx
        # Look ahead a few lines for add_class("light")
        window_after_if = self.content[if_not_escuro_idx:if_not_escuro_idx + 200]  # reasonable window
        self.assertIn('add_class("light")', window_after_if,
                      'add_class("light") not found after "if not escuro:"')

    def test_scroll_gets_preview_area_class(self):
        # Look for the line where self.scroll gets the preview-area class
        pattern = r'self\.scroll\.get_style_context\(\)\.add_class\("preview-area"\)'
        self.assertRegex(self.content, pattern,
                         'add_class("preview-area") not found on self.scroll')


if __name__ == "__main__":
    unittest.main()