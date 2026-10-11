PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;

CREATE TABLE IF NOT EXISTS meta (
  chave TEXT PRIMARY KEY,
  valor TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS componentes (
  id INTEGER PRIMARY KEY,
  nome TEXT NOT NULL UNIQUE COLLATE NOCASE,
  categoria TEXT NOT NULL,
  descricao TEXT,
  path_principal TEXT,
  prioridade INTEGER NOT NULL DEFAULT 3 CHECK (prioridade BETWEEN 1 AND 5),
  status_hyprmac TEXT
);

CREATE TABLE IF NOT EXISTS bundles (
  id INTEGER PRIMARY KEY,
  bundle_id TEXT,
  nome TEXT NOT NULL,
  path TEXT NOT NULL UNIQUE,
  tipo TEXT NOT NULL,
  executavel TEXT,
  versao TEXT,
  componente_id INTEGER REFERENCES componentes(id)
);
CREATE INDEX IF NOT EXISTS idx_bundles_id ON bundles(bundle_id);
CREATE INDEX IF NOT EXISTS idx_bundles_componente ON bundles(componente_id);

CREATE TABLE IF NOT EXISTS arquivos (
  id INTEGER PRIMARY KEY,
  path TEXT NOT NULL UNIQUE,
  nome TEXT NOT NULL,
  tipo TEXT NOT NULL,
  extensao TEXT,
  tamanho INTEGER,
  mtime INTEGER,
  bundle_id INTEGER REFERENCES bundles(id),
  categoria TEXT,
  componente_id INTEGER REFERENCES componentes(id),
  analisado INTEGER NOT NULL DEFAULT 0 CHECK (analisado IN (0,1)),
  analysis_level TEXT NOT NULL DEFAULT 'nenhum' CHECK (analysis_level IN ('nenhum','metadata','strings','deep')),
  motivo_analise TEXT,
  analisado_em TEXT,
  relevancia INTEGER NOT NULL DEFAULT 0 CHECK (relevancia BETWEEN 0 AND 5),
  sha256 TEXT
);
CREATE INDEX IF NOT EXISTS idx_arquivos_nome ON arquivos(nome COLLATE NOCASE);
CREATE INDEX IF NOT EXISTS idx_arquivos_tipo ON arquivos(tipo);
CREATE INDEX IF NOT EXISTS idx_arquivos_bundle ON arquivos(bundle_id);
CREATE INDEX IF NOT EXISTS idx_arquivos_componente ON arquivos(componente_id);

CREATE TABLE IF NOT EXISTS descobertas (
  id INTEGER PRIMARY KEY,
  componente_id INTEGER REFERENCES componentes(id),
  arquivo_id INTEGER REFERENCES arquivos(id),
  tipo TEXT NOT NULL,
  chave TEXT NOT NULL,
  valor TEXT NOT NULL,
  evidencia TEXT,
  confianca TEXT NOT NULL CHECK (confianca IN ('DIRETO','CONFIG','ASSET','SIMBOLO','INFERIDO','ESTIMADO')),
  observacao TEXT,
  criado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(componente_id, arquivo_id, tipo, chave, valor)
);
CREATE INDEX IF NOT EXISTS idx_descobertas_componente ON descobertas(componente_id);
CREATE INDEX IF NOT EXISTS idx_descobertas_arquivo ON descobertas(arquivo_id);

CREATE TABLE IF NOT EXISTS relacoes (
  id INTEGER PRIMARY KEY,
  origem_tipo TEXT NOT NULL,
  origem_id INTEGER NOT NULL,
  relacao TEXT NOT NULL,
  destino_tipo TEXT NOT NULL,
  destino_id INTEGER NOT NULL,
  observacao TEXT,
  UNIQUE(origem_tipo, origem_id, relacao, destino_tipo, destino_id)
);
CREATE INDEX IF NOT EXISTS idx_relacoes_origem ON relacoes(origem_tipo, origem_id);
CREATE INDEX IF NOT EXISTS idx_relacoes_destino ON relacoes(destino_tipo, destino_id);

CREATE TABLE IF NOT EXISTS mapeamento_hyprmac (
  id INTEGER PRIMARY KEY,
  componente_id INTEGER NOT NULL REFERENCES componentes(id),
  arquivo_hyprmac TEXT NOT NULL,
  status TEXT NOT NULL CHECK (status IN ('IGUAL','PROXIMO','PARCIAL','DIFERENTE','AUSENTE','NAO_APLICAVEL')),
  diferenca TEXT,
  recomendacao TEXT,
  atualizado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(componente_id, arquivo_hyprmac)
);

CREATE TABLE IF NOT EXISTS investigacoes (
  id INTEGER PRIMARY KEY,
  componente_id INTEGER REFERENCES componentes(id),
  pergunta TEXT NOT NULL,
  resultado TEXT,
  status TEXT NOT NULL DEFAULT 'ABERTA' CHECK (status IN ('ABERTA','PARCIAL','CONCLUIDA')),
  data TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  UNIQUE(componente_id, pergunta)
);

CREATE TABLE IF NOT EXISTS analises (
  id INTEGER PRIMARY KEY,
  arquivo_id INTEGER NOT NULL REFERENCES arquivos(id),
  nivel TEXT NOT NULL CHECK (nivel IN ('metadata','strings','deep')),
  motivo TEXT NOT NULL,
  ferramenta TEXT,
  analisado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE VIRTUAL TABLE IF NOT EXISTS conhecimento_fts USING fts5(
  componente, tipo, chave, valor, evidencia, observacao,
  tokenize='unicode61 remove_diacritics 2'
);

CREATE TRIGGER IF NOT EXISTS descobertas_ai AFTER INSERT ON descobertas BEGIN
  INSERT INTO conhecimento_fts(rowid, componente, tipo, chave, valor, evidencia, observacao)
  VALUES (new.id, COALESCE((SELECT nome FROM componentes WHERE id=new.componente_id),''),
          new.tipo, new.chave, new.valor, COALESCE(new.evidencia,''), COALESCE(new.observacao,''));
END;
CREATE TRIGGER IF NOT EXISTS descobertas_ad AFTER DELETE ON descobertas BEGIN
  DELETE FROM conhecimento_fts WHERE rowid=old.id;
END;
CREATE TRIGGER IF NOT EXISTS descobertas_au AFTER UPDATE ON descobertas BEGIN
  DELETE FROM conhecimento_fts WHERE rowid=old.id;
  INSERT INTO conhecimento_fts(rowid, componente, tipo, chave, valor, evidencia, observacao)
  VALUES (new.id, COALESCE((SELECT nome FROM componentes WHERE id=new.componente_id),''),
          new.tipo, new.chave, new.valor, COALESCE(new.evidencia,''), COALESCE(new.observacao,''));
END;
