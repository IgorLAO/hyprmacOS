"""Tests for GALLERY_CATS and GALLERY_KEY_CAT extracted via AST."""

import ast
import os
import unittest


def _shell_path():
    here = os.path.abspath(os.path.dirname(__file__))
    root = os.path.abspath(os.path.join(here, os.pardir))
    return os.path.join(root, "shell", "hyprmac-shell")


def _load_assignments(path):
    with open(path, "r", encoding="utf-8") as f:
        source = f.read()
    tree = ast.parse(source, filename=path)
    assignments = {}
    for node in tree.body:
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id in ("GALLERY_CATS", "GALLERY_KEY_CAT"):
                    try:
                        value = ast.literal_eval(node.value)
                    except Exception:
                        value = None
                    assignments[target.id] = value
    return assignments


class TestCcGallery(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        path = _shell_path()
        cls.assignments = _load_assignments(path)
        cls.cats = cls.assignments.get("GALLERY_CATS")
        cls.key_cat = cls.assignments.get("GALLERY_KEY_CAT")

    def test_gallery_cats_exists(self):
        self.assertIsNotNone(self.cats, "GALLERY_CATS not found")
        self.assertIsInstance(self.cats, list)

    def test_first_item(self):
        self.assertTrue(len(self.cats) >= 1)
        first = self.cats[0]
        self.assertIsInstance(first, tuple)
        self.assertEqual(first[0], "all")
        self.assertEqual(first[1], "All Controls")

    def test_names_alphabetical(self):
        names = [item[1] for item in self.cats[1:]]
        self.assertEqual(names, sorted(names), "Category names are not alphabetical")

    def test_key_cat_categories_exist(self):
        self.assertIsNotNone(self.key_cat, "GALLERY_KEY_CAT not found")
        self.assertIsInstance(self.key_cat, dict)
        cat_keys = {item[0] for item in self.cats}
        for key, cat in self.key_cat.items():
            self.assertIn(cat, cat_keys, f"Category '{cat}' for key '{key}' not in GALLERY_CATS")

    def test_names_in_allowed_set(self):
        allowed = {
            "All Controls",
            "Accessibility",
            "Battery",
            "Clock",
            "Connectivity",
            "Desktop & Finder",
            "Display & Brightness",
            "Fast User Switching",
            "Focus",
            "Keyboards",
            "Lock Screen",
            "Now Playing",
            "Screenshot",
            "Sounds",
            "Utilities",
            "Suggestions",
            "Weather",
            "What’s New",
            "Time Machine",
        }
        names = [item[1] for item in self.cats]
        for name in names:
            self.assertIn(name, allowed, f"Name '{name}' not in allowed set")


if __name__ == "__main__":
    unittest.main()
