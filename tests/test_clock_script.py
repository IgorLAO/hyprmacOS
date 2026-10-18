"""Tests for the Rust Waybar clock subprocess behavior.

Roda o script com HOME temporário, verifica primeira linha JSON e
releitura via SIGUSR1.
"""
import json
import os
import re
import select
import signal
import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT_PATH = Path(__file__).resolve().parents[1] / "core/waybar-status/target/release/hyprmac-waybar"


def _read_line(proc, timeout=2.0):
    """Read one line from proc.stdout with timeout using select."""
    rlist, _, _ = select.select([proc.stdout], [], [], timeout)
    if not rlist:
        raise TimeoutError("Timeout waiting for output from clock.py")
    line = proc.stdout.readline()
    if not line:
        raise RuntimeError("Process closed stdout unexpectedly")
    return line


class TestClockScript(unittest.TestCase):
    def test_clock_script_reload_via_sigusr1(self):
        with tempfile.TemporaryDirectory() as tmp_home:
            config_dir = Path(tmp_home) / ".config" / "hyprmac"
            config_dir.mkdir(parents=True, exist_ok=True)
            relogio_path = config_dir / "relogio.json"
            # start with empty prefs
            relogio_path.write_text("{}")

            env = os.environ.copy()
            env["HOME"] = tmp_home

            proc = subprocess.Popen(
                [str(SCRIPT_PATH), "clock"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=env,
                text=True,
                bufsize=1,
            )
            try:
                # First line
                line1 = _read_line(proc, timeout=3.0)
                data1 = json.loads(line1)
                self.assertIn("text", data1)
                self.assertIn("tooltip", data1)

                tooltip = data1["tooltip"]
                # Format: Sunday, October 11, 2026
                self.assertRegex(
                    tooltip,
                    r"^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday), (January|February|March|April|May|June|July|August|September|October|November|December) \d{1,2}, \d{4}$",
                    f"Tooltip format unexpected: {tooltip}",
                )

                # Change prefs to show date always and seconds
                new_prefs = {"show_date": "always", "show_seconds": True}
                relogio_path.write_text(json.dumps(new_prefs))

                # Trigger reload
                os.kill(proc.pid, signal.SIGUSR1)

                line2 = _read_line(proc, timeout=3.0)
                data2 = json.loads(line2)
                self.assertIn("text", data2)

                text = data2["text"]
                # Should contain abbreviated month (e.g., Oct 11) and seconds pattern
                self.assertRegex(
                    text,
                    r"\b(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec) \d{1,2}\b",
                    f"Text missing abbreviated month: {text}",
                )
                self.assertRegex(
                    text,
                    r"\d+:\d{2}:\d{2}",
                    f"Text missing seconds pattern: {text}",
                )
            finally:
                # Ensure process is terminated
                try:
                    proc.terminate()
                except Exception:
                    pass
                try:
                    proc.wait(timeout=2)
                except subprocess.TimeoutExpired:
                    try:
                        proc.kill()
                        proc.wait(timeout=1)
                    except Exception:
                        pass
                # Close pipes
                try:
                    proc.stdout.close()
                except Exception:
                    pass
                try:
                    proc.stderr.close()
                except Exception:
                    pass


if __name__ == "__main__":
    unittest.main()
