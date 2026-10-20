"""Integração do destaque entre gerador, Ajustes e Mission Control."""
import ast
from pathlib import Path
import os
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'shell'))
from accent_palette import CORES, GNOME_ACCENTS, accent_hex


class AccentIntegrationTests(unittest.TestCase):
    def test_generated_outputs_follow_shared_palette_in_both_appearances(self):
        binary = ROOT / 'core/accent/target/release/hyprmac-accent'
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for directory in ('gtk', 'waybar', 'wofi'):
                (root / directory).mkdir()
            fake = root / 'gsettings'
            fake.write_text("#!/bin/sh\nif [ \"$1\" = get ]; then echo \"$HYPRMAC_TEST_SCHEME\"; fi\n")
            fake.chmod(0o755)
            for command in ('kwriteconfig6', 'pkill'):
                path = root / command
                path.write_text('#!/bin/sh\nexit 0\n')
                path.chmod(0o755)
            for dark in (True, False):
                env = {**os.environ, 'HYPRMAC_ROOT': temp,
                       'HYPRMAC_TEST_SCHEME': 'prefer-dark' if dark else 'default',
                       'PATH': f"{temp}:{os.environ['PATH']}"}
                for name in CORES:
                    subprocess.run([binary, name], env=env, check=True)
                    expected = CORES[name][0 if dark else 1]
                    for path in ('gtk/accent3.css', 'gtk/accent4.css', 'waybar/accent.css', 'wofi/accent.css'):
                        self.assertIn(expected, (root / path).read_text())
                    before = (root / 'gtk/accent3.css').stat().st_mtime_ns
                    subprocess.run([binary, name], env=env, check=True)
                    self.assertEqual(before, (root / 'gtk/accent3.css').stat().st_mtime_ns)

    def test_overview_uses_theme_and_gnome_aliases(self):
        tree = ast.parse((ROOT / 'shell/hyprmac-overview').read_text())
        fn = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == 'overview_accent')
        namespace = {'accent_hex': accent_hex}
        exec(compile(ast.Module(body=[fn], type_ignores=[]), 'overview', 'exec'), namespace)
        iface = Mock()
        for dark in (True, False):
            for name in ('purple', 'slate', 'teal', 'unknown'):
                iface.get_string.side_effect = lambda key: ('prefer-dark' if dark else 'default') if key == 'color-scheme' else name
                result = namespace['overview_accent'](iface)
                self.assertEqual('#%02X%02X%02X' % tuple(round(c * 255) for c in result), accent_hex(name, dark))
        self.assertEqual(GNOME_ACCENTS['slate'], CORES['graphite'])


if __name__ == '__main__':
    unittest.main()
