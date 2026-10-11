-- An unchanged scanner UPSERT must not rescan the FTS catalog or invalidate vectors.
DROP TRIGGER hybrid_catalog_arquivos_update;
CREATE TRIGGER hybrid_catalog_arquivos_update AFTER UPDATE ON arquivos
WHEN old.nome IS NOT new.nome OR old.tipo IS NOT new.tipo
 OR old.path IS NOT new.path OR old.componente_id IS NOT new.componente_id BEGIN
 DELETE FROM catalog_fts WHERE source='arquivos' AND source_id=old.id;
 INSERT INTO catalog_fts VALUES('arquivos',new.id,new.componente_id,new.nome,new.tipo,new.path);
END;
DROP TRIGGER hybrid_catalog_bundles_update;
CREATE TRIGGER hybrid_catalog_bundles_update AFTER UPDATE ON bundles
WHEN old.nome IS NOT new.nome OR old.bundle_id IS NOT new.bundle_id
 OR old.path IS NOT new.path OR old.componente_id IS NOT new.componente_id BEGIN
 DELETE FROM catalog_fts WHERE source='bundles' AND source_id=old.id;
 INSERT INTO catalog_fts VALUES('bundles',new.id,new.componente_id,new.nome,COALESCE(new.bundle_id,''),new.path);
END;
DROP TRIGGER hybrid_catalog_componentes_update;
CREATE TRIGGER hybrid_catalog_componentes_update AFTER UPDATE ON componentes
WHEN old.nome IS NOT new.nome OR old.descricao IS NOT new.descricao OR old.path_principal IS NOT new.path_principal BEGIN
 DELETE FROM catalog_fts WHERE source='componentes' AND source_id=old.id;
 INSERT INTO catalog_fts VALUES('componentes',new.id,new.id,new.nome,COALESCE(new.descricao,''),COALESCE(new.path_principal,''));
END;
DROP TRIGGER hybrid_component_update;
CREATE TRIGGER hybrid_component_update AFTER UPDATE OF nome ON componentes
WHEN old.nome IS NOT new.nome BEGIN
 DELETE FROM knowledge_documents WHERE component_id=old.id;
END;
CREATE TRIGGER hybrid_file_path_update AFTER UPDATE OF path ON arquivos
WHEN old.path IS NOT new.path BEGIN
 DELETE FROM knowledge_documents WHERE source='descobertas'
 AND source_id IN (SELECT id FROM descobertas WHERE arquivo_id=old.id);
END;
UPDATE hybrid_meta SET value='2' WHERE key='schema_version';
