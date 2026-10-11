"""Journal Store (shell/hyprmac-diario): pure functions for diary entries.
Tests cover: get_diario_dir, load_entries, count_this_year, save_entry.
Uses tempfile for root and os.utime for dates (current year and previous year)."""
import importlib.machinery
import importlib.util
import os
import sys
import tempfile
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "shell"))


def carregar_diario():
    loader = importlib.machinery.SourceFileLoader("hyprmac_diario", str(ROOT / "shell" / "hyprmac-diario"))
    spec = importlib.util.spec_from_loader("hyprmac_diario", loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


class JournalStoreTests(unittest.TestCase):
    def setUp(self):
        self.m = carregar_diario()
        self.tmpdir = tempfile.mkdtemp()
        self.root = os.path.join(self.tmpdir, "diario")

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def test_get_diario_dir_creates_directory(self):
        """get_diario_dir creates the directory if it doesn't exist."""
        d = self.m.get_diario_dir(self.root)
        self.assertTrue(os.path.isdir(d))
        self.assertEqual(d, self.root)

    def test_get_diario_dir_returns_existing(self):
        """get_diario_dir returns the same path if directory exists."""
        os.makedirs(self.root, exist_ok=True)
        d = self.m.get_diario_dir(self.root)
        self.assertEqual(d, self.root)

    def test_load_entries_empty_directory(self):
        """load_entries returns empty list for empty/non-existent directory."""
        # Non-existent directory (writable under tmp)
        nonexist = os.path.join(self.tmpdir, "nonexistent_dir")
        entries = self.m.load_entries(nonexist)
        self.assertEqual(entries, [])
        # Directory should have been created by get_diario_dir
        self.assertTrue(os.path.isdir(nonexist))

        # Empty directory
        os.makedirs(self.root, exist_ok=True)
        entries = self.m.load_entries(self.root)
        self.assertEqual(entries, [])

    def test_load_entries_order_by_mtime_desc(self):
        """Entries are sorted by mtime descending (newest first)."""
        os.makedirs(self.root, exist_ok=True)

        # Create three entries with different mtimes
        paths = []
        for i in range(3):
            p = os.path.join(self.root, f"entry_{i}.md")
            with open(p, "w", encoding="utf-8") as f:
                f.write(f"Title {i}\nBody {i}")
            paths.append(p)
            time.sleep(0.01)  # Ensure different mtimes

        # Set mtimes explicitly: oldest first, newest last
        now = time.time()
        os.utime(paths[0], (now - 300, now - 300))  # oldest
        os.utime(paths[1], (now - 200, now - 200))
        os.utime(paths[2], (now - 100, now - 100))  # newest

        entries = self.m.load_entries(self.root)
        self.assertEqual(len(entries), 3)
        # Should be sorted by mtime desc (newest first)
        self.assertEqual(entries[0].path, paths[2])
        self.assertEqual(entries[1].path, paths[1])
        self.assertEqual(entries[2].path, paths[0])

    def test_load_entries_title_is_first_line(self):
        """Entry title is the first line of the file, stripped."""
        os.makedirs(self.root, exist_ok=True)

        p = os.path.join(self.root, "test.md")
        with open(p, "w", encoding="utf-8") as f:
            f.write("  My Title  \nBody line 1\nBody line 2")

        entries = self.m.load_entries(self.root)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].title, "My Title")
        self.assertEqual(entries[0].text, "Body line 1\nBody line 2")

    def test_load_entries_title_untitled_when_empty(self):
        """Entry title is 'Untitled' when file is empty."""
        os.makedirs(self.root, exist_ok=True)

        p = os.path.join(self.root, "empty.md")
        with open(p, "w", encoding="utf-8") as f:
            f.write("")

        entries = self.m.load_entries(self.root)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].title, "Untitled")
        self.assertEqual(entries[0].text, "")

    def test_load_entries_only_md_files(self):
        """load_entries only loads .md files."""
        os.makedirs(self.root, exist_ok=True)

        with open(os.path.join(self.root, "a.md"), "w") as f:
            f.write("A\nbody")
        with open(os.path.join(self.root, "b.txt"), "w") as f:
            f.write("B\nbody")
        with open(os.path.join(self.root, "c.MD"), "w") as f:
            f.write("C\nbody")

        entries = self.m.load_entries(self.root)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0].title, "A")

    def test_count_this_year_current_year_only(self):
        """count_this_year counts only entries from the current year."""
        os.makedirs(self.root, exist_ok=True)

        now = time.time()
        current_year = time.localtime(now).tm_year
        prev_year = current_year - 1

        # Create entries with different years
        paths = []
        for i in range(4):
            p = os.path.join(self.root, f"entry_{i}.md")
            with open(p, "w", encoding="utf-8") as f:
                f.write(f"Title {i}\nBody")
            paths.append(p)

        # Two entries from current year
        os.utime(paths[0], (now, now))
        os.utime(paths[1], (now - 86400, now - 86400))  # 1 day ago

        # Two entries from previous year
        prev_year_time = time.mktime((prev_year, 6, 15, 12, 0, 0, 0, 0, 0))
        os.utime(paths[2], (prev_year_time, prev_year_time))
        os.utime(paths[3], (prev_year_time - 86400, prev_year_time - 86400))

        entries = self.m.load_entries(self.root)
        count = self.m.count_this_year(entries)
        self.assertEqual(count, 2)

    def test_count_this_year_all_current_year(self):
        """count_this_year returns total when all entries are current year."""
        os.makedirs(self.root, exist_ok=True)

        now = time.time()
        paths = []
        for i in range(3):
            p = os.path.join(self.root, f"entry_{i}.md")
            with open(p, "w", encoding="utf-8") as f:
                f.write(f"Title {i}\nBody")
            paths.append(p)
            os.utime(p, (now - i * 86400, now - i * 86400))

        entries = self.m.load_entries(self.root)
        count = self.m.count_this_year(entries)
        self.assertEqual(count, 3)

    def test_count_this_year_none_current_year(self):
        """count_this_year returns 0 when no entries are from current year."""
        os.makedirs(self.root, exist_ok=True)

        prev_year = time.localtime(time.time()).tm_year - 1
        prev_year_time = time.mktime((prev_year, 6, 15, 12, 0, 0, 0, 0, 0))

        paths = []
        for i in range(2):
            p = os.path.join(self.root, f"entry_{i}.md")
            with open(p, "w", encoding="utf-8") as f:
                f.write(f"Title {i}\nBody")
            paths.append(p)
            os.utime(p, (prev_year_time - i * 86400, prev_year_time - i * 86400))

        entries = self.m.load_entries(self.root)
        count = self.m.count_this_year(entries)
        self.assertEqual(count, 0)

    def test_save_entry_creates_new_file(self):
        """save_entry creates a new file when path is None."""
        path = self.m.save_entry("New Title", "New body text", root=self.root)

        self.assertTrue(os.path.exists(path))
        self.assertTrue(path.endswith(".md"))

        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertEqual(content, "New Title\nNew body text")

    def test_save_entry_updates_existing_file(self):
        """save_entry updates existing file when path is provided."""
        os.makedirs(self.root, exist_ok=True)

        # Create initial entry
        p = os.path.join(self.root, "existing.md")
        with open(p, "w", encoding="utf-8") as f:
            f.write("Old Title\nOld body")

        # Update it
        returned_path = self.m.save_entry("Updated Title", "Updated body", path=p)

        self.assertEqual(returned_path, p)
        with open(p, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertEqual(content, "Updated Title\nUpdated body")

    def test_save_entry_preserves_path_on_update(self):
        """save_entry returns the same path when updating."""
        os.makedirs(self.root, exist_ok=True)

        p = os.path.join(self.root, "test.md")
        with open(p, "w", encoding="utf-8") as f:
            f.write("Title\nBody")

        path1 = self.m.save_entry("Title 1", "Body 1", path=p)
        path2 = self.m.save_entry("Title 2", "Body 2", path=p)

        self.assertEqual(path1, path2)
        self.assertEqual(path1, p)

    def test_save_entry_creates_directory_if_needed(self):
        """save_entry creates the directory if it doesn't exist."""
        new_root = os.path.join(self.tmpdir, "new_diario")
        self.assertFalse(os.path.exists(new_root))

        path = self.m.save_entry("Title", "Body", root=new_root)

        self.assertTrue(os.path.exists(new_root))
        self.assertTrue(os.path.exists(path))

    def test_entry_object_has_correct_attributes(self):
        """Entry object has path, title, text, mtime attributes."""
        os.makedirs(self.root, exist_ok=True)

        p = os.path.join(self.root, "test.md")
        with open(p, "w", encoding="utf-8") as f:
            f.write("My Title\nMy body text")

        entries = self.m.load_entries(self.root)
        self.assertEqual(len(entries), 1)

        e = entries[0]
        self.assertEqual(e.path, p)
        self.assertEqual(e.title, "My Title")
        self.assertEqual(e.text, "My body text")
        self.assertIsInstance(e.mtime, float)
        self.assertGreater(e.mtime, 0)


if __name__ == "__main__":
    unittest.main()