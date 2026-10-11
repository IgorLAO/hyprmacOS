"""Regressões funcionais dos subpainéis da Central, sem iniciar GTK."""

import ast
import os
from pathlib import Path
import re
import shlex
import sys
from types import SimpleNamespace
import unittest
from unittest.mock import Mock


ROOT = Path(__file__).resolve().parents[1]
SHELL = Path(os.environ.get("HYPRMAC_SYSTEM_SHELL", ROOT / "shell/hyprmac-shell"))
sys.path.insert(0, str(ROOT / "shell"))
from spotlight_search import (SPOT_WEIGHT, spot_calc, spot_filter_command,
                              spot_fold, spot_score)  # noqa: E402


def wifi_methods():
    """Executa os métodos reais; somente serviços e widgets são substituídos."""
    tree = ast.parse(SHELL.read_text())
    wifi = next(node for node in tree.body
                if isinstance(node, ast.ClassDef) and node.name == "WifiMenu")
    fields = next(node for node in tree.body
                  if isinstance(node, ast.FunctionDef) and node.name == "nm_fields")
    methods = [node for node in wifi.body if isinstance(node, ast.FunctionDef)
               and node.name in {"fetch", "signature", "_net_row"}]
    namespace = {
        "re": re, "run": Mock(), "spawn": Mock(),
        "time": SimpleNamespace(monotonic=lambda: 10),
        "GLib": SimpleNamespace(shell_quote=shlex.quote), "I": {"lock": "lock"},
    }
    module = ast.Module(body=[fields, *methods], type_ignores=[])
    exec(compile(module, str(SHELL), "exec"), namespace)
    return namespace


class ControlCenterWifiTests(unittest.TestCase):
    def setUp(self):
        self.ns = wifi_methods()
        self.menu = SimpleNamespace(_scanned=0, _network_rows={},
                                    _bars=lambda signal: str(signal), device=Mock())
        self.outputs = {
            "nmcli -t -f DEVICE,TYPE,STATE,CONNECTION device": "wlan0:wifi:disconnected:",
            "nmcli radio wifi": "enabled",
            "nmcli -t -f IN-USE,SSID,SIGNAL,SECURITY device wifi list --rescan no":
                r":Office\: Guest:70:WPA2" + "\n:Public:40:--",
            "nmcli -t -f UUID,TYPE connection show":
                "saved-uuid:802-11-wireless\nwired-uuid:802-3-ethernet",
            "nmcli -t -f 802-11-wireless.ssid connection show uuid saved-uuid":
                r"802-11-wireless.ssid:Office\: Guest",
        }
        self.ns["run"].side_effect = lambda command: self.outputs[command]

    def test_renamed_profile_recognized_by_escaped_ssid(self):
        data = self.ns["fetch"](self.menu)
        self.assertEqual(data["profiles"], {"Office: Guest": "saved-uuid"})
        self.assertEqual(data["nets"], [("Office: Guest", 70, False, True, True),
                                       ("Public", 40, False, False, False)])
        self.assertFalse(any("wired-uuid" in call.args[0]
                             for call in self.ns["run"].call_args_list))

    def test_saved_network_activates_uuid_and_new_network_quotes_ssid(self):
        self.menu.data = self.ns["fetch"](self.menu)
        self.ns["_net_row"](self.menu, "Office: Guest", 70, False, True, True)
        self.menu.device.call_args.kwargs["action"]()
        self.ns["spawn"].assert_called_with("nmcli connection up uuid saved-uuid")
        ssid = "Cafe's $(touch /tmp/unwanted)"
        self.ns["_net_row"](self.menu, ssid, 40, False, True, False)
        self.menu.device.call_args.kwargs["action"]()
        self.assertEqual(shlex.split(self.ns["spawn"].call_args.args[0]),
                         ["nmcli", "device", "wifi", "connect", ssid])

    def test_signature_preserves_rows_for_signal_but_rebinds_profile(self):
        data = self.ns["fetch"](self.menu)
        signature = self.ns["signature"](self.menu, data)
        changed_signal = dict(data, nets=[("Public", 95, False, False, False),
                                         ("Office: Guest", 35, False, True, True)])
        self.assertEqual(signature, self.ns["signature"](self.menu, changed_signal))
        changed_profile = dict(data, profiles={"Office: Guest": "replacement-uuid"})
        self.assertNotEqual(signature, self.ns["signature"](self.menu, changed_profile))

    def test_disabled_radio_skips_profiles_and_network_scan(self):
        self.outputs["nmcli radio wifi"] = "disabled"
        data = self.ns["fetch"](self.menu)
        self.assertEqual(data["nets"], [])
        self.assertEqual(data["profiles"], {})
        self.assertEqual(self.ns["run"].call_count, 2)

    def test_profile_lookup_cached_between_polls_and_expires(self):
        self.ns["fetch"](self.menu)
        detail = "nmcli -t -f 802-11-wireless.ssid connection show uuid saved-uuid"
        self.ns["run"].reset_mock()
        self.ns["fetch"](self.menu)
        self.assertEqual(self.ns["run"].call_count, 4)
        self.assertFalse(any(call.args[0] == detail for call in self.ns["run"].call_args_list))
        self.ns["time"].monotonic = lambda: 30
        self.ns["run"].reset_mock()
        self.outputs[detail] = "802-11-wireless.ssid:Public"
        data = self.ns["fetch"](self.menu)
        self.assertEqual(self.ns["run"].call_count, 5)
        self.assertEqual(data["profiles"], {"Public": "saved-uuid"})

    def test_uuid_changes_invalidate_profile_cache_before_expiration(self):
        self.ns["fetch"](self.menu)
        self.outputs["nmcli -t -f UUID,TYPE connection show"] = "new-uuid:802-11-wireless"
        self.outputs["nmcli -t -f 802-11-wireless.ssid connection show uuid new-uuid"] = (
            "802-11-wireless.ssid:Public")
        self.ns["run"].reset_mock()
        data = self.ns["fetch"](self.menu)
        self.assertEqual(self.ns["run"].call_count, 5)
        self.assertEqual(data["profiles"], {"Public": "new-uuid"})
        self.assertFalse(any("saved-uuid" in call.args[0]
                             for call in self.ns["run"].call_args_list))


