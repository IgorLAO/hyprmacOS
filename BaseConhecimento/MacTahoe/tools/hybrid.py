"""Local retrieval. SQLite owns facts, provenance, text indexes and vectors."""
from __future__ import annotations

import hashlib
import heapq
import json
import re
import sqlite3
import unicodedata
from datetime import datetime, timezone
from contextlib import closing
from pathlib import Path

from common import ROOT

MODEL_NAME = 'sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2'
MODEL_DIR = ROOT / 'models/minilm'
DIM = 384
KINDS = {'animation': 'animacao', 'behavior': 'comportamento', 'structure': 'estrutura',
         'state': 'estado', 'material': 'material', 'decision': 'decisao',
         'microinteraction': 'microinteracao', 'summary': 'resumo', 'class': 'classe'}
CONFIDENCES = {'direct': 'DIRETO', 'config': 'CONFIG', 'asset': 'ASSET',
               'symbol': 'SIMBOLO', 'inferred': 'INFERIDO', 'estimated': 'ESTIMADO'}
INTERPRETED = {'animacao', 'comportamento', 'estrutura', 'estado', 'material', 'decisao',
               'microinteracao', 'resumo', 'descoberta', 'convergencia_visual',
               'progresso', 'validacao_hyprmac', 'relacao', 'diferenca'}


def normalize(text):
    text = unicodedata.normalize('NFKD', text).casefold()
    return ' '.join(re.findall(r'\w+', ''.join(c for c in text if not unicodedata.combining(c))))


def digest(value):
    return hashlib.sha256(value.encode()).hexdigest()


def model_id():
    if not (MODEL_DIR / 'revision.json').exists():
        raise RuntimeError('Modelo ausente. Execute tools/index_knowledge.py --download-model.')
    return MODEL_NAME + '@' + json.loads((MODEL_DIR / 'revision.json').read_text())['revision'] + ':mean-l2-v2'


def ready(conn):
    return bool(conn.execute("SELECT 1 FROM sqlite_master WHERE name='hybrid_meta'").fetchone())


def migrate(conn):
    if ready(conn):
        version = conn.execute("SELECT value FROM hybrid_meta WHERE key='schema_version'").fetchone()[0]
        if version == '1':
            upgrade_triggers(conn)
            version = '2'
        if version == '2':
            upgrade_classification(conn)
            version = '3'
        if version != '3':
            raise RuntimeError(f'Versão híbrida não suportada: {version}')
        return None
    db_path = Path(conn.execute('PRAGMA database_list').fetchone()[2])
    backup_dir = db_path.parent / 'backups'
    backup_dir.mkdir(exist_ok=True)
    backup = backup_dir / (db_path.stem + '-pre-hybrid-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ') + '.db')
    with closing(sqlite3.connect(backup)) as target:
        conn.backup(target)
    try:
        conn.executescript('BEGIN IMMEDIATE;\n' + (ROOT / 'migrations/001_hybrid.sql').read_text())
        for table, name, description, path, component in [
            ('arquivos', 'nome', 'tipo', 'path', 'componente_id'),
            ('bundles', 'nome', "COALESCE(bundle_id,'')", 'path', 'componente_id'),
            ('componentes', 'nome', "COALESCE(descricao,'')", "COALESCE(path_principal,'')", 'id'),
        ]:
            columns = f"'{table}',id,{component},{name},{description},{path}"
            conn.execute(f'INSERT INTO catalog_fts SELECT {columns} FROM {table}')
            newcols = ','.join([f"'{table}'", 'new.id', f'new.{component}', f'new.{name}',
                                description.replace('COALESCE(', 'COALESCE(new.') if 'COALESCE' in description else f'new.{description}',
                                path.replace('COALESCE(', 'COALESCE(new.') if 'COALESCE' in path else f'new.{path}'])
            for event in ('INSERT', 'UPDATE', 'DELETE'):
                commands = ''
                if event != 'INSERT':
                    commands += f"DELETE FROM catalog_fts WHERE source='{table}' AND source_id=old.id;"
                if event != 'DELETE':
                    commands += f'INSERT INTO catalog_fts VALUES({newcols});'
                conn.execute(f'CREATE TRIGGER hybrid_catalog_{table}_{event.lower()} AFTER {event} ON {table} BEGIN {commands} END')
        # Invalidate stale derived records even when an existing tool writes SQL directly.
        for table in ('descobertas', 'investigacoes', 'mapeamento_hyprmac'):
            for event in ('UPDATE', 'DELETE'):
                conn.execute(f"CREATE TRIGGER hybrid_invalidate_{table}_{event.lower()} AFTER {event} ON {table} BEGIN DELETE FROM knowledge_documents WHERE source='{table}' AND source_id=old.id; END")
        conn.execute('CREATE TRIGGER hybrid_component_update AFTER UPDATE ON componentes BEGIN DELETE FROM knowledge_documents WHERE component_id=old.id; END')
        conn.execute("INSERT INTO hybrid_meta VALUES('backup',?)", (str(backup),))
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    upgrade_triggers(conn)
    upgrade_classification(conn)
    return backup


