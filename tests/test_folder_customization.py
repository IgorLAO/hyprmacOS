"""Persistência da aparência individual de pastas da Mesa."""

import errno
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "shell"))
from folder_appearance import folder_customization, set_folder_customization  # noqa: E402


class FolderCustomization(unittest.TestCase):
    def test_attributes_follow_rename_and_can_be_cleared(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "Folder"
            path.mkdir()
            try:
                set_folder_customization(path, color="#A1B2C3", emoji="🎨")
            except OSError as error:
                if error.errno in (errno.ENOTSUP, errno.EOPNOTSUPP):
                    self.skipTest("filesystem without user xattrs")
                raise
            self.assertEqual(folder_customization(path), ("#A1B2C3", "🎨"))
            renamed = path.with_name("Renamed")
            path.rename(renamed)
            self.assertEqual(folder_customization(renamed), ("#A1B2C3", "🎨"))
            set_folder_customization(renamed, color="", emoji="")
            self.assertEqual(folder_customization(renamed), (None, None))

    def test_invalid_color_does_not_write(self):
        with tempfile.TemporaryDirectory() as directory:
            with self.assertRaises(ValueError):
                set_folder_customization(directory, color="red")
            self.assertEqual(folder_customization(directory), (None, None))
