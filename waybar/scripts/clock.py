#!/usr/bin/env python3
"""Relógio da barra de menus com as Clock Options do Tahoe 26.

Lê ~/.config/hyprmac/relogio.json (Ajustes ▸ Control Center ▸ Clock Options…)
e o 24 horas de ajustes.json (Date & Time). Atualiza na virada do minuto, ou de
cada segundo com segundos/separadores piscando; SIGUSR1 relê as opções na hora.
A data completa fica na dica, em inglês como os menus.
"""
import datetime
import json
import os
import signal
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "shell"))
from clock_format import clock_text, needs_seconds_tick  # noqa: E402

CONF = os.path.expanduser("~/.config/hyprmac")
DAYS = ("Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday")
LONG_MONTHS = ("January", "February", "March", "April", "May", "June", "July",
               "August", "September", "October", "November", "December")


def load(name):
    try:
        with open(os.path.join(CONF, name)) as fh:
            return json.load(fh)
    except (OSError, ValueError):
        return {}


def main():
    signal.pthread_sigmask(signal.SIG_BLOCK, {signal.SIGUSR1})
    while True:
        prefs = load("relogio.json")
        h24 = load("ajustes.json").get("clock_24h", True)
        now = datetime.datetime.now()
        # "When Space Allows": sem medir a sobra da barra, a data fica oculta (como antes)
        text = clock_text(now, prefs, h24, space_allows=False, markup=True)
        tip = f"{DAYS[now.weekday()]}, {LONG_MONTHS[now.month - 1]} {now.day}, {now.year}"
        print(json.dumps({"text": text, "tooltip": tip}), flush=True)
        now = datetime.datetime.now()
        wait = 1 - now.microsecond / 1e6
        if not needs_seconds_tick(prefs):
            wait += 59 - now.second
        signal.sigtimedwait({signal.SIGUSR1}, max(wait, 0.01))


if __name__ == "__main__":
    main()
