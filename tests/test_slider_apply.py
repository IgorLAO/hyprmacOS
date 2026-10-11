"""CCN-05: sliders da Central respondem já durante o arrasto, sem empilhar processos.

LatestCommand roda um processo por vez e sempre com o valor mais novo: um wpctl/ddcutil
antigo nunca termina depois do novo (antes cada passo do slider abria um processo e o
brilho só aplicava 350 ms depois de parar). Classe real carregada por AST.
"""

import ast
from pathlib import Path
import tempfile
import unittest

import gi
from gi.repository import Gio, GLib

SOURCE = Path(__file__).resolve().parents[1] / "shell" / "hyprmac-shell"
TEXT = SOURCE.read_text()


def load():
    tree = ast.parse(TEXT)
    nodes = [n for n in tree.body if isinstance(n, (ast.ClassDef, ast.FunctionDef))
             and n.name in ("LatestCommand", "volume_argv")]
    ns = dict(Gio=Gio, GLib=GLib)
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(SOURCE), "exec"), ns)
    return ns


class LatestValue(unittest.TestCase):
    def test_drag_applies_in_order_and_ends_on_last_value(self):
        ns = load()
        with tempfile.TemporaryDirectory() as d:
            log = Path(d) / "log"
            # cada "escrita" demora 30 ms e registra início/fim: dá para ver sobreposição
            cmd = ns["LatestCommand"](lambda v: ["sh", "-c", f"echo start {v} >> {log}; sleep 0.03; "
                                                             f"echo end {v} >> {log}"])
            loop = GLib.MainLoop()
            values = list(range(0, 101, 5))
            for i, v in enumerate(values):
                GLib.timeout_add(3 * i, lambda v=v: cmd.set(v) or False)
            GLib.timeout_add(1500, lambda: loop.quit() or False)
            loop.run()
            lines = log.read_text().split()
        events = list(zip(lines[::2], map(int, lines[1::2])))
        running = 0
        for kind, _v in events:
            running += 1 if kind == "start" else -1
            self.assertLessEqual(running, 1)                 # nunca dois ao mesmo tempo
        applied = [v for kind, v in events if kind == "end"]
        self.assertEqual(applied[-1], 100)                   # termina no valor mais novo
        self.assertEqual(applied, sorted(applied))           # nunca volta para um valor velho
        self.assertLess(len(applied), len(values))           # valores intermediários pulados
        self.assertFalse(cmd.busy)

    def test_volume_unmutes_like_the_mac(self):
        argv = load()["volume_argv"](42)
        self.assertIn("set-mute @DEFAULT_AUDIO_SINK@ 0", argv[-1])
        self.assertIn("set-volume @DEFAULT_AUDIO_SINK@ 0.42", argv[-1])

    def test_sliders_use_it(self):
        self.assertNotIn("GLib.timeout_add(350, apply)", TEXT)
        self.assertGreaterEqual(TEXT.count("LatestCommand("), 4)


if __name__ == "__main__":
    unittest.main()
