"""Lógica Basic sem GTK, janelas ou display."""
import importlib.machinery
import importlib.util
from decimal import Decimal, localcontext
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
loader = importlib.machinery.SourceFileLoader(
    "hyprmac_calculadora", str(ROOT / "shell" / "hyprmac-calculadora"))
spec = importlib.util.spec_from_loader(loader.name, loader)
calculator = importlib.util.module_from_spec(spec)
loader.exec_module(calculator)


class CalculatorTests(unittest.TestCase):
    def setUp(self):
        self.calc = calculator.Calculator()

    def enter(self, *keys):
        for key in keys:
            self.calc.press(key)
        return self.calc.display

    def sequence(self, keys):
        return self.enter(*keys)

    def test_initial_state(self):
        self.assertEqual(self.calc.display, "0")
        self.assertEqual(self.calc.clear_label, "AC")
        self.assertIsNone(self.calc.active_operator)

    def test_four_operations(self):
        for keys, expected in [("12+3=", "15"), ("12-3=", "9"),
                               ("12*3=", "36"), ("12/3=", "4")]:
            with self.subTest(keys=keys):
                self.calc.reset()
                self.assertEqual(self.sequence(keys), expected)

    def test_decimal_arithmetic_is_exact(self):
        self.assertEqual(self.sequence("0.1+0.2="), "0.3")
        self.assertEqual(self.calc.value, Decimal("0.3"))
        self.assertEqual(self.sequence("-0.3="), "0")

    def test_display_rounding_does_not_round_accumulator(self):
        self.assertEqual(self.sequence("1/3="), "0.333333333")
        self.assertEqual(self.sequence("*3="), "1")
        self.assertGreater(self.calc.value, Decimal("0.999999999"))

    def test_context_is_local(self):
        with localcontext() as ctx:
            ctx.prec = 3
            self.assertEqual(self.sequence("12345+1="), "12346")
            self.assertEqual(ctx.prec, 3)

    def test_chained_operations(self):
        self.assertEqual(self.sequence("2+3*4="), "20")
        self.assertEqual(self.calc.expression, "5 × 4 =")
        self.assertEqual(self.sequence("/2-3="), "7")

    def test_operator_replacement(self):
        self.assertEqual(self.sequence("8+*/2="), "4")

    def test_operator_highlight(self):
        self.sequence("4+")
        self.assertEqual(self.calc.active_operator, "+")
        self.sequence("2")
        self.assertIsNone(self.calc.active_operator)
        self.sequence("=")
        self.assertIsNone(self.calc.active_operator)

    def test_repeated_equals(self):
        for keys, expected in [("2+3===", "11"), ("20-2===", "14"),
                               ("2*3===", "54"), ("64/2===", "8")]:
            with self.subTest(keys=keys):
                self.calc.reset()
                self.assertEqual(self.sequence(keys), expected)

    def test_equals_without_second_operand(self):
        self.assertEqual(self.sequence("5+=="), "15")

    def test_equals_without_operation(self):
        self.assertEqual(self.sequence("42==="), "42")

    def test_new_entry_resets_repeat_and_expression(self):
        self.sequence("2+3=")
        self.assertEqual(self.sequence("7="), "7")
        self.assertEqual(self.calc.expression, "")

    def test_percent_standalone(self):
        self.assertEqual(self.sequence("25%"), "0.25")

    def test_percent_with_operations(self):
        for keys, expected in [("200+10%=", "220"), ("200-10%=", "180"),
                               ("200*10%=", "20"), ("200/10%=", "2000"),
                               ("200+10%==", "240")]:
            with self.subTest(keys=keys):
                self.calc.reset()
                self.assertEqual(self.sequence(keys), expected)

    def test_change_sign(self):
        self.sequence("12.5")
        self.assertEqual(self.enter("+/−"), "-12.5")
        self.assertEqual(self.enter("+/−"), "12.5")
        self.sequence("+2=")
        self.assertEqual(self.enter("+/−"), "-14.5")

    def test_negative_operand(self):
        self.sequence("6*")
        self.enter("+/−")
        self.assertEqual(self.sequence("2="), "-12")

    def test_clear_entry_preserves_pending_operation(self):
        self.sequence("12+99")
        self.assertEqual(self.calc.clear_label, "C")
        self.assertEqual(self.enter("C"), "0")
        self.assertEqual(self.calc.clear_label, "AC")
        self.assertEqual(self.sequence("3="), "15")

    def test_clear_entry_then_equals(self):
        self.sequence("12+99")
        self.assertEqual(self.enter("C", "="), "12")

    def test_all_clear_resets_everything(self):
        self.sequence("8*9=")
        self.assertEqual(self.enter("AC", "="), "0")
        self.assertEqual(self.calc.clear_label, "AC")
        self.assertEqual(self.calc.expression, "")
        self.assertIsNone(self.calc.repeat)
        self.assertIsNone(self.calc.operator)

    def test_clear_result_resets_repeat(self):
        self.sequence("8*9=")
        self.assertEqual(self.enter("C", "="), "0")

    def test_division_by_zero_and_recovery(self):
        for keys in ("1/0=", "0/0=", "1/0+"):
            with self.subTest(keys=keys):
                self.calc.reset()
                self.assertEqual(self.sequence(keys), "Error")
                self.assertEqual(self.enter("=", "+", "%"), "Error")
                self.assertEqual(self.enter("7"), "7")
        self.sequence("/0=")
        self.assertEqual(self.enter("C"), "0")
        self.sequence("1/0=")
        self.assertEqual(self.enter("AC"), "0")

    def test_backspace_and_pending_operation(self):
        self.sequence("123.4")
        self.assertEqual(self.enter("Backspace"), "123.")
        self.assertEqual(self.enter("Backspace"), "123")
        self.enter(*(["Backspace"] * 3))
        self.assertEqual(self.calc.display, "0")
        self.sequence("8+")
        self.enter("Backspace")
        self.assertIsNone(self.calc.operator)
        self.assertEqual(self.calc.expression, "")
        self.assertEqual(self.enter("="), "8")

    def test_decimal_entry_and_scientific_display(self):
        self.assertEqual(self.sequence("..1200"), "0.1200")
        self.calc.reset()
        self.assertEqual(self.sequence("0001234567890"), "1.23456789e9")
        self.assertEqual(self.calc.value, Decimal("1234567890"))
        self.calc.reset()
        self.assertEqual(self.sequence("0,5"), "0.5")

    def test_operator_aliases(self):
        self.assertEqual(self.enter("8", "÷", "2", "×", "3", "−", "1", "="), "11")

    def test_unknown_keys_are_ignored(self):
        self.sequence("123")
        self.assertEqual(self.enter("x", "__import__", "", "🧮"), "123")


