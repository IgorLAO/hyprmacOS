"""Local media player panel backed by one GStreamer playbin instance."""

from pathlib import Path

import gi

gi.require_version("Gtk", "3.0")
gi.require_version("GdkPixbuf", "2.0")
gi.require_version("Gst", "1.0")
from gi.repository import GdkPixbuf, Gio, GLib, Gst, Gtk
from tahoe.compatibility.button import TahoeButton


Gst.init(None)


def _clock_time(nanoseconds):
    seconds = max(0, int(nanoseconds // Gst.SECOND))
    return f"{seconds // 3600:02d}:{seconds // 60 % 60:02d}:{seconds % 60:02d}"


class QuickTimePanel(Gtk.Box):
    """Open, play and seek local files; pipeline lives only with this widget."""

    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=10)
        self.pipeline = Gst.ElementFactory.make("playbin", None)
        if self.pipeline is None:
            raise RuntimeError("GStreamer playbin is unavailable")
        self._playing = False
        self._frame_pending = False
        self._source = None
        self._bus = None
        self._bus_handler = None

        # appsink keeps video in this GTK window on Wayland instead of opening a
        # second video-sink window. Limit buffering to one frame.
        sink = Gst.parse_bin_from_description(
            "videoconvert ! video/x-raw,format=RGB ! "
            "appsink name=hyprmac_frames emit-signals=true max-buffers=1 drop=true sync=true",
            True,
        )
        self._video_sink = sink.get_by_name("hyprmac_frames")
        self._video_sink.connect("new-sample", self._new_sample)
        self.pipeline.set_property("video-sink", sink)

        toolbar = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        open_button = TahoeButton(label="Open…")
        open_button.connect("clicked", self._open_dialog)
        toolbar.pack_start(open_button, False, False, 0)
        self.play_button = TahoeButton(label="Play")
        self.play_button.set_sensitive(False)
        self.play_button.connect("clicked", self._toggle_play)
        toolbar.pack_start(self.play_button, False, False, 0)
        self.title = Gtk.Label(label="Open a local audio or video file")
        self.title.set_ellipsize(3)
        self.title.set_halign(Gtk.Align.START)
        toolbar.pack_start(self.title, True, True, 0)
        self.pack_start(toolbar, False, False, 0)

        self.video = Gtk.Image()
        self.video.set_size_request(480, 270)
        self.video.set_vexpand(True)
        self.video.set_hexpand(True)
        self.pack_start(self.video, True, True, 0)

        transport = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=8)
        self.position_label = Gtk.Label(label="00:00:00")
        transport.pack_start(self.position_label, False, False, 0)
        self.seek = Gtk.Scale.new_with_range(Gtk.Orientation.HORIZONTAL, 0, 1, 1)
        self.seek.set_draw_value(False)
        self.seek.set_sensitive(False)
        self.seek.connect("button-release-event", self._seek_to_selection)
        self.seek.connect("key-release-event", self._seek_to_selection)
        transport.pack_start(self.seek, True, True, 0)
        self.duration_label = Gtk.Label(label="00:00:00")
        transport.pack_start(self.duration_label, False, False, 0)
        self.pack_start(transport, False, False, 0)
        self.message = Gtk.Label()
        self.message.set_halign(Gtk.Align.START)
        self.pack_start(self.message, False, False, 0)

        self._bus = self.pipeline.get_bus()
        self._bus.add_signal_watch()
        self._bus_handler = self._bus.connect("message", self._on_message)
        self._source = GLib.timeout_add(250, self._update_position)
        self.connect("destroy", self._destroy)

    def open_file(self, path):
        path = Path(path).expanduser().resolve()
        if not path.is_file():
            raise ValueError("Media file does not exist")
        self.pipeline.set_state(Gst.State.NULL)
        self.pipeline.set_property("uri", Gio.File.new_for_path(str(path)).get_uri())
        self.pipeline.set_state(Gst.State.PLAYING)
        self.title.set_text(path.name)
        self.video.clear()
        self.message.set_text("")
        self.play_button.set_sensitive(True)
        self.play_button.set_label("Pause")
        self._playing = True

    def _open_dialog(self, *_args):
        dialog = Gtk.FileChooserNative.new("Open Media", self.get_toplevel(),
                                          Gtk.FileChooserAction.OPEN, "Open", "Cancel")
        response = dialog.run()
        path = dialog.get_filename() if response == Gtk.ResponseType.ACCEPT else None
        dialog.destroy()
        if path:
            try:
                self.open_file(path)
            except (OSError, ValueError) as error:
                self.message.set_text(str(error))

    def _toggle_play(self, *_args):
        self._playing = not self._playing
        self.pipeline.set_state(Gst.State.PLAYING if self._playing else Gst.State.PAUSED)
        self.play_button.set_label("Pause" if self._playing else "Play")

    def _seek_to_selection(self, *_args):
        position = int(self.seek.get_value() * Gst.SECOND)
        self.pipeline.seek_simple(Gst.Format.TIME,
                                  Gst.SeekFlags.FLUSH | Gst.SeekFlags.KEY_UNIT, position)
        return False

    def _update_position(self):
        if not self.play_button.get_sensitive():
            return True
        ok_position, position = self.pipeline.query_position(Gst.Format.TIME)
        ok_duration, duration = self.pipeline.query_duration(Gst.Format.TIME)
        if ok_duration and duration > 0:
            total = duration / Gst.SECOND
            self.seek.set_range(0, total)
            self.seek.set_sensitive(True)
            self.duration_label.set_text(_clock_time(duration))
        if ok_position and position >= 0:
            self.position_label.set_text(_clock_time(position))
            if not self.seek.has_grab():
                self.seek.set_value(position / Gst.SECOND)
        return True

    def _new_sample(self, sink):
        sample = sink.emit("pull-sample")
        if sample is None:
            return Gst.FlowReturn.ERROR
        if self._frame_pending:
            return Gst.FlowReturn.OK
        structure = sample.get_caps().get_structure(0)
        width, height = structure.get_value("width"), structure.get_value("height")
        ok, info = sample.get_buffer().map(Gst.MapFlags.READ)
        if not ok:
            return Gst.FlowReturn.ERROR
        try:
            frame = bytes(info.data)
        finally:
            sample.get_buffer().unmap(info)
        stride = len(frame) // height
        if stride < width * 3:
            return Gst.FlowReturn.ERROR
        self._frame_pending = True
        GLib.idle_add(self._show_frame, frame, width, height, stride)
        return Gst.FlowReturn.OK

    def _show_frame(self, frame, width, height, stride):
        self._frame_pending = False
        if self.pipeline is None:
            return False
        pixbuf = GdkPixbuf.Pixbuf.new_from_bytes(GLib.Bytes.new(frame),
                                                  GdkPixbuf.Colorspace.RGB, False, 8,
                                                  width, height, stride)
        allocation = self.video.get_allocation()
        scale = min(max(1, allocation.width) / width, max(1, allocation.height) / height)
        if scale < 1:
            pixbuf = pixbuf.scale_simple(max(1, round(width * scale)),
                                         max(1, round(height * scale)),
                                         GdkPixbuf.InterpType.BILINEAR)
        self.video.set_from_pixbuf(pixbuf)
        return False

    def _on_message(self, _bus, message):
        if message.type == Gst.MessageType.ERROR:
            error, _debug = message.parse_error()
            self.message.set_text(error.message)
            self.pipeline.set_state(Gst.State.NULL)
            self._playing = False
            self.play_button.set_label("Play")
        elif message.type == Gst.MessageType.EOS:
            self.pipeline.set_state(Gst.State.PAUSED)
            self._playing = False
            self.play_button.set_label("Play")

    def _destroy(self, *_args):
        if self._source is not None:
            GLib.source_remove(self._source)
            self._source = None
        if self._bus is not None:
            self._bus.disconnect(self._bus_handler)
            self._bus.remove_signal_watch()
            self._bus = None
        if self.pipeline is not None:
            self.pipeline.set_state(Gst.State.NULL)
            self.pipeline = None
