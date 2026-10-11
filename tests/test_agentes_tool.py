"""Tests for BaseConhecimento/ferramentas/agentes.py without network."""
import importlib.util
import json
import os
import tempfile
import unittest
from unittest import mock

# Import agentes via importlib to avoid side effects and path issues
AGENTES_PATH = "/home/igor/Projects/hyprmac/BaseConhecimento/ferramentas/agentes.py"
spec = importlib.util.spec_from_file_location("agentes", AGENTES_PATH)
agentes = importlib.util.module_from_spec(spec)
spec.loader.exec_module(agentes)


class AgentesToolTests(unittest.TestCase):
    def test_contexto_faixa_numera_linhas_corretas(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "sample.txt")
            with open(path, "w", encoding="utf-8") as f:
                f.write("line1\nline2\nline3\nline4\nline5")
            original_raiz = agentes.RAIZ
            agentes.RAIZ = tmp
            try:
                out = agentes.contexto(["sample.txt:2-3"])
                self.assertIn("### sample.txt:2-3", out)
                self.assertIn("2\tline2", out)
                self.assertIn("3\tline3", out)
                self.assertNotIn("1\tline1", out)
                self.assertNotIn("4\tline4", out)
            finally:
                agentes.RAIZ = original_raiz

    def test_contexto_limite_caracteres_sistema_exit(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "big.txt")
            # 70k chars > LIMITE_CONTEXTO 60_000
            with open(path, "w", encoding="utf-8") as f:
                f.write("a" * 70000)
            original_raiz = agentes.RAIZ
            agentes.RAIZ = tmp
            try:
                with self.assertRaises(SystemExit) as cm:
                    agentes.contexto(["big.txt"])
                self.assertIn("excede", str(cm.exception))
            finally:
                agentes.RAIZ = original_raiz

    def test_rodar_reusa_cache_quando_hash_igual(self):
        with tempfile.TemporaryDirectory() as tmp:
            original_dir = agentes.DIR
            agentes.DIR = tmp
            try:
                tid = "cache-test"
                papel = "pesquisa"
                tarefa = "tarefa teste"
                modelo = "test-model"
                especs = []
                criterios = ""

                # Compute hash exactly as rodar does
                ctx = ""  # contexto([]) -> ""
                usuario = f"## Tarefa {tid}\n{tarefa}\n"
                msgs = [
                    {"role": "system", "content": agentes.PAPEIS[papel]},
                    {"role": "user", "content": usuario},
                ]
                import hashlib
                h = hashlib.sha256(
                    json.dumps([modelo, msgs], ensure_ascii=False).encode()
                ).hexdigest()[:16]

                pasta = os.path.join(tmp, tid)
                os.makedirs(pasta, exist_ok=True)
                meta_path = os.path.join(pasta, "meta.json")
                meta = {
                    "id": tid,
                    "papel": papel,
                    "modelo_pedido": modelo,
                    "hash": h,
                    "contexto": [],
                    "inicio": "2020-01-01T00:00:00",
                    "estado": "respondido",
                    "tentativas": 0,
                }
                with open(meta_path, "w", encoding="utf-8") as f:
                    json.dump(meta, f)

                with mock.patch.object(agentes, "http") as mock_http:
                    mock_http.side_effect = Exception("http should not be called")
                    result = agentes.rodar(tid, papel, tarefa, especs, modelo, criterios)
                    self.assertTrue(result.get("cache"), "cache flag should be True")
                    mock_http.assert_not_called()
            finally:
                agentes.DIR = original_dir


if __name__ == "__main__":
    unittest.main()
