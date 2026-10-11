"""Pequena extensão compatível da memória técnica Tahoe."""
import json
import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parents[1] / "base.db"


def ensure_schema():
    with sqlite3.connect(DB) as db:
        db.execute("""CREATE TABLE IF NOT EXISTS comparacoes (
            id INTEGER PRIMARY KEY,
            componente_id INTEGER NOT NULL REFERENCES componentes(id),
            tipo TEXT NOT NULL CHECK(tipo IN ('imagem', 'movimento')),
            tahoe_path TEXT NOT NULL,
            hyprmac_path TEXT NOT NULL,
            resultado_path TEXT NOT NULL,
            metricas_json TEXT NOT NULL,
            prioridade TEXT NOT NULL,
            criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
        )""")


def save_result(component, kind, tahoe, hyprmac, result, metrics, priority):
    ensure_schema()
    with sqlite3.connect(DB) as db:
        db.execute("PRAGMA foreign_keys=ON")
        row = db.execute("SELECT id FROM componentes WHERE lower(nome)=lower(?)", (component,)).fetchone()
        if row is None:
            options = ", ".join(r[0] for r in db.execute("SELECT nome FROM componentes ORDER BY prioridade, nome"))
            raise ValueError(f"Componente '{component}' não cadastrado em base.db. Opções: {options}")
        cursor = db.execute("""INSERT INTO comparacoes
            (componente_id, tipo, tahoe_path, hyprmac_path, resultado_path, metricas_json, prioridade)
            VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (row[0], kind, str(Path(tahoe).resolve()), str(Path(hyprmac).resolve()),
             str(Path(result).resolve()), json.dumps(metrics, ensure_ascii=False), priority))
        return cursor.lastrowid
