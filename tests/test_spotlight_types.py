"""Fontes do seletor e filtros MIME, sem criar janelas."""
import os
from pathlib import Path
import tempfile
import time
import unittest
from unittest.mock import Mock

from test_spotlight_selector import methods
from spotlight_search import (spot_app_results, spot_app_scope, spot_file_matches,
                              spot_file_query, spot_filter_results, spot_filter_scope,
                              SPOT_WEIGHT, spot_calc, spot_score)


class SourceSelectorTests(unittest.TestCase):
    def test_shell_sources_and_original_filters(self):
        results = spot_filter_results("/", include_sources=True)
        self.assertEqual([it["name"] for it in results],
                         ["Applications", "Files", "Folders", "Settings", "Actions", "Clipboard"])
        self.assertEqual([it["key"] for it in spot_filter_results("/f", True)],
                         ["files", "folders"])
        for it in results:
            self.assertEqual(spot_filter_scope(it, True)["key"], it["key"])

    def test_actions_has_distinct_symbolic_icon(self):
        action = spot_filter_results("/Actions", True)[0]
        settings = spot_filter_results("/Settings", True)[0]
        self.assertEqual(action["icons"], ["system-run-symbolic"])
        self.assertNotEqual(action["icons"], settings["icons"])
        obj, _ = methods("_filter_of")
        self.assertEqual(obj._filter_of({"kind": "action"})[2], "system-run-symbolic")

    def test_files_enters_existing_mode(self):
        obj, _ = methods("_run")
        obj.clipboard = Mock()
        obj._set_scope, obj._set_mode, obj.entry = Mock(), Mock(), Mock()
        obj._run(spot_filter_results("/Files", True)[0])
        obj._set_scope.assert_called_once_with(None, search=False)
        obj._set_mode.assert_called_once_with("files")
        obj.entry.set_text.assert_called_once_with("")

    def test_clipboard_reuses_panel_and_history(self):
        obj, _ = methods("_run", "_pick_mode")
        obj.clipboard, obj.hide = Mock(), Mock()
        obj._run(spot_filter_results("/Clipboard", True)[0])
        obj.hide.assert_called_once_with()
        obj.clipboard.show.assert_called_once_with()

    def test_return_before_debounce_uses_new_source(self):
        for query, expected in (("/Files", "files"), ("/Clipboard", "clipboard")):
            obj, _ = methods("_activate")
            obj.clipboard, obj.entry, obj._run = Mock(), Mock(), Mock()
            obj.entry.get_text.return_value = query
            obj.scope = None
            obj._selected = Mock(return_value=spot_filter_results("/Actions", True)[0])
            obj._activate()
            self.assertEqual(obj._run.call_args.args[0]["key"], expected)


class FileTypeTests(unittest.TestCase):
    def setUp(self):
        self.files = [
            {"kind": "file", "id": "pdf", "name": "Annual Report.PDF", "path": "/Annual Report.PDF"},
            {"kind": "file", "id": "png", "name": "Holiday.png", "path": "/Holiday.png"},
            {"kind": "file", "id": "heic", "name": "Photo", "path": "/Photo", "mime": "image/heic"},
            {"kind": "file", "id": "dir", "name": "Report.pdf", "is_dir": True},
            {"kind": "file", "id": "txt", "name": "Report.txt", "mime": "text/plain"},
        ]

    def test_query_aliases_and_name_terms(self):
        for query, text, kind in (("kind:pdf", "", "pdf"), ("pdf", "", "pdf"),
                                  ("images", "", "image"), ("kind:image", "", "image"),
                                  ("kind:folder", "", "folder"), ("folders Report", "Report", "folder"),
                                  ("Report KIND:PDF", "Report", "pdf"),
                                  ("kind:images Holiday", "Holiday", "image")):
            with self.subTest(query=query):
                self.assertEqual(spot_file_query(query), (text, (kind,)))

    def test_unknown_types_and_substrings_stay_literal(self):
        for text in ("kind:audio", "mykind:pdf", "pdfium", "report.pdf", "/tmp/images"):
            self.assertEqual(spot_file_query(text), (text, ()))

    def test_mime_and_extension_exclude_misleading_folder_names(self):
        for kind, expected in (("pdf", ["pdf"]), ("image", ["png", "heic"]),
                               ("folder", ["dir"])):
            self.assertEqual([f["id"] for f in self.files if spot_file_matches(f, (kind,))], expected)
        self.assertTrue(all(spot_file_matches(f, ()) for f in self.files))
        self.assertFalse(spot_file_matches(self.files[0], ("pdf", "image")))
        self.assertFalse(spot_file_matches({"name": "Fake.pdf", "mime": "text/plain"}, ("pdf",)))

    def search(self, query, mode="all", scope=None):
        obj, ns = methods("_search")
        ns.update(SPOT_WEIGHT=SPOT_WEIGHT, spot_calc=spot_calc, spot_score=spot_score)
        obj.clipboard, obj.entry, obj._fill = Mock(), Mock(), Mock()
        obj.entry.get_text.return_value = query
        obj.scope, obj.mode, obj.files = scope, mode, self.files
        obj.apps = [{"kind": "app", "id": "app", "name": "pdf", "extra": ""}]
        obj.settings, obj.actions = [], []
        obj.hist = {"apps": [], "files": [], "actions": []}
        obj._filter_of = Mock(return_value=(None, None, None))
        obj._folder_items = Mock(return_value=self.files)
        obj._search()
        return obj

    def test_real_search_all_and_files_filter_without_matching_literal_token(self):
        for mode in ("all", "files"):
            for query, expected in (("kind:pdf", ["pdf"]), ("pdf Report", ["pdf"]),
                                    ("images", ["png", "heic"]), ("kind:folder", ["dir"])):
                with self.subTest(mode=mode, query=query):
                    self.assertEqual([it["id"] for it in self.search(query, mode).results], expected)

    def test_real_selector_includes_sources(self):
        self.assertEqual([it["key"] for it in self.search("/f").results], ["files", "folders"])

    def test_folder_scope_respects_type_and_name(self):
        obj = self.search("Report kind:pdf", scope={"key": "folders", "path": "/example"})
        self.assertEqual([it["id"] for it in obj.results], ["pdf"])
        obj._folder_items.assert_called_once_with("/example")

    def test_finder_scope_applies_same_mime_filter(self):
        scope = spot_app_scope({"kind": "app", "id": "finder.desktop", "name": "Finder"})
        self.assertEqual([it["id"] for it in spot_app_results(scope, "images", files=self.files)],
                         ["png", "heic"])
        self.assertEqual([it["id"] for it in self.search("kind:pdf", scope=scope).results], ["pdf"])

    def test_file_entry_caches_real_gio_mime(self):
        try:
            from gi.repository import Gio
        except ImportError:
            self.skipTest("Gio indisponível")
        obj, ns = methods("_file_entry")
        ns.update(os=os, time=time, Gio=Gio)
        obj.mod = None
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "Report.PDF"
            path.write_bytes(b"%PDF-1.7\n")
            self.assertEqual(obj._file_entry(str(path))["mime"], "application/pdf")
            self.assertEqual(obj._file_entry(tmp)["mime"], "inode/directory")


if __name__ == "__main__":
    unittest.main()
