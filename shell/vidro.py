"""Liquid Glass do hyprmac (plugin hyprglass) para janelas GTK.

O vidro é desenhado pelo compositor; a janela GTK só precisa ser transparente onde o
vidro deve aparecer. Este módulo pede o efeito ao Hyprland via `hyprctl eval`.

    import vidro
    vidro.garantir()                                    # carrega o plugin se preciso
    vidro.janela("dev.hyprmac.Algo", preset="pomme")    # preset embutido ou da config
    vidro.config(refraction_strength=1.4)               # opções globais, valem na hora

Ao vivo só valem `config` (globais), presets embutidos e tags de janela: presets próprios
e camadas layer-shell só entram quando o Hyprland relê a config (ver a doc).
Tudo vale até o Hyprland reiniciar. Doc: BaseConhecimento/padroes/liquid-glass-hyprland.md
"""

import re
import subprocess

VIDRO = __file__.rsplit("/shell/", 1)[0] + "/scripts/vidro"


def _eval(lua_codigo):
    out = subprocess.run(["hyprctl", "eval", lua_codigo], capture_output=True, text=True).stdout
    if out.strip() != "ok":
        raise RuntimeError(f"hyprctl eval falhou: {out.strip()}\n{lua_codigo}")


def lua(valor):
    """Converte valor Python em literal Lua (dict vira tabela; "#RRGGBBAA" vira 0xRRGGBBAA)."""
    if isinstance(valor, bool):
        return "true" if valor else "false"
    if isinstance(valor, (int, float)):
        return repr(valor)
    if isinstance(valor, str) and re.fullmatch(r"#[0-9A-Fa-f]{8}", valor):
        return "0x" + valor[1:].upper()
    if isinstance(valor, str):
        return '"' + valor.replace("\\", "\\\\").replace('"', '\\"') + '"'
    if isinstance(valor, dict):
        return "{" + ", ".join(f"{k}={lua(v)}" for k, v in valor.items()) + "}"
    raise TypeError(f"sem conversão Lua para {valor!r}")


def carregado():
    out = subprocess.run(["hyprctl", "plugin", "list"], capture_output=True, text=True).stdout
    return "Plugin hyprglass" in out


def garantir():
    """Carrega o plugin (compila na primeira vez), desligado no resto do sistema."""
    if not carregado():
        subprocess.run([VIDRO, "carregar"], check=True)


def config(**opcoes):
    """Opções globais do plugin: valem na hora para toda janela com vidro sem preset."""
    _eval(f"hl.plugin.hyprglass.config({lua(opcoes)})")


def regra(classe, **campos):
    """Regra de janela do Hyprland para a classe (app_id) literal `classe`."""
    nome = campos.pop("name", "regra-" + re.sub(r"[^a-z0-9]+", "-", classe.lower()))
    corpo = {"name": nome, "match": {"class": "^" + re.escape(classe) + "$"}, **campos}
    _eval(f"hl.window_rule({lua(corpo)})")


def janela(classe, preset=None, tema=None):
    """Liga o vidro nas janelas da classe (app_id). Canto e contorno vêm do Hyprland."""
    base = "vidro-" + re.sub(r"[^a-z0-9]+", "-", classe.lower())
    tags = ["hyprglass_enabled"]
    if preset:
        tags.append("hyprglass_preset_" + preset)
    if tema:
        tags.append("hyprglass_theme_" + tema)
    for tag in tags:  # uma regra por tag: o campo `tag` aceita uma só
        regra(classe, name=f"{base}-{tag}", tag="+" + tag)
