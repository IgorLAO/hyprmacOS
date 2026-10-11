"""SPT-07: quick keys do Spotlight (Mac User Guide ▸ Take actions and shortcuts in Spotlight).

"Click 'Add quick keys' next to an action, then enter the keyboard shortcut";
"Click the assigned quick key field, make your change, then press Return";
"Suggested quick keys are automatically assigned after running an action once".
"""

from pathlib import Path
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "shell"))
import spotlight_quickkeys as qk  # noqa: E402

ACTIONS = [{"id": "q:nt", "key": "nt", "label": "New Terminal Window"},
           {"id": "q:lk", "key": "lk", "label": "Lock Screen"},
           {"id": "m:facetime", "label": "Start FaceTime Call"},
           {"id": "m:show", "label": "Show Fonts"}]


class QuickKeys(unittest.TestCase):
    def test_defaults_are_suggestions_and_overrides_win(self):
        self.assertEqual(qk.effective(ACTIONS, {}), {"q:nt": "nt", "q:lk": "lk"})
        keys = qk.effective(ACTIONS, {"q:nt": "term", "q:lk": ""})
        self.assertEqual(keys, {"q:nt": "term"})          # "" remove a tecla

    def test_assign_normalizes_and_moves_taken_key(self):
        keys = qk.effective(ACTIONS, {})
        out = qk.assign({}, "m:facetime", " F T! ", keys)
        self.assertEqual(out["m:facetime"], "ft")
        out = qk.assign({}, "m:facetime", "NT", keys)
        self.assertEqual((out["m:facetime"], out["q:nt"]), ("nt", ""))   # tecla trocou de dono
        self.assertEqual(qk.effective(ACTIONS, out)["m:facetime"], "nt")

    def test_suggestion_after_first_run_only(self):
        keys = qk.effective(ACTIONS, {})
        out = qk.after_run({}, ACTIONS[2], keys)
        self.assertEqual(out["m:facetime"], "sfc")
        self.assertIs(qk.after_run(out, ACTIONS[2], qk.effective(ACTIONS, out)), out)
        removed = {"m:facetime": ""}                      # removida pela pessoa: fica removida
        self.assertIs(qk.after_run(removed, ACTIONS[2], qk.effective(ACTIONS, removed)), removed)

    def test_suggestion_avoids_taken_keys(self):
        self.assertEqual(qk.suggest("Show Fonts", {"sf"}), "sfo")
        self.assertEqual(qk.suggest("Lock", set()), "lo")
        self.assertNotIn(qk.suggest("Show Fonts", {"sf", "sfo", "sfon", "sfont", "sfonts"}),
                         {"sf", "sfo", "sfon", "sfont", "sfonts"})

    def test_save_and_load_roundtrip(self):
        with tempfile.TemporaryDirectory() as d:
            path = str(Path(d) / "sub" / "qk.json")
            qk.save({"m:facetime": "ft"}, path)
            self.assertEqual(qk.load(path), {"m:facetime": "ft"})
        self.assertEqual(qk.load("/nonexistent/qk.json"), {})

    def test_spotlight_uses_them(self):
        shell = (ROOT / "shell" / "hyprmac-shell").read_text()
        self.assertIn('"Add quick keys"', shell)
        self.assertIn("quickkeys.after_run(", shell)
        self.assertNotIn("tecla rápida", shell)            # interface em inglês


if __name__ == "__main__":
    unittest.main()
