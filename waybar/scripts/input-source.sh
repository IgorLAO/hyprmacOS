#!/usr/bin/env python3
"""Fonte de entrada na barra ("BR", como no Tahoe): sigla do layout ativo do teclado
principal, em maiúsculas. Reescreve a cada troca de layout (evento activelayout do
Hyprland) e sai sozinho quando a Waybar fecha o pipe (recarregar não deixa órfãos)."""
import json, os, select, socket, subprocess, sys


def mostrar():
    kbs = json.loads(subprocess.run(["hyprctl", "devices", "-j"], capture_output=True, text=True).stdout)["keyboards"]
    k = next((k for k in kbs if k["main"]), kbs[0] if kbs else None)
    if not k:
        return
    ls = k["layout"].split(",")
    sigla = ls[min(k["active_layout_index"], len(ls) - 1)].strip().upper()
    print(json.dumps({"text": sigla, "tooltip": k["active_keymap"]}), flush=True)


sock = socket.socket(socket.AF_UNIX)
sock.connect(os.path.join(os.environ["XDG_RUNTIME_DIR"], "hypr",
                          os.environ["HYPRLAND_INSTANCE_SIGNATURE"], ".socket2.sock"))
mostrar()
p = select.poll()
p.register(sock, select.POLLIN)
p.register(sys.stdout, 0)           # só POLLERR/POLLHUP: a Waybar fechou o pipe
buf = b""
while True:
    for fd, ev in p.poll():
        if fd == sys.stdout.fileno() or not ev & select.POLLIN:
            sys.exit(0)
        data = sock.recv(65536)
        if not data:
            sys.exit(0)
        buf += data
        *linhas, buf = buf.split(b"\n")
        if any(l.startswith(b"activelayout>>") for l in linhas):
            mostrar()
