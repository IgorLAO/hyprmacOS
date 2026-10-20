//! Índice incremental da BaseConhecimento, preservando a curadoria SQLite.
use regex::Regex;
use rusqlite::{params, types::Value as SqlValue, Connection, OptionalExtension};
use serde_json::{json, Value};
use sha2::{Digest, Sha256};
use std::collections::HashSet;
use std::env;
use std::error::Error;
use std::fs;
use std::path::{Path, PathBuf};
use std::process::Command;
use walkdir::WalkDir;

type Result<T> = std::result::Result<T, Box<dyn Error>>;
const SKIP_DIRS: &[&str] = &["imagens", "icones-apps", "ponteiros", "papeis-de-parede", "macos-pour-windows", "models", "backups"];
const HISTORICOS: &[&str] = &["ANALISE-", "APPS-SISTEMA-", "CONVERGENCIA-", "CORRECAO-", "EFEITOS-", "EXECUCAO-", "FONTES.md", "GAPS-", "INVESTIGACAO-", "SCRAPING_", "TAHOE-BLOCOS-", "VIDEO-INSIGHT-", "comparacao/MATRIZ.md", "INDICE-VISUAL-OTIMIZADO.md"];

fn hash(bytes: &[u8]) -> String { format!("{:x}", Sha256::digest(bytes)) }
fn text(path: &Path) -> Result<String> { Ok(String::from_utf8_lossy(&fs::read(path)?).into_owned()) }
fn data(path: &Path) -> Result<Value> { Ok(serde_json::from_str(&text(path)?)?) }
fn value<'a>(item: &'a Value, key: &str) -> &'a Value { item.get(key).unwrap_or(&Value::Null) }
fn sql(item: &Value, key: &str) -> SqlValue {
    match value(item, key) {
        Value::Null => SqlValue::Null,
        Value::Bool(boolean) => SqlValue::Integer(i64::from(*boolean)),
        Value::Number(number) => number.as_i64().map(SqlValue::Integer).or_else(|| number.as_f64().map(SqlValue::Real)).unwrap_or(SqlValue::Null),
        Value::String(text) => SqlValue::Text(text.clone()),
        other => SqlValue::Text(py_json(other)),
    }
}
fn string(item: &Value, key: &str) -> String { item.get(key).and_then(Value::as_str).unwrap_or("").to_string() }
fn join_array(item: &Value, key: &str) -> String { item.get(key).and_then(Value::as_array).map(|items| items.iter().filter_map(Value::as_str).collect::<Vec<_>>().join(", ")).unwrap_or_default() }
fn py_json(item: &Value) -> String {
    match item {
        Value::Array(items) => format!("[{}]", items.iter().map(py_json).collect::<Vec<_>>().join(", ")),
        Value::Object(items) => format!("{{{}}}", items.iter().map(|(key, value)| format!("{}: {}", serde_json::to_string(key).unwrap(), py_json(value))).collect::<Vec<_>>().join(", ")),
        _ => serde_json::to_string(item).unwrap(),
    }
}
fn tipo_de(path: &str) -> &'static str {
    for (prefix, kind) in [("componentes/", "componente"), ("padroes/", "padrao"), ("hig/wwdc/", "wwdc"), ("hig/", "hig"), ("referencias/pdfs/", "pdf"), ("referencias/kit/contornos/", "contorno"), ("referencias/kit-visionos/contornos/", "contorno"), ("tokens/", "token"), ("referencias/telas/", "tela"), ("dev/", "dev"), ("apple-support-scraped/", "suporte")] {
        if path.starts_with(prefix) { return kind; }
    }
    "outro"
}
struct Metadata { state: String, version: String, component: Option<String>, url: Option<String>, summary: String }
fn initial_metadata(path: &str, content: &str) -> Metadata {
    let state = if HISTORICOS.iter().any(|prefix| path.starts_with(prefix)) || path.starts_with("historico/") { "archived" } else { "experimental" }.to_string();
    let first = content.chars().take(2500).collect::<String>();
    let version = if path.contains("macos27/") { "macOS 27 (declared)" } else if path.contains("kit-visionos/") { "visionOS" }
        else if Regex::new(r"(?i)macOS Tahoe 26|macOS 26|Tahoe 26").unwrap().is_match(&first) { "Tahoe 26" }
        else if Regex::new(r"(?i)macOS 27|Tahoe\s*/\s*27").unwrap().is_match(&first) { "macOS 27 (declared)" }
        else { "unknown" }.to_string();
    let component = path.strip_prefix("componentes/").map(|part| part.rsplit_once('.').map_or(part, |(head, _)| head).to_string());
    let url = Regex::new(r"https?://[^\s<>\)\]`]+") .unwrap().find(&content.chars().take(3500).collect::<String>()).map(|match_| match_.as_str().trim_end_matches(&['.', ',', ';'][..]).to_string());
    let lines = content.lines().filter(|line| !line.trim().is_empty()).map(|line| line.trim_matches(&[' ', '#', '>', '*', '\t'][..]).to_string()).collect::<Vec<_>>();
    let summary = if lines.len() > 1 { lines[1..lines.len().min(3)].join(" ") } else { lines.first().cloned().unwrap_or_default() };
    Metadata { state, version, component, url, summary: summary.chars().take(350).collect() }
}
fn markdown_parts(content: &str) -> (String, Vec<(String, String)>) {
    let pattern = Regex::new(r"^(#{1,4})\s+(.*)").unwrap();
    let mut title = String::new(); let mut stack: Vec<String> = Vec::new(); let mut current: Vec<String> = Vec::new(); let mut parts = Vec::new();
    for line in content.lines() {
        if let Some(captures) = pattern.captures(line) {
            if !current.is_empty() && !current.join("").trim().is_empty() { parts.push((stack.join(" › "), current.join("\n"))); }
            let level = captures[1].len(); let name = captures[2].trim().to_string();
            if level == 1 && title.is_empty() { title = name.clone(); }
            stack.truncate(level - 1); stack.push(name);
            current = vec![line.to_string()];
        } else { current.push(line.to_string()); }
    }
    if !current.is_empty() && !current.join("").trim().is_empty() { parts.push((stack.join(" › "), current.join("\n"))); }
    (title, parts)
}
fn contour_parts(content: &str) -> Vec<(String, String)> {
    let pattern = Regex::new(r"\w+ '([^']*)'").unwrap();
    let mut parts = Vec::new(); let mut current = Vec::new(); let mut name = String::new();
    for line in content.lines() {
        if !line.starts_with(' ') && !line.starts_with('#') {
            if !current.is_empty() { parts.push((name.clone(), current.join("\n"))); }
            name = pattern.captures(line).map(|capture| capture[1].to_string()).unwrap_or_else(|| line.chars().take(60).collect());
            current = vec![line.to_string()];
        } else if !line.trim().is_empty() { current.push(line.to_string()); }
    }
    if !current.is_empty() { parts.push((name, current.join("\n"))); }
    parts
}
fn text_parts(content: &str) -> Vec<(String, String)> {
    let lines = content.lines().filter(|line| !line.trim().is_empty()).collect::<Vec<_>>();
    lines.chunks(60).enumerate().map(|(index, lines)| (format!("linhas {}–{}", index * 60 + 1, index * 60 + 60), lines.join("\n"))).collect()
}
fn image_links(connection: &Connection, path: &str, content: &str) -> Result<()> {
    let pattern = Regex::new(r"!\[([^\]]*)\]\(([^)]+)\)")?;
    for captures in pattern.captures_iter(content) {
        let parent = Path::new(path).parent().unwrap_or(Path::new(""));
        let normalized = normalize(&parent.join(&captures[2]));
        connection.execute("INSERT INTO imagens VALUES (?,?,?)", params![normalized, &captures[1], path])?;
    }
    Ok(())
}
fn normalize(path: &Path) -> String {
    let mut parts = Vec::new();
    for part in path.components() {
        match part { std::path::Component::ParentDir => { parts.pop(); }, std::path::Component::CurDir => {}, other => parts.push(other.as_os_str().to_string_lossy().to_string()) }
    }
    parts.join("/")
}
fn migrate(connection: &Connection, base: &Path) -> Result<()> {
    let mut current: i64 = connection.query_row("PRAGMA user_version", [], |row| row.get(0))?;
    let mut files = fs::read_dir(base.join("ferramentas/migrations"))?.filter_map(|entry| entry.ok().map(|entry| entry.path()))
        .filter(|path| path.extension().is_some_and(|ext| ext == "sql")).collect::<Vec<_>>();
    files.sort();
    for file in files {
        let Some(name) = file.file_name().and_then(|name| name.to_str()) else { continue; };
        let Some(version) = name.split('_').next().and_then(|head| head.parse::<i64>().ok()) else { continue; };
        if version > current {
            connection.execute_batch(&text(&file)?)?;
            println!("migração {version}: {name}");
            current = version;
        }
    }
    Ok(())
}
fn setup(connection: &Connection, base: &Path) -> Result<()> {
    connection.execute_batch(r#"
        PRAGMA foreign_keys=ON;
        PRAGMA busy_timeout=5000;
        CREATE VIRTUAL TABLE IF NOT EXISTS trechos USING fts5(
            conteudo, titulo, secao, caminho UNINDEXED, tipo UNINDEXED,
            tokenize = "unicode61 remove_diacritics 2");
        CREATE TABLE IF NOT EXISTS cores (kit TEXT, grupo TEXT, nome TEXT, hex TEXT, css TEXT);
        CREATE TABLE IF NOT EXISTS tipografia (kit TEXT, nome TEXT, fonte TEXT, tamanho REAL, entrelinha REAL, cor TEXT);
        CREATE TABLE IF NOT EXISTS estilos (kit TEXT, nome TEXT, json TEXT);
        CREATE TABLE IF NOT EXISTS imagens (caminho TEXT, descricao TEXT, origem TEXT);
        CREATE TABLE IF NOT EXISTS imagens_catalogo (
            id TEXT PRIMARY KEY, caminho TEXT, categoria TEXT, estado TEXT,
            prioridade TEXT, titulo TEXT, descricao TEXT, ancoras TEXT,
            uso TEXT, largura INT, altura INT, proporcao REAL, sha256 TEXT,
            triagem TEXT, sequencia TEXT, classificacao_fonte TEXT, confianca TEXT
        );
        CREATE TABLE IF NOT EXISTS codigo_catalogo (
            caminho TEXT PRIMARY KEY, linguagem TEXT, linhas INT, bytes INT,
            resumo TEXT, simbolos TEXT, imports TEXT, tags TEXT, sha256 TEXT
        );
        CREATE TABLE IF NOT EXISTS meta (chave TEXT PRIMARY KEY, valor TEXT);
    "#)?;
    migrate(connection, base)
}
fn source_files(base: &Path) -> Vec<PathBuf> {
    let mut files = WalkDir::new(base).into_iter().filter_entry(|entry| {
        if entry.depth() == 0 || !entry.file_type().is_dir() { return true; }
        let name = entry.file_name().to_string_lossy();
        !name.starts_with('.') && !SKIP_DIRS.contains(&name.as_ref())
    }).filter_map(|entry| entry.ok()).filter(|entry| entry.path().is_file()).map(|entry| entry.path().to_owned())
        .filter(|path| matches!(path.extension().and_then(|ext| ext.to_str()), Some("md" | "txt")))
        .filter(|path| !path.strip_prefix(base).is_ok_and(|rel| rel.starts_with("ferramentas"))).collect::<Vec<_>>();
    files.sort();
    files
}
fn index_sources(connection: &Connection, base: &Path) -> Result<(usize, usize, usize)> {
    let mut seen = HashSet::new(); let mut unchanged = 0; let mut created = 0;
    for file in source_files(base) {
        let rel = file.strip_prefix(base)?.to_string_lossy().replace('\\', "/");
        let name = file.file_name().unwrap().to_string_lossy().to_string();
        let bytes = fs::read(&file)?; let content = String::from_utf8_lossy(&bytes).into_owned();
        let digest = hash(&bytes); let kind = tipo_de(&rel);
        seen.insert(rel.clone());
        let prior: Option<(Option<String>, String)> = connection.query_row("SELECT sha256,confianca FROM documentos WHERE caminho=?", [&rel], |row| Ok((row.get(0)?, row.get(1)?))).optional()?;
        if let Some((old_digest, confidence)) = &prior {
            connection.execute("UPDATE documentos SET sha256=?,presente=1,tipo=?,atualizado_em=CURRENT_TIMESTAMP WHERE caminho=?", params![digest, kind, rel])?;
            if old_digest.as_deref() != Some(&digest) && confidence == "unverified" {
                let meta = initial_metadata(&rel, &content);
                connection.execute("UPDATE documentos SET versao_macos=?,componente=?,url_fonte=?,resumo=? WHERE caminho=?", params![meta.version, meta.component, meta.url, meta.summary, rel])?;
            }
        } else {
            let meta = initial_metadata(&rel, &content);
            connection.execute("INSERT INTO documentos(caminho,sha256,presente,tipo,estado,versao_macos,componente,fonte,url_fonte,resumo) VALUES (?,?,1,?,?,?,?,?,?,?)",
                params![rel, digest, kind, meta.state, meta.version, meta.component, rel, meta.url, meta.summary])?;
        }
        let changed = prior.as_ref().is_none_or(|(old, _)| old.as_deref() != Some(&digest));
        if changed { connection.execute("DELETE FROM trechos WHERE caminho=?", [&rel])?; } else { unchanged += 1; }
        if name.ends_with(".md") { image_links(connection, &rel, &content)?; }
        if !changed { continue; }
        let (title, parts) = if kind == "contorno" {
            (name.strip_suffix(".txt").unwrap_or(&name).replace('_', " "), contour_parts(&content))
        } else if name.ends_with(".md") {
            let (title, parts) = markdown_parts(&content);
            (if title.is_empty() { name.trim_end_matches(".md").to_string() } else { title }, parts)
        } else { (name.trim_end_matches(".txt").to_string(), text_parts(&content)) };
        for (section, chunk) in parts {
            connection.execute("INSERT INTO trechos VALUES (?,?,?,?,?)", params![chunk, title, section, rel, kind])?;
            created += 1;
        }
    }
    let mut statement = connection.prepare("SELECT DISTINCT caminho FROM trechos")?;
    let paths = statement.query_map([], |row| row.get::<_, String>(0))?.collect::<rusqlite::Result<Vec<_>>>()?;
    drop(statement);
    for rel in paths {
        if seen.contains(&rel) { continue; }
        let registered: Option<i64> = connection.query_row("SELECT 1 FROM documentos WHERE caminho=?", [&rel], |row| row.get(0)).optional()?;
        if registered.is_some() {
            connection.execute("UPDATE documentos SET presente=0, estado=CASE WHEN estado IN ('verified','experimental') THEN 'archived' ELSE estado END WHERE caminho=?", [&rel])?;
        } else {
            connection.execute("INSERT INTO documentos(caminho,presente,tipo,estado,fonte,resumo) VALUES (?,0,?,'archived',?,?)", params![rel, tipo_de(&rel), "legacy FTS snapshot", "Fonte ausente da árvore; texto preservado no índice legado."])?;
        }
    }
    Ok((seen.len(), unchanged, created))
}
fn derived_images(connection: &Connection, base: &Path) -> Result<()> {
    let index = base.join("referencias/telas/INDICE.md");
    if index.exists() {
        let pattern = Regex::new(r"\|\s*`([^`]+)`[^|]*\|\s*([^|]+)\|\s*([^|]+)\|")?;
        for line in text(&index)?.lines() {
            if let Some(capture) = pattern.captures(line) {
                connection.execute("INSERT INTO imagens VALUES (?,?,?)", params![format!("referencias/telas/{}", capture[1].split(' ').next().unwrap_or("")), format!("{} — {}", capture[2].trim(), capture[3].trim()), "referencias/telas/INDICE.md"])?;
            }
        }
    }
    for (dir, origin) in [("referencias/kit/icones-apps", "ícone de app (kit macOS 27)"), ("referencias/kit/ponteiros", "ponteiro do macOS (kit)"), ("referencias/kit/papeis-de-parede", "papel de parede oficial do macOS 27")] {
        let folder = base.join(dir); if !folder.is_dir() { continue; }
        let mut files = fs::read_dir(&folder)?.filter_map(|entry| entry.ok().map(|entry| entry.file_name().to_string_lossy().into_owned())).collect::<Vec<_>>();
        files.sort();
        for name in files {
            let stem = Path::new(&name).file_stem().unwrap_or_default().to_string_lossy().replace(['_', '-'], " ");
            connection.execute("INSERT INTO imagens VALUES (?,?,?)", params![format!("{dir}/{name}"), stem, origin])?;
        }
    }
    let frames = base.join("video/frames-meta.json");
    if frames.exists() {
        for frame in data(&frames)?.as_array().into_iter().flatten() {
            let description = [string(frame, "title").trim().to_string(), string(frame, "component").trim().to_string(), join_array(frame, "shows")].into_iter().filter(|part| !part.is_empty()).collect::<Vec<_>>().join(" — ");
            let description = if description.is_empty() { "(frame sem descrição — preencher)".into() } else { description };
            connection.execute("INSERT INTO imagens VALUES (?,?,?)", params![string(frame, "arquivo"), description, format!("vídeo macOS 27 ({})", string(frame, "origem"))])?;
        }
    }
    let catalog = base.join("referencias/telas/catalogo.json");
    if catalog.exists() {
        let catalog_data = data(&catalog)?;
        for item in catalog_data.get("items").and_then(Value::as_array).into_iter().flatten() {
            let size = value(item, "dimensoes_px");
            connection.execute("INSERT OR REPLACE INTO imagens_catalogo VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", params![
                sql(item,"id"), sql(item,"arquivo"), sql(item,"categoria"), join_array(item,"estado"), sql(item,"prioridade"),
                sql(item,"titulo"), sql(item,"descricao"), join_array(item,"ancoras_visuais"), join_array(item,"usar_para"),
                sql(size,"largura"), sql(size,"altura"), sql(item,"proporcao"), sql(item,"sha256"), sql(item,"triagem"),
                py_json(value(item,"sequencia")), sql(item,"classificacao_fonte"), sql(item,"confianca")])?;
        }
    }
    let code = base.join("codigo.json");
    if code.exists() {
        let code_data = data(&code)?;
        for item in code_data.get("items").and_then(Value::as_array).into_iter().flatten() {
            connection.execute("INSERT OR REPLACE INTO codigo_catalogo VALUES (?,?,?,?,?,?,?,?,?)", params![
                sql(item,"path"), sql(item,"language"), sql(item,"lines"), sql(item,"bytes"), sql(item,"summary"),
                join_array(item,"symbols"), join_array(item,"imports"), join_array(item,"tags"), sql(item,"sha256")])?;
        }
    }
    Ok(())
}
fn tokens(connection: &Connection, base: &Path) -> Result<()> {
    for kit in ["macos27", "visionos"] {
        let folder = base.join("tokens").join(kit);
        for color in data(&folder.join("cores.json"))?.as_array().into_iter().flatten() {
            let full = string(color,"nome"); let (group, name) = full.rsplit_once('/').unwrap_or(("", &full));
            connection.execute("INSERT INTO cores VALUES (?,?,?,?,?)", params![kit, group, name, sql(color,"hex"), sql(color,"css")])?;
        }
        for font in data(&folder.join("tipografia.json"))?.as_array().into_iter().flatten() {
            connection.execute("INSERT INTO tipografia VALUES (?,?,?,?,?,?)", params![kit, sql(font,"nome"), sql(font,"fonte"), sql(font,"tamanho"), sql(font,"entrelinha"), sql(font,"cor")])?;
        }
        for style in data(&folder.join("estilos.json"))?.as_array().into_iter().flatten() {
            let mut properties = style.clone();
            let name = string(style, "nome");
            properties.as_object_mut().map(|object| object.shift_remove("nome"));
            connection.execute("INSERT INTO estilos VALUES (?,?,?)", params![kit, name, py_json(&properties)])?;
        }
    }
    Ok(())
}
fn record_hashes(connection: &Connection) -> Result<()> {
    let mut stmt = connection.prepare("SELECT id,titulo,resumo,evidencia,fonte_caminho,fonte_url,sha256 FROM registros")?;
    let rows = stmt.query_map([], |row| Ok((row.get::<_, String>(0)?, row.get::<_, String>(1)?, row.get::<_, String>(2)?, row.get::<_, Option<String>>(3)?, row.get::<_, Option<String>>(4)?, row.get::<_, Option<String>>(5)?, row.get::<_, Option<String>>(6)?)))?.collect::<rusqlite::Result<Vec<_>>>()?;
    drop(stmt);
    for (id, title, summary, evidence, source, url, old) in rows {
        let content = py_json(&json!([title, summary, evidence, source, url]));
        let digest = hash(content.as_bytes());
        if old.as_deref() != Some(&digest) { connection.execute("UPDATE registros SET sha256=? WHERE id=?", params![digest, id])?; }
    }
    Ok(())
}
fn count(connection: &Connection, table: &str) -> Result<i64> { Ok(connection.query_row(&format!("SELECT count(*) FROM {table}"), [], |row| row.get(0))?) }
fn run(base: &Path) -> Result<()> {
    if env::var_os("HYPRMAC_INDEX_SKIP_COMPARE").is_none() {
        let compare = base.join("ferramentas/comparar.py");
        let status = Command::new(compare).status()?;
        if !status.success() { return Err(format!("comparar.py falhou: {status}").into()); }
    }
    let db_path = base.join("base.db");
    let connection = Connection::open(&db_path)?;
    setup(&connection, base)?;
    connection.execute_batch("BEGIN IMMEDIATE")?;
    for table in ["cores", "tipografia", "estilos", "imagens", "imagens_catalogo", "codigo_catalogo"] {
        connection.execute(&format!("DELETE FROM {table}"), [])?;
    }
    let (seen, unchanged, created) = index_sources(&connection, base)?;
    derived_images(&connection, base)?;
    tokens(&connection, base)?;
    connection.execute("INSERT OR REPLACE INTO meta VALUES ('trechos', ?)", [count(&connection,"trechos")?.to_string()])?;
    record_hashes(&connection)?;
    connection.execute_batch("COMMIT")?;
    for table in ["trechos", "cores", "tipografia", "estilos", "imagens", "imagens_catalogo", "codigo_catalogo"] {
        println!("{table:12} {}", count(&connection, table)?);
    }
    println!("fontes alteradas: {}; inalteradas: {unchanged}; trechos novos: {created}", seen - unchanged);
    let duplicates: i64 = connection.query_row("SELECT count(*) FROM (SELECT sha256 FROM documentos WHERE presente=1 AND sha256 IS NOT NULL GROUP BY sha256 HAVING count(*)>1)", [], |row| row.get(0))?;
    println!("fontes textuais exatamente duplicadas (SHA-256): {duplicates}");
    let duplicate_records: i64 = connection.query_row("SELECT count(*) FROM (SELECT sha256 FROM registros WHERE sha256 IS NOT NULL GROUP BY sha256 HAVING count(*)>1)", [], |row| row.get(0))?;
    println!("registros curados exatamente duplicados (SHA-256): {duplicate_records}");
    println!("→ {}", db_path.display());
    Ok(())
}
fn main() {
    let base = env::var_os("HYPRMAC_BASE_DIR").map(PathBuf::from).unwrap_or_else(|| PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../../BaseConhecimento"));
    if let Err(error) = run(&base) { eprintln!("indexar: {error}"); std::process::exit(1); }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn source_classification_is_conservative() {
        let current = initial_metadata("componentes/teste.md", "# Teste\nmacOS Tahoe 26");
        assert_eq!(current.state, "experimental");
        assert_eq!(current.version, "Tahoe 26");
        let old = initial_metadata("historico/teste.md", "# Teste\nmacOS Tahoe 26");
        assert_eq!(old.state, "archived");
        let secondary = initial_metadata("referencias/macos27/teste.md", "# Teste\nTahoe 26");
        assert_eq!(secondary.version, "macOS 27 (declared)");
    }

    #[test]
    fn markdown_sections_keep_their_ancestry() {
        let (title, sections) = markdown_parts("# A\nintro\n## B\nbody\n### C\nmore");
        assert_eq!(title, "A");
        assert_eq!(sections[2].0, "A › B › C");
        assert!(sections[2].1.contains("more"));
    }
}
