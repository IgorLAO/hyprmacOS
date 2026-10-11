#!/usr/bin/env python3
"""Reproduz seis consultas em FTS/vetor/híbrido, sem acessar /mnt/macos."""
import argparse
import json
import sqlite3
import time
from contextlib import closing
from pathlib import Path
from common import DB, connect
from hybrid import Encoder, search, index

QUERIES = [
    'control center wifi', 'dock hover neighboring icons', 'popover spring',
    'window inactive material', 'system settings sidebar', 'now playing transition',
]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--db',type=Path,default=DB)
    parser.add_argument('--output',type=Path)
    args = parser.parse_args()
    with closing(connect(args.db)) as conn:
        start = time.perf_counter()
        encoder = Encoder()
        report = {'model':encoder.model_id,'load_ms':round((time.perf_counter()-start)*1000,2),
                  'queries':[], 'note':'Scores dos modos não têm a mesma escala; latência com modelo carregado. Resultados podem ser parciais.'}
        for query in QUERIES:
            item = {'query':query,'modes':{}}
            for mode in ('fts','vector','hybrid'):
                start = time.perf_counter()
                rows = search(conn,query,mode,3,encoder=encoder)
                item['modes'][mode] = {'ms':round((time.perf_counter()-start)*1000,2),
                    'results':[{k:r[k] for k in ('source','source_id','component','title','score','cosine','confidence')} for r in rows]}
            report['queries'].append(item)
        report['incremental_noop'] = index(conn)
        report['integrity'] = conn.execute('PRAGMA integrity_check').fetchone()[0]
        report['foreign_key_errors'] = len(conn.execute('PRAGMA foreign_key_check').fetchall())
        report['counts'] = {t:conn.execute(f'SELECT count(*) FROM {t}').fetchone()[0]
                            for t in ('arquivos','descobertas','knowledge_documents','knowledge_vectors')}
        backup = conn.execute("SELECT value FROM hybrid_meta WHERE key='backup'").fetchone()[0]
        report['backup'] = backup
        with closing(sqlite3.connect(backup)) as old:
            preserved = {}
            for (table,) in old.execute("SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE '%fts%'"):
                # Compare streaming row-by-row, not giant inventory lists in memory.
                left = old.execute(f'SELECT * FROM "{table}" ORDER BY rowid')
                right = conn.execute(f'SELECT * FROM "{table}" ORDER BY rowid')
                sentinel = object()
                from itertools import zip_longest
                preserved[table] = all(a is not sentinel and b is not sentinel and tuple(a)==tuple(b)
                                       for a,b in zip_longest(left,right,fillvalue=sentinel))
            report['original_tables_preserved'] = preserved
        output = json.dumps(report,ensure_ascii=False,indent=2)+'\n'
        if args.output:
            args.output.write_text(output)
        else:
            print(output,end='')


if __name__ == '__main__':
    from runtime import local_runtime
    local_runtime()
    main()
