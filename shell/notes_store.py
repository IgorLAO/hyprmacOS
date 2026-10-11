"""Núcleo do Notas (hyprmac-notas), sem GTK.

Cada nota é um arquivo Markdown em ~/.local/share/hyprmac/notas: a primeira linha
é o título (como no Notes do macOS) e as listas de verificação usam "- [ ]"/"- [x]",
legíveis em qualquer editor. A ordem e os grupos seguem o padrão do Notes do Tahoe
(Sort By ▸ Date Edited, Newest First; Group By Date: Today, Yesterday, Previous 7 Days,
Previous 30 Days, depois mês e ano), conforme o menu View do Notes.app 26.6.1.
"""
import datetime
import os
import re
import time
from dataclasses import dataclass


@dataclass(frozen=True)
class Folder:
    path: str
    name: str
    count: int


def folder_path(root, folder=None):
    """Resolve uma pasta local; links e caminhos fora da raiz não são pastas do app."""
    root = os.path.realpath(root)
    path = os.path.abspath(folder or root)
    if os.path.commonpath((root, path)) != root or os.path.realpath(path) != path:
        raise ValueError("Folder must be inside the notes directory")
    if not os.path.isdir(path):
        raise ValueError("Folder does not exist")
    return path


def folder_name(name):
    name = name.strip()
    if not name or name in (".", "..") or "/" in name or "\x00" in name:
        raise ValueError("Invalid folder name")
    return name


def list_folders(root):
    """Raiz Notes e subpastas, com contagem dos Markdown diretamente em cada pasta."""
    root = folder_path(root)
    paths = [root]
    for parent, dirs, _files in os.walk(root, followlinks=False):
        dirs[:] = sorted([d for d in dirs if not os.path.islink(os.path.join(parent, d))],
                         key=str.casefold)
        paths.extend(os.path.join(parent, d) for d in dirs)
    return [Folder(path, "Notes" if path == root else os.path.relpath(path, root),
                   sum(name.endswith(".md") and os.path.isfile(os.path.join(path, name))
                       and not os.path.islink(os.path.join(path, name))
                       for name in os.listdir(path))) for path in paths]


def create_folder(root, name="New Folder"):
    root, name = folder_path(root), folder_name(name)
    suffix = 1
    while True:
        path = os.path.join(root, name if suffix == 1 else f"{name} {suffix}")
        try:
            os.mkdir(path)
            return path
        except FileExistsError:
            suffix += 1


def rename_folder(root, folder, name):
    path = folder_path(root, folder)
    if path == os.path.realpath(root):
        raise ValueError("The Notes folder cannot be renamed")
    dest = os.path.join(os.path.dirname(path), folder_name(name))
    if dest != path:
        if os.path.lexists(dest):
            raise FileExistsError(dest)
        os.rename(path, dest)
    return dest


def move_note(root, note, folder=None):
    """Move sem sobrescrever homônimos e mantém a identidade da nota em memória."""
    source = os.path.abspath(note.path)
    folder_path(root, os.path.dirname(source))
    if os.path.islink(source) or not os.path.isfile(source):
        raise ValueError("Invalid note path")
    dest = os.path.join(folder_path(root, folder), os.path.basename(source))
    if dest == source:
        return note
    stem, ext = os.path.splitext(dest)
    suffix = 2
    while os.path.lexists(dest):
        dest = f"{stem}-{suffix}{ext}"
        suffix += 1
    os.rename(source, dest)
    note.path = dest
    return note

ROOT = os.path.expanduser("~/.local/share/hyprmac/notas")
CHECK_RE = re.compile(r"^(\s*)- \[( |x|X)\] ?(.*)$")
MONTHS = ("January", "February", "March", "April", "May", "June", "July",
          "August", "September", "October", "November", "December")


class Note:
    __slots__ = ("path", "text", "mtime")

    def __init__(self, path, text="", mtime=None):
        self.path = path
        self.text = text
        self.mtime = time.time() if mtime is None else mtime

    @property
    def title(self):
        for line in self.text.splitlines():
            line = strip_check(line).strip()
            if line:
                return line
        return "New Note"

    @property
    def preview(self):
        """Texto depois do título, numa linha; "No additional text" como no Notes."""
        lines = [strip_check(x).strip() for x in self.text.splitlines()]
        lines = [x for x in lines if x]
        rest = " ".join(lines[1:])
        return rest or "No additional text"


def strip_check(line):
    m = CHECK_RE.match(line)
    return m.group(3) if m else line


def is_check(line):
    return CHECK_RE.match(line) is not None


def is_checked(line):
    m = CHECK_RE.match(line)
    return bool(m and m.group(2) in "xX")


def toggle_check(line):
    """Marca/desmarca um item; uma linha comum vira item desmarcado (⇧⌘L)."""
    m = CHECK_RE.match(line)
    if not m:
        return f"- [ ] {line}"
    mark = " " if m.group(2) in "xX" else "x"
    return f"{m.group(1)}- [{mark}] {m.group(3)}"


def checklist_off(line):
    """⇧⌘L de novo: tira a caixa e devolve o texto."""
    m = CHECK_RE.match(line)
    return m.group(1) + m.group(3) if m else line


def move_checked_to_bottom(text):
    """Format ▸ More ▸ Move Checked to Bottom, por bloco contíguo de itens."""
    out, block = [], []

    def flush():
        out.extend([x for x in block if not is_checked(x)] + [x for x in block if is_checked(x)])
        block.clear()
    for line in text.split("\n"):
        if is_check(line):
            block.append(line)
        else:
            flush()
            out.append(line)
    flush()
    return "\n".join(out)


