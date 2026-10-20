//! Consulta somente leitura à Base de Conhecimento.
use regex::Regex;
use rusqlite::{params, params_from_iter, types::Value as SqlValue, Connection, OpenFlags};
use serde_json::{Map, Value};
use std::env;
use std::path::{Path, PathBuf};
use unicode_normalization::{char::is_combining_mark, UnicodeNormalization};

#[derive(Default)]
struct Options {
    terms: Vec<String>,
    kind: Option<String>,
    count: usize,
    complete: bool,
    color: Option<String>,
    typography: Option<String>,
    style: Option<String>,
    image: Option<String>,
    code: Option<String>,
    record: Option<String>,
    document: Option<String>,
    historical: bool,
    all: bool,
    sql: Option<String>,
}

fn parse(args: &[String]) -> Result<Options, String> {
    let mut opts = Options { count: 5, ..Default::default() };
    let mut index = 0;
    while index < args.len() {
        let argument = args[index].as_str();
        let mut value = || -> Result<String, String> {
            index += 1;
            args.get(index).cloned().ok_or_else(|| format!("valor ausente para {argument}"))
        };
        match argument {
            "-t" | "--tipo-trecho" => opts.kind = Some(value()?),
            "-n" => opts.count = value()?.parse().map_err(|_| "-n deve ser inteiro".to_string())?,
            "--completo" => opts.complete = true,
            "--cor" => opts.color = Some(value()?),
            "--tipo-texto" | "--tipografia" => opts.typography = Some(value()?),
            "--estilo" => opts.style = Some(value()?),
            "--imagem" => opts.image = Some(value()?),
            "--codigo" => opts.code = Some(value()?),
            "--registro" => opts.record = Some(value()?),
            "--documento" => opts.document = Some(value()?),
            "--historico" => opts.historical = true,
            "--todos" => opts.all = true,
            "--sql" => opts.sql = Some(value()?),
            "-h" | "--help" => { help(); std::process::exit(0); }
            other if other.starts_with('-') => return Err(format!("opção desconhecida: {other}")),
            other => opts.terms.push(other.to_string()),
        }
        index += 1;
    }
    if !(1..=20).contains(&opts.count) { return Err("-n deve estar entre 1 e 20".into()); }
    if opts.all && opts.historical { return Err("--todos e --historico são mutuamente exclusivos".into()); }
    Ok(opts)
}

fn help() {
    println!("consultar.py <termos> [-t TIPO] [-n 1..20] [--completo] [--historico|--todos]");
    println!("consultar.py --cor|--tipo-texto|--estilo|--imagem|--codigo|--registro|--documento TERMO");
    println!("consultar.py --sql 'SELECT …' (somente leitura)");
}

fn query(connection: &Connection, sql: &str, arguments: &[SqlValue]) -> Result<Vec<Vec<SqlValue>>, String> {
    let mut statement = connection.prepare(sql).map_err(|error| error.to_string())?;
    let columns = statement.column_count();
    let rows = statement.query_map(params_from_iter(arguments), |row| {
        (0..columns).map(|index| row.get::<_, SqlValue>(index)).collect::<Result<Vec<_>, _>>()
    }).map_err(|error| error.to_string())?;
    rows.collect::<Result<Vec<_>, _>>().map_err(|error| error.to_string())
}

fn display(value: &SqlValue) -> String {
    match value {
        SqlValue::Null => "None".into(), SqlValue::Integer(number) => number.to_string(),
        SqlValue::Real(number) => number.to_string(), SqlValue::Text(text) => text.clone(),
        SqlValue::Blob(bytes) => format!("{bytes:?}"),
    }
}

fn cell(row: &[SqlValue], index: usize) -> String {
    row.get(index).map(display).unwrap_or_default()
}

fn nonnull(row: &[SqlValue], index: usize) -> String {
    let value = cell(row, index);
    if value == "None" { String::new() } else { value }
}

