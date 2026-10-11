"""Behavior checks for local App Factory backends."""

import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "shell"))

from app_factory_activity import sample_processes
from app_factory_calendar import CalendarStore
from app_factory_disk_utility import format_capacity
from app_factory_reminders import ReminderStore
from app_factory_system_info import collect_system_info
from app_factory_voice_memos import _stop_process


class LocalBackendTests(unittest.TestCase):
    def test_reminders_persist_and_toggle(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "reminders.json"
            store = ReminderStore(path)
            identifier = store.add("Buy milk")
            self.assertIsNotNone(identifier)
            self.assertTrue(store.complete(identifier, True))
            loaded = ReminderStore(path)
            self.assertEqual(loaded.items[0]["completed"], True)
            self.assertTrue(loaded.delete(identifier))
            self.assertEqual(ReminderStore(path).items, [])
            self.assertEqual(path.stat().st_mode & 0o777, 0o600)

    def test_calendar_persists_and_orders_events(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "calendar.json"
            store = CalendarStore(path)
            late = store.save_event("2026-10-11", "Late", "18:30")
            early = store.save_event("2026-10-11", "Early", "08:15")
            self.assertEqual([v["id"] for v in CalendarStore(path).for_day("2026-10-11")],
                             [early, late])
            store.save_event("2026-10-11", "Earlier", "07:00", late)
            self.assertEqual(store.for_day("2026-10-11")[0]["title"], "Earlier")
            self.assertTrue(store.remove_event("2026-10-11", early))
            with self.assertRaises(ValueError):
                store.save_event("2026-10-11", "Invalid", "25:99")

    def test_linux_readers_and_recording_process_cleanup(self):
        rows, counters = sample_processes()
        self.assertIn(os.getpid(), {pid for pid, *_ in rows})
        self.assertIn("total", counters)
        info = collect_system_info()
        self.assertTrue(info["Processor"])
        self.assertTrue(info["Memory"])
        self.assertEqual(format_capacity(1500000000), "1.5 GB")
        process = subprocess.Popen(["sleep", "30"])
        try:
            _stop_process(process)
            self.assertIsNotNone(process.poll())
        finally:
            if process.poll() is None:
                process.kill()
                process.wait()


if __name__ == "__main__":
    unittest.main()
