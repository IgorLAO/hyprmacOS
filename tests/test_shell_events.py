"""Regressões do assinante único do Hyprland e dos menus dinâmicos da barra."""

import importlib.util
import json
import os
from pathlib import Path
from queue import Queue
import re
import socket
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "shell"))
from hypr_events import EventBus  # noqa: E402

spec = importlib.util.spec_from_file_location(
    "app_menu", ROOT / "waybar/scripts/app-menu.py")
app_menu = importlib.util.module_from_spec(spec)
spec.loader.exec_module(app_menu)


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
                with mock.patch.object(subprocess, "run") as run:
                    result = app_menu.active_class()
                run.assert_not_called()
                self.assertEqual(expected, "Selection" if re.search("^Code$", result) else "")

    def test_stale_snapshot_falls_back_to_hyprctl(self):
        with tempfile.TemporaryDirectory() as temp, mock.patch.dict(
                os.environ, {"XDG_RUNTIME_DIR": temp}):
            path = Path(temp) / "hyprmac-active-class.json"
            path.write_text(json.dumps({"pid": 99999999, "class": "stale"}))
            with mock.patch.object(subprocess, "run", return_value=mock.Mock(
                    stdout='{"class":"org.gnome.Nautilus"}')) as run:
                self.assertEqual(app_menu.active_class(), "org.gnome.Nautilus")
            run.assert_called_once()


if __name__ == "__main__":
    unittest.main()
