"""Seletor e busca em app, sem GTK nem display."""
import ast
from pathlib import Path
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import Mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "shell"))
from spotlight_search import (spot_app_results, spot_app_scope, spot_filter_command,
                              spot_filter_results, spot_filter_scope, spot_fold)


def methods(*names):
    tree = ast.parse((ROOT / "shell/hyprmac-shell").read_text())
    cls = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "Spotlight")
    nodes = [n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name in names]
    gdk = SimpleNamespace(**{name: name for name in (
        "KEY_Escape", "KEY_BackSpace", "KEY_Tab", "KEY_Down", "KEY_Up", "KEY_Left",
        "KEY_Right", "KEY_r", "KEY_R", "KEY_Return", "KEY_KP_Enter")},
        ModifierType=SimpleNamespace(CONTROL_MASK=1, SUPER_MASK=2, MOD4_MASK=4))
    ns = {"spot_filter_command": spot_filter_command, "spot_fold": spot_fold,
          "Gdk": gdk, "is_modified_arrow": lambda ev: False,
          "Gio": SimpleNamespace(ThemedIcon=SimpleNamespace(new=lambda name: name)),
          "hypr_json": Mock(return_value=[])}
    exec(compile(ast.Module(body=nodes, type_ignores=[]), "spotlight", "exec"), ns)
    obj = type("SpotlightMethods", (), {name: ns[name] for name in names})()
    return obj, ns


class SelectorTests(unittest.TestCase):
    def test_only_supported_filters_in_stable_order(self):
        self.assertEqual([it["name"] for it in spot_filter_results("/")],
                         ["Applications", "Folders", "Settings", "Actions"])

    def test_prefix_and_aliases(self):
        for query, expected in (("/f", ["folders"]), (" /APP ", ["apps"]),
                                ("/a", ["apps", "actions"]),
                                ("/System S", ["settings"]), ("/unknown", [])):
            self.assertEqual([it["key"] for it in spot_filter_results(query)], expected)

    def test_normal_queries_paths_and_calculations_are_not_selectors(self):
        for query in ("Files", "8/2", "/home/user", "//folders", "/tmp/report.pdf"):
            self.assertIsNone(spot_filter_results(query))

    def test_result_becomes_supported_token(self):
        for it in spot_filter_results("/"):
            scope = spot_filter_scope(it)
            self.assertEqual(scope["key"], spot_filter_command("/" + it["name"]))
            self.assertTrue(scope["icon"])
        self.assertIsNone(spot_filter_scope({"kind": "filter", "key": "clipboard"}))
        self.assertIsNone(spot_filter_scope({"kind": "app"}))

    def test_real_search_renders_selector_without_other_sources(self):
        obj, _ = methods("_search")
        obj.entry = Mock()
        obj.entry.get_text.return_value = "/f"
        obj.scope, obj.mode = None, "all"
        obj._fill = Mock()
        obj._search()
        self.assertEqual([it["key"] for it in obj.results], ["folders"])
        self.assertEqual(obj.filters, [])
        obj._fill.assert_called_once()

    def test_return_uses_selected_filter_or_current_prefix(self):
        for query, selected_key, expected in (("/", "actions", "actions"),
                                              ("/f", "actions", "folders")):
            obj, _ = methods("_activate")
            obj.entry = Mock()
            obj.entry.get_text.return_value = query
            obj.scope = None
            obj.results = spot_filter_results("/")
            obj._selected = Mock(return_value=next(it for it in obj.results
                                                   if it["key"] == selected_key))
            obj._run = Mock()
            obj._activate()
            self.assertEqual(obj._run.call_args.args[0]["key"], expected)

    def test_click_applies_token_without_launching_or_hiding(self):
        obj, _ = methods("_run")
        obj.mode = "files"
        obj._set_mode, obj._set_scope = Mock(), Mock()
        obj.entry, obj.hide = Mock(), Mock()
        obj._run(spot_filter_results("/f")[0])
        obj._set_mode.assert_called_once_with("all")
        obj.entry.set_text.assert_called_once_with("")
        self.assertEqual(obj._set_scope.call_args.args[0]["key"], "folders")
        obj.hide.assert_not_called()


