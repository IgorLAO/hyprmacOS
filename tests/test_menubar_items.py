"""Itens da barra de menus mostrados/ocultados por Ajustes e pela galeria da Central."""
import json
import os
from pathlib import Path
import sys
import tempfile
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "shell"))
import menubar_items as mb  # noqa: E402


class MenuBarItemsTests(unittest.TestCase):
    def setUp(self):
        self.conf = tempfile.mkdtemp()
        self.root = tempfile.mkdtemp()
        os.makedirs(os.path.join(self.root, "waybar"))

    def css(self):
        with open(os.path.join(self.root, "waybar", "barra-ocultos.css")) as fh:
            return fh.read()

    def test_ocultar_e_mostrar_gera_css_e_preserva_outras_chaves(self):
        with open(os.path.join(self.conf, "barra.json"), "w") as fh:
            json.dump({"hidden": ["battery"], "outra": 1}, fh)
        h = mb.set_shown("vpn", False, self.conf, self.root, reload_bar=False)
        self.assertEqual(h, {"battery", "vpn"})
        self.assertIn("#custom-vpn", self.css())
        self.assertIn("#battery", self.css())
        with open(os.path.join(self.conf, "barra.json")) as fh:
            self.assertEqual(json.load(fh)["outra"], 1)
        h = mb.set_shown("vpn", True, self.conf, self.root, reload_bar=False)
        self.assertEqual(h, {"battery"})
        self.assertNotIn("#custom-vpn", self.css())

    def test_config_ausente_ou_corrompida(self):
        self.assertEqual(mb.hidden(self.conf), set())
        with open(os.path.join(self.conf, "barra.json"), "w") as fh:
            fh.write("{quebrado")
        self.assertEqual(mb.hidden(self.conf), set())
        mb.set_shown("wifi", False, self.conf, self.root, reload_bar=False)
        self.assertEqual(mb.hidden(self.conf), {"wifi"})

    def test_mapa_da_central_aponta_para_itens_existentes(self):
        for cc, bar in mb.CC_TO_BAR.items():
            self.assertIn(bar, mb.SELECTORS, cc)

    def test_chave_desconhecida_nao_vira_seletor(self):
        self.assertNotIn("{", mb.css_for({"inexistente"}).split("\n", 1)[1])


if __name__ == "__main__":
    unittest.main()
