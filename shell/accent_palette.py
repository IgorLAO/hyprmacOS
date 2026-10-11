"""Destaques AppKit Tahoe 26; não confundir com system*Color do kit."""

# nome → (escuro, claro): controlAccent*Color do macOS Tahoe 26.6.1 (25G76), lidos de
# SystemAppearance.bundle/{DarkAqua,Aqua}.car — as cores de destaque clássicas, não os
# systemBlue/systemPurple… (os valores anteriores vinham do kit macOS 27 "System Colors")
CORES = {
    "blue":     ("#007AFF", "#007AFF"),
    "purple":   ("#A550A7", "#953D96"),
    "pink":     ("#F74F9E", "#F74F9E"),
    "red":      ("#FF5257", "#E0383E"),
    "orange":   ("#F7821B", "#F7821B"),
    "yellow":   ("#FFC600", "#FFC726"),
    "green":    ("#62BA46", "#62BA46"),
    "graphite": ("#8C8C8C", "#989898"),
}

GNOME_ACCENTS = {**{k: v for k, v in CORES.items() if k != "graphite"},
                 "slate": CORES["graphite"], "teal": CORES["blue"]}


def accent_hex(name, dark):
    return GNOME_ACCENTS.get(name, CORES["blue"])[0 if dark else 1]
