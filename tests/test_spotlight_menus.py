"""SPT-06: o Spotlight busca os comandos dos menus do app à frente, com os nomes da barra.

Os módulos de menu da Waybar só aparecem para certos apps (app-menu.py <rótulo> <regex>);
o spotlight-itens aplica o mesmo filtro e usa o mesmo rótulo ("History", não "Historico").
"""

import importlib.machinery
import importlib.util
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]


def load():
    loader = importlib.machinery.SourceFileLoader("spotlight_itens", str(ROOT / "scripts" / "spotlight-itens"))
    spec = importlib.util.spec_from_loader("spotlight_itens", loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


class FrontmostAppMenus(unittest.TestCase):
    def setUp(self):
        self.si = load()

    def menus(self, classe):
        items, cmds = self.si.menu_actions(classe)
        return {i["menu"] for i in items}, cmds

    def test_browser_menus_only_with_browser_in_front(self):
        browser, _ = self.menus("brave-origin")
        terminal, _ = self.menus("com.mitchellh.ghostty")
        self.assertTrue({"History", "Bookmarks"} <= browser)
        self.assertFalse({"History", "Bookmarks", "Go", "Selection"} & terminal)
        self.assertTrue({"Apple", "File", "Edit", "Help"} <= terminal)

    def test_editor_menus_with_code_in_front(self):
        code, _ = self.menus("code")
        self.assertTrue({"Selection", "Go", "Run", "Terminal"} <= code)
        self.assertNotIn("History", code)

    def test_titles_match_the_bar(self):
        everything = set()
        for classe in ("brave-origin", "code", "", "spotify"):
            everything |= self.menus(classe)[0]
        self.assertFalse({"Arquivo", "Editar", "Historico", "Favoritos", "Codigo-ir"} & everything)

    def test_commands_of_hidden_menus_stay_available_for_quick_actions(self):
        _, cmds = self.menus("com.mitchellh.ghostty")
        self.assertTrue(any(name == "custom/apple" for name, _ in cmds))


if __name__ == "__main__":
    unittest.main()
