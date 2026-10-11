-- Metadados de curadoria separados dos fatos originais: não alteram IDs,
-- confiança, evidência, embeddings ou texto de descobertas existentes.
BEGIN IMMEDIATE;
CREATE TABLE IF NOT EXISTS classificacao_registros (
  origem TEXT NOT NULL CHECK(origem IN ('descobertas','investigacoes','mapeamento_hyprmac')),
  origem_id INTEGER NOT NULL,
  estado TEXT NOT NULL DEFAULT 'experimental'
    CHECK(estado IN ('verified','experimental','superseded','archived','invalid')),
  versao_macos TEXT NOT NULL DEFAULT 'unknown',
  verificado_em TEXT,
  revisado_em TEXT,
  implementacao TEXT,
  substitui_origem TEXT,
  substitui_id INTEGER,
  observacao TEXT,
  PRIMARY KEY(origem,origem_id)
);
CREATE INDEX IF NOT EXISTS classificacao_estado_versao
  ON classificacao_registros(estado,versao_macos,origem);
INSERT OR IGNORE INTO classificacao_registros(origem,origem_id)
  SELECT 'descobertas',id FROM descobertas;
INSERT OR IGNORE INTO classificacao_registros(origem,origem_id)
  SELECT 'investigacoes',id FROM investigacoes;
INSERT OR IGNORE INTO classificacao_registros(origem,origem_id)
  SELECT 'mapeamento_hyprmac',id FROM mapeamento_hyprmac;
CREATE TRIGGER IF NOT EXISTS classificacao_descobertas_ai AFTER INSERT ON descobertas BEGIN
  INSERT OR IGNORE INTO classificacao_registros(origem,origem_id) VALUES('descobertas',new.id);
END;
CREATE TRIGGER IF NOT EXISTS classificacao_investigacoes_ai AFTER INSERT ON investigacoes BEGIN
  INSERT OR IGNORE INTO classificacao_registros(origem,origem_id) VALUES('investigacoes',new.id);
END;
CREATE TRIGGER IF NOT EXISTS classificacao_mapeamento_ai AFTER INSERT ON mapeamento_hyprmac BEGIN
  INSERT OR IGNORE INTO classificacao_registros(origem,origem_id) VALUES('mapeamento_hyprmac',new.id);
END;
UPDATE hybrid_meta SET value='3' WHERE key='schema_version';
COMMIT;