fn fallback(value: String) -> String {
    if value.is_empty() { "—".into() } else { value }
}

fn python_json(value: &Value) -> String {
    match value {
        Value::Array(items) => format!("[{}]", items.iter().map(python_json).collect::<Vec<_>>().join(", ")),
        Value::Object(items) => format!("{{{}}}", items.iter().map(|(key, value)| {
            format!("{}: {}", serde_json::to_string(key).unwrap(), python_json(value))
        }).collect::<Vec<_>>().join(", ")),
        _ => serde_json::to_string(value).unwrap(),
    }
}

fn fts_query(text: &str) -> String {
    let syntax = Regex::new(r#"["()*]|\b(?:OR|AND|NOT|NEAR)\b"#).unwrap();
    if syntax.is_match(text) { return text.into(); }
    let terms = Regex::new(r"[\w#./-]+").unwrap();
    terms.find_iter(text).map(|term| format!("\"{}\"*", term.as_str())).collect::<Vec<_>>().join(" ")
}

fn like(connection: &Connection, table: &str, columns: &[&str], text: &str) -> Result<Vec<Vec<SqlValue>>, String> {
    let words: Vec<_> = text.split_whitespace().collect();
    let expression = columns.join(" || \" \" || ");
    let conditions = (0..words.len()).map(|_| format!("lower({expression}) LIKE ?")).collect::<Vec<_>>().join(" AND ");
    let sql = if conditions.is_empty() { format!("SELECT * FROM {table}") }
        else { format!("SELECT * FROM {table} WHERE {conditions}") };
    let arguments = words.iter().map(|word| SqlValue::Text(format!("%{}%", word.to_lowercase()))).collect::<Vec<_>>();
    query(connection, &sql, &arguments)
}

fn no_accents(value: &str) -> String {
    value.to_lowercase().nfd().filter(|character| !is_combining_mark(*character)).collect()
}

fn is_word(character: char) -> bool {
    character.is_alphanumeric() || character == '_'
}

fn whole_word(haystack: &str, needle: &str) -> bool {
    if needle.is_empty() { return true; }
    haystack.match_indices(needle).any(|(index, _)| {
        let before = haystack[..index].chars().next_back();
        let after = haystack[index + needle.len()..].chars().next();
        !before.is_some_and(is_word) && !after.is_some_and(is_word)
    })
}

fn norm_code(value: &str) -> String {
    let accents = no_accents(value);
    Regex::new(r"[_/.-]+").unwrap().replace_all(&accents, " ").to_string()
}

fn main_query(connection: &Connection, base: &Path, opts: &Options) -> Result<(), String> {
    if let Some(sql) = &opts.sql {
        let mut statement = connection.prepare(sql).map_err(|error| error.to_string())?;
        let columns = statement.column_count();
        let rows = statement.query_map([], |row| (0..columns).map(|index| row.get::<_, SqlValue>(index)).collect::<Result<Vec<_>, _>>())
            .map_err(|error| error.to_string())?;
        for row in rows { println!("{}", row.map_err(|error| error.to_string())?.iter().map(display).collect::<Vec<_>>().join(" | ")); }
        return Ok(());
    }
    if let Some(document) = &opts.document {
        let mut statement = connection.prepare("SELECT * FROM documentos WHERE caminho=?").map_err(|error| error.to_string())?;
        let columns = statement.column_names().iter().map(|name| name.to_string()).collect::<Vec<_>>();
        let rows = statement.query_map(params![document], |row| {
            let mut object = Map::new();
            for (index, name) in columns.iter().enumerate() {
                let value: SqlValue = row.get(index)?;
                let json = match value {
                    SqlValue::Null => Value::Null, SqlValue::Integer(v) => Value::from(v),
                    SqlValue::Real(v) => Value::from(v), SqlValue::Text(v) => Value::from(v),
                    SqlValue::Blob(_) => Value::Null,
                };
                object.insert(name.clone(), json);
            }
            Ok(Value::Object(object))
        }).map_err(|error| error.to_string())?;
        if let Some(row) = rows.into_iter().next() {
            println!("{}", serde_json::to_string_pretty(&row.map_err(|error| error.to_string())?).unwrap());
        } else { println!("documento não registrado"); }
        return Ok(());
    }
    if let Some(record) = &opts.record {
        let states = if opts.all { "" } else if opts.historical {
            " AND r.estado IN ('archived','superseded','invalid')"
        } else { " AND r.estado IN ('verified','experimental')" };
        let sql = format!("SELECT r.id,r.tipo,r.componente,r.estado,r.versao_macos,r.titulo,r.resumo,r.evidencia,r.fonte_caminho,r.fonte_url,r.confianca,r.implementacao,bm25(registros_fts) AS rank FROM registros_fts JOIN registros r ON r.rowid=registros_fts.rowid WHERE registros_fts MATCH ?{states} ORDER BY rank LIMIT ?");
        let rows = query(connection, &sql, &[SqlValue::Text(fts_query(record)), SqlValue::Integer(opts.count as i64)])?;
        for row in &rows {
            println!("\n■ {} [{}; {}; {}] {} · {}\n  {}\n  {}", cell(row, 0), cell(row, 3), cell(row, 4), cell(row, 10), cell(row, 1), fallback(nonnull(row, 2)), cell(row, 5), cell(row, 6));
            println!("  Evidência: {} · Fonte: {} · Código: {}", fallback(nonnull(row, 7)), fallback(if nonnull(row, 9).is_empty() { nonnull(row, 8) } else { nonnull(row, 9) }), fallback(nonnull(row, 11)));
        }
        if rows.is_empty() { println!("nenhum registro com estes filtros"); }
        return Ok(());
    }
    if let Some(color) = &opts.color {
        for row in like(connection, "cores", &["kit", "grupo", "nome"], color)?.iter().take(opts.count) {
            println!("{:<9} {:<62} {:<12} {}", cell(row, 0), format!("{}/{}", cell(row, 1), cell(row, 2)), cell(row, 3), cell(row, 4));
        }
        return Ok(());
    }
    if let Some(typography) = &opts.typography {
        for row in like(connection, "tipografia", &["kit", "nome", "fonte"], typography)?.iter().take(opts.count) {
            println!("{:<9} {:<55} {} {}/{} {}", cell(row, 0), cell(row, 1), cell(row, 2), cell(row, 3), if nonnull(row, 4).is_empty() { "0".into() } else { cell(row, 4) }, cell(row, 5));
        }
        return Ok(());
    }
    if let Some(style) = &opts.style {
        for row in like(connection, "estilos", &["kit", "nome"], style)?.iter().take(opts.count) {
            println!("\n■ {} · {}", cell(row, 0), cell(row, 1));
            let data: Value = serde_json::from_str(&cell(row, 2)).map_err(|error| error.to_string())?;
            if let Some(object) = data.as_object() {
                for (key, value) in object { println!("   {key}: {}", python_json(value)); }
            }
        }
        return Ok(());
    }
    if let Some(image) = &opts.image {
        let sql = "SELECT caminho, categoria, estado, prioridade, titulo, descricao, uso, largura, altura, triagem, classificacao_fonte, confianca, sequencia FROM imagens_catalogo ORDER BY CASE prioridade WHEN 'golden' THEN 0 WHEN 'canonical' THEN 1 ELSE 2 END, caminho";
        let terms = image.to_lowercase().split_whitespace().map(str::to_string).collect::<Vec<_>>();
        let rows = query(connection, sql, &[]).unwrap_or_default().into_iter().filter(|row| {
            let text = no_accents(&row.iter().map(|value| if *value == SqlValue::Null { String::new() } else { display(value) }).collect::<Vec<_>>().join(" "));
            terms.iter().all(|term| whole_word(&text, &no_accents(term)))
        }).take(opts.count).collect::<Vec<_>>();
        for row in &rows {
            println!("\n■ [{}] {} · {}\n  {}", cell(row, 3), cell(row, 1), cell(row, 2), base.join(cell(row, 0)).display());
            println!("  {} — {}", cell(row, 4), cell(row, 5));
            let sequence = nonnull(row, 12);
            let sequence = if sequence.is_empty() || sequence == "null" { String::new() }
                else if let Ok(data) = serde_json::from_str::<Value>(&sequence) {
                    if data["grupo"].is_string() && !data["ordem"].is_null() && !data["total"].is_null() {
                        format!(" · sequência: {} {}/{}", data["grupo"].as_str().unwrap(), data["ordem"], data["total"])
                    } else { format!(" · sequência: {sequence}") }
                } else { format!(" · sequência: {sequence}") };
            println!("  uso: {} · dimensão: {}×{} · triagem: {}", cell(row, 6), cell(row, 7), cell(row, 8), base.join("referencias/telas").join(cell(row, 9)).display());
            println!("  classificação: {} ({}){sequence}", cell(row, 10), cell(row, 11));
        }
        if !rows.is_empty() { return Ok(()); }
        for row in like(connection, "imagens", &["caminho", "descricao"], image)?.iter().take(opts.count) {
            println!("{}\n    {}  [{}]", base.join(cell(row, 0)).display(), cell(row, 1).chars().take(220).collect::<String>(), cell(row, 2));
        }
        return Ok(());
    }
    if let Some(code) = &opts.code {
        let terms = code.to_lowercase().split_whitespace().map(str::to_string).collect::<Vec<_>>();
        let mut rows = query(connection, "SELECT caminho, linguagem, linhas, resumo, simbolos, imports, tags FROM codigo_catalogo ORDER BY linhas DESC", &[]).unwrap_or_default()
            .into_iter().filter(|row| {
                let text = norm_code(&row.iter().map(|value| if *value == SqlValue::Null { String::new() } else { display(value) }).collect::<Vec<_>>().join(" "));
                terms.iter().all(|term| whole_word(&text, &norm_code(term)))
            }).collect::<Vec<_>>();
        rows.sort_by_key(|row| {
            let basename = Path::new(&cell(row, 0)).file_name().unwrap().to_string_lossy().into_owned();
            let tokens = norm_code(&basename).split_whitespace().map(str::to_string).collect::<Vec<_>>();
            (!terms.iter().all(|term| tokens.contains(term)), -cell(row, 2).parse::<i64>().unwrap_or(0))
        });
        for row in rows.iter().take(opts.count) {
            println!("\n■ {} · {} · {} linhas", cell(row, 0), cell(row, 1), cell(row, 2));
            println!("  {}", cell(row, 3));
            let symbols = nonnull(row, 4).split(", ").take(12).collect::<Vec<_>>().join(", ");
            println!("  símbolos: {}", fallback(symbols));
            println!("  imports: {} · tags: {}", fallback(nonnull(row, 5)), fallback(nonnull(row, 6)));
        }
        return Ok(());
    }
    if opts.terms.is_empty() { help(); return Ok(()); }
    let fts = fts_query(&opts.terms.join(" "));
    let states = if opts.all { "" } else if opts.historical {
        " AND d.estado IN ('archived','superseded','invalid')"
    } else { " AND d.estado IN ('verified','experimental')" };
    let extra = if opts.kind.is_some() { " AND trechos.tipo = ?" } else { "" };
    let sql = format!("WITH candidatos AS MATERIALIZED (SELECT trechos.rowid AS rid, trechos.caminho, trechos.tipo, trechos.titulo, trechos.secao, d.estado, d.versao_macos, (bm25(trechos, 1.0, 4.0, 3.0) - CASE trechos.tipo WHEN 'componente' THEN 0.15 WHEN 'padrao' THEN 0.10 ELSE 0 END - CASE d.versao_macos WHEN 'Tahoe 26' THEN 0.08 WHEN 'macOS 27 (declared)' THEN -0.05 ELSE 0 END) AS rank FROM trechos JOIN documentos d ON d.caminho=trechos.caminho WHERE trechos MATCH ?{states}{extra}) SELECT caminho,tipo,titulo,secao,estado,versao_macos,rid,MIN(rank) AS melhor FROM candidatos GROUP BY caminho ORDER BY melhor LIMIT ?");
    let mut arguments = vec![SqlValue::Text(fts.clone())];
    if let Some(kind) = &opts.kind { arguments.push(SqlValue::Text(kind.clone())); }
    arguments.push(SqlValue::Integer(opts.count as i64));
    let rows = query(connection, &sql, &arguments)?;
    if rows.is_empty() { println!("nada para: {fts}"); }
    for row in &rows {
        let id = cell(row, 6).parse::<i64>().map_err(|error| error.to_string())?;
        let text: String = if opts.complete {
            connection.query_row("SELECT conteudo FROM trechos WHERE rowid=?", params![id], |row| row.get(0))
        } else {
            connection.query_row("SELECT snippet(trechos, 0, '»', '«', ' … ', 40) FROM trechos WHERE trechos MATCH ? AND rowid=?", params![fts, id], |row| row.get(0))
        }.map_err(|error| error.to_string())?;
        println!("\n■ [{}; {}; {}] {} › {}\n  {}", cell(row, 1), cell(row, 4), cell(row, 5), cell(row, 2), cell(row, 3), base.join(cell(row, 0)).display());
        println!("  {}", text.trim().replace('\n', "\n  "));
    }
    Ok(())
}

fn main() {
    let args: Vec<_> = env::args().skip(1).collect();
    let opts = match parse(&args) { Ok(opts) => opts, Err(error) => { eprintln!("{error}"); std::process::exit(2); } };
    let root = env::var_os("HYPRMAC_REPO_ROOT").map(PathBuf::from).unwrap_or_else(|| PathBuf::from("."));
    let base = root.join("BaseConhecimento");
    let db = base.join("base.db");
    if !db.exists() { eprintln!("sem índice: rode {}", base.join("ferramentas/indexar.py").display()); std::process::exit(1); }
    let connection = match Connection::open_with_flags(&db, OpenFlags::SQLITE_OPEN_READ_ONLY) {
        Ok(connection) => connection, Err(error) => { eprintln!("{error}"); std::process::exit(1); }
    };
    if let Err(error) = connection.execute_batch("PRAGMA query_only=ON") { eprintln!("{error}"); std::process::exit(1); }
    if let Err(error) = main_query(&connection, &base, &opts) { eprintln!("{error}"); std::process::exit(1); }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn fts_preserves_explicit_syntax_and_expands_plain_terms() {
        assert_eq!(fts_query("liquid glass"), "\"liquid\"* \"glass\"*");
        assert_eq!(fts_query("dock OR spotlight"), "dock OR spotlight");
        assert_eq!(fts_query("\"control center\""), "\"control center\"");
    }

    #[test]
    fn normalized_catalog_search_keeps_word_boundaries() {
        assert!(whole_word(&no_accents("Central de Controle"), "controle"));
        assert!(!whole_word(&norm_code("dock_widget.py"), "dockw"));
        assert!(whole_word(&norm_code("dock_widget.py"), "widget"));
    }

    #[test]
    fn sql_mode_cannot_modify_database() {
        let connection = Connection::open_in_memory().unwrap();
        connection.execute_batch("CREATE TABLE exemplo (valor INTEGER); PRAGMA query_only=ON").unwrap();
        let opts = Options { sql: Some("INSERT INTO exemplo VALUES (1)".into()), ..Default::default() };
        assert!(main_query(&connection, Path::new("."), &opts).is_err());
        let count: i64 = connection.query_row("SELECT COUNT(*) FROM exemplo", [], |row| row.get(0)).unwrap();
        assert_eq!(count, 0);
    }
}