def upgrade_triggers(conn):
    db_path = Path(conn.execute('PRAGMA database_list').fetchone()[2])
    folder = db_path.parent / 'backups'
    folder.mkdir(exist_ok=True)
    backup = folder / (db_path.stem + '-pre-hybrid-v2-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ') + '.db')
    with closing(sqlite3.connect(backup)) as target:
        conn.backup(target)
    try:
        conn.executescript('BEGIN IMMEDIATE;\n' + (ROOT / 'migrations/002_incremental_triggers.sql').read_text())
        conn.execute("INSERT INTO hybrid_meta VALUES('backup_v2',?)", (str(backup),))
        conn.commit()
    except Exception:
        conn.rollback()
        raise


def upgrade_classification(conn):
    db_path = Path(conn.execute('PRAGMA database_list').fetchone()[2])
    folder = db_path.parent / 'backups'
    folder.mkdir(exist_ok=True)
    backup = folder / (db_path.stem + '-pre-classification-v3-' + datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ') + '.db')
    with closing(sqlite3.connect(backup)) as target:
        conn.backup(target)
    try:
        conn.executescript((ROOT / 'migrations/003_classificacao.sql').read_text())
        conn.execute("INSERT OR REPLACE INTO hybrid_meta VALUES('backup_v3',?)", (str(backup),))
        conn.commit()
    except Exception:
        conn.rollback()
        raise


def sources(conn):
    for row in conn.execute('''SELECT d.*,COALESCE(c.nome,'Geral') component,COALESCE(a.path,'') path
        FROM descobertas d LEFT JOIN componentes c ON c.id=d.componente_id
        LEFT JOIN arquivos a ON a.id=d.arquivo_id ORDER BY d.id'''):
        r = dict(row)
        eligible = r['tipo'] in INTERPRETED
        # Curated explanatory symbol/config findings are useful; bare names/values aren't.
        if r['tipo'] in ('classe', 'config'):
            eligible = len(r['valor'].split()) >= 6 and not r['chave'].startswith(('CFBundle', 'NS', 'LS'))
        yield document('descobertas', r, r['tipo'], r['chave'], r['valor'],
                       r['evidencia'] or '', r['path'] or r['evidencia'] or '',
                       r['confianca'], r['observacao'] or '', eligible)
    known = {}
    for row in conn.execute('SELECT componente_id,valor FROM descobertas ORDER BY length(valor) DESC'):
        known.setdefault(row['componente_id'], []).append(row['valor'])
    for row in conn.execute('''SELECT i.*,COALESCE(c.nome,'Geral') component FROM investigacoes i
        LEFT JOIN componentes c ON c.id=i.componente_id WHERE length(trim(i.resultado))>0 ORDER BY i.id'''):
        r = dict(row)
        summary, evidence, notes = r['resultado'], '', f"Status: {r['status']}. Confiança do resumo não certificada."
        try:
            data = json.loads(summary)
        except (ValueError, TypeError):
            data = None
        if isinstance(data, dict):
            summary = str(data.get('resultado', ''))
            evidence = str(data.get('evidencia', data.get('relatorio', '')))
            notes += ' ' + '; '.join(f'{k}: {v}' for k, v in data.items() if k not in ('resultado','evidencia'))
        for conclusion in known.get(r['componente_id'], []):
            if len(conclusion) > 40 and summary.startswith(conclusion):
                notes += ' ' + summary[len(conclusion):]
                summary = conclusion
                break
        if summary:
            yield document('investigacoes', r, 'resumo', r['pergunta'], summary,
                           evidence, evidence, 'ESTIMADO', notes, True)
    for row in conn.execute('''SELECT m.*,COALESCE(c.nome,'Geral') component FROM mapeamento_hyprmac m
        LEFT JOIN componentes c ON c.id=m.componente_id ORDER BY m.id'''):
        r = dict(row)
        summary = ' '.join(x for x in (r['diferenca'], r['recomendacao']) if x)
        if summary:
            yield document('mapeamento_hyprmac', r, 'decisao', r['arquivo_hyprmac'], summary,
                           r['arquivo_hyprmac'], r['arquivo_hyprmac'], 'ESTIMADO', f"Status registrado: {r['status']}", True)


def document(source, r, kind, title, summary, evidence, path, confidence, notes, eligible):
    d = dict(source=source, source_id=r['id'], component_id=r['componente_id'],
             component=r['component'], kind=kind, title=title, summary=summary,
             evidence=evidence, path=path, confidence=confidence, notes=notes, eligible=int(eligible))
    d['content_hash'] = digest(json.dumps(d, sort_keys=True, ensure_ascii=False))
    return d


class Encoder:
    def __init__(self):
        if not (MODEL_DIR / 'revision.json').exists():
            raise RuntimeError('Modelo ausente. Execute tools/index_knowledge.py --download-model.')
        from fastembed import TextEmbedding
        import warnings
        self.model_id = model_id()
        with warnings.catch_warnings():
            warnings.filterwarnings('ignore', message='The model .* now uses mean pooling')
            self.model = TextEmbedding(MODEL_NAME, specific_model_path=str(MODEL_DIR), threads=2,
                                       local_files_only=True)

    def encode(self, texts):
        import numpy as np
        # Reject oversized discoveries: never silently truncate interpreted knowledge.
        for text in texts:
            tokenizer = self.model.model.tokenizer
            if len(tokenizer.encode(text).ids) >= 512:
                raise ValueError('Unidade semântica longa demais; resuma ou separe por descobertas antes de indexar.')
        result = np.asarray(list(self.model.embed(texts, batch_size=8)), dtype='<f4')
        result /= np.maximum(np.linalg.norm(result, axis=1, keepdims=True), 1e-12)
        return result


def semantic_text(d):
    # Evidence paths, metrics boilerplate and source IDs are metadata, never embeddings.
    title = re.sub(r'^.*?\d{4}[-]?\d{2}[-]?\d{2}[^:]*:\s*', '', d['title'])
    if len(d['summary'].split()) > 20 or d['source'] == 'mapeamento_hyprmac':
        title = ''
    return f"{d['component']}. {title}. {d['summary']}"


def numeric_signature(text):
    return re.findall(r'[<>≤≥=]+|[-+−]?\d+(?:[.,]\d+)?', text)


def index(conn, encoder_factory=Encoder):
    migrate(conn)
    stats = dict(documents=0, changed=0, generated=0, reused=0, near_duplicates=0)
    encoder = None
    current = set()
    expected_model = model_id()
    with conn:
        for d in sources(conn):
            current.add((d['source'], d['source_id']))
            stats['documents'] += 1
            old = conn.execute('SELECT d.content_hash,d.vector_id,v.model FROM knowledge_documents d LEFT JOIN knowledge_vectors v ON v.id=d.vector_id WHERE source=? AND source_id=?',
                               (d['source'], d['source_id'])).fetchone()
            if old and old['content_hash'] == d['content_hash'] and (not d['eligible'] or (old['vector_id'] and old['model'] == expected_model)):
                continue
            stats['changed'] += 1
            vector_id, similarity = None, None
            if d['eligible']:
                # Identical conclusions share a vector, even across investigation/discovery sources.
                content_key = digest(str(d['component_id']) + ':' + ' '.join(unicodedata.normalize('NFC', semantic_text(d)).split()))
                if encoder is None:
                    encoder = encoder_factory()
                found = conn.execute('SELECT id FROM knowledge_vectors WHERE model=? AND content_hash=?',
                                     (encoder.model_id, content_key)).fetchone()
                if found:
                    vector_id = found[0]
                    stats['reused'] += 1
                else:
                    import numpy as np
                    text = semantic_text(d)
                    vector = encoder.encode([text])[0]
                    stats['generated'] += 1
                    # Conservative semantic dedup: same component, numbers and negation vocabulary.
                    # Retain every relational record and its provenance; only share the vector.
                    best = (0.97, None)
                    negation = lambda s: set(normalize(s).split()) & {'nao','sem','not','no','never','without','enabled','disabled','ativo','inativo','active','inactive','ativado','desativado'}
                    for row in conn.execute('SELECT id,text,vector FROM knowledge_vectors WHERE component_id IS ? AND model=?',
                                            (d['component_id'], encoder.model_id)):
                        score = float(np.dot(vector, np.frombuffer(row['vector'], dtype='<f4')))
                        if (score > best[0] and numeric_signature(text) == numeric_signature(row['text'])
                                and negation(text) == negation(row['text'])):
                            best = (score, row['id'])
                    if best[1] is not None:
                        similarity, vector_id = best
                        stats['near_duplicates'] += 1
                    else:
                        vector_id = conn.execute('INSERT INTO knowledge_vectors(model,content_hash,component_id,text,vector) VALUES(?,?,?,?,?)',
                            (encoder.model_id, content_key, d['component_id'], text, vector.astype('<f4').tobytes())).lastrowid
            d.update(vector_id=vector_id, duplicate_similarity=similarity)
            columns = ','.join(d)
            updates = ','.join(f'{k}=excluded.{k}' for k in d if k not in ('source','source_id'))
            conn.execute(f"INSERT INTO knowledge_documents({columns}) VALUES({','.join('?' for _ in d)}) ON CONFLICT(source,source_id) DO UPDATE SET {updates}", tuple(d.values()))
        for row in conn.execute('SELECT id,source,source_id FROM knowledge_documents').fetchall():
            if (row['source'],row['source_id']) not in current:
                conn.execute('DELETE FROM knowledge_documents WHERE id=?', (row['id'],))
        conn.execute('DELETE FROM knowledge_vectors WHERE id NOT IN (SELECT vector_id FROM knowledge_documents WHERE vector_id IS NOT NULL)')
        if encoder:
            conn.execute("INSERT OR REPLACE INTO hybrid_meta VALUES('model',?)", (encoder.model_id,))
    return stats


def filters(component=None, kind=None, confidence=None, state=None):
    clauses, params = [], []
    for column, value in [('component',component), ('kind',KINDS.get(kind,kind)),
                           ('confidence',CONFIDENCES.get((confidence or '').lower(),(confidence or '').upper()))]:
        if value:
            clauses.append(f'd.{column} = ? COLLATE NOCASE')
            params.append(value)
    if state == 'active':
        clauses.append("EXISTS (SELECT 1 FROM classificacao_registros c WHERE c.origem=d.source "
                       "AND c.origem_id=d.source_id AND c.estado IN ('verified','experimental'))")
    elif state == 'historical':
        clauses.append("EXISTS (SELECT 1 FROM classificacao_registros c WHERE c.origem=d.source "
                       "AND c.origem_id=d.source_id AND c.estado IN ('superseded','archived','invalid'))")
    return (' AND ' + ' AND '.join(clauses) if clauses else ''), params


def fts_query(text):
    # Quoted tokens prevent raw MATCH syntax, punctuation-only errors and SQL injection.
    words = re.findall(r'\w+', text, re.UNICODE)
    words = [w for w in words if normalize(w) not in {'do','da','de','dos','das','o','a','the','of','and','e'}]
    return ' AND '.join(f'"{word}"*' for word in words)


def search(conn, query, mode='hybrid', limit=5, component=None, kind=None, confidence=None,
           encoder=None, min_similarity=0.30, historical=False, all_status=False):
    classified = bool(conn.execute("SELECT 1 FROM sqlite_master WHERE name='classificacao_registros'").fetchone())
    state = None if all_status or not classified else ('historical' if historical else 'active')
    clause, params = filters(component,kind,confidence,state)
    lexical, semantic = {}, {}
    match = fts_query(query)
    if not match:
        return []
    if mode in ('fts','hybrid'):
        for rank,row in enumerate(conn.execute('''SELECT d.id,bm25(hybrid_fts,2,0.3,3,1,0.4) score
             FROM hybrid_fts JOIN knowledge_documents d ON d.id=hybrid_fts.rowid
             WHERE hybrid_fts MATCH ?''' + clause + ' ORDER BY score LIMIT 60', [match,*params]), 1):
            lexical[row['id']] = (rank, -row['score'])
    if mode in ('vector','hybrid'):
        import numpy as np
        encoder = encoder or Encoder()
        stored = conn.execute("SELECT value FROM hybrid_meta WHERE key='model'").fetchone()
        if stored and stored[0] != encoder.model_id:
            raise RuntimeError('Modelo alterado; execute index_knowledge.py antes de consultar vetores.')
        query_vector = encoder.encode([query])[0]
        cursor = conn.execute('''SELECT v.id,v.vector FROM knowledge_vectors v WHERE v.model=? AND EXISTS
            (SELECT 1 FROM knowledge_documents d WHERE d.vector_id=v.id''' + clause + ')', [encoder.model_id,*params])
        top = []
        while rows := cursor.fetchmany(64):
            matrix = np.stack([np.frombuffer(row['vector'], dtype='<f4') for row in rows])
            for row, score in zip(rows, matrix @ query_vector):
                if score >= min_similarity:
                    item = (float(score), row['id'])
                    if len(top) < 60:
                        heapq.heappush(top,item)
                    elif item > top[0]:
                        heapq.heapreplace(top,item)
        cutoff = max(min_similarity, max((item[0] for item in top), default=0) * 0.85)
        for rank,(score,vid) in enumerate(sorted(top,reverse=True),1):
            if score < cutoff:
                continue
            for row in conn.execute('SELECT d.id FROM knowledge_documents d WHERE vector_id=?'+clause,[vid,*params]):
                semantic[row['id']] = (rank,score)
    scores = {}
    mentioned = []
    if mode == 'hybrid' and not component:
        normalized_query = ' ' + normalize(query) + ' '
        for row in conn.execute('SELECT nome FROM componentes'):
            if ' ' + normalize(row['nome']) + ' ' in normalized_query:
                mentioned.append(row['nome'])
    for doc_id in lexical.keys() | semantic.keys():
        if mode == 'fts':
            scores[doc_id] = lexical[doc_id][1]
        elif mode == 'vector':
            scores[doc_id] = semantic[doc_id][1]
        else:
            # Reciprocal rank fusion: no mixing BM25 and cosine scales.
            scores[doc_id] = sum(weight/(60+ranks[doc_id][0]) for ranks,weight in ((lexical,1),(semantic,3)) if doc_id in ranks)
            doc = conn.execute('SELECT component,eligible,title FROM knowledge_documents WHERE id=?',(doc_id,)).fetchone()
            if mentioned and doc['component'] not in mentioned:
                scores[doc_id] *= 0.6
            if not doc['eligible'] and normalize(query) != normalize(doc['title']):
                scores[doc_id] *= 0.5
    results, seen = [], set()
    for doc_id,score in sorted(scores.items(),key=lambda x:(-x[1],x[0])):
        row = dict(conn.execute('SELECT * FROM knowledge_documents WHERE id=?',(doc_id,)).fetchone())
        if row['vector_id']:
            # Present the discovery with evidence when an investigation repeats it.
            canonical = conn.execute('SELECT d.* FROM knowledge_documents d WHERE vector_id=?' + clause +
                " ORDER BY (source='descobertas') DESC,(evidence!='') DESC,id LIMIT 1",[row['vector_id'],*params]).fetchone()
            row = dict(canonical)
        if classified:
            classification = conn.execute('SELECT estado,versao_macos,revisado_em FROM classificacao_registros '
                                          'WHERE origem=? AND origem_id=?',(row['source'],row['source_id'])).fetchone()
            row.update(status=classification['estado'] if classification else 'experimental',
                       macos_version=classification['versao_macos'] if classification else 'unknown',
                       reviewed_at=classification['revisado_em'] if classification else None)
        else:
            row.update(status='experimental',macos_version='unknown',reviewed_at=None)
        dedup = row['vector_id'] or (row['component_id'], normalize(row['summary']))
        if dedup in seen:
            continue
        seen.add(dedup)
        row.update(score=score, cosine=semantic.get(doc_id,(None,None))[1],
                   bm25=lexical.get(doc_id,(None,None))[1])
        row['related'] = [dict(r) for r in conn.execute('''SELECT source,source_id FROM knowledge_documents
            WHERE vector_id=? AND id!=? ORDER BY id LIMIT 5''',(row['vector_id'],row['id']))]
        results.append(row)
        if len(results) >= limit:
            break
    return results
