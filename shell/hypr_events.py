"""Uma conexão com o socket de eventos do Hyprland para todo o shell GTK."""

import os
import socket
import threading
import time
import traceback


class EventBus:
    """Entrega eventos, na ordem, no laço principal fornecido pelo chamador."""

    def __init__(self, schedule, runtime_dir, signature=None, retry_seconds=2):
        self._schedule = schedule
        self._runtime_dir = runtime_dir
        self._signature = signature
        self._retry_seconds = retry_seconds
        self._callbacks = []
        self._started = False

    def subscribe(self, callback):
        signature = self._signature or os.environ.get("HYPRLAND_INSTANCE_SIGNATURE")
        if not signature:
            return
        self._callbacks.append(callback)
        if not self._started:
            self._started = True
            path = os.path.join(self._runtime_dir, "hypr", signature, ".socket2.sock")
            threading.Thread(target=self._reader, args=(path,), daemon=True,
                             name="hyprmac-events").start()

    def _reader(self, path):
        while True:
            try:
                with socket.socket(socket.AF_UNIX, socket.SOCK_STREAM) as conn:
                    conn.connect(path)
                    for line in conn.makefile(encoding="utf-8", errors="replace"):
                        self._schedule(self._deliver, line.rstrip("\n"))
            except OSError:
                pass
            time.sleep(self._retry_seconds)

    def _deliver(self, line):
        for callback in tuple(self._callbacks):
            try:
                callback(line)
            except Exception:
                traceback.print_exc()
        return False
