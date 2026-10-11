"""O instalador não substitui configurações por fontes ausentes."""

from pathlib import Path
import shlex
import subprocess
import tempfile
import unittest


INSTALL = (Path(__file__).resolve().parents[1] / "install.sh").read_text()


def section(start, end):
    return INSTALL[INSTALL.index(start):INSTALL.index(end, INSTALL.index(start)) + len(end)]


FUNCTIONS = section("backup() {", "\n}\n") + section("link() {", "\n}\n")
GTK_BLOCK = section("for v in 3 4; do\n  css=", "\ndone\n")


class InstallPreflightTests(unittest.TestCase):
    def test_missing_link_source_preserves_user_file_and_existing_link_is_idempotent(self):
        with tempfile.TemporaryDirectory() as temp:
            home = Path(temp)
            source = home / "project/kitty/kitty.conf"
            target = home / "config/kitty/kitty.conf"
            target.parent.mkdir(parents=True)
            target.write_text("user config")
            variables = f'H={shlex.quote(str(home / "project"))}\nC={shlex.quote(str(home / "config"))}\n'
            command = variables + FUNCTIONS + '\nlink "$H/kitty/kitty.conf" "$C/kitty/kitty.conf" kitty/kitty.conf\n'
            subprocess.run(["bash", "-c", command], check=True, capture_output=True)
            self.assertEqual(target.read_text(), "user config")
            source.parent.mkdir(parents=True)
            source.write_text("hyprmac config")
            subprocess.run(["bash", "-c", command], check=True, capture_output=True)
            self.assertTrue(target.is_symlink())
            backup = home / "project/backup/kitty/kitty.conf"
            self.assertEqual(backup.read_text(), "user config")
            subprocess.run(["bash", "-c", command], check=True, capture_output=True)
            self.assertEqual(backup.read_text(), "user config")

    def test_missing_gtk3_stylesheet_does_not_replace_user_css(self):
        with tempfile.TemporaryDirectory() as temp:
            home = Path(temp)
            css = home / "config/gtk-3.0/gtk.css"
            css.parent.mkdir(parents=True)
            css.write_text("user css")
            (home / "project/gtk").mkdir(parents=True)
            (home / "project/gtk/gtk4.css").write_text("gtk4 css")
            command = (f'H={shlex.quote(str(home / "project"))}\n'
                       f'C={shlex.quote(str(home / "config"))}\n' + FUNCTIONS + GTK_BLOCK)
            subprocess.run(["bash", "-c", command], check=True, capture_output=True)
            self.assertEqual(css.read_text(), "user css")
            self.assertEqual((home / "project/backup/gtk-3.0/gtk.css").read_text(), "user css")
            self.assertIn("gtk4.css", (home / "config/gtk-4.0/gtk.css").read_text())


if __name__ == "__main__":
    unittest.main()
