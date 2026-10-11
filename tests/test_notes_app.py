"""App Notes (shell/hyprmac-notas): clique no círculo da lista, salvamento sem perder os
marcadores ocultos e troca de nota sem laço salvar/selecionar. Defeitos achados pelos
testes do agente FreeLLM TST-NOTAS e corrigidos; aqui fica a verificação do orquestrador."""
import importlib.machinery
import importlib.util
import os
from pathlib import Path
import sys
import tempfile
import time
import unittest
from unittest import mock

import gi
gi.require_version("Gtk", "3.0")
gi.require_version("Gdk", "3.0")
from gi.repository import Gdk, Gtk  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "shell"))
import notes_store  # noqa: E402


def carregar_app():
    loader = importlib.machinery.SourceFileLoader("hyprmac_notas", str(ROOT / "shell" / "hyprmac-notas"))
    spec = importlib.util.spec_from_loader("hyprmac_notas", loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


def bombear(segundos=0.8):
    fim = time.time() + segundos
    while time.time() < fim:
        while Gtk.events_pending():
            Gtk.main_iteration_do(False)
        time.sleep(0.01)


@unittest.skipUnless(Gdk.Display.get_default(), "sem display")
class NotesAppTests(unittest.TestCase):
    def setUp(self):
        self.m = carregar_app()
        self.store = notes_store.Store(root=tempfile.mkdtemp())
        outra = self.store.new()
        outra.text = "Outra\ntexto"
        self.store.save(outra)
        os.utime(outra.path, (time.time() - 100,) * 2)
        self.nota = self.store.new()
        self.nota.text = "Title\n- [ ] a"
        self.store.save(self.nota)
        self.win = Gtk.OffscreenWindow()
        self.win.set_size_request(1000, 650)
        self.view = self.m.NotesView(self.store, window=self.win)
        self.win.add(self.view)
        self.win.show_all()
        bombear()
        self.tv = self.view.textview
        self.buf = self.tv.get_buffer()

    def tearDown(self):
        self.win.destroy()

    def texto(self):
        return self.buf.get_text(self.buf.get_start_iter(), self.buf.get_end_iter(), True)

    def clicar_linha(self, linha, x):
        r = self.tv.get_iter_location(self.buf.get_iter_at_line(linha))
        _, wy = self.tv.buffer_to_window_coords(Gtk.TextWindowType.TEXT, r.x, r.y + r.height // 2)
        return self.view.on_textview_button_press(self.tv, mock.Mock(button=1, x=x, y=wy))

    def test_constantes_medidas(self):
        self.assertEqual(self.m.MARGEM, 24)
        self.assertEqual(self.m.CHECK_D, 17)

    def test_clique_no_circulo_alterna_e_fora_nao(self):
        self.assertFalse(self.clicar_linha(1, self.m.MARGEM + 60))
        self.assertEqual(self.texto(), "Title\n- [ ] a")
        self.assertTrue(self.clicar_linha(1, self.m.MARGEM + 8))
        self.assertEqual(self.texto(), "Title\n- [x] a")
        self.assertTrue(self.clicar_linha(1, self.m.MARGEM + 8))
        self.assertEqual(self.texto(), "Title\n- [ ] a")

    def test_salvar_mantem_marcadores_ocultos(self):
        self.clicar_linha(1, self.m.MARGEM + 8)
        self.buf.insert(self.buf.get_end_iter(), "b")
        bombear(1.2)                       # salvamento automático em 500 ms
        with open(self.nota.path, encoding="utf-8") as fh:
            self.assertEqual(fh.read(), "Title\n- [x] ab")
        self.assertEqual(self.texto(), "Title\n- [x] ab")

    def test_trocar_de_nota_sem_laco(self):
        self.buf.insert(self.buf.get_end_iter(), "b")
        bombear(1.2)
        lista = self.view.notes_list
        lista.select_row(lista.get_children()[1])
        bombear(0.4)
        self.assertEqual(self.texto(), "Outra\ntexto")
        lista.select_row(lista.get_children()[0])
        bombear(0.4)
        self.assertEqual(self.texto(), "Title\n- [ ] ab")


if __name__ == "__main__":
    unittest.main()
