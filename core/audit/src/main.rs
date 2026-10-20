//! Auditoria da base curada, fontes locais e links operacionais.
use percent_encoding::percent_decode_str;
use regex::Regex;
use rusqlite::{params, Connection, OpenFlags};
use serde_json::{json, Map, Value};
use sha2::{Digest, Sha256};
use std::fs;
use std::path::{Path, PathBuf};

const OPERATIONAL: [&str; 7] = [
    "AGENTS.md",
    "ARCHITECTURE.md",
    "STATUS.md",
    "README.md",
    "CLAUDE.md",
    "ONBOARDING.md",
    "TODO.md",
];

#[derive(Debug)]
struct Document {
    path: String,
    digest: Option<String>,
    present: bool,
    state: String,
}

fn database(path: &Path) -> Result<Connection, String> {
    Connection::open_with_flags(path, OpenFlags::SQLITE_OPEN_READ_ONLY)
        .map_err(|error| error.to_string())
}

fn count(connection: &Connection, sql: &str) -> Result<i64, String> {
    connection
        .query_row(sql, [], |row| row.get(0))
        .map_err(|error| error.to_string())
}

fn check_db(name: &str, path: &Path) -> Result<Value, String> {
    let connection = database(path)?;
    let integrity: String = connection
        .query_row("PRAGMA integrity_check", [], |row| row.get(0))
        .map_err(|error| error.to_string())?;
    let mut foreign_keys = 0;
    let mut statement = connection
        .prepare("PRAGMA foreign_key_check")
        .map_err(|error| error.to_string())?;
    let mut rows = statement.query([]).map_err(|error| error.to_string())?;
    while rows.next().map_err(|error| error.to_string())?.is_some() {
        foreign_keys += 1;
    }
    drop(rows);
    drop(statement);
    let mut object = Map::new();
    object.insert(
        "bytes".into(),
        json!(fs::metadata(path).map_err(|error| error.to_string())?.len()),
    );
    object.insert("integridade".into(), json!(integrity));
    object.insert("erros_fk".into(), json!(foreign_keys));
    if name == "tahoe_local" {
        let mut failures = 0;
        for table in ["descobertas", "investigacoes", "mapeamento_hyprmac"] {
            let missing = connection.query_row(
                &format!("SELECT count(*) FROM {table} s LEFT JOIN classificacao_registros c ON c.origem=? AND c.origem_id=s.id WHERE c.origem_id IS NULL"),
                params![table], |row| row.get::<_, i64>(0)).map_err(|error| error.to_string())?;
            let orphaned = connection.query_row(
                &format!("SELECT count(*) FROM classificacao_registros c LEFT JOIN {table} s ON s.id=c.origem_id WHERE c.origem=? AND s.id IS NULL"),
                params![table], |row| row.get::<_, i64>(0)).map_err(|error| error.to_string())?;
            failures += missing + orphaned;
        }
        object.insert("classificacao_sem_fonte_ou_ausente".into(), json!(failures));
    }
    Ok(Value::Object(object))
}

fn documents(connection: &Connection) -> Result<Vec<Document>, String> {
    let mut statement = connection
        .prepare("SELECT caminho,sha256,presente,estado FROM documentos")
        .map_err(|error| error.to_string())?;
    let rows = statement
        .query_map([], |row| {
            Ok(Document {
                path: row.get(0)?,
                digest: row.get(1)?,
                present: row.get::<_, i64>(2)? != 0,
                state: row.get(3)?,
            })
        })
        .map_err(|error| error.to_string())?;
    rows.collect::<Result<Vec<_>, _>>()
        .map_err(|error| error.to_string())
}

fn links(path: &Path, root: &Path, regex: &Regex) -> Vec<Value> {
    let content = String::from_utf8_lossy(&fs::read(path).unwrap_or_default()).into_owned();
    let mut broken = Vec::new();
    for capture in regex.captures_iter(&content) {
        let raw = capture.get(1).unwrap().as_str();
        let reference = raw
            .trim()
            .split_once(" \"")
            .map_or(raw.trim(), |(head, _)| head)
            .trim_matches(&['<', '>'][..]);
        if reference.is_empty()
            || ["https://", "http://", "mailto:", "#", "data:"]
                .iter()
                .any(|prefix| reference.starts_with(prefix))
        {
            continue;
        }
        let target = if let Some(uri) = reference.strip_prefix("file://") {
            let path = if uri.starts_with('/') {
                uri
            } else {
                uri.find('/').map_or("", |index| &uri[index..])
            };
            PathBuf::from(path)
        } else if reference.starts_with('/') {
            PathBuf::from(reference.split('#').next().unwrap_or(""))
        } else {
            let relative = reference.split('#').next().unwrap_or("");
            let decoded = percent_decode_str(relative).decode_utf8_lossy();
            path.parent().unwrap_or(root).join(decoded.as_ref())
        };
        if !target.exists() {
            broken.push(json!({
                "arquivo": path.strip_prefix(root).unwrap_or(path).to_string_lossy(),
                "destino": reference,
            }));
        }
    }
    broken
}

