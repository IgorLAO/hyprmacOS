"""Testes unitários para a lógica do shell/hyprmac-preview sem abrir janelas GTK."""
import importlib.machinery
import importlib.util
import sys
import unittest
from pathlib import Path
from unittest.mock import Mock, patch

ROOT = Path(__file__).resolve().parents[1]


def load_preview_module():
    """Carrega o módulo preview sem extensão .py usando SourceFileLoader."""
    loader = importlib.machinery.SourceFileLoader('preview', str(ROOT / 'shell/hyprmac-preview'))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


class PreviewLogicTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.preview_module = load_preview_module()
        cls.Preview = cls.preview_module.Preview

    def setUp(self):
        """Cria instância Preview sem chamar __init__ e preenche atributos com Mocks."""
        self.preview = self.Preview.__new__(self.Preview)
        
        # Atributos básicos
        self.preview.document = None
        self.preview.image = None
        self.preview.path = None
        self.preview.page = 0
        self.preview.rotation = 0
        self.preview.zoom = 1.0
        self.preview.auto_fit = True
        self.preview.thumbnail_job = None
        
        # Mocks para widgets GTK
        self.preview.title_sub = Mock()
        self.preview.thumbnails = Mock()
        self.preview.canvas = Mock()
        self.preview.scroll = Mock()
        self.preview.rotate_button = Mock()
        self.preview.inspector_button = Mock()
        self.preview.sidebar_button = Mock()
        self.preview.window = Mock()
        self.preview.sidebar = Mock()
        self.preview.title_name = Mock()
        self.preview.header = Mock()

    def test_set_zoom_manual_disables_auto_fit_and_clamps(self):
        """set_zoom com manual=True desliga auto_fit e limita zoom entre 0.1 e 4.0."""
        # Teste limite inferior
        self.preview.set_zoom(0.05, manual=True)
        self.assertFalse(self.preview.auto_fit)
        self.assertAlmostEqual(self.preview.zoom, 0.1)
        
        # Teste limite superior
        self.preview.set_zoom(5.0, manual=True)
        self.assertFalse(self.preview.auto_fit)
        self.assertAlmostEqual(self.preview.zoom, 4.0)
        
        # Teste valor normal
        self.preview.set_zoom(1.5, manual=True)
        self.assertFalse(self.preview.auto_fit)
        self.assertAlmostEqual(self.preview.zoom, 1.5)

    def test_set_zoom_auto_keeps_auto_fit(self):
        """set_zoom com manual=False mantém auto_fit ativo."""
        self.preview.auto_fit = True
        self.preview.set_zoom(2.0, manual=False)
        self.assertTrue(self.preview.auto_fit)
        self.assertAlmostEqual(self.preview.zoom, 2.0)

    def test_key_press_page_down_right_advances_page(self):
        """key_press com Page_Down/Right avança página e retorna True."""
        # Configura documento mock com 3 páginas
        mock_doc = Mock()
        mock_doc.get_n_pages.return_value = 3
        mock_page = Mock()
        mock_page.get_size.return_value = (600, 800)
        mock_doc.get_page.return_value = mock_page
        self.preview.document = mock_doc
        self.preview.page = 0
        
        # Mock para Gdk.KEY_Page_Down
        with patch('gi.repository.Gdk.KEY_Page_Down', 65366), \
             patch('gi.repository.Gdk.KEY_Right', 65363), \
             patch('gi.repository.Gdk.KEY_Down', 65364):
            
            event = Mock()
            event.keyval = 65366  # Gdk.KEY_Page_Down
            result = self.preview.key_press(None, event)
            self.assertTrue(result)
            self.assertEqual(self.preview.page, 1)
            
            event.keyval = 65363  # Gdk.KEY_Right
            result = self.preview.key_press(None, event)
            self.assertTrue(result)
            self.assertEqual(self.preview.page, 2)
            
            event.keyval = 65364  # Gdk.KEY_Down
            result = self.preview.key_press(None, event)
            self.assertTrue(result)
            self.assertEqual(self.preview.page, 2)  # Não avança além da última (página 2 é a última)

    def test_key_press_page_up_left_goes_back(self):
        """key_press com Page_Up/Left volta página e retorna True."""
        mock_doc = Mock()
        mock_doc.get_n_pages.return_value = 3
        mock_page = Mock()
        mock_page.get_size.return_value = (600, 800)
        mock_doc.get_page.return_value = mock_page
        self.preview.document = mock_doc
        self.preview.page = 2
        
        with patch('gi.repository.Gdk.KEY_Page_Up', 65365), \
             patch('gi.repository.Gdk.KEY_Left', 65361), \
             patch('gi.repository.Gdk.KEY_Up', 65362):
            
            event = Mock()
            event.keyval = 65365  # Gdk.KEY_Page_Up
            result = self.preview.key_press(None, event)
            self.assertTrue(result)
            self.assertEqual(self.preview.page, 1)
            
            event.keyval = 65361  # Gdk.KEY_Left
            result = self.preview.key_press(None, event)
            self.assertTrue(result)
            self.assertEqual(self.preview.page, 0)
            
            event.keyval = 65362  # Gdk.KEY_Up
            result = self.preview.key_press(None, event)
            self.assertTrue(result)
            self.assertEqual(self.preview.page, 0)  # Não volta antes da primeira

    def test_key_press_other_key_returns_false(self):
        """key_press com outra tecla retorna False."""
        mock_doc = Mock()
        mock_doc.get_n_pages.return_value = 3
        self.preview.document = mock_doc
        self.preview.page = 1
        
        event = Mock()
        event.keyval = 65307  # Escape
        result = self.preview.key_press(None, event)
        self.assertFalse(result)
        self.assertEqual(self.preview.page, 1)  # Página não muda

    def test_key_press_no_document_returns_false(self):
        """key_press sem documento retorna False."""
        self.preview.document = None
        event = Mock()
        event.keyval = 65366  # Page_Down
        result = self.preview.key_press(None, event)
        self.assertFalse(result)

    def test_update_pdf_shows_page_of_count(self):
        """update escreve 'Page 2 of 3' em title_sub para PDF de 3 páginas na página 1."""
        mock_doc = Mock()
        mock_doc.get_n_pages.return_value = 3
        mock_page = Mock()
        mock_page.get_size.return_value = (600, 800)
        mock_doc.get_page.return_value = mock_page
        
        self.preview.document = mock_doc
        self.preview.image = None
        self.preview.path = Mock()
        self.preview.path.name = "test.pdf"
        self.preview.page = 1  # Segunda página (índice 1)
        self.preview.rotation = 0
        self.preview.zoom = 1.0
        
        self.preview.update()
        
        self.preview.title_sub.set_text.assert_called_with("Page 2 of 3")

    def test_update_image_shows_dimensions(self):
        """update escreve 'W × H pixels' em title_sub para imagem."""
        mock_image = Mock()
        mock_image.get_width.return_value = 1920
        mock_image.get_height.return_value = 1080
        
        self.preview.document = None
        self.preview.image = mock_image
        self.preview.path = Mock()
        self.preview.path.name = "test.png"
        
        self.preview.update()
        
        self.preview.title_sub.set_text.assert_called_with("1920 × 1080 pixels")

    def test_update_no_document_no_image_clears_title(self):
        """update limpa title_sub quando não há documento nem imagem."""
        self.preview.document = None
        self.preview.image = None
        self.preview.path = None
        
        self.preview.update()
        
        self.preview.title_sub.set_text.assert_called_with("")

    def test_update_rotated_dimensions(self):
        """update usa dimensões rotacionadas quando rotation é ímpar."""
        mock_doc = Mock()
        mock_doc.get_n_pages.return_value = 1
        mock_page = Mock()
        mock_page.get_size.return_value = (600, 800)
        mock_doc.get_page.return_value = mock_page
        
        self.preview.document = mock_doc
        self.preview.image = None
        self.preview.path = Mock()
        self.preview.path.name = "test.pdf"
        self.preview.page = 0
        self.preview.rotation = 1  # 90 graus
        self.preview.zoom = 1.0
        
        self.preview.update()
        
        # Verifica que canvas.set_size_request foi chamado com dimensões trocadas
        # width=800, height=600 (rotacionado)
        self.preview.canvas.set_size_request.assert_called()
        args = self.preview.canvas.set_size_request.call_args[0]
        self.assertEqual(args[0], 800)  # width rotacionado
        self.assertEqual(args[1], 600)  # height rotacionado


if __name__ == '__main__':
    unittest.main()