"""Preferências dos extras: isolamento, persistência e identidades SNI."""
import importlib.machinery
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[1]
loader = importlib.machinery.SourceFileLoader('menu_extras', str(ROOT / 'scripts/menu-extras'))
spec = importlib.util.spec_from_loader(loader.name, loader)
extras = importlib.util.module_from_spec(spec)
loader.exec_module(extras)


class ExtraPreferences(unittest.TestCase):
    def setUp(self):
        self.directory = tempfile.TemporaryDirectory()
        self.config = patch.object(extras, 'CONFIG', Path(self.directory.name) / 'menu-extras.json')
        self.config.start()
        self.addCleanup(self.config.stop)
        self.addCleanup(self.directory.cleanup)

    def command(self, *args):
        with patch('sys.argv', ['menu-extras', *args]), \
                patch.object(extras, 'CACHE', Path(self.directory.name)):
            extras.main()

    def test_hide_show_preserves_order_and_other_preferences(self):
        extras.save({'tray': {'order-items': ['vlc'], 'show-passive-items': False}, 'other': True})
        self.command('hide', 'title:Application with spaces')
        data = extras.load()
        self.assertEqual(data['tray']['hidden-items'], ['title:Application with spaces'])
        self.assertEqual(data['tray']['order-items'], ['vlc'])
        self.assertTrue(data['other'])
        self.command('show', 'title:Application with spaces')
        self.assertEqual(extras.load()['tray']['hidden-items'], [])

    def test_order_is_stable_and_duplicates_are_removed(self):
        self.command('order', 'nm-applet', 'vlc', 'nm-applet')
        self.assertEqual(extras.load()['tray']['order-items'], ['nm-applet', 'vlc'])
        self.command('order')
        self.assertEqual(extras.load()['tray']['order-items'], [])

    def test_invalid_config_is_not_overwritten(self):
        extras.CONFIG.write_text('{"tray": []}')
        with self.assertRaises(ValueError):
            self.command('hide', 'vlc')
        self.assertEqual(extras.CONFIG.read_text(), '{"tray": []}')



class WaybarSupervisor(unittest.TestCase):
    """A Waybar cai no mpris quando um player some (SIGSEGV/SIGABRT): o start a relança."""

    def run_codes(self, codes):
        from types import SimpleNamespace
        seq, slept, clock = list(codes), [], [0.0]

        def run(cmd):
            clock[0] += 5
            return SimpleNamespace(returncode=seq.pop(0))
        rc = extras.supervise(["waybar"], run=run, sleep=slept.append, clock=lambda: clock[0])
        return rc, len(codes) - len(seq), slept

    def test_crash_is_relaunched_until_requested_stop(self):
        rc, launches, slept = self.run_codes([-11, -6, -15])
        self.assertEqual((rc, launches, slept), (-15, 3, [1, 1]))

    def test_clean_exit_or_kill_stops(self):
        for code in (0, -9, -2, -1):
            self.assertEqual(self.run_codes([code])[:2], (code, 1))

    def test_crash_loop_gives_up(self):
        rc, launches, _ = self.run_codes([-11] * 10)
        self.assertEqual((rc, launches), (-11, 6))


if __name__ == '__main__':
    unittest.main()
