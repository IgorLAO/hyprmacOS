"""Tests for shell/hyprmac-fotos pure functions: get_media_files, get_albums, load_favoritos/save_favoritos."""
import importlib.machinery
import importlib.util
import os
import sys
import tempfile
import time
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]

def carregar_app():
    loader = importlib.machinery.SourceFileLoader("hyprmac_fotos", str(ROOT / "shell" / "hyprmac-fotos"))
    spec = importlib.util.spec_from_loader("hyprmac_fotos", loader)
    mod = importlib.util.module_from_spec(spec)
    loader.exec_module(mod)
    return mod


def touch(path, mtime=None):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "wb") as f:
        f.write(b"")
    if mtime is not None:
        os.utime(path, (mtime, mtime))


class PhotosLibraryTests(unittest.TestCase):
    def setUp(self):
        self.mod = carregar_app()
        self.tmp = tempfile.mkdtemp()
        self.pics = os.path.join(self.tmp, "Pictures")
        os.makedirs(self.pics, exist_ok=True)

        # estrutura base
        # arquivos na raiz
        touch(os.path.join(self.pics, "a.jpg"), mtime=100)
        touch(os.path.join(self.pics, "B.PNG"), mtime=200)
        touch(os.path.join(self.pics, "video.MP4"), mtime=150)
        touch(os.path.join(self.pics, "ignore.txt"), mtime=300)
        touch(os.path.join(self.pics, ".hidden.jpg"), mtime=400)

        # pasta oculta
        hidden_dir = os.path.join(self.pics, ".hidden_dir")
        os.makedirs(hidden_dir, exist_ok=True)
        touch(os.path.join(hidden_dir, "secret.jpg"), mtime=500)

        # álbum 1 com subpasta
        album1 = os.path.join(self.pics, "album1")
        os.makedirs(album1, exist_ok=True)
        touch(os.path.join(album1, "img1.jpg"), mtime=300)
        touch(os.path.join(album1, "img2.jpeg"), mtime=250)
        touch(os.path.join(album1, ".hidden.jpg"), mtime=600)
        subalbum = os.path.join(album1, "subalbum")
        os.makedirs(subalbum, exist_ok=True)
        touch(os.path.join(subalbum, "deep.png"), mtime=400)

        # álbum 2 vazio
        album2 = os.path.join(self.pics, "album2")
        os.makedirs(album2, exist_ok=True)

        # álbum oculto
        hidden_album = os.path.join(self.pics, ".hidden_album")
        os.makedirs(hidden_album, exist_ok=True)
        touch(os.path.join(hidden_album, "x.jpg"), mtime=700)

        self.album1_path = album1
        self.album2_path = album2

        # favoritos: sobrescrever caminho para temp
        self.fav_path = os.path.join(self.tmp, "fotos.json")
        self.mod.FAVORITOS_PATH = self.fav_path

    def test_get_media_files_filtro_extensao_maiusculas_recursao_ordem(self):
        files = self.mod.get_media_files(self.pics)
        # nomes esperados (sem ocultos, sem txt)
        expected_names = {
            "a.jpg": 100,
            "B.PNG": 200,
            "video.MP4": 150,
            "img1.jpg": 300,
            "img2.jpeg": 250,
            "deep.png": 400,
        }
        # verifica presença
        found = {}
        for p in files:
            name = os.path.basename(p)
            if name in expected_names:
                found[name] = p
        self.assertEqual(set(found.keys()), set(expected_names.keys()))
        # verifica ordem por mtime desc
        mtimes = []
        for p in files:
            name = os.path.basename(p)
            if name in expected_names:
                mtimes.append(os.path.getmtime(p))
        # deve estar decrescente
        self.assertEqual(mtimes, sorted(mtimes, reverse=True))
        # ordem específica dos esperados
        ordered_names = [os.path.basename(p) for p in files if os.path.basename(p) in expected_names]
        self.assertEqual(ordered_names, ["deep.png", "img1.jpg", "img2.jpeg", "B.PNG", "video.MP4", "a.jpg"])

    def test_get_media_files_ignora_ocultos(self):
        files = self.mod.get_media_files(self.pics)
        basenames = [os.path.basename(p) for p in files]
        # arquivos ocultos não devem aparecer
        self.assertNotIn(".hidden.jpg", basenames)
        self.assertNotIn("secret.jpg", basenames)
        self.assertNotIn("x.jpg", basenames)
        # .hidden.jpg na raiz e dentro de album1
        for p in files:
            self.assertFalse(os.path.basename(p).startswith("."))
            self.assertFalse(os.path.basename(os.path.dirname(p)).startswith("."))
        # ignore.txt não deve aparecer
        self.assertNotIn("ignore.txt", basenames)

    def test_get_media_files_dir_inexistente(self):
        files = self.mod.get_media_files(os.path.join(self.tmp, "nao_existe"))
        self.assertEqual(files, [])

    def test_get_albums_subpastas_diretas(self):
        albums = self.mod.get_albums(self.pics)
        # deve retornar apenas subpastas diretas não ocultas
        names = [a[0] for a in albums]
        paths = [a[1] for a in albums]
        self.assertIn("album1", names)
        self.assertIn("album2", names)
        self.assertNotIn(".hidden_album", names)
        # verifica caminho
        self.assertIn(self.album1_path, paths)
        self.assertIn(self.album2_path, paths)
        # álbum1 deve ter mídia (recursivo)
        album1_entry = next(a for a in albums if a[0] == "album1")
        # thumb pode ser None por arquivo vazio, mas nome e path corretos
        self.assertEqual(album1_entry[1], self.album1_path)
        # álbum2 vazio
        album2_entry = next(a for a in albums if a[0] == "album2")
        self.assertEqual(album2_entry[1], self.album2_path)

    def test_favoritos_ida_e_volta(self):
        favs = {"/path/a.jpg", "/path/b.png"}
        self.mod.save_favoritos(favs)
        loaded = self.mod.load_favoritos()
        self.assertEqual(loaded, favs)

    def test_favoritos_arquivo_ausente(self):
        # garante arquivo não existe
        if os.path.exists(self.fav_path):
            os.remove(self.fav_path)
        loaded = self.mod.load_favoritos()
        self.assertEqual(loaded, set())

    def test_favoritos_arquivo_corrompido(self):
        with open(self.fav_path, "w") as f:
            f.write("{ invalid json")
        loaded = self.mod.load_favoritos()
        self.assertEqual(loaded, set())

    def test_favoritos_persiste_vazio(self):
        self.mod.save_favoritos(set())
        loaded = self.mod.load_favoritos()
        self.assertEqual(loaded, set())
        self.assertTrue(os.path.exists(self.fav_path))
        with open(self.fav_path, "r") as f:
            import json
            data = json.load(f)
            self.assertEqual(data, {"favoritos": []})


if __name__ == "__main__":
    unittest.main()
