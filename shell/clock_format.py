"""Texto do relógio da barra de menus com as Clock Options do Tahoe 26.

Opções e padrões conforme ClockPreferences (ControlCenter.app) e as strings de
ControlCenterSettings.appex do macOS 26.6.1 (25G76): Show date (When Space
Allows/Always/Never), Show the day of the week, Show AM/PM, Display the time
with seconds e Flash the time separators. Sempre em inglês, como os menus,
sem depender do locale instalado. O formato de 24 horas vem de Date & Time.
Rascunho inicial delegado (FMT-01), corrigido e validado pelo orquestrador.
"""

DEFAULTS = {
    "show_date": "when_space_allows",
    "show_day_of_week": True,
    "show_ampm": True,
    "show_seconds": False,
    "flash_separators": False,
}
SHOW_DATE = ("when_space_allows", "always", "never")
DAYS = ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun")  # datetime.weekday()
MONTHS = ("Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec")
# separador apagado no markup: transparente, mantém a largura do ":" na fonte proporcional
HIDDEN_SEP = '<span alpha="1">:</span>'


def prefs_of(raw):
    """Mescla com os padrões; valores inválidos voltam ao padrão."""
    p = dict(DEFAULTS)
    p.update({k: v for k, v in (raw or {}).items() if k in DEFAULTS})
    if p["show_date"] not in SHOW_DATE:
        p["show_date"] = DEFAULTS["show_date"]
    return p


def needs_seconds_tick(prefs):
    """A barra precisa atualizar a cada segundo."""
    p = prefs_of(prefs)
    return bool(p["show_seconds"] or p["flash_separators"])


def clock_text(dt, prefs, h24, space_allows=False, markup=False):
    p = prefs_of(prefs)
    parts = []
    if p["show_day_of_week"]:
        parts.append(DAYS[dt.weekday()])
    if p["show_date"] == "always" or (p["show_date"] == "when_space_allows" and space_allows):
        parts.append(f"{MONTHS[dt.month - 1]} {dt.day}")

    sep = ":"
    if p["flash_separators"] and dt.second % 2:
        sep = HIDDEN_SEP if markup else " "
    hour = dt.hour if h24 else (dt.hour % 12 or 12)
    time = f"{hour}{sep}{dt.minute:02d}"
    if p["show_seconds"]:
        time += f"{sep}{dt.second:02d}"
    if not h24 and p["show_ampm"]:
        time += " AM" if dt.hour < 12 else " PM"
    parts.append(time)
    return " ".join(parts)
