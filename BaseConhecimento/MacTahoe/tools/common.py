#!/usr/bin/env python3
from __future__ import annotations

import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DB = ROOT / "base.db"
SOURCE = Path("/mnt/macos/root")
PROJECT = Path("/home/igor/Projects/hyprmac")


def connect(db: Path = DB) -> sqlite3.Connection:
    conn = sqlite3.connect(db)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys=ON")
    conn.execute("PRAGMA busy_timeout=5000")
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript((ROOT / "schema.sql").read_text())


def source_path(value: str) -> Path:
    path = Path(value).resolve()
    source = SOURCE.resolve()
    if path != source and source not in path.parents:
        raise ValueError(f"o caminho deve estar sob {SOURCE}")
    return path

