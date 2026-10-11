-- Additive migration: original tables, FTS and IDs remain untouched.
CREATE TABLE hybrid_meta (key TEXT PRIMARY KEY, value TEXT NOT NULL);
CREATE TABLE knowledge_vectors (
 id INTEGER PRIMARY KEY,
 model TEXT NOT NULL,
 content_hash TEXT NOT NULL,
 component_id INTEGER REFERENCES componentes(id),
 text TEXT NOT NULL,
 vector BLOB NOT NULL CHECK(length(vector)=1536),
 created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
 UNIQUE(model,content_hash)
);
CREATE INDEX knowledge_vectors_component ON knowledge_vectors(component_id);
CREATE TABLE knowledge_documents (
 id INTEGER PRIMARY KEY,
 source TEXT NOT NULL CHECK(source IN ('descobertas','investigacoes','mapeamento_hyprmac')),
 source_id INTEGER NOT NULL,
 component_id INTEGER REFERENCES componentes(id),
 component TEXT NOT NULL,
 kind TEXT NOT NULL,
 title TEXT NOT NULL,
 summary TEXT NOT NULL,
 evidence TEXT NOT NULL,
 path TEXT NOT NULL,
 confidence TEXT NOT NULL,
 notes TEXT NOT NULL,
 eligible INTEGER NOT NULL CHECK(eligible IN (0,1)),
 content_hash TEXT NOT NULL,
 vector_id INTEGER REFERENCES knowledge_vectors(id),
 duplicate_similarity REAL,
 UNIQUE(source,source_id)
);
CREATE INDEX knowledge_documents_filters ON knowledge_documents(component_id,kind,confidence);
CREATE INDEX knowledge_documents_vector ON knowledge_documents(vector_id);
CREATE VIRTUAL TABLE hybrid_fts USING fts5(component,kind,title,summary,notes,
 content='knowledge_documents',content_rowid='id',tokenize='unicode61 remove_diacritics 2');
CREATE TRIGGER hybrid_documents_ai AFTER INSERT ON knowledge_documents BEGIN
 INSERT INTO hybrid_fts(rowid,component,kind,title,summary,notes) VALUES(new.id,new.component,new.kind,new.title,new.summary,new.notes);
END;
CREATE TRIGGER hybrid_documents_ad AFTER DELETE ON knowledge_documents BEGIN
 INSERT INTO hybrid_fts(hybrid_fts,rowid,component,kind,title,summary,notes) VALUES('delete',old.id,old.component,old.kind,old.title,old.summary,old.notes);
END;
CREATE TRIGGER hybrid_documents_au AFTER UPDATE ON knowledge_documents BEGIN
 INSERT INTO hybrid_fts(hybrid_fts,rowid,component,kind,title,summary,notes) VALUES('delete',old.id,old.component,old.kind,old.title,old.summary,old.notes);
 INSERT INTO hybrid_fts(rowid,component,kind,title,summary,notes) VALUES(new.id,new.component,new.kind,new.title,new.summary,new.notes);
END;
-- Names/keys/descriptions only: no binary content, no raw plist/strings dump.
CREATE VIRTUAL TABLE catalog_fts USING fts5(source UNINDEXED,source_id UNINDEXED,
 component_id UNINDEXED,name,description,path UNINDEXED,tokenize='unicode61 remove_diacritics 2');
INSERT INTO hybrid_meta VALUES('schema_version','1');
