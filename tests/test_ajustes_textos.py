"""Textos dos Ajustes conferidos nas tabelas en/Base do Tahoe 26.6.1, sem GTK."""
import ast
import json
from pathlib import Path
import unittest
from unittest.mock import Mock


ROOT = Path(__file__).resolve().parents[1]
TEXTOS = Path(
    "/home/igor/.local/share/hyprmac-pesquisa/macos-26.6.1/"
    "minerar/codex-2026-10-11/textos"
)
TREE = ast.parse((ROOT / "shell" / "hyprmac-ajustes").read_text(encoding="utf-8"))
PANES = {node.name: node for node in ast.walk(TREE)
         if isinstance(node, ast.FunctionDef) and node.name.startswith("pane_")}

# Painel, bundle, tabela, chave, texto exato (incluindo o NBSP de Apple Pay).
ORIGENS = (
    ("pane_accessibility", "com.apple.Accessibility-Settings.extension", "Localizable.loctable",
     "accessibilityPlacardInfo",
     "Personalize Mac in ways that work best for you with accessibility features for "
     "vision, hearing, motor, speech, and cognition."),
    ("pane_siri", "com.apple.Siri-Settings.extension", "Localizable.loctable",
     "ASK_SIRI_DESCRIPTION",
     "Siri helps you get things done, just by asking. Dictate a note, check the weather, and more."),
    ("pane_password", "com.apple.BiometricsAndPasswordSettingsAppIntentsExtension",
     "Localizable.loctable",
     "A login password can be used to unlock your device, authorize purchases, and access sensitive data.",
     "A login password can be used to unlock your device, authorize purchases, and access sensitive data."),
    ("pane_wallet", "com.apple.WalletSettingsExtension", "InfoPlist.loctable",
     "CFBundleDisplayName", "Wallet & Apple\u00a0Pay"),
)

REMOVIDOS = (
    "This pane is not available on this computer yet.",
    "Share subscriptions, purchases, locations and more with up to five family members.",
    "Family Sharing lets you share with your family.",
    "Manage your overall setup and preferences for Mac, such as software updates, "
    "device language, AirDrop, and more.",
    "Personalize your computer in ways that work for you.",
    "Apple Intelligence is not available on this computer.",
    "Get insights about your screen time and set limits for what you want to manage.",
    "Change the password used to log in.",
    "Play with friends and track achievements.",
    "Add Card…",
    "Use Apple Pay to make secure purchases in apps and on the web.",
    "No cards have been added.",
    "Click Add Printer to set one up.",
)


def strings(node):
    return {item.value for item in ast.walk(node)
            if isinstance(item, ast.Constant) and isinstance(item.value, str)}


class AjustesTextosTests(unittest.TestCase):
    def test_wifi_preserva_rotulo_do_controle_de_hotspots(self):
        self.assertIn("Ask to join hotspots", strings(PANES["pane_wifi"]))
        self.assertNotIn("Personal Hotspot", strings(PANES["pane_wifi"]))

    @unittest.skipUnless(TEXTOS.is_dir(), "Extração local do Tahoe 26.6.1 ausente")
    def test_rotulo_de_hotspots_existe_nos_termos_de_busca_originais(self):
        data = json.loads((TEXTOS / "com.apple.wifi-settings-extension.json")
                          .read_text(encoding="utf-8"))
        table = data["en.lproj/WiFiSettings.searchTerms"]
        self.assertEqual(table["idioma"], "en")
        entries = table["valores"]["General_Join"]["localizableStrings"]
        self.assertIn("Ask to join hotspots", [entry["title"] for entry in entries])

    def test_hero_omite_rotulo_vazio_e_preserva_descricao(self):
        node = next(node for node in TREE.body
                    if isinstance(node, ast.FunctionDef) and node.name == "hero")
        code = compile(ast.Module(body=[node], type_ignores=[]), "hero", "exec")
        for text in ("", "Description"):
            with self.subTest(text=text):
                gtk = Mock()
                make_label = Mock(side_effect=lambda *args: Mock())
                namespace = {"Gtk": gtk, "label": make_label, "AppIcon": Mock(),
                             "add_class": Mock(), "glyph_of": Mock()}
                exec(code, namespace)
                box = namespace["hero"](("icon", "#FFFFFF"), "Title", text)
                self.assertEqual(box.pack_start.call_count, 3 if text else 2)
                self.assertEqual(make_label.call_count, 2 if text else 1)
                if text:
                    make_label.assert_called_with(text, "hero-text", 0.5)
                    description = box.pack_start.call_args.args[0]
                    description.set_line_wrap.assert_called_once_with(True)
                    description.set_justify.assert_called_once_with(gtk.Justification.CENTER)
                    description.set_max_width_chars.assert_called_once_with(58)

    def test_substituicoes_presentes_no_painel_correto(self):
        for pane, _bundle, _table, _key, text in ORIGENS:
            with self.subTest(pane=pane):
                self.assertIn(text, strings(PANES[pane]))

    @unittest.skipUnless(TEXTOS.is_dir(), "Extração local do Tahoe 26.6.1 ausente")
    def test_cada_texto_alterado_existe_no_json_de_origem(self):
        for pane, bundle, table, key, text in ORIGENS:
            with self.subTest(pane=pane, bundle=bundle, key=key):
                data = json.loads((TEXTOS / (bundle + ".json")).read_text(encoding="utf-8"))
                self.assertIn(data[table]["idioma"], ("en", "Base"))
                self.assertEqual(data[table]["valores"][key], text)
                self.assertIn(text, strings(PANES[pane]))

    def test_textos_sem_fonte_removidos(self):
        literals = strings(TREE)
        for text in REMOVIDOS:
            with self.subTest(text=text):
                self.assertNotIn(text, literals)

    def test_heroes_sem_descricao_comprovada(self):
        for pane in ("pane_family", "pane_general", "pane_screentime",
                     "pane_gamecenter", "pane_wallet"):
            with self.subTest(pane=pane):
                heroes = [node for node in ast.walk(PANES[pane])
                          if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                          and node.func.id == "hero"]
                self.assertEqual(len(heroes), 1)
                self.assertEqual(ast.literal_eval(heroes[0].args[2]), "")

    def test_wallet_preserva_botao_de_adicao(self):
        buttons = [node for node in ast.walk(PANES["pane_wallet"])
                   if isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                   and node.func.id == "push_button"]
        self.assertEqual(len(buttons), 1)
        # Símbolo de adição, sem inventar uma string Apple ausente na extração.
        self.assertEqual(ast.literal_eval(buttons[0].args[0]), "+")
        callback = buttons[0].args[1]
        self.assertIsInstance(callback, ast.Lambda)
        self.assertIsNone(ast.literal_eval(callback.body))


if __name__ == "__main__":
    unittest.main()