class AppScopeTests(unittest.TestCase):
    def app(self, name="Editor", desktop="org.example.Editor", **extra):
        return {"kind": "app", "id": "/apps/" + desktop + ".desktop", "name": name,
                "gicon": "app-icon", **extra}

    def test_special_apps_and_icon_identity(self):
        for name, desktop, target in (("Finder", "finder", "files"),
                                      ("Files", "org.gnome.Nautilus", "files"),
                                      ("System Settings", "hyprmac-ajustes", "settings"),
                                      ("Editor", "org.example.Editor", "windows")):
            scope = spot_app_scope(self.app(name, desktop))
            self.assertEqual(scope["target"], target)
            self.assertEqual(scope["label"], name)
            self.assertEqual(scope["gicon"], "app-icon")
        self.assertIsNone(spot_app_scope({"kind": "file"}))

    def test_files_and_settings_do_not_mix_sources(self):
        files = [{"kind": "file", "name": "Report.txt"}]
        settings = [{"kind": "setting", "name": "Display"}]
        for name, query, expected in (("Files", "rep", files),
                                      ("System Settings", "dis", settings)):
            scope = spot_app_scope(self.app(name))
            self.assertEqual(spot_app_results(scope, query, files=files, settings=settings), expected)

    def test_windows_use_exact_identity_and_ignore_hidden_or_unmapped(self):
        scope = spot_app_scope(self.app(wm_class="editor-window", executable="edit-bin"))
        clients = [{"address": str(i), "class": cls, "title": "Document", **extra}
                   for i, (cls, extra) in enumerate((
                       ("org.example.Editor", {}), ("editor-window", {}),
                       ("edit-bin", {}), ("EditorOther", {}),
                       ("Editor", {"hidden": True}), ("Editor", {"mapped": False}),
                       ("Wrapper", {"initialClass": "Editor"})))]
        actions = [{"kind": "app_action", "name": "New Document"}]
        results = spot_app_results(scope, "doc", clients=clients, actions=actions)
        self.assertEqual({it["id"] for it in results if it["kind"] == "window"},
                         {"0", "1", "2", "6"})
        self.assertIn(actions[0], results)
        self.assertEqual(spot_app_results(scope, "missing", clients=clients), [])

    def test_tab_enters_first_app_and_empty_backspace_removes_scope(self):
        obj, _ = methods("_on_key")
        obj.entry = Mock()
        obj.entry.get_text.return_value = "edi"
        obj.results = [self.app()]
        obj.scope, obj.calc_item = None, None
        obj._files_view = Mock(return_value=False)
        obj._enter_app_scope = Mock()
        self.assertTrue(obj._on_key(None, SimpleNamespace(keyval="KEY_Tab", state=0)))
        scope = obj._enter_app_scope.call_args.args[0]
        self.assertEqual(scope["target"], "windows")
        obj.scope = scope
        obj.entry.get_text.return_value = ""
        obj._set_scope = Mock()
        self.assertTrue(obj._on_key(None, SimpleNamespace(keyval="KEY_BackSpace", state=0)))
        obj._set_scope.assert_called_once_with(None)

    def test_real_app_search_uses_clients_only_for_window_target(self):
        obj, ns = methods("_search")
        obj.entry = Mock()
        obj.entry.get_text.return_value = ""
        obj.mode, obj.files, obj.settings = "all", [], []
        obj._fill = Mock()
        for name, calls in (("Files", 0), ("Editor", 1)):
            obj.scope = spot_app_scope(self.app(name))
            obj._search()
            self.assertEqual(ns["hypr_json"].call_count, calls)

    def test_enter_scope_loads_only_selected_desktop_actions(self):
        obj, ns = methods("_enter_app_scope")
        info = Mock()
        info.list_actions.return_value = ["new-window"]
        info.get_action_name.return_value = "New Window"
        factory = Mock(return_value=info)
        ns["Gio"].DesktopAppInfo = SimpleNamespace(new_from_filename=factory)
        obj.mode, obj.entry, obj._set_scope = "all", Mock(), Mock()
        scope = spot_app_scope(self.app())
        obj._enter_app_scope(scope)
        factory.assert_called_once_with(scope["app"]["id"])
        self.assertEqual(scope["app_actions"][0]["desktop"], scope["app"]["id"])
        self.assertEqual(scope["app_actions"][0]["action"], "new-window")
        obj.entry.set_text.assert_called_once_with("")
        obj._set_scope.assert_called_once_with(scope)

    def test_run_window_focuses_address_and_app_action_uses_gio(self):
        obj, ns = methods("_run")
        ns["dispatch"] = Mock()
        info = Mock()
        ns["Gio"].DesktopAppInfo = SimpleNamespace(new_from_filename=Mock(return_value=info))
        obj.mod, obj.hide, obj._remember_query = None, Mock(), Mock()
        obj._run({"kind": "window", "address": "0x123"})
        ns["dispatch"].assert_called_once_with("focuswindow address:0x123")
        obj._run({"kind": "app_action", "desktop": "/apps/editor.desktop", "action": "new"})
        info.launch_action.assert_called_once_with("new", None)


if __name__ == "__main__":
    unittest.main()
