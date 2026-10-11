"""Lógica e renderização de marcação, sem criar janelas GTK."""
import importlib.machinery
import importlib.util
from pathlib import Path
import tempfile
import unittest
from unittest.mock import Mock

import cairo


def load_preview():
    path = Path(__file__).resolve().parents[1] / "shell/hyprmac-preview"
    loader = importlib.machinery.SourceFileLoader("preview_markup", str(path))
    spec = importlib.util.spec_from_loader(loader.name, loader)
    module = importlib.util.module_from_spec(spec)
    loader.exec_module(module)
    return module


preview = load_preview()
Gdk, GdkPixbuf = preview.Gdk, preview.GdkPixbuf


class PreviewMarkupTests(unittest.TestCase):
    def test_annotations_capture_style_and_copy_points(self):
        model = preview.MarkupModel()
        points = [(10, 20), (30, 40)]
        annotation = model.add("sketch", points, "#007AFF", 8)
        points.append((50, 60))
        self.assertEqual(annotation, dict(tool="sketch", points=[(10, 20), (30, 40)],
                                          color="#007AFF", width=8, text=""))
        self.assertEqual(model.annotations, [annotation])
        with self.assertRaises(ValueError):
            model.add("unknown", [])

    def test_undo_removes_last_annotation(self):
        model = preview.MarkupModel()
        first = model.add("rectangle", [(0, 0), (20, 20)])
        last = model.add("text", [(5, 10)], text="Hello")
        self.assertEqual(model.undo(), last)
        self.assertEqual(model.annotations, [first])
        self.assertEqual(model.undo(), first)
        self.assertIsNone(model.undo())

    def test_coordinates_invert_canvas_transform_at_every_rotation_and_zoom(self):
        for rotation in range(4):
            for zoom in (0.1, 0.5, 1, 2, 4):
                context = cairo.Context(cairo.ImageSurface(cairo.FORMAT_ARGB32, 1, 1))
                preview.image_transform(context, 320, 180, zoom, rotation)
                for point in ((0, 0), (23, 47), (320, 180)):
                    screen = context.user_to_device(*point)
                    result = preview.screen_to_image(*screen, 320, 180, zoom, rotation)
                    for actual, expected in zip(result, point):
                        self.assertAlmostEqual(actual, expected)

    def test_output_name_handles_collisions_and_marked_original(self):
        with tempfile.TemporaryDirectory() as directory:
            original = Path(directory) / "photo.jpg"
            original.write_bytes(b"original")
            output = preview.markup_output_path(original)
            self.assertEqual(output.name, "photo (marcado).png")
            output.write_bytes(b"existing")
            self.assertEqual(preview.markup_output_path(original).name, "photo (marcado 2).png")
            self.assertNotEqual(preview.markup_output_path(output), output)
            self.assertEqual(original.read_bytes(), b"original")
            self.assertEqual(output.read_bytes(), b"existing")

    def test_every_tool_draws_on_cairo_surface_and_preserves_transform(self):
        for tool in ("sketch", "rectangle", "oval", "arrow", "text"):
            with self.subTest(tool=tool):
                surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 120, 100)
                context = cairo.Context(surface)
                model = preview.MarkupModel()
                model.add(tool, [(15, 35), (90, 75)], text="Hello")
                matrix = tuple(context.get_matrix())
                model.draw(context)
                surface.flush()
                self.assertTrue(any(surface.get_data()))
                self.assertEqual(tuple(context.get_matrix()), matrix)

    def make_app(self, path):
        app = preview.Preview.__new__(preview.Preview)
        app.document = None
        app.path = path
        app.image = GdkPixbuf.Pixbuf.new(GdkPixbuf.Colorspace.RGB, True, 8, 80, 50)
        app.image.fill(0x00000000)
        app.rotation = 0
        app.zoom = 2
        app.markup = preview.MarkupModel()
        app.pending_annotation = None
        app.markup_tool = "rectangle"
        app.markup_color = "#FF3B30"
        app.markup_width = 4
        app.markup_button = Mock()
        app.markup_button.get_active.return_value = True
        app.canvas = Mock()
        app.title_sub = Mock()
        return app

    def test_drag_uses_image_coordinates_and_retains_only_final_shape_endpoint(self):
        app = self.make_app(Path("photo.png"))
        self.assertTrue(app.markup_press(None, Mock(button=1, x=20, y=20)))
        app.markup_motion(None, Mock(x=60, y=40))
        self.assertTrue(app.markup_release(None, Mock(button=1, x=100, y=60)))
        self.assertEqual(app.markup.annotations[0]["points"], [(10, 10), (50, 30)])
        self.assertIsNone(app.pending_annotation)
        app.undo_markup()
        self.assertEqual(app.markup.annotations, [])

    def test_drag_clamps_to_image_and_disabled_markup_ignores_input(self):
        app = self.make_app(Path("photo.png"))
        self.assertFalse(app.markup_press(None, Mock(button=1, x=-1, y=20)))
        app.markup_press(None, Mock(button=1, x=20, y=20))
        app.markup_release(None, Mock(button=1, x=1000, y=1000))
        self.assertEqual(app.markup.annotations[0]["points"][-1], (80, 50))
        app.markup_button.get_active.return_value = False
        self.assertFalse(app.markup_press(None, Mock(button=1, x=20, y=20)))

    def test_sketch_click_draws_a_dot_and_pending_stroke_is_not_committed(self):
        app = self.make_app(Path("photo.png"))
        app.markup_tool = "sketch"
        app.markup_press(None, Mock(button=1, x=20, y=20))
        surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, 80, 50)
        app.markup.draw(cairo.Context(surface), app.pending_annotation)
        surface.flush()
        self.assertTrue(any(surface.get_data()))
        self.assertEqual(app.markup.annotations, [])
        app.markup_release(None, Mock(button=1, x=20, y=20))
        self.assertEqual(app.markup.annotations[0]["points"], [(10, 10)])

    def test_save_preserves_original_and_exports_native_rotated_dimensions(self):
        with tempfile.TemporaryDirectory() as directory:
            original = Path(directory) / "photo.png"
            original.write_bytes(b"original content")
            app = self.make_app(original)
            app.markup.add("rectangle", [(10, 10), (40, 30)], "#FF3B30", 4)
            app.rotation = 1
            self.assertTrue(app.save_markup())
            output = original.with_name("photo (marcado).png")
            surface = cairo.ImageSurface.create_from_png(str(output))
            self.assertEqual((surface.get_width(), surface.get_height()), (50, 80))
            self.assertTrue(any(surface.get_data()))
            # Original (10, 20) is rotated to (30, 10); it lies on the red stroke.
            data = bytes(surface.get_data())
            self.assertEqual(data[10 * surface.get_stride() + 30 * 4 + 3], 255)
            self.assertEqual(data[0:4], b"\x00\x00\x00\x00")
            self.assertTrue(app.save_markup())
            self.assertTrue(original.with_name("photo (marcado 2).png").exists())
            self.assertEqual(original.read_bytes(), b"original content")

    def test_shortcuts_accept_control_and_super_for_images_only(self):
        app = self.make_app(Path("photo.png"))
        app.undo_markup = Mock()
        app.save_markup = Mock()
        for modifier in (Gdk.ModifierType.CONTROL_MASK, Gdk.ModifierType.SUPER_MASK):
            self.assertTrue(app.key_press(None, Mock(keyval=Gdk.KEY_z, state=modifier)))
            self.assertTrue(app.key_press(None, Mock(keyval=Gdk.KEY_s, state=modifier)))
        self.assertEqual(app.undo_markup.call_count, 2)
        self.assertEqual(app.save_markup.call_count, 2)
        self.assertFalse(app.key_press(None, Mock(keyval=Gdk.KEY_s, state=0)))
        app.image = None
        self.assertFalse(app.key_press(None, Mock(keyval=Gdk.KEY_s, state=Gdk.ModifierType.CONTROL_MASK)))


if __name__ == "__main__":
    unittest.main()
