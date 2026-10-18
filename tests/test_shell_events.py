"""Regressões do assinante único do Hyprland e dos menus dinâmicos da barra."""

import json
import os
from pathlib import Path
from queue import Queue
import socket
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "shell"))
from hypr_events import EventBus  # noqa: E402

MENU_BINARY = ROOT / "core/waybar-status/target/release/hyprmac-waybar"


class EventBusTests(unittest.TestCase):
    def test_one_socket_delivers_ordered_lines_to_all_subscribers(self):
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp) / "hypr" / "test-signature"
            directory.mkdir(parents=True)
            path = directory / ".socket2.sock"
            with socket.socket(socket.AF_UNIX) as listener:
                listener.bind(str(path))
                listener.listen(2)
                listener.settimeout(2)
                scheduled = Queue()
                seen = []
                bus = EventBus(lambda fn, line: scheduled.put((fn, line)), temp,
                               signature="test-signature", retry_seconds=0.05)
                bus.subscribe(lambda line: seen.append(("dock", line)))
                bus.subscribe(lambda line: seen.append(("menu", line)))
                with listener.accept()[0] as conn:
                    conn.sendall(b"activewindow>>Code,title\nconfigreloaded>>\n")
                    for _ in range(2):
                        fn, line = scheduled.get(timeout=2)
                        self.assertFalse(fn(line))
                    self.assertEqual(seen, [
                        ("dock", "activewindow>>Code,title"),
                        ("menu", "activewindow>>Code,title"),
                        ("dock", "configreloaded>>"),
                        ("menu", "configreloaded>>"),
                    ])
                    listener.settimeout(0.1)
                    with self.assertRaises(socket.timeout):
                        listener.accept()


class MenuTests(unittest.TestCase):
    def test_reads_focus_snapshot_and_preserves_visibility_rules(self):
        with tempfile.TemporaryDirectory() as temp, mock.patch.dict(
                os.environ, {"XDG_RUNTIME_DIR": temp}):
            path = Path(temp) / "hyprmac-active-class.json"
            for cls, expected in (("Code", "Selection"), ("firefox", ""), ("", "")):
                path.write_text(json.dumps({"pid": os.getpid(), "class": cls}))
                out = subprocess.check_output([MENU_BINARY, "app-menu", "Selection", "^Code$"],
                                              env={**os.environ, "XDG_RUNTIME_DIR": temp})
                self.assertEqual(expected, json.loads(out)["text"])

    def test_stale_snapshot_falls_back_to_hyprctl(self):
        with tempfile.TemporaryDirectory() as temp, mock.patch.dict(
                os.environ, {"XDG_RUNTIME_DIR": temp}):
            path = Path(temp) / "hyprmac-active-class.json"
            path.write_text(json.dumps({"pid": 99999999, "class": "stale"}))
            mock_hyprctl = Path(temp) / "hyprctl"
            mock_hyprctl.write_text('#!/bin/sh\necho \'{"class":"org.gnome.Nautilus"}\'\n')
            mock_hyprctl.chmod(0o755)
            out = subprocess.check_output([MENU_BINARY, "app-menu", "Go", "^org\\.gnome\\.Nautilus$"],
                                          env={**os.environ, "XDG_RUNTIME_DIR": temp,
                                               "PATH": f"{temp}:{os.environ['PATH']}"})
            self.assertEqual("Go", json.loads(out)["text"])


if __name__ == "__main__":
    unittest.main()
