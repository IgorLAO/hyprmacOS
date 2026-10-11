-- 001: metadados canônicos sobre fontes e fatos curados. Os trechos FTS continuam
-- sendo um índice derivado; o texto original permanece no arquivo ou no snapshot
-- legado do próprio índice quando a fonte já foi removida da árvore.
BEGIN;
CREATE TABLE IF NOT EXISTS documentos (
    caminho TEXT PRIMARY KEY,
    sha256 TEXT,
    presente INTEGER NOT NULL DEFAULT 1 CHECK (presente IN (0, 1)),
    tipo TEXT NOT NULL,
    estado TEXT NOT NULL CHECK (estado IN ('verified','experimental','superseded','archived','invalid')),
    versao_macos TEXT NOT NULL DEFAULT 'unknown',
    componente TEXT,
    fonte TEXT NOT NULL,
    url_fonte TEXT,
    confianca TEXT NOT NULL DEFAULT 'unverified',
    implementacao TEXT,
    verificado_em TEXT,
    revisado_em TEXT,
    resumo TEXT,
    atualizado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS documentos_estado_versao ON documentos(estado, versao_macos, componente);
CREATE INDEX IF NOT EXISTS documentos_hash ON documentos(sha256);

CREATE TABLE IF NOT EXISTS relacoes_documentos (
    origem TEXT NOT NULL REFERENCES documentos(caminho) ON UPDATE CASCADE,
    destino TEXT NOT NULL REFERENCES documentos(caminho) ON UPDATE CASCADE,
    relacao TEXT NOT NULL CHECK (relacao IN ('supersedes','duplicates','supports','contradicts')),
    evidencia TEXT,
    PRIMARY KEY (origem, destino, relacao)
);

CREATE TABLE IF NOT EXISTS registros (
    id TEXT PRIMARY KEY,
    tipo TEXT NOT NULL,
    componente TEXT,
    estado TEXT NOT NULL CHECK (estado IN ('verified','experimental','superseded','archived','invalid')),
    versao_macos TEXT NOT NULL DEFAULT 'unknown',
    titulo TEXT NOT NULL,
    resumo TEXT NOT NULL,
    evidencia TEXT,
    fonte_caminho TEXT,
    fonte_url TEXT,
    confianca TEXT NOT NULL DEFAULT 'unverified',
    implementacao TEXT,
    verificado_em TEXT,
    revisado_em TEXT,
    substitui TEXT REFERENCES registros(id),
    sha256 TEXT,
    atualizado_em TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS registros_filtros ON registros(estado, versao_macos, componente, tipo);
CREATE INDEX IF NOT EXISTS registros_fonte ON registros(fonte_caminho);
CREATE VIRTUAL TABLE IF NOT EXISTS registros_fts USING fts5(
    titulo, resumo, evidencia, content='registros', content_rowid='rowid',
    tokenize='unicode61 remove_diacritics 2'
);
CREATE TRIGGER IF NOT EXISTS registros_ai AFTER INSERT ON registros BEGIN
    INSERT INTO registros_fts(rowid,titulo,resumo,evidencia) VALUES (new.rowid,new.titulo,new.resumo,new.evidencia);
END;
CREATE TRIGGER IF NOT EXISTS registros_ad AFTER DELETE ON registros BEGIN
    INSERT INTO registros_fts(registros_fts,rowid,titulo,resumo,evidencia)
    VALUES ('delete',old.rowid,old.titulo,old.resumo,old.evidencia);
END;
CREATE TRIGGER IF NOT EXISTS registros_au AFTER UPDATE ON registros BEGIN
    INSERT INTO registros_fts(registros_fts,rowid,titulo,resumo,evidencia)
    VALUES ('delete',old.rowid,old.titulo,old.resumo,old.evidencia);
    INSERT INTO registros_fts(rowid,titulo,resumo,evidencia) VALUES (new.rowid,new.titulo,new.resumo,new.evidencia);
END;

INSERT OR IGNORE INTO registros(id,tipo,componente,estado,versao_macos,titulo,resumo,evidencia,fonte_caminho,confianca,verificado_em,revisado_em)
VALUES ('decision:tahoe26','decisao','projeto','verified','Tahoe 26',
        'Objetivo principal: macOS Tahoe 26',
        'Toda decisão visual e comportamental deve priorizar evidências do macOS Tahoe 26. Fontes de outras versões são secundárias e devem ser identificadas.',
        'Instrução explícita do usuário na missão de consolidação.', 'AGENTS.md','user_instruction','2026-10-10','2026-10-10');
INSERT OR IGNORE INTO registros(id,tipo,componente,estado,versao_macos,titulo,resumo,evidencia,fonte_caminho,confianca,verificado_em,revisado_em)
VALUES ('decision:linux-cursors','decisao','cursores','verified','Tahoe 26',
        'Manter os cursores do Linux',
        'Preferência registrada do usuário em 2026-10-02: manter os cursores do Linux.',
        'Nota órfã anteriormente presente em comparacao/parametros.json.',
        'comparacao/parametros.json','user_decision_record','2026-10-02','2026-10-10');
INSERT OR IGNORE INTO registros(id,tipo,componente,estado,versao_macos,titulo,resumo,evidencia,fonte_url,confianca,revisado_em)
VALUES ('external:nothing-liquid','implementacao_externa','Liquid Glass','experimental','Tahoe 26',
        'Nothing Liquid: Hyprland, Quickshell e fork de hyprglass',
        'Candidato para estudar máscaras alfa de layer surfaces, refração e animação genie. Integração exige verificar ABI do Hyprland e fidelidade às referências Apple; não importar o shell inteiro.',
        'Análise do README público em 2026-10-10.',
        'https://github.com/shlok-shinde/nothing-liquid','readme_only','2026-10-10');
INSERT OR IGNORE INTO registros(id,tipo,componente,estado,versao_macos,titulo,resumo,evidencia,fonte_url,confianca,revisado_em)
VALUES ('external:macos-linux','implementacao_externa','metodologia','experimental','Tahoe 26',
        'MacOS-Linux: tokens e comparação visual em Plasma/KWin',
        'Útil para métodos de medição e organização de tokens; código visual depende de KDE/KWin e requer adaptação para Hyprland.',
        'Análise do README público em 2026-10-10.',
        'https://github.com/kevinhirsch/MacOS-Linux','readme_only','2026-10-10');
INSERT OR IGNORE INTO registros(id,tipo,componente,estado,versao_macos,titulo,resumo,evidencia,fonte_url,confianca,revisado_em)
VALUES ('external:darling','implementacao_externa','compatibilidade','archived','unknown',
        'Darling: emulação de aplicações macOS',
        'Camada de compatibilidade de executáveis e APIs macOS; fora do escopo da interface visual atual. Consultar somente se houver objetivo de executar apps macOS.',
        'Análise do README público em 2026-10-10.',
        'https://github.com/darlinghq/darling','readme_only','2026-10-10');

PRAGMA user_version=1;
COMMIT;