class FormatTests(unittest.TestCase):
    def test_format(self):
        cases = {"0": "0", "-0": "0", "12.500": "12.5",
                 "123456789": "123456789", "1234567890": "1.23456789e9",
                 "12300000000": "1.23e10", "999999999.5": "1e9",
                 "1.234567895": "1.2345679", "-1.234567895": "-1.2345679",
                 "0.00000001": "0.00000001", "0.000000001": "1e-9",
                 "Infinity": "Error", "NaN": "Error", "1e100": "1e100"}
        for value, expected in cases.items():
            with self.subTest(value=value):
                self.assertEqual(calculator.format_number(Decimal(value)), expected)


class KeyboardTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        try:
            cls.Gtk, _glib, cls.View, _app, _css = calculator.gtk_types()
            from gi.repository import Gdk
            cls.Gdk = Gdk
        except ImportError:
            raise unittest.SkipTest("PyGObject indisponível; lógica testada sem GTK")

    def setUp(self):
        self.view = SimpleNamespace(model=calculator.Calculator(), refresh=mock.Mock())

    def key(self, keyval, state=0):
        return self.View.on_key(self.view, None, SimpleNamespace(keyval=keyval, state=state))

    def test_physical_keys_and_escape(self):
        for char in "12+3":
            self.assertTrue(self.key(ord(char)))
        self.assertTrue(self.key(self.Gdk.KEY_Return))
        self.assertEqual(self.view.model.display, "15")
        self.assertTrue(self.key(self.Gdk.KEY_Escape))
        self.assertEqual(self.view.model.display, "0")
        self.assertEqual(self.view.model.clear_label, "AC")
        self.assertFalse(self.key(self.Gdk.KEY_F1))

    def test_numpad_and_backspace(self):
        for key in (self.Gdk.KEY_KP_1, self.Gdk.KEY_KP_Decimal, self.Gdk.KEY_KP_5):
            self.assertTrue(self.key(key))
        self.assertEqual(self.view.model.display, "1.5")
        self.assertTrue(self.key(self.Gdk.KEY_BackSpace))
        self.assertEqual(self.view.model.display, "1.")

    def test_copy_with_control_or_super(self):
        self.view.model.press("7")
        clipboard = mock.Mock()
        with mock.patch.object(self.Gtk.Clipboard, "get", return_value=clipboard):
            for mask in (self.Gdk.ModifierType.CONTROL_MASK, self.Gdk.ModifierType.SUPER_MASK):
                self.assertTrue(self.key(self.Gdk.KEY_c, mask))
                clipboard.set_text.assert_called_with("7", -1)
        self.assertEqual(self.view.model.display, "7")

    def test_css_is_valid_gtk3_ascii(self):
        self.assertTrue(calculator.CSS.isascii())
        errors = []
        provider = self.Gtk.CssProvider()
        provider.connect("parsing-error", lambda _p, _s, error: errors.append(str(error)))
        provider.load_from_data(calculator.CSS)
        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
