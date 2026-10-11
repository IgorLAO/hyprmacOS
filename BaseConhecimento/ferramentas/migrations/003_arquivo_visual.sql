BEGIN;
-- O índice visual antigo mistura medidas não verificadas e referências macOS 27.
-- Seu texto continua no FTS e pode ser recuperado com --historico.
UPDATE documentos SET estado='archived', versao_macos='macOS 27 (declared)',
    resumo='Índice visual legado; métricas e instruções exigem validação Tahoe 26.'
WHERE caminho='INDICE-VISUAL-OTIMIZADO.md';
PRAGMA user_version=3;
COMMIT;
