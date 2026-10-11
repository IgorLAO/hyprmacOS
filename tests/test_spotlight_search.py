"""Comportamentos de busca preservados após extrair a lógica do Spotlight."""

from pathlib import Path
import sys
import unittest


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "shell"))
from spotlight_search import spot_app_category, spot_calc, spot_fold, spot_score  # noqa: E402


class SpotlightSearchTests(unittest.TestCase):
    def test_accent_insensitive_exact_prefix_and_extra(self):
        self.assertEqual(spot_fold("Ações"), "acoes")
        self.assertEqual(spot_score("acoes", "Ações"), 100)
        self.assertGreater(spot_score("goo", "Google Chrome"),
                           spot_score("goo", "Chrome", "Google"))
        self.assertEqual(spot_score("term", "Ghostty", "Terminal"), 55)

    def test_categories_and_calculator(self):
        self.assertEqual(spot_app_category("Office;Email;"), "Productivity & Finance")
        self.assertIsNone(spot_app_category("Unknown;"))
        self.assertEqual(spot_calc("12*7+1"), "85")
        self.assertEqual(spot_calc("15% de 80"), "12")
        self.assertIsNone(spot_calc("2^101"))
        self.assertIsNone(spot_calc("__import__('os')"))


if __name__ == "__main__":
    unittest.main()
