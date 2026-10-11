BEGIN;
CREATE INDEX IF NOT EXISTS relacoes_documentos_destino ON relacoes_documentos(destino, relacao);

INSERT OR IGNORE INTO registros(id,tipo,componente,estado,versao_macos,titulo,resumo,evidencia,fonte_caminho,confianca,revisado_em)
VALUES ('goal:legacy27','rotulo_legado','projeto','superseded','macOS 27 (declared)',
        'Rótulo legado Tahoe / macOS 27',
        'Documentos operacionais anteriores chamavam o objetivo de macOS Tahoe / macOS 27. Esse rótulo foi substituído pela instrução explícita de priorizar Tahoe 26; métricas antigas precisam ser revalidadas.',
        'Snapshot anterior de AGENTS.md no backup da consolidação de 2026-10-10.',
        'BaseConhecimento/.backups/consolidacao-20261010T225055Z.tar.gz',
        'source_snapshot','2026-10-10');
UPDATE registros SET substitui='goal:legacy27' WHERE id='decision:tahoe26';

INSERT OR IGNORE INTO registros(id,tipo,componente,estado,versao_macos,titulo,resumo,evidencia,fonte_caminho,confianca,implementacao,verificado_em,revisado_em)
VALUES ('animation:macpop-current','animacao_implementada','painéis','verified','HyprMac runtime',
        'Configuração atual da animação macPop',
        'hypr/hyprmac.lua define macPop com pontos Bezier (0.2,1.08) e (0.32,1), e layersIn com speed 3.2. A duração efetiva e a curva nativa Tahoe 26 não foram verificadas por este registro.',
        '[real:hypr/hyprmac.lua:118] [real:hypr/hyprmac.lua:120]',
        'hypr/hyprmac.lua','code_inspection','hypr/hyprmac.lua','2026-10-10','2026-10-10');
INSERT OR IGNORE INTO registros(id,tipo,componente,estado,versao_macos,titulo,resumo,evidencia,confianca,revisado_em)
VALUES ('animation:tahoe-native-pending','animacao_nativa','painéis','experimental','Tahoe 26',
        'Curva e duração nativas pendentes',
        'A duração e a curva correspondentes no macOS Tahoe 26 ainda dependem de captura temporal verificável; não inferir do valor local speed 3.2.',
        'O comentário de hypr/hyprmac.lua:124 reconhece ausência de gravação equivalente.',
        'pending_evidence','2026-10-10');
INSERT OR IGNORE INTO registros(id,tipo,componente,estado,versao_macos,titulo,resumo,evidencia,fonte_caminho,confianca,implementacao,verificado_em,revisado_em)
VALUES ('glass:shape-patch-missing','implementacao_atual','Liquid Glass','verified','HyprMac runtime',
        'Patch de formas do hyprglass ausente no checkout',
        'O carregador aplica patches em hypr/hyprglass/*.patch somente quando existem; o diretório/patch foi removido antes desta tarefa. As chamadas hyprglass shape em Ajustes exigem revisão de runtime.',
        '[real:scripts/vidro:42] [real:shell/hyprmac-ajustes:1217]',
        'hypr/hyprglass/forma-pela-mascara.patch','code_and_tree_inspection',
        'scripts/vidro; shell/hyprmac-ajustes','2026-10-10','2026-10-10');

PRAGMA user_version=2;
COMMIT;
