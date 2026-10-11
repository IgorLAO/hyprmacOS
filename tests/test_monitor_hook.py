"""Monitor que volta do sono profundo: o shell agenda um único reload 3 s após o último monitoradded."""
from pathlib import Path
import textwrap
import unittest
from unittest import mock

SHELL = (Path(__file__).resolve().parents[1] / "shell" / "hyprmac-shell").read_text(encoding="utf-8")


def carregar_handler(glib, subprocess):
    ini = SHELL.index("    _volta = {")
    fim = SHELL.index("    hypr_events(_monitor_voltou)")
    ns = {"GLib": glib, "subprocess": subprocess, "os": __import__("os"), "__file__": "/x/hyprmac-shell"}
    exec(textwrap.dedent(SHELL[ini:fim]), ns)
    return ns["_monitor_voltou"], ns["_volta"]


class MonitorHookTests(unittest.TestCase):
    def setUp(self):
        self.glib = mock.Mock()
        self.ids = iter(range(1, 100))
        self.glib.timeout_add_seconds.side_effect = lambda s, fn: next(self.ids)
        self.sub = mock.Mock()
        self.handler, self.estado = carregar_handler(self.glib, self.sub)

    def test_inscrito_nos_eventos(self):
        self.assertIn("hypr_events(_monitor_voltou)", SHELL)

    def test_outros_eventos_nao_agendam(self):
        self.handler("monitorremoved>>HDMI-A-2")
        self.handler("monitoraddedv2>>1,HDMI-A-2,x")
        self.glib.timeout_add_seconds.assert_not_called()

    def test_dois_eventos_deixam_um_agendamento(self):
        self.handler("monitoradded>>HDMI-A-1")
        self.handler("monitoradded>>HDMI-A-2")
        self.assertEqual(self.glib.timeout_add_seconds.call_count, 2)
        self.glib.source_remove.assert_called_once_with(1)
        self.assertEqual(self.estado["id"], 2)
        self.assertEqual(self.glib.timeout_add_seconds.call_args[0][0], 3)

    def test_recarregar_chama_reload(self):
        self.handler("monitoradded>>HDMI-A-1")
        recarregar = self.glib.timeout_add_seconds.call_args[0][1]
        self.assertFalse(recarregar())
        args = self.sub.Popen.call_args[0][0]
        self.assertEqual(args[-1], "reload")
        self.assertIsNone(self.estado["id"])


if __name__ == "__main__":
    unittest.main()
