"""Testes de regressão para Reduce Motion (Reduzir Movimento).

Verifica por inspeção de código-fonte (AST/regex, sem abrir janelas):
1. Em shell/hyprmac-ajustes, o interruptor 'Reduce motion' chama
   gsettings set org.gnome.desktop.interface enable-animations e em seguida
   'hyprctl reload' no mesmo comando.
2. Em shell/hyprmac-ajustes, o método _go da classe do slider de vidro
   (GlassKnob) consulta enable-animations e, quando falso, atribui
   self.t = target e retorna antes de agendar add_tick_callback.
3. Em hypr/hyprmac.lua, quando RM é verdadeiro as animações
   workspaces/workspacesIn/workspacesOut usam style = "fade".
"""

import ast
import re
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
AJUSTES = ROOT / "shell/hyprmac-ajustes"
HYPRMAC_LUA = ROOT / "hypr/hyprmac.lua"


class ReduceMotionTests(unittest.TestCase):
    """Testes de inspeção estática para Reduce Motion."""

    def test_reduce_motion_switch_calls_gsettings_and_hyprctl_reload(self):
        """O interruptor 'Reduce motion' deve chamar gsettings set enable-animations
        seguido de hyprctl reload no mesmo comando (encadeados com &&)."""
        source = AJUSTES.read_text()

        # Localiza a linha do switch "Reduce motion" - usa regex para achar o comando spawn
        # O padrão esperado: spawn("gsettings set org.gnome.desktop.interface enable-animations ... && hyprctl reload")
        pattern = r'Reduce motion.*?spawn\([^)]*gsettings set org\.gnome\.desktop\.interface enable-animations[^)]*&&\s*hyprctl reload'
        match = re.search(pattern, source, re.DOTALL)
        self.assertIsNotNone(
            match,
            "O interruptor 'Reduce motion' deve conter comando gsettings set enable-animations "
            "encadeado com hyprctl reload (via &&) no mesmo spawn."
        )

        # Verifica que o comando tem a estrutura correta
        command_text = match.group(0)
        self.assertIn("gsettings set org.gnome.desktop.interface enable-animations", command_text)
        self.assertIn("hyprctl reload", command_text)
        self.assertIn("&&", command_text)

    def test_glass_knob_go_method_checks_enable_animations_and_returns_early(self):
        """O método _go da classe GlassKnob deve consultar enable-animations via
        Gio.Settings e, quando falso, atribuir self.t = target e retornar antes
        de chamar add_tick_callback."""
        source = AJUSTES.read_text()

        # Parseia o AST para encontrar a classe GlassKnob e seu método _go
        tree = ast.parse(source)

        glass_knob_class = None
        for node in tree.body:
            if isinstance(node, ast.ClassDef) and node.name == "GlassKnob":
                glass_knob_class = node
                break

        self.assertIsNotNone(glass_knob_class, "Classe GlassKnob não encontrada em hyprmac-ajustes")

        go_method = None
        for node in glass_knob_class.body:
            if isinstance(node, ast.FunctionDef) and node.name == "_go":
                go_method = node
                break

        self.assertIsNotNone(go_method, "Método _go não encontrado na classe GlassKnob")

        # Converte o método _go para código fonte para inspeção
        go_source = ast.get_source_segment(source, go_method)
        self.assertIsNotNone(go_source, "Não foi possível extrair o código do método _go")

        # Verifica que há a verificação de enable-animations via Gio.Settings
        self.assertIn(
            'Gio.Settings.new("org.gnome.desktop.interface").get_boolean("enable-animations")',
            go_source,
            "O método _go deve consultar enable-animations via Gio.Settings"
        )

        # Verifica que quando enable-animations é falso, atribui self.t = target e retorna
        # O padrão: if not Gio.Settings...: self.t = target; ...; return
        self.assertIn("self.t = target", go_source)
        self.assertIn("return", go_source)

        # Verifica que add_tick_callback NÃO é chamado quando enable-animations é falso
        # (o return deve vir antes)
        # Encontra a posição do return e do add_tick_callback
        return_pos = go_source.find("return")
        tick_pos = go_source.find("add_tick_callback")

        self.assertNotEqual(return_pos, -1, "Deve haver um return no método _go")
        self.assertNotEqual(tick_pos, -1, "Deve haver add_tick_callback no método _go")

        # O return (do early exit) deve aparecer antes do add_tick_callback
        # Encontra o primeiro return que está dentro do bloco if not enable-animations
        # Procuramos pelo padrão: if not ...get_boolean("enable-animations"): ... self.t = target ... return
        early_return_pattern = (
            r'if not Gio\.Settings\.new\("org\.gnome\.desktop\.interface"\)'
            r'\.get_boolean\("enable-animations"\):.*?self\.t = target.*?return'
        )
        early_match = re.search(early_return_pattern, go_source, re.DOTALL)
        self.assertIsNotNone(
            early_match,
            "Deve haver um return antecipado (early return) após self.t = target "
            "quando enable-animations é falso, antes de add_tick_callback"
        )

    def test_hyprmac_lua_workspaces_animations_use_fade_when_rm_true(self):
        """Quando RM (reduce_motion) é verdadeiro, as animações workspaces,
        workspacesIn e workspacesOut devem usar style = 'fade'."""
        source = HYPRMAC_LUA.read_text()

        # Verifica que existe a função reduce_motion e a variável RM
        self.assertIn("reduce_motion", source)
        self.assertIn("local RM = reduce_motion()", source)

        # Verifica que há um bloco if RM then que redefine as animações de workspaces
        # com style = "fade"
        rm_block_pattern = r'if RM then.*?workspaces.*?style = "fade".*?workspacesIn.*?style = "fade".*?workspacesOut.*?style = "fade"'
        match = re.search(rm_block_pattern, source, re.DOTALL)
        self.assertIsNotNone(
            match,
            "Quando RM é verdadeiro, deve haver redefinição das animações "
            "workspaces/workspacesIn/workspacesOut com style = 'fade'"
        )

        # Verifica cada animação individualmente dentro do bloco if RM
        rm_block = match.group(0)
        self.assertIn('leaf = "workspaces"', rm_block)
        self.assertIn('leaf = "workspacesIn"', rm_block)
        self.assertIn('leaf = "workspacesOut"', rm_block)
        self.assertIn('style = "fade"', rm_block)

        # Conta quantas vezes "style = \"fade\"" aparece no bloco RM para workspaces
        fade_count = rm_block.count('style = "fade"')
        self.assertGreaterEqual(
            fade_count, 3,
            "Espera-se pelo menos 3 ocorrências de style = 'fade' no bloco RM "
            "(workspaces, workspacesIn, workspacesOut)"
        )

    def test_hyprmac_lua_workspaces_default_uses_slide(self):
        """Verifica que o padrão (sem RM) usa style = 'slide' para workspaces."""
        source = HYPRMAC_LUA.read_text()

        # As animações padrão (antes do if RM) devem usar style = "slide"
        default_workspaces = re.search(
            r'hl\.animation\(\{ leaf = "workspaces".*?style = "slide" \}',
            source,
            re.DOTALL
        )
        self.assertIsNotNone(default_workspaces, "Animação padrão workspaces deve usar style = 'slide'")

        default_workspaces_in = re.search(
            r'hl\.animation\(\{ leaf = "workspacesIn".*?style = "slide" \}',
            source,
            re.DOTALL
        )
        self.assertIsNotNone(default_workspaces_in, "Animação padrão workspacesIn deve usar style = 'slide'")

        default_workspaces_out = re.search(
            r'hl\.animation\(\{ leaf = "workspacesOut".*?style = "slide" \}',
            source,
            re.DOTALL
        )
        self.assertIsNotNone(default_workspaces_out, "Animação padrão workspacesOut deve usar style = 'slide'")


if __name__ == "__main__":
    unittest.main()