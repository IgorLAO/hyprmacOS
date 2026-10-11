"""Casos dimensionais conferidos com emulação ARM64 independente (25G76)."""
import importlib.util
from pathlib import Path
import unittest

PATH = Path(__file__).resolve().parents[1] / 'BaseConhecimento/ferramentas/receita_dock.py'
spec = importlib.util.spec_from_file_location('dock_recipe', PATH)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
recipe = module.dock_refraction


class DockRecipeTests(unittest.TestCase):
    def test_absent_dimensions_use_fallback(self):
        r = recipe(dimensions_absent=True, pixel_length=.5)
        for name, value in {'innerHeight': 6.096, 'innerAmount': -20.16,
                            'outerHeight': 6.24, 'outerAmount': 20.16}.items():
            self.assertAlmostEqual(r[name], value)
        self.assertEqual(r['outerDistances'], [-1, -.5])
        self.assertEqual(r['outerOpacity'], .20000000298023224)

    def test_different_dimensions_and_independent_clamps(self):
        r = recipe(80, 200, pixel_length=1)
        self.assertEqual(r['innerHeight'], 10.16)
        self.assertEqual(r['innerAmount'], -33.6)
        self.assertEqual(r['outerHeight'], 26)
        self.assertEqual(r['outerAmount'], 84)
        r = recipe(500, 300)
        self.assertEqual((r['innerHeight'], r['innerAmount']), (20, -60))
        self.assertEqual((r['outerHeight'], r['outerAmount']), (39, 126))

    def test_optional_largest_uses_own_value_even_without_minimum(self):
        r = recipe(None, 120)
        self.assertAlmostEqual(r['innerHeight'], 6.096)
        self.assertAlmostEqual(r['outerHeight'], 15.6)
        r = recipe(0, None)
        self.assertEqual((r['innerHeight'], r['innerAmount'], r['outerHeight']), (0, 0, 0))

    def test_invalid_input_is_rejected(self):
        for kwargs in [{'minimum': float('nan')}, {'largest': float('inf')},
                       {'minimum': -1}, {'pixel_length': 0},
                       {'minimum': 64, 'dimensions_absent': True}]:
            with self.assertRaises(ValueError):
                recipe(**kwargs)

    def test_conditional_inner_height_only(self):
        base = recipe(80, 200, w27_bit5=False, w24_bit9=False)
        for bit5, bit9, expected in ((True, False, 0), (True, True, 10.16),
                                     (False, False, 10.16)):
            actual = recipe(80, 200, w27_bit5=bit5, w24_bit9=bit9)
            self.assertAlmostEqual(actual['innerHeight'], expected)
            self.assertEqual({k: v for k, v in actual.items() if k != 'innerHeight'},
                             {k: v for k, v in base.items() if k != 'innerHeight'})
        with self.assertRaises(ValueError):
            recipe(80, 200, w27_bit5=True)

if __name__ == '__main__':
    unittest.main()