fn audit(root: &Path) -> Result<(Value, bool), String> {
    let base = root.join("BaseConhecimento");
    let connection = database(&base.join("base.db"))?;
    let mut report = Map::new();
    let mut banks = Map::new();
    for (name, path) in [
        ("geral", base.join("base.db")),
        ("tahoe_local", base.join("MacTahoe/base.db")),
    ] {
        if path.exists() {
            banks.insert(name.into(), check_db(name, &path)?);
        }
    }
    report.insert("bancos".into(), Value::Object(banks));
    let records = documents(&connection)?;
    let mut states = Map::new();
    for record in &records {
        let value = states.entry(record.state.clone()).or_insert(json!(0));
        *value = json!(value.as_i64().unwrap_or(0) + 1);
    }
    let mut docs = Map::new();
    docs.insert("estados".into(), Value::Object(states));
    docs.insert(
        "fontes_ausentes_preservadas".into(),
        json!(records.iter().filter(|record| !record.present).count()),
    );
    docs.insert("duplicatas_exatas".into(), json!(count(&connection,
        "SELECT count(*) FROM (SELECT sha256 FROM documentos WHERE presente=1 AND sha256 IS NOT NULL GROUP BY sha256 HAVING count(*)>1)")?));
    report.insert("documentos".into(), Value::Object(docs));
    let mut active: Vec<PathBuf> = OPERATIONAL.iter().map(|name| root.join(name)).collect();
    let mut divergent = Vec::new();
    for record in &records {
        if !record.present {
            continue;
        }
        let path = base.join(&record.path);
        let hash_mismatch = if path.exists() {
            if let Some(expected) = &record.digest {
                let bytes = fs::read(&path).map_err(|error| error.to_string())?;
                hex::encode(Sha256::digest(bytes)) != *expected
            } else {
                false
            }
        } else {
            true
        };
        if hash_mismatch {
            divergent.push(json!(record.path));
        }
        if ["verified", "experimental"].contains(&record.state.as_str())
            && path.extension().and_then(|ext| ext.to_str()) == Some("md")
            && path.exists()
        {
            active.push(path);
        }
    }
    let regex = Regex::new(r"!?\[[^\]]*\]\(([^)]+)\)").unwrap();
    let mut broken = Vec::new();
    for path in active {
        if path.exists() {
            broken.extend(links(&path, root, &regex));
        }
    }
    report.insert("links_quebrados".into(), Value::Array(broken));
    report.insert("hash_divergente".into(), Value::Array(divergent));
    report.insert("registros_duplicados".into(), json!(count(&connection,
        "SELECT count(*) FROM (SELECT sha256 FROM registros WHERE sha256 IS NOT NULL GROUP BY sha256 HAVING count(*)>1)")?));
    report.insert("trechos_sem_documento".into(), json!(count(&connection,
        "SELECT count(*) FROM (SELECT DISTINCT t.caminho FROM trechos t LEFT JOIN documentos d ON d.caminho=t.caminho WHERE d.caminho IS NULL)")?));
    let value = Value::Object(report);
    let bad_bank = value["bancos"].as_object().unwrap().values().any(|bank| {
        bank["integridade"] != "ok"
            || bank["erros_fk"].as_i64().unwrap_or(0) != 0
            || bank["classificacao_sem_fonte_ou_ausente"]
                .as_i64()
                .unwrap_or(0)
                != 0
    });
    let bad = bad_bank
        || value["documentos"]["duplicatas_exatas"]
            .as_i64()
            .unwrap_or(0)
            != 0
        || value["registros_duplicados"].as_i64().unwrap_or(0) != 0
        || value["trechos_sem_documento"].as_i64().unwrap_or(0) != 0
        || !value["links_quebrados"].as_array().unwrap().is_empty()
        || !value["hash_divergente"].as_array().unwrap().is_empty();
    Ok((value, bad))
}

fn main() {
    let root = std::env::var_os("HYPRMAC_REPO_ROOT")
        .map(PathBuf::from)
        .unwrap_or_else(|| PathBuf::from("."));
    match audit(&root) {
        Ok((report, bad)) => {
            println!("{}", serde_json::to_string_pretty(&report).unwrap());
            if bad {
                std::process::exit(1);
            }
        }
        Err(error) => {
            eprintln!("{error}");
            std::process::exit(2);
        }
    }
}
