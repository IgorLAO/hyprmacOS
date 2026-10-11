"""Local Voice Memos panel using PipeWire recording and GStreamer playback."""

from datetime import datetime
from pathlib import Path
import shutil
import subprocess
from uuid import uuid4

import gi

gi.require_version("Gtk", "3.0")
from gi.repository import GLib, Gtk, Pango


RECORDINGS = Path.home() / ".local/share/hyprmac/voice-memos"


def list_recordings(directory=RECORDINGS):
    """List only WAV files in the app's own directory, newest first."""
    try:
        return sorted((path for path in Path(directory).iterdir()
                       if path.is_file() and path.suffix.lower() == ".wav"),
                      key=lambda path: path.stat().st_mtime, reverse=True)
    except OSError:
        return []


def _stop_process(process):
    if process is None or process.poll() is not None:
        return
    process.terminate()
    try:
        process.wait(timeout=1)
    except subprocess.TimeoutExpired:
        process.kill()
        process.wait(timeout=1)


class VoiceMemosPanel(Gtk.Box):
    def __init__(self):
        super().__init__(orientation=Gtk.Orientation.VERTICAL, spacing=12)
        self.recording = None
        self.recording_path = None
        self.playing = None
        self._source = GLib.timeout_add(300, self._poll)
        self.connect("destroy", self._destroy)

        description = Gtk.Label(label="Recordings saved on this computer")
        description.set_halign(Gtk.Align.START)
        description.get_style_context().add_class("dim-label")
        self.pack_start(description, False, False, 0)

        controls = Gtk.Box(spacing=8)
        self.record_button = Gtk.Button(label="Record")
        self.record_button.connect("clicked", self._toggle_recording)
        controls.pack_start(self.record_button, False, False, 0)
        self.stop_button = Gtk.Button(label="Stop playback")
        self.stop_button.connect("clicked", self._stop_playback)
        self.stop_button.set_sensitive(False)
        controls.pack_start(self.stop_button, False, False, 0)
        self.pack_start(controls, False, False, 0)

        self.status = Gtk.Label(label="Ready")
        self.status.set_halign(Gtk.Align.START)
        self.status.set_line_wrap(True)
        self.pack_start(self.status, False, False, 0)

        scroller = Gtk.ScrolledWindow()
        scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        self.pack_start(scroller, True, True, 0)
        self.listbox = Gtk.ListBox()
        self.listbox.set_selection_mode(Gtk.SelectionMode.NONE)
        scroller.add(self.listbox)
        self._refresh()

    def _toggle_recording(self, *_args):
        if self.recording is not None:
            self._stop_recording()
            return
        executable = shutil.which("pw-record")
        if executable is None:
            self.status.set_text("PipeWire recorder (pw-record) is unavailable.")
            return
        try:
            RECORDINGS.mkdir(parents=True, exist_ok=True, mode=0o700)
            name = datetime.now().strftime("Recording %Y-%m-%d %H-%M-%S")
            path = RECORDINGS / f"{name}-{uuid4().hex[:6]}.wav"
            self.recording = subprocess.Popen(
                [executable, str(path)], stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, umask=0o077)
            self.recording_path = path
        except OSError as error:
            self.status.set_text(f"Could not start recording: {error.strerror or error}")
            return
        self.record_button.set_label("Stop recording")
        self.status.set_text("Recording…")

    def _stop_recording(self):
        process, path = self.recording, self.recording_path
        self.recording = None
        self.recording_path = None
        _stop_process(process)
        self.record_button.set_label("Record")
        if path is not None and path.is_file() and path.stat().st_size > 44:
            self.status.set_text(f"Saved {path.name}")
        else:
            if path is not None:
                path.unlink(missing_ok=True)
            self.status.set_text("No audio was saved. Check the recording device.")
        self._refresh()

    def _play(self, _button, path):
        executable = shutil.which("gst-play-1.0")
        if executable is None:
            self.status.set_text("GStreamer player (gst-play-1.0) is unavailable.")
            return
        _stop_process(self.playing)
        self.playing = None
        try:
            self.playing = subprocess.Popen(
                [executable, str(path)], stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        except OSError as error:
            self.status.set_text(f"Could not play recording: {error.strerror or error}")
            return
        self.stop_button.set_sensitive(True)
        self.status.set_text(f"Playing {path.name}")

    def _stop_playback(self, *_args):
        _stop_process(self.playing)
        self.playing = None
        self.stop_button.set_sensitive(False)
        self.status.set_text("Playback stopped")

    def _poll(self):
        if self.recording is not None and self.recording.poll() is not None:
            self._stop_recording()
        if self.playing is not None and self.playing.poll() is not None:
            code = self.playing.returncode
            self.playing = None
            self.stop_button.set_sensitive(False)
            self.status.set_text("Playback finished" if code == 0 else "Playback failed")
        return True

    def _refresh(self):
        for child in self.listbox.get_children():
            child.destroy()
        for path in list_recordings():
            row = Gtk.Box(spacing=8)
            row.set_border_width(6)
            title = Gtk.Label(label=path.stem)
            title.set_halign(Gtk.Align.START)
            title.set_ellipsize(Pango.EllipsizeMode.END)
            row.pack_start(title, True, True, 0)
            play = Gtk.Button(label="Play")
            play.connect("clicked", self._play, path)
            row.pack_end(play, False, False, 0)
            self.listbox.add(row)
        self.listbox.show_all()

    def _destroy(self, *_args):
        GLib.source_remove(self._source)
        _stop_process(self.recording)
        _stop_process(self.playing)
        self.recording = None
        self.playing = None