def set_all(text, checked):
    """Check All / Uncheck All."""
    mark = "x" if checked else " "
    return "\n".join(CHECK_RE.sub(lambda m: f"{m.group(1)}- [{mark}] {m.group(3)}", x)
                     for x in text.split("\n"))


def delete_checked(text):
    return "\n".join(x for x in text.split("\n") if not is_checked(x))


def group_label(mtime, now=None):
    now = now or datetime.datetime.now()
    d = datetime.datetime.fromtimestamp(mtime).date()
    days = (now.date() - d).days
    if days <= 0:
        return "Today"
    if days == 1:
        return "Yesterday"
    if days <= 7:
        return "Previous 7 Days"
    if days <= 30:
        return "Previous 30 Days"
    if d.year == now.year:
        return MONTHS[d.month - 1]
    return str(d.year)


def list_time(mtime, now=None, h24=True):
    """Hora na lista: hoje só a hora; antes, a data curta (como no Notes)."""
    now = now or datetime.datetime.now()
    dt = datetime.datetime.fromtimestamp(mtime)
    if dt.date() == now.date():
        return f"{dt.hour}:{dt.minute:02d}" if h24 else \
            f"{dt.hour % 12 or 12}:{dt.minute:02d} {'AM' if dt.hour < 12 else 'PM'}"
    if (now.date() - dt.date()).days == 1:
        return "Yesterday"
    return f"{dt.month}/{dt.day}/{dt.year % 100:02d}"


def header_date(mtime, h24=True):
    """Data no topo do editor: "October 22, 2025 at 17:43"."""
    dt = datetime.datetime.fromtimestamp(mtime)
    hora = f"{dt.hour}:{dt.minute:02d}" if h24 else \
        f"{dt.hour % 12 or 12}:{dt.minute:02d} {'AM' if dt.hour < 12 else 'PM'}"
    return f"{MONTHS[dt.month - 1]} {dt.day}, {dt.year} at {hora}"


class Store:
    def __init__(self, root=ROOT):
        self.root = root
        os.makedirs(root, exist_ok=True)

    def load(self, folder=None):
        notes = []
        directory = folder_path(self.root, folder)
        for name in os.listdir(directory):
            if not name.endswith(".md"):
                continue
            path = os.path.join(directory, name)
            if not os.path.isfile(path) or os.path.islink(path):
                continue
            try:
                with open(path, encoding="utf-8") as fh:
                    notes.append(Note(path, fh.read(), os.path.getmtime(path)))
            except OSError:
                continue
        notes.sort(key=lambda n: n.mtime, reverse=True)
        return notes

    def new(self, folder=None):
        directory = folder_path(self.root, folder)
        stamp = time.strftime("%Y%m%d-%H%M%S")
        path, n = os.path.join(directory, f"{stamp}.md"), 1
        while os.path.exists(path):
            n += 1
            path = os.path.join(directory, f"{stamp}-{n}.md")
        note = Note(path, "")
        self.save(note)
        return note

    def list_folders(self):
        return list_folders(self.root)

    def create_folder(self, name="New Folder"):
        return create_folder(self.root, name)

    def rename_folder(self, folder, name):
        return rename_folder(self.root, folder, name)

    def move_note(self, note, folder=None):
        return move_note(self.root, note, folder)

    def recently_deleted(self):
        """Lê só notas deste app na lixeira já usada por delete(), sem alterar a API."""
        trash = os.path.expanduser("~/.local/share/Trash")
        info = os.path.join(trash, "info")
        notes = []
        if not os.path.isdir(info):
            return notes
        root = os.path.realpath(self.root)
        for name in os.listdir(info):
            if not name.endswith(".trashinfo"):
                continue
            try:
                with open(os.path.join(info, name), encoding="utf-8") as fh:
                    original = next((line[5:].rstrip("\n") for line in fh
                                     if line.startswith("Path=")), "")
                if not original or not original.endswith(".md") or \
                        os.path.commonpath((root, os.path.realpath(original))) != root:
                    continue
                path = os.path.join(trash, "files", name[:-10])
                if os.path.islink(path):
                    continue
                with open(path, encoding="utf-8") as fh:
                    notes.append(Note(path, fh.read(), os.path.getmtime(path)))
            except (OSError, ValueError, UnicodeError):
                continue
        return sorted(notes, key=lambda note: note.mtime, reverse=True)

    def save(self, note):
        tmp = note.path + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            fh.write(note.text)
        os.replace(tmp, note.path)
        note.mtime = os.path.getmtime(note.path)

    def delete(self, note):
        """Vai para a lixeira do sistema (Recently Deleted), nunca apaga de vez."""
        trash = os.path.expanduser("~/.local/share/Trash")
        files, info = os.path.join(trash, "files"), os.path.join(trash, "info")
        os.makedirs(files, exist_ok=True)
        os.makedirs(info, exist_ok=True)
        base = os.path.basename(note.path)
        dest, n = os.path.join(files, base), 1
        while os.path.exists(dest):
            n += 1
            dest = os.path.join(files, f"{n}-{base}")
        with open(os.path.join(info, os.path.basename(dest) + ".trashinfo"), "w") as fh:
            fh.write(f"[Trash Info]\nPath={note.path}\n"
                     f"DeletionDate={time.strftime('%Y-%m-%dT%H:%M:%S')}\n")
        os.replace(note.path, dest)

    @staticmethod
    def matches(note, query):
        q = query.strip().lower()
        return not q or q in note.text.lower()
