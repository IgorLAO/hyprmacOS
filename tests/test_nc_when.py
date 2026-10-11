import os
import unittest
import time
import datetime
from pathlib import Path


def get_when_text_func():
    script_path = Path(__file__).resolve().parents[1] / "shell" / "hyprmac-shell"
    content = script_path.read_text(encoding="utf-8")
    # Find start of function
    start = content.find("def when_text")
    if start == -1:
        raise ValueError("when_text not found")
    # Find the next line that starts with 'class ClickCatchers' after start
    end = content.find("\nclass ClickCatchers", start)
    if end == -1:
        # fallback: maybe class at start of line
        end = content.find("\nclass ClickCatchers", start)
    snippet = content[start:end]  # excludes the class line
    # Prepare namespace with time and datetime
    ns = {"time": time, "datetime": datetime}
    exec(snippet, ns)
    return ns["when_text"]


class TestWhenText(unittest.TestCase):
    def setUp(self):
        os.environ["HOME"] = "/nonexistent"
        self.when_text = get_when_text_func()
        # Fixed now: 2026-10-11 12:00:00 local time (as used in other tests)
        self.fixed_dt = datetime.datetime(2026, 10, 11, 12, 0, 0)
        self.now = time.mktime(self.fixed_dt.timetuple())

    def test_now(self):
        ts = self.now - 30
        self.assertEqual(self.when_text(ts, now=self.now), "now")

    def test_minutes_ago(self):
        ts = self.now - 150  # 2 minutes 30 seconds -> should be 2m ago
        self.assertEqual(self.when_text(ts, now=self.now), "2m ago")

    def test_same_day_hours_ago(self):
        # 3 hours before same day
        ts = self.now - 3 * 3600  # 09:00:00
        expected = "9:00"  # hour without leading zero
        self.assertEqual(self.when_text(ts, now=self.now), expected)

    def test_yesterday(self):
        # exactly 1 day before
        ts = self.now - 24 * 3600
        self.assertEqual(self.when_text(ts, now=self.now), "Yesterday")

    def test_three_days_ago(self):
        ts = self.now - 3 * 24 * 3600
        self.assertEqual(self.when_text(ts, now=self.now), "3 days ago")

    def test_twenty_days_ago(self):
        ts = self.now - 20 * 24 * 3600
        # Expect month/day/year format from time.localtime(ts)
        lt = time.localtime(ts)
        expected = f"{lt.tm_mon}/{lt.tm_mday}/{lt.tm_year % 100:02d}"
        self.assertEqual(self.when_text(ts, now=self.now), expected)


if __name__ == "__main__":
    unittest.main()