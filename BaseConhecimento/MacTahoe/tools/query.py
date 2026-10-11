#!/usr/bin/env python3
"""Busca curta Tahoe: semântica + FTS5 + filtros relacionais; não abre evidências."""
from __future__ import annotations

import argparse
import json
import sqlite3
from pathlib import Path
from common import DB
from hybrid import ready, search, fts_query


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('consulta')
    parser.add_argument('--db', type=Path, default=DB)
    parser.add_argument('--mode', choices=['fts','vector','hybrid'], default='hybrid')
    parser.add_argument('--limit', type=int, default=5)
    parser.add_argument('--component')
    parser.add_argument('--type', dest='kind')
    parser.add_argument('--confidence')
    group = parser.add_mutually_exclusive_group()
    group.add_argument('--historico', action='store_true', help='Somente registros arquivados, substituídos ou inválidos.')
    group.add_argument('--todos', action='store_true', help='Incluir todos os estados.')
    parser.add_argument('--json', action='store_true')
    parser.add_argument('--catalog', action='store_true', help='FTS de nomes/paths de arquivos, bundles e componentes, sem vetores.')
    args = parser.parse_args()
    if not 1 <= args.limit <= 20:
        parser.error('--limit deve estar entre 1 e 20')
    if not fts_query(args.consulta):
        parser.error('A consulta deve conter palavras ou números.')
    conn = sqlite3.connect(args.db.resolve().as_uri()+'?mode=ro',uri=True)
    conn.row_factory = sqlite3.Row
    if not ready(conn):
        parser.error('Execute tools/index_knowledge.py antes da primeira consulta híbrida.')
    if args.catalog:
        if args.kind or args.confidence:
            parser.error('--type/--confidence aplicam-se a descobertas, não ao catálogo bruto.')
        clause = ' AND c.nome=? COLLATE NOCASE' if args.component else ''
        rows = [dict(r) for r in conn.execute('''SELECT f.source,f.source_id,c.nome component,
            f.name,f.description,f.path,-bm25(catalog_fts) score FROM catalog_fts f
            LEFT JOIN componentes c ON c.id=f.component_id WHERE catalog_fts MATCH ?'''+clause+
            ' ORDER BY bm25(catalog_fts) LIMIT ?', [fts_query(args.consulta),*([args.component] if args.component else []),args.limit])]
    else:
        try:
            rows = search(conn,args.consulta,args.mode,args.limit,args.component,args.kind,args.confidence,
                          historical=args.historico, all_status=args.todos)
        except (ImportError, RuntimeError) as exc:
            parser.error(f'{exc} Use --mode fts ou instale requirements-semantic.txt na .venv local.')
    if args.json:
        # Bound text in machine-readable output too. Full records remain available via SQL IDs.
        print(json.dumps([{k:(v[:650] if isinstance(v,str) and k in ('summary','notes') else v)
                           for k,v in r.items() if k not in ('content_hash',)} for r in rows],ensure_ascii=False,indent=2))
    else:
        for r in rows:
            if args.catalog:
                print(f"[{r['score']:.4f}] {r['component']} · {r['source']}:{r['source_id']} · {r['name']}\n  {r['path']}")
                continue
            print(f"[{r['score']:.4f}] {r['component']} · {r['kind']} · {r['confidence']} · "
                  f"{r['status']} · {r['macos_version']} · {r['source']}:{r['source_id']}")
            print(f"  {r['title'][:140]}\n  {r['summary'][:450]}")
            if r['notes']:
                print(f"  Ressalva: {r['notes'][:230]}")
            print(f"  Evidência: {r['evidence'] or 'não registrada'}\n  Path: {r['path'] or 'não registrado'}")
            if r['related']:
                print('  Relacionados: '+', '.join(f"{x['source']}:{x['source_id']}" for x in r['related']))
        if not rows:
            print('Nenhum resultado relevante com estes filtros; consulte FTS/SQL antes de abrir o Tahoe.')
    conn.close()


if __name__ == '__main__':
    import sys
    if '--catalog' not in sys.argv and not ('--mode' in sys.argv and 'fts' in sys.argv):
        from runtime import local_runtime
        local_runtime()
    main()
