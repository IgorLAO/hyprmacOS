"""MIC-10: abertura dos painéis (emerge) contínua, sincronizada e interrompível.

HIG Motion: "Let people cancel motion… don't make people wait for an animation
to complete". As margens acompanham o popin do Hyprland (macPop, POP_MS); o
fechamento no meio não pode saltar. Executa as funções reais do hyprmac-shell
(carregadas por AST) com relógio de quadros simulado a 60 Hz.
"""

import ast
from pathlib import Path
import re
import sys
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "shell" / "hyprmac-shell"
sys.path.insert(0, str(ROOT / "shell"))
from glass_motion import spring_step  # noqa: E402
NAMES = {"cubic_bezier", "emerge", "stop_emerge", "set_margins"}


class Edge:
    TOP, BOTTOM, LEFT, RIGHT = "top", "bottom", "left", "right"


class LayerShell:
    def __init__(self):
        self.margins = {}

    def set_margin(self, win, edge, value):
        self.margins[edge] = value


class Clock:
    def __init__(self):
        self.us = 1_000_000

    def get_frame_time(self):
        return self.us

    def start_at_monotonic(self):
        self.us = int(time.monotonic() * 1e6)


class Size:
    width, height = 320, 400


class Window:
    def __init__(self):
        self.ticks, self.next_id = {}, 1

    def get_preferred_size(self):
        return None, Size()

    def add_tick_callback(self, step):
        tick_id, self.next_id = self.next_id, self.next_id + 1
        self.ticks[tick_id] = step
        return tick_id

    def remove_tick_callback(self, tick_id):
        del self.ticks[tick_id]


def load(reduced=False):
    text = SOURCE.read_text()
    tree = ast.parse(text)
    nodes = [n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name in NAMES]
    ls = LayerShell()
    consts = {name: ast.literal_eval(re.search(rf"^{name} = (.+?)(?:\s+#.*)?$", text, re.M).group(1))
              for name in ("POP_FROM", "POP_MS", "POP_CURVE")}
    ns = dict(E=Edge, LS=ls, reduce_motion=lambda: reduced, spring_step=spring_step, time=time, **consts)
    exec(compile(ast.Module(body=nodes, type_ignores=[]), str(SOURCE), "exec"), ns)
    ns["_pop_ease"] = ns["cubic_bezier"](*consts["POP_CURVE"])
    return ns, ls


def run_frames(win, clock, frames):
    for _ in range(frames):
        for tick_id, step in list(win.ticks.items()):
            if not step(win, clock):
                win.ticks.pop(tick_id, None)
        clock.us += 16_667


class EmergeMotion(unittest.TestCase):
    base = {Edge.TOP: 8, Edge.RIGHT: 40}

    def open_panel(self, reduced=False):
        ns, ls = load(reduced)
        win, clock = Window(), Clock()
        clock.start_at_monotonic()                  # o código antigo media com time.monotonic
        ns["emerge"](win, self.base, (320, 0))      # origem no canto do ícone
        return ns, ls, win, clock

    def test_first_frame_keeps_origin_and_ends_at_base(self):
        ns, ls, win, clock = self.open_panel()
        self.assertNotEqual(ls.margins, self.base)  # 1º quadro desloca para fixar a origem
        run_frames(win, clock, 30)                  # 500 ms > POP_MS
        self.assertEqual(ls.margins, self.base)
        self.assertEqual(win.ticks, {})

    def test_progress_has_no_jump(self):
        ns, ls, win, clock = self.open_panel()
        start = ls.margins[Edge.RIGHT]
        span = abs(start - self.base[Edge.RIGHT])
        values = [start]
        for _ in range(int(ns["POP_MS"] / 16.667) + 2):
            run_frames(win, clock, 1)
            values.append(ls.margins[Edge.RIGHT])
        biggest = max(abs(b - a) for a, b in zip(values, values[1:]))
        self.assertLessEqual(biggest, span * 0.25, values)   # o salto antigo era ~84 %
        self.assertEqual(values[-1], self.base[Edge.RIGHT])

    def test_duration_matches_hyprland_popin(self):
        ns, ls, win, clock = self.open_panel()
        lua = (ROOT / "hypr" / "hyprmac.lua").read_text()
        speed = float(re.search(r'leaf = "layersIn",\s+enabled = true, speed = ([\d.]+), bezier = "macPop"', lua).group(1))
        self.assertEqual(ns["POP_MS"], round(speed * 100))
        frames = 0
        while win.ticks:
            run_frames(win, clock, 1)
            frames += 1
        self.assertAlmostEqual(frames * 16.667, ns["POP_MS"], delta=34)

    def test_closing_midway_freezes_margins(self):
        ns, ls, win, clock = self.open_panel()
        run_frames(win, clock, 6)                   # ~100 ms
        frozen = dict(ls.margins)
        ns["stop_emerge"](win, self.base)
        run_frames(win, clock, 10)
        self.assertEqual(ls.margins, frozen)        # sem salto durante o esmaecer
        self.assertEqual(win.ticks, {})

    def test_reopen_midway_restarts_with_popin(self):
        ns, ls, win, clock = self.open_panel()
        first = dict(ls.margins)
        run_frames(win, clock, 6)
        ns["emerge"](win, self.base, (320, 0))
        self.assertEqual(ls.margins, first)
        self.assertEqual(len(win.ticks), 1)

    def test_reduce_motion_places_base_at_once(self):
        ns, ls, win, clock = self.open_panel(reduced=True)
        self.assertEqual(ls.margins, self.base)
        self.assertEqual(win.ticks, {})


if __name__ == "__main__":
    unittest.main()
