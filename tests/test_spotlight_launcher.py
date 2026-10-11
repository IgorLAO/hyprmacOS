"""O atalho não troca para o Wofi quando o shell está iniciando."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/spotlight'


class LauncherTests(unittest.TestCase):
    def run_launcher(self, failures):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            bin_dir = root / 'bin'
            bin_dir.mkdir()
            shell = root / 'Projects/hyprmac/shell/hyprmac-shell'
            shell.parent.mkdir(parents=True)
            shell.write_text('#!/bin/bash\nprintf started > "$XDG_RUNTIME_DIR/started"\n')
            shell.chmod(0o755)
            for name, body in {
                'gdbus': '''n=0
[ ! -f "$XDG_RUNTIME_DIR/calls" ] || read -r n < "$XDG_RUNTIME_DIR/calls"
n=$((n+1)); printf '%s\\n' "$n" > "$XDG_RUNTIME_DIR/calls"
printf '%s\\n' "$*" >> "$XDG_RUNTIME_DIR/args"
[ "$n" -gt "$FAILURES" ]
''',
                'sleep': 'exit 0\n',
                'wofi': 'printf forbidden > "$XDG_RUNTIME_DIR/wofi"; exit 99\n',
            }.items():
                p = bin_dir / name
                p.write_text('#!/bin/bash\n' + body)
                p.chmod(0o755)
            env = {**os.environ, 'HOME': temp, 'XDG_RUNTIME_DIR': temp,
                   'PATH': str(bin_dir) + ':' + os.environ['PATH'], 'FAILURES': str(failures)}
            env.pop('HYPRMAC_SPOTLIGHT_WOFI', None)
            result = subprocess.run(['bash', str(SCRIPT), 'mode', 'files'], env=env,
                                    capture_output=True, text=True, timeout=5)
            self.assertFalse((root / 'wofi').exists())
            self.assertIn('spotlight mode files', (root / 'args').read_text())
            return result, int((root / 'calls').read_text())

    def test_ready_shell_dispatches_immediately(self):
        result, calls = self.run_launcher(0)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(calls, 1)

    def test_startup_waits_for_native_shell(self):
        result, calls = self.run_launcher(3)
        self.assertEqual(result.returncode, 0)
        self.assertEqual(calls, 4)

    def test_failure_never_silently_launches_old_ui(self):
        result, calls = self.run_launcher(100)
        self.assertEqual(result.returncode, 1)
        self.assertEqual(calls, 26)
        self.assertIn('shell não respondeu', result.stderr)

if __name__ == '__main__':
    unittest.main()
