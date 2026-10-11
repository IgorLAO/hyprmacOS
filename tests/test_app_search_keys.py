"""Shared Cocoa editing reaches the actual search fields of the three apps."""

import importlib.machinery
import importlib.util
import os
from pathlib import Path
from types import SimpleNamespace
import sys
import tempfile
import unittest
from unittest import mock

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gdk, Gtk


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "shell"))
import notes_store


def load_app(name):
    source = ROOT / "shell" / name
    loader = importlib.machinery.SourceFileLoader(name.replace("-", "_"), str(source))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


@unittest.skipUnless(Gdk.Display.get_default(), "sem display GTK")
class AppSearchKeysTests(unittest.TestCase):
    def test_shared_editing_in_notes_journal_and_photos(self):
        with tempfile.TemporaryDirectory() as root:
            cases = (
                ("hyprmac-notas", lambda m: m.NotesView(notes_store.Store(root=root))),
                ("hyprmac-diario", lambda m: m.JournalView(root_dir=root)),
                ("hyprmac-fotos", lambda m: m.PhotosAppView()),
            )
            with mock.patch.dict(os.environ, {"HYPRMAC_FOTOS_DIR": root}):
                for name, make_view in cases:
                    with self.subTest(app=name):
                        module = load_app(name)
                        window = Gtk.OffscreenWindow()
                        try:
                            view = make_view(module)
                            window.add(view)
                            window.show_all()
                            entry = view.search_entry
                            entry.set_text("Tahoe search")
                            entry.set_position(6)
                            handled = view._search_cocoa_keys.on_key(
                                entry, SimpleNamespace(keyval=Gdk.KEY_k,
                                                       state=Gdk.ModifierType.CONTROL_MASK))
                            self.assertTrue(handled)
                            self.assertEqual(entry.get_text(), "Tahoe ")
                        finally:
                            window.destroy()


if __name__ == "__main__":
    unittest.main()
