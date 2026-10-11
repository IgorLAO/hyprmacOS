"""Edição compartilhada dos campos GTK3 próprios do HyprMac.

Mapeamentos: AppKit StandardKeyBinding.dict, Tahoe 26.6.1 (25G76).
Option = Alt; Command = Super. Limites de palavras/clusters usam GTK/Pango;
a equivalência com o editor Cocoa em runtime ainda não foi verificada.
"""
import gi

gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gdk, Gtk


def is_modified_arrow(event):
    """Deixe o campo receber setas de edição antes de navegar nos resultados."""
    return (event.keyval in (Gdk.KEY_Left, Gdk.KEY_Right, Gdk.KEY_Up, Gdk.KEY_Down)
            and bool(event.state & (Gdk.ModifierType.SHIFT_MASK |
                                    Gdk.ModifierType.CONTROL_MASK |
                                    Gdk.ModifierType.MOD1_MASK |
                                    Gdk.ModifierType.SUPER_MASK |
                                    Gdk.ModifierType.MOD4_MASK)))


class CocoaEntryKeys:
    """Edição de linha do StandardKeyBinding.dict Tahoe 26.6.1.

    Movimento/seleção por palavra, linha, parágrafo e documento; edição e kill/yank.
    O buffer de kill pertence ao campo; não altera a área de transferência.
    """

    def __init__(self, entry):
        self.killed = ""
        entry.connect("key-press-event", self.on_key)

    def on_key(self, entry, event):
        state = event.state
        ctrl = bool(state & Gdk.ModifierType.CONTROL_MASK)
        command = bool(state & (Gdk.ModifierType.SUPER_MASK | Gdk.ModifierType.MOD4_MASK))
        option = bool(state & Gdk.ModifierType.MOD1_MASK)
        shift = bool(state & Gdk.ModifierType.SHIFT_MASK)
        key = Gdk.keyval_to_lower(event.keyval)
        # Option+Control+B/F é a única combinação dupla aqui declarada no recurso.
        word_key = ctrl and option and not command and key in (Gdk.KEY_b, Gdk.KEY_f)
        if not word_key and sum((ctrl, command, option)) != 1:
            return False
        direction = -1 if key in (Gdk.KEY_Left, Gdk.KEY_Up, Gdk.KEY_a, Gdk.KEY_b) else 1
        movement = None
        if word_key:
            movement = Gtk.MovementStep.WORDS
        elif key in (Gdk.KEY_Left, Gdk.KEY_Right):
            movement = Gtk.MovementStep.WORDS if option else Gtk.MovementStep.DISPLAY_LINE_ENDS
        elif option and key in (Gdk.KEY_Up, Gdk.KEY_Down):
            movement = Gtk.MovementStep.PARAGRAPH_ENDS
        elif command and key in (Gdk.KEY_Up, Gdk.KEY_Down):
            movement = Gtk.MovementStep.BUFFER_ENDS
        elif ctrl and key in (Gdk.KEY_a, Gdk.KEY_e):
            movement = Gtk.MovementStep.PARAGRAPH_ENDS
        if movement is not None:
            entry.emit("move-cursor", movement, direction, shift)
            return True
        if shift:
            return False
        text, pos = entry.get_text(), entry.get_position()
        selection = entry.get_selection_bounds()
        if command and key == Gdk.KEY_a:
            entry.select_region(0, -1)
            return True
        if not entry.get_editable():
            return False
        if ctrl and key == Gdk.KEY_k:
            self.killed = text[pos:]
            entry.delete_text(pos, -1)
        elif ctrl and key == Gdk.KEY_y:
            if self.killed:
                if selection:
                    start, end = selection
                    entry.delete_text(start, end)
                    pos = start
                entry.set_text(entry.get_text()[:pos] + self.killed + entry.get_text()[pos:])
                entry.set_position(pos + len(self.killed))
        elif ctrl and key == Gdk.KEY_t:
            if not selection and len(text) > 1 and pos > 0:
                end = min(pos + 1, len(text))
                # Movimento lógico do GTK respeita clusters Unicode inteiros.
                entry.set_position(end)
                entry.emit("move-cursor", Gtk.MovementStep.LOGICAL_POSITIONS, -1, False)
                b = entry.get_position()
                entry.emit("move-cursor", Gtk.MovementStep.LOGICAL_POSITIONS, -1, False)
                a = entry.get_position()
                if a < b < end:
                    entry.set_text(text[:a] + text[b:end] + text[a:b] + text[end:])
                    entry.set_position(end)
                else:
                    entry.set_position(pos)
        elif key == Gdk.KEY_BackSpace and command:
            if selection:
                entry.delete_text(*selection)
            else:
                entry.delete_text(0, pos)
        elif key == Gdk.KEY_BackSpace and option:
            if selection:
                entry.delete_text(*selection)
            else:
                entry.emit("delete-from-cursor", Gtk.DeleteType.WORD_ENDS, -1)
        else:
            return False
        return True
