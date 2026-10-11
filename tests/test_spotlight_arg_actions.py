"""SPT-03: ações que rodam pelo Spotlight sem abrir o app ("ar buy milk" → lembrete).

Mac User Guide (Tahoe 26) ▸ Take actions and shortcuts in Spotlight: digitar a quick key
pede o texto no próprio campo ("ft Ashley") e Return roda a ação. Métodos reais do
Spotlight e run_arg_action carregados por AST.
"""

import ast
from pathlib import Path
import sys
import tempfile
from types import SimpleNamespace
from unittest.mock import Mock, patch
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "shell" / "hyprmac-shell"
sys.path.insert(0, str(ROOT / "shell"))
from spotlight_search import spot_fold  # noqa: E402


def load():
    tree = ast.parse(SOURCE.read_text())
    nodes = [n for n in tree.body if (isinstance(n, ast.Assign) and any(
        getattr(t, "id", "") == "SPOT_ARG_ACTIONS" for t in n.targets))
        or (isinstance(n, ast.FunctionDef) and n.name == "run_arg_action")]
    spot = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "Spotlight")
    methods = [n for n in spot.body if isinstance(n, ast.FunctionDef) and n.name in ("_arg_action", "_action_entry")]
    klass = ast.ClassDef(name="Spotlight", bases=[], keywords=[], body=methods, decorator_list=[], type_params=[])
    spawn = Mock()
    ns = dict(spot_fold=spot_fold, spawn=spawn, GLib=SimpleNamespace(shell_quote=lambda s: repr(s)))
    exec(compile(ast.fix_missing_locations(ast.Module(body=nodes + [klass], type_ignores=[])),
                 str(SOURCE), "exec"), ns)
    return ns, spawn


class ArgActions(unittest.TestCase):
    def spotlight(self, ns):
        spot = ns["Spotlight"].__new__(ns["Spotlight"])
        spot.actions = list(ns["SPOT_ARG_ACTIONS"])
        spot._qk_keys = {"q:ar": "ar"}
        spot.mod = SimpleNamespace(MENU_ICONS={})
        return spot

    def test_quick_key_with_text_becomes_ready_result(self):
        ns, _ = load()
        hit = self.spotlight(ns)._arg_action("AR buy milk")
        self.assertEqual(hit["name"], "Add Reminder “buy milk”")
        self.assertEqual(hit["argtext"], "buy milk")
        self.assertIsNone(self.spotlight(ns)._arg_action("ar"))          # sem texto: pede no campo
        self.assertIsNone(self.spotlight(ns)._arg_action("xx buy milk"))

    def test_custom_quick_key_is_used(self):
        ns, _ = load()
        spot = self.spotlight(ns)
        spot._qk_keys = {"q:ar": "rem"}
        self.assertIsNotNone(spot._arg_action("rem call mom"))
        self.assertIsNone(spot._arg_action("ar call mom"))

    def test_reminder_is_saved_without_opening_the_app(self):
        ns, spawn = load()
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / "reminders.json"
            import app_factory_reminders as rem
            store = rem.ReminderStore
            with patch.object(rem, "ReminderStore", lambda: store(path)):
                ns["run_arg_action"]("reminder", "  buy milk ")
            self.assertEqual([i["title"] for i in store(path).items], ["buy milk"])
        self.assertIn("Reminder Added", spawn.call_args[0][0])


if __name__ == "__main__":
    unittest.main()
