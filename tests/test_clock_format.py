"""Clock Options do relógio da barra (Tahoe 26). Casos-base escritos às cegas
pelo auxiliar TST-01 a partir do contrato; os do fim são do orquestrador."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "shell"))

import unittest
from datetime import datetime
from clock_format import clock_text, needs_seconds_tick, DEFAULTS

class TestClockFormat(unittest.TestCase):
    # Fixed datetimes for deterministic testing
    DT_SUN = datetime(2026, 10, 11, 17, 5, 9)   # Sunday 17:05:09
    DT_MIDNIGHT = datetime(2026, 10, 11, 0, 0, 0)  # 00:00:00
    DT_NOON = datetime(2026, 10, 11, 12, 0, 0)   # 12:00:00
    DT_SINGLE_HOUR_24 = datetime(2026, 10, 11, 9, 5, 0)  # 09:05:00 -> should be "9:05"
    DT_FLASH_EVEN = datetime(2026, 10, 11, 17, 5, 8)   # second 8 (even)
    DT_FLASH_ODD = datetime(2026, 10, 11, 17, 5, 9)    # second 9 (odd)

    def setUp(self):
        self.base_prefs = dict(DEFAULTS)  # copy defaults for each test

    # ----- DEFAULTS -------------------------------------------------
    def test_defaults(self):
        expected = {
            "show_date": "when_space_allows",
            "show_day_of_week": True,
            "show_ampm": True,
            "show_seconds": False,
            "flash_separators": False,
        }
        self.assertEqual(DEFAULTS, expected)

    # ----- needs_seconds_tick ---------------------------------------
    def test_needs_seconds_tick(self):
        # Neither flag set -> False
        self.assertFalse(needs_seconds_tick({}))
        # Only show_seconds True -> True
        prefs = dict(self.base_prefs, show_seconds=True)
        self.assertTrue(needs_seconds_tick(prefs))
        # Only flash_separators True -> True
        prefs = dict(self.base_prefs, flash_separators=True)
        self.assertTrue(needs_seconds_tick(prefs))
        # Both True -> True
        prefs = dict(self.base_prefs, show_seconds=True, flash_separators=True)
        self.assertTrue(needs_seconds_tick(prefs))

    # ----- clock_text: basic examples -------------------------------
    def test_example_default_h24_true(self):
        self.assertEqual(
            clock_text(self.DT_SUN, self.base_prefs, h24=True, space_allows=False),
            "Sun 17:05"
        )

    def test_example_show_date_always_h24_true(self):
        prefs = dict(self.base_prefs, show_date="always")
        self.assertEqual(
            clock_text(self.DT_SUN, prefs, h24=True, space_allows=False),
            "Sun Oct 11 17:05"
        )

    def test_example_show_date_always_no_dow_h24_false(self):
        prefs = dict(self.base_prefs, show_date="always", show_day_of_week=False, show_ampm=True)
        self.assertEqual(
            clock_text(self.DT_SUN, prefs, h24=False, space_allows=False),
            "Oct 11 5:05 PM"
        )

    def test_example_h24_false_no_ampm_with_seconds(self):
        prefs = dict(self.base_prefs, show_ampm=False, show_seconds=True)
        self.assertEqual(
            clock_text(self.DT_SUN, prefs, h24=False, space_allows=False),
            "Sun 5:05:09"
        )

    def test_example_flash_odd_seconds(self):
        prefs = dict(self.base_prefs, flash_separators=True, show_seconds=True)
        # second 9 -> odd -> colons become spaces
        self.assertEqual(
            clock_text(self.DT_SUN, prefs, h24=True, space_allows=False),
            "Sun 17 05 09"
        )

    # ----- midnight and noon in 12h ---------------------------------
    def test_midnight_12h(self):
        prefs = dict(self.base_prefs, show_ampm=True)
        self.assertEqual(
            clock_text(self.DT_MIDNIGHT, prefs, h24=False, space_allows=False),
            "Sun 12:00 AM"
        )
        # without AM/PM
        prefs_noampm = dict(self.base_prefs, show_ampm=False)
        self.assertEqual(
            clock_text(self.DT_MIDNIGHT, prefs_noampm, h24=False, space_allows=False),
            "Sun 12:00"
        )

    def test_noon_12h(self):
        prefs = dict(self.base_prefs, show_ampm=True)
        self.assertEqual(
            clock_text(self.DT_NOON, prefs, h24=False, space_allows=False),
            "Sun 12:00 PM"
        )
        prefs_noampm = dict(self.base_prefs, show_ampm=False)
        self.assertEqual(
            clock_text(self.DT_NOON, prefs_noampm, h24=False, space_allows=False),
            "Sun 12:00"
        )

    # ----- single-digit hour in 24h ---------------------------------
    def test_single_digit_hour_24h(self):
        # hour 9 should appear as "9:05" (no leading zero)
        self.assertEqual(
            clock_text(self.DT_SINGLE_HOUR_24, self.base_prefs, h24=True, space_allows=False),
            "Sun 9:05"
        )
        # with seconds
        prefs_sec = dict(self.base_prefs, show_seconds=True)
        self.assertEqual(
            clock_text(self.DT_SINGLE_HOUR_24, prefs_sec, h24=True, space_allows=False),
            "Sun 9:05:00"
        )

    # ----- show_date values -----------------------------------------
    def test_show_date_always(self):
        prefs = dict(self.base_prefs, show_date="always")
        self.assertIn("Oct 11", clock_text(self.DT_SUN, prefs, h24=True, space_allows=False))

    def test_show_date_never(self):
        prefs = dict(self.base_prefs, show_date="never")
        self.assertNotIn("Oct 11", clock_text(self.DT_SUN, prefs, h24=True, space_allows=True))

    def test_show_date_when_space_allows_false(self):
        prefs = dict(self.base_prefs, show_date="when_space_allows")
        self.assertNotIn("Oct 11", clock_text(self.DT_SUN, prefs, h24=True, space_allows=False))

    def test_show_date_when_space_allows_true(self):
        prefs = dict(self.base_prefs, show_date="when_space_allows")
        self.assertIn("Oct 11", clock_text(self.DT_SUN, prefs, h24=True, space_allows=True))

    def test_show_date_invalid_defaults_to_when_space_allows(self):
        prefs = dict(self.base_prefs, show_date="invalid_value")
        # behaves like "when_space_allows"
        self.assertNotIn("Oct 11", clock_text(self.DT_SUN, prefs, h24=True, space_allows=False))
        self.assertIn("Oct 11", clock_text(self.DT_SUN, prefs, h24=True, space_allows=True))

    def test_show_date_missing_key_uses_default(self):
        prefs = {}  # missing show_date key
        self.assertNotIn("Oct 11", clock_text(self.DT_SUN, prefs, h24=True, space_allows=False))
        self.assertIn("Oct 11", clock_text(self.DT_SUN, prefs, h24=True, space_allows=True))

    # ----- show_day_of_week -----------------------------------------
    def test_show_day_of_week_false_with_date(self):
        prefs = dict(self.base_prefs, show_day_of_week=False, show_date="always")
        txt = clock_text(self.DT_SUN, prefs, h24=True, space_allows=False)
        self.assertNotIn("Sun", txt)
        self.assertIn("Oct 11", txt)

    def test_show_day_of_week_false_without_date(self):
        prefs = dict(self.base_prefs, show_day_of_week=False, show_date="never")
        txt = clock_text(self.DT_SUN, prefs, h24=True, space_allows=False)
        self.assertNotIn("Sun", txt)
        self.assertNotIn("Oct 11", txt)
        # only time remains
        self.assertEqual(txt.strip(), "17:05")

    # ----- flash separators length equality -------------------------
    def test_flash_separators_length_even_vs_odd(self):
        prefs = dict(self.base_prefs, flash_separators=True, show_seconds=True)
        txt_even = clock_text(self.DT_FLASH_EVEN, prefs, h24=True, space_allows=False)
        txt_odd = clock_text(self.DT_FLASH_ODD, prefs, h24=True, space_allows=False)
        self.assertEqual(len(txt_even), len(txt_odd))
        # even second -> colons unchanged
        self.assertIn(":", txt_even)
        # odd second -> colons replaced by spaces
        self.assertNotIn(":", txt_odd)
        self.assertIn(" ", txt_odd)

    def test_flash_separators_without_seconds(self):
        prefs = dict(self.base_prefs, flash_separators=True, show_seconds=False)
        # time part is H:mm (one colon)
        txt_even = clock_text(self.DT_FLASH_EVEN, prefs, h24=True, space_allows=False)
        txt_odd = clock_text(self.DT_FLASH_ODD, prefs, h24=True, space_allows=False)
        self.assertEqual(len(txt_even), len(txt_odd))
        self.assertIn(":", txt_even)
        self.assertNotIn(":", txt_odd)
        self.assertIn(" ", txt_odd)

    # ----- show_ampm only affects 12h -------------------------------
    def test_show_ampm_no_effect_in_24h(self):
        prefs = dict(self.base_prefs, show_ampm=False)
        txt_24 = clock_text(self.DT_SUN, prefs, h24=True, space_allows=False)
        self.assertNotIn("AM", txt_24)
        self.assertNotIn("PM", txt_24)
        self.assertIn("17:05", txt_24)

    def test_show_ampm_effect_in_12h(self):
        prefs_on = dict(self.base_prefs, show_ampm=True)
        prefs_off = dict(self.base_prefs, show_ampm=False)
        txt_on = clock_text(self.DT_SUN, prefs_on, h24=False, space_allows=False)
        txt_off = clock_text(self.DT_SUN, prefs_off, h24=False, space_allows=False)
        self.assertIn("PM", txt_on)
        self.assertNotIn("PM", txt_off)
        self.assertIn("5:05", txt_on)
        self.assertIn("5:05", txt_off)

    # ----- orquestrador: locale, markup e preferências -------------
    def test_english_names_regardless_of_locale(self):
        import locale
        old = locale.setlocale(locale.LC_TIME)
        alt = next((n for n in ("pt_BR.UTF-8", "de_DE.UTF-8", "fr_FR.UTF-8")
                    if self._try_locale(locale, n)), None)
        try:
            txt = clock_text(self.DT_SUN, {"show_date": "always"}, h24=True)
        finally:
            locale.setlocale(locale.LC_TIME, old)
        self.assertEqual(txt, "Sun Oct 11 17:05", alt)

    @staticmethod
    def _try_locale(locale, name):
        try:
            locale.setlocale(locale.LC_TIME, name)
            return True
        except locale.Error:
            return False

    def test_markup_flash_keeps_colon_width(self):
        from clock_format import HIDDEN_SEP
        prefs = {"flash_separators": True, "show_seconds": True}
        odd = clock_text(self.DT_FLASH_ODD, prefs, h24=True, markup=True)
        self.assertEqual(odd, f"Sun 17{HIDDEN_SEP}05{HIDDEN_SEP}09")
        self.assertEqual(clock_text(self.DT_FLASH_EVEN, prefs, h24=True, markup=True), "Sun 17:05:08")

    def test_unknown_keys_and_none_are_ignored(self):
        from clock_format import prefs_of
        self.assertEqual(prefs_of(None), DEFAULTS)
        self.assertEqual(prefs_of({"x": 1, "show_date": 3}), DEFAULTS)


if __name__ == "__main__":
    unittest.main()
