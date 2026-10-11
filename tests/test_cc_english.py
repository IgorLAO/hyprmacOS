"""Central de Controle e nomes de apps em inglês, como os menus (strings do ControlCenter 26.6.1)."""
from pathlib import Path
import re
import unittest

SHELL = (Path(__file__).resolve().parents[1] / "shell" / "hyprmac-shell").read_text(encoding="utf-8")
PT = ("Rede", "Tela", "Som", "Arquivos", "Ligado", "Desligado", "Microfone", "Modo Escuro",
      "Não Perturbe", "Flutuar", "Cheia", "Tocando", "Configurações", "Sobre", "Capturar",
      "Notificação", "Limpar", "agora", "Nenhuma")


class CCEnglishTests(unittest.TestCase):
    def portugues(self, textos):
        return [t for t in textos if any(re.search(rf"\b{re.escape(p)}\b", t) for p in PT)]

    def test_titulos_de_toggle_e_slider(self):
        titulos = re.findall(r'(?:Toggle|SliderTile)\(\s*I\[[^\]]+\],\s*"([^"]+)"', SHELL)
        titulos += re.findall(r'SliderTile\(\s*"([^"]+)"', SHELL)
        self.assertGreater(len(titulos), 5)
        self.assertEqual(self.portugues(titulos), [])

    def test_nomes_de_apps(self):
        bloco = SHELL[SHELL.index("APP_NAMES = {"):SHELL.index("}", SHELL.index("APP_NAMES = {"))]
        valores = re.findall(r':\s*"([^"]+)"', bloco)
        self.assertEqual(self.portugues(valores), [])

    def test_central_de_notificacoes(self):
        ini = SHELL.index("class NotifPanel")
        bloco = SHELL[ini:SHELL.index("\nclass ", ini + 10)]
        textos = re.findall(r'label\(\s*"([^"]+)"', bloco)
        self.assertIn("Clear All", textos)
        self.assertIn("No notifications available", textos)
        self.assertEqual(self.portugues(textos), [])

    def test_todos_os_textos_de_interface_do_shell(self):
        pat = re.compile(r'(label\(|label=|title=|set_title\(|set_tooltip_text\(|set_placeholder_text\('
                         r'|text=|add_button\(|format_secondary_text\(|set_text\(|Gtk\.Label\()\s*f?"([^"]{2,})"')
        # palavras curtas só em minúscula ("Do you…" é inglês); as longas em qualquer caixa
        pt = re.compile(r"[áàâãçéêíóôõú]|\b(de|do|da|para|com)\b|(?i:\b(senha|abrir|fechar|salvar|cancelar|"
                        r"nada|buscar|limpar|janela|aplicativo|encerrar|conectar|lembrar)\b)")
        achados = []
        for n, linha in enumerate(SHELL.split("\n"), 1):
            if linha.strip().startswith("#"):
                continue
            achados += [f"{n}: {m.group(2)}" for m in pat.finditer(linha) if pt.search(m.group(2))]
        self.assertEqual(achados, [])


if __name__ == "__main__":
    unittest.main()
