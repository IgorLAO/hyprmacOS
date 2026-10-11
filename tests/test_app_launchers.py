"""Identidade e entrada executável dos apps GTK próprios instalados."""

from pathlib import Path
import unittest

import gi

gi.require_version("GdkPixbuf", "2.0")
from gi.repository import GdkPixbuf, Gio


ROOT = Path(__file__).resolve().parents[1]
APPS = ("Calculator", "Notes", "Photos", "Preview", "Journal", "Settings")


class AppLaunchersTests(unittest.TestCase):
    def test_exec_and_tahoe_icon_are_resolvable(self):
        for name in APPS:
            with self.subTest(app=name):
                desktop = ROOT / "shell" / f"dev.hyprmac.{name}.desktop"
                info = Gio.DesktopAppInfo.new_from_filename(str(desktop))
                self.assertIsNotNone(info)
                executable = Path(info.get_executable())
                self.assertTrue(executable.is_file(), executable)
                self.assertTrue(executable.stat().st_mode & 0o111, executable)
                icon = Path(info.get_icon().to_string())
                self.assertTrue(icon.is_file(), icon)
                pixbuf = GdkPixbuf.Pixbuf.new_from_file(str(icon))
                self.assertEqual((pixbuf.get_width(), pixbuf.get_height()), (256, 256))


if __name__ == "__main__":
    unittest.main()