def spotlight_methods():
    tree = ast.parse(SHELL.read_text())
    spotlight = next(node for node in tree.body
                     if isinstance(node, ast.ClassDef) and node.name == "Spotlight")
    names = {"_activate", "_filter_of", "_pick_filter", "_search"}
    methods = [node for node in spotlight.body if isinstance(node, ast.FunctionDef)
               and node.name in names]
    namespace = {
        "spot_filter_command": spot_filter_command, "spot_fold": spot_fold,
        "spot_calc": spot_calc, "spot_score": spot_score, "SPOT_WEIGHT": SPOT_WEIGHT,
        "Gio": SimpleNamespace(ThemedIcon=SimpleNamespace(new=lambda name: name)),
    }
    exec(compile(ast.Module(body=methods, type_ignores=[]), str(SHELL), "exec"), namespace)
    return type("SpotlightMethods", (), {name: namespace[name] for name in names})()


class SpotlightTypeFilterTests(unittest.TestCase):
    def test_only_complete_supported_commands_are_recognized(self):
        for command, key in (("/Apps", "apps"), (" /Applications ", "apps"),
                             ("/Folders", "folders"), ("/Settings", "settings"),
                             ("/System Settings", "settings"), ("/Actions", "actions")):
            with self.subTest(command=command):
                self.assertEqual(spot_filter_command(command), key)
        for text in ("", "/", "/PDF", "/unknown", "/folders photos", "/apps/search",
                     "/home/apps", "//folders", "8/2", "folders", "kind:folders"):
            with self.subTest(text=text):
                self.assertIsNone(spot_filter_command(text))

    def make_spotlight(self, text, mode="all"):
        spot = spotlight_methods()
        spot.mode, spot.scope = mode, None
        entry_text = [text]
        self.events = []
        spot.entry = Mock()
        spot.entry.get_text.side_effect = lambda: entry_text[0]

        def set_text(text):
            entry_text[0] = text
            self.events.append(("text", text))

        def set_mode(mode):
            spot.mode = mode
            self.events.append(("mode", mode))

        def set_scope(scope):
            spot.scope = scope
            self.events.append(("scope", scope["key"]))

        spot.entry.set_text.side_effect = set_text
        spot._set_mode = Mock(side_effect=set_mode)
        spot._set_scope = Mock(side_effect=set_scope)
        spot._selected = Mock(return_value={"kind": "app", "id": "stale-result"})
        spot._run = Mock()
        return spot

    def test_return_reuses_real_filter_and_token_methods_from_browse_mode(self):
        for command, key, label in (("/Applications", "apps", "Applications"),
                                    ("/Folders", "folders", "Folders"),
                                    ("/Settings", "settings", "System Settings"),
                                    ("/Actions", "actions", "Actions")):
            with self.subTest(command=command):
                spot = self.make_spotlight(command, "files")
                spot._activate()
                self.assertEqual(self.events, [("mode", "all"), ("text", ""), ("scope", key)])
                self.assertEqual(spot.scope["label"], label)
                spot.entry.grab_focus_without_selecting.assert_called_once()
                spot._selected.assert_not_called()
                spot._run.assert_not_called()

    def test_unknown_and_paths_keep_normal_activation(self):
        for text in ("/PDF", "/home/apps", "budget/2026", "/folders query", "/"):
            with self.subTest(text=text):
                spot = self.make_spotlight(text)
                spot._activate()
                spot._set_mode.assert_not_called()
                spot._set_scope.assert_not_called()
                spot.entry.set_text.assert_not_called()
                spot._run.assert_called_once_with(spot._selected.return_value)

    def test_filtered_search_uses_supported_scope_without_other_result_kinds(self):
        spot = self.make_spotlight("/Folders")
        spot._activate()
        spot.apps = [{"kind": "app", "id": "app", "name": "Browser", "extra": ""}]
        spot.settings = [{"kind": "setting", "id": "settings", "name": "Wi-Fi", "extra": ""}]
        spot.actions = []
        spot.files = [{"kind": "file", "id": "folder", "name": "Projects", "is_dir": True},
                      {"kind": "file", "id": "pdf", "name": "Report.pdf", "is_dir": False}]
        spot.hist = {"apps": [], "actions": [], "files": []}
        spot._file_app = Mock(return_value=None)
        spot._fill = Mock()
        spot._search()
        self.assertEqual([item["id"] for item in spot.results], ["folder"])
        self.assertEqual(spot.filters, [])

    def test_calculator_uses_normal_activation(self):
        spot = self.make_spotlight("8/2")
        spot._selected.return_value = {"kind": "calc", "name": spot_calc("8/2")}
        spot._activate()
        spot._run.assert_called_once_with({"kind": "calc", "name": "4"})
        spot._set_scope.assert_not_called()


if __name__ == "__main__":
    unittest.main()
