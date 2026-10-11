"""Abrir documentos no app de destino do Dock; sem GTK, cópia ou execução shell."""

import os
import re
from urllib.parse import unquote, urlsplit


def supports_documents(info):
    return bool(info and (info.supports_files() or info.supports_uris()))


def open_documents(info, uris, new_file, launch_context=None):
    """Valida o lote inteiro antes de entregar URIs/GFiles ao AppInfo existente.

    ``new_file`` é Gio.File.new_for_uri; injetado para testes sem GI. Arquivos
    locais devem existir; URIs remotas só passam para apps com supports_uris.
    O resultado confirma a entrega ao launcher, não que o app abriu o documento.
    """
    if not supports_documents(info) or not uris:
        return False
    files = []
    try:
        for uri in uris:
            if (not isinstance(uri, str) or any(c.isspace() for c in uri) or
                    "\x00" in unquote(uri) or re.search(r"%(?![0-9a-fA-F]{2})", uri)):
                return False
            parsed = urlsplit(uri)
            if not parsed.scheme or not (parsed.path or parsed.netloc):
                return False
            if parsed.scheme in ("http", "https") and not parsed.hostname:
                return False
            if parsed.scheme == "file":
                if parsed.query or parsed.fragment:
                    return False
                file = new_file(uri)
                path = file.get_path()
                if not path or not os.path.isfile(path):
                    return False
                files.append(file)
            elif not info.supports_uris():
                return False
        if info.supports_uris():
            return bool(info.launch_uris(list(uris), launch_context))
        return bool(info.launch(files, launch_context))
    except Exception:
        # GLib.Error de launch ou URI inválida: o receiver deve finalizar rejeitado.
        return False
