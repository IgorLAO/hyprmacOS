"""MIC-12: "Play feedback when volume is changed" (Ajustes ▸ Som do macOS Tahoe 26).

support.apple.com/guide/mac-help/mchlp2207/26: "when you press one of the volume
keys, a sound plays to let you hear the new volume"; Shift inverte a opção.
Métodos reais do LevelOSD carregados por AST, sem GTK nem PipeWire.
"""

import ast
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock
import unittest

SOURCE = Path(__file__).resolve().parents[1] / "shell" / "hyprmac-shell"


def load(config, volume_out="Volume: 0.40"):
    tree = ast.parse(SOURCE.read_text())
    osd = next(n for n in tree.body if isinstance(n, ast.ClassDef) and n.name == "LevelOSD")
    methods = [n for n in osd.body if isinstance(n, ast.FunctionDef)
               and n.name in ("command", "_feedback", "_read_volume")]
    klass = ast.ClassDef(name="LevelOSD", bases=[], keywords=[], body=methods, decorator_list=[], type_params=[])
    spawn = Mock()
    clock = SimpleNamespace(now=100.0)
    ns = dict(load_config=lambda: config, spawn=spawn, run=lambda cmd: volume_out,
              in_thread=lambda fn, *a: fn(*a), time=SimpleNamespace(monotonic=lambda: clock.now),
              GLib=SimpleNamespace(idle_add=lambda fn, *a: fn(*a)))
    exec(compile(ast.fix_missing_locations(ast.Module(body=[klass], type_ignores=[])), str(SOURCE), "exec"), ns)
    osd = ns["LevelOSD"].__new__(ns["LevelOSD"])
    osd._sink_name = lambda: "Speakers"
    osd.title, osd.present = Mock(), Mock()
    return osd, spawn, clock


class VolumeFeedback(unittest.TestCase):
    def test_volume_key_plays_feedback_by_default(self):
        osd, spawn, _clock = load({})
        osd.command("volume")
        spawn.assert_called_once()
        self.assertIn("audio-volume-change", spawn.call_args[0][0])
        osd.present.assert_called_once_with("volume", 40, False)

    def test_shift_inverts_the_setting(self):
        osd, spawn, _clock = load({})
        osd.command("volume shift")
        spawn.assert_not_called()
        osd, spawn, _clock = load({"volume_feedback": False})
        osd.command("volume shift")
        spawn.assert_called_once()
        osd, spawn, _clock = load({"volume_feedback": False})
        osd.command("volume")
        spawn.assert_not_called()

    def test_mute_key_and_muted_output_stay_silent(self):
        osd, spawn, _clock = load({})
        osd.command("volume mute")
        spawn.assert_not_called()
        osd, spawn, _clock = load({}, "Volume: 0.40 [MUTED]")
        osd.command("volume")
        spawn.assert_not_called()

    def test_key_repeat_does_not_stack_sounds(self):
        osd, spawn, clock = load({})
        osd.command("volume")
        clock.now += 0.05
        osd.command("volume")
        self.assertEqual(spawn.call_count, 1)
        clock.now += 0.2
        osd.command("volume")
        self.assertEqual(spawn.call_count, 2)


if __name__ == "__main__":
    unittest.main()
