"""Integração do destaque entre gerador, Ajustes e Mission Control."""
import ast
import importlib.machinery
import importlib.util
from pathlib import Path
import sys
import tempfile
import unittest
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'shell'))
from accent_palette import CORES, GNOME_ACCENTS, accent_hex


def generator():
    loader = importlib.machinery.SourceFileLoader('accent_generator', str(ROOT / 'scripts/accent'))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


class AccentIntegrationTests(unittest.TestCase):
    def test_generated_outputs_follow_shared_palette_in_both_appearances(self):
        module = generator()
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for directory in ('gtk', 'waybar', 'wofi'):
                (root / directory).mkdir()
            with patch.object(module, 'H', temp), patch.object(module.subprocess, 'run'):
                for dark in (True, False):
                    with patch.object(module, 'modo_escuro', return_value=dark):
                        for name in CORES:
                            module.aplicar(name)
                            expected = CORES[name][0 if dark else 1]
                            for path in ('gtk/accent3.css', 'gtk/accent4.css', 'waybar/accent.css', 'wofi/accent.css'):
                                self.assertIn(expected, (root / path).read_text())
                            before = (root / 'gtk/accent3.css').stat().st_mtime_ns
                            module.aplicar(name)
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
