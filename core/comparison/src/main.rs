//! Recalcula a matriz interna a partir de parametros.json e de valores no código.
use regex::Regex;
use rusqlite::{params, Connection};
use serde_json::Value;
use std::env;
use std::fs;
use std::path::{Path, PathBuf};

struct Area {
    name: String,
    sum: f64,
    weight: i64,
    indices: Vec<usize>,
}

fn string<'a>(value: &'a Value, key: &str) -> &'a str {
    value.get(key).and_then(Value::as_str).unwrap_or("")
}

fn icon(status: &str) -> &'static str {
    match status {
        "conforme" => "✅",
        "proximo" => "🟡",
        "diverge" => "🔴",
        "ausente" => "⬜",
        "limitacao" => "➖",
        _ => "?",
    }
}

fn points(status: &str) -> Option<f64> {
    match status {
        "conforme" => Some(1.0),
        "proximo" => Some(0.5),
        "diverge" | "ausente" => Some(0.0),
        _ => None,
    }
}

fn read_value(p: &Value, root: &Path) -> (Option<String>, Option<f64>) {
    let Some(reading) = p.get("leitura") else {
        return (None, None);
    };
    let file = root.join(string(reading, "arquivo"));
    let Ok(content) = fs::read_to_string(file) else {
        return (Some("arquivo não encontrado".into()), None);
    };
    let Ok(regex) = Regex::new(&format!("(?m){}", string(reading, "regex"))) else {
        return (Some("não encontrado (regex)".into()), None);
    };
    let Some(capture) = regex.captures(&content) else {
        return (Some("não encontrado (regex)".into()), None);
    };
    let Some(value) = capture.get(1) else {
        return (Some("não encontrado (regex)".into()), None);
    };
    let value = value.as_str().to_string();
    let divisor_pattern = string(reading, "divisor_regex");
    if !divisor_pattern.is_empty() {
        if let Ok(divisor_regex) = Regex::new(&format!("(?m){divisor_pattern}")) {
            if let Some(divisor) = divisor_regex
                .captures(&content)
                .and_then(|groups| groups.get(1))
            {
                if let (Ok(numerator), Ok(denominator)) =
                    (value.parse::<f64>(), divisor.as_str().parse::<f64>())
                {
                    let number = numerator / denominator;
                    return (
                        Some(format!("{value} ÷ {} = {number:.3}", divisor.as_str())),
                        Some(number),
                    );
                }
            }
        }
    }
    let number = value.parse::<f64>().ok();
    (Some(value), number)
}

fn evaluate(p: &mut Value, root: &Path) {
    let (text, number) = read_value(p, root);
    if let Some(text) = text {
        p["hyprmac"] = Value::String(text.clone());
        p["medido"] = Value::Bool(true);
        let reading = &p["leitura"];
        let equal = string(reading, "igual");
        if !equal.is_empty() {
            p["status"] = Value::String(
                if text.to_lowercase() == equal.to_lowercase() {
                    "conforme"
                } else {
                    "diverge"
                }
                .into(),
            );
        } else if let (Some(number), Some(target)) = (number, p.get("alvo").and_then(Value::as_f64))
        {
            let diff = (number - target).abs();
            let tolerance = p.get("tolerancia").and_then(Value::as_f64).unwrap_or(0.0);
            let status = if diff <= tolerance + 1e-9 {
                "conforme"
            } else if diff <= (3.0 * tolerance).max(0.10 * target.abs()) {
                "proximo"
            } else {
                "diverge"
            };
            p["status"] = Value::String(status.into());
        } else if p.get("status").is_none() {
            p["status"] = Value::String("diverge".into());
        }
    }
    if p.get("status").is_none() {
        p["status"] = Value::String("ausente".into());
    }
    if p.get("hyprmac").is_none() {
        p["hyprmac"] = Value::String("—".into());
    }
}

fn areas_for(items: &[Value]) -> Vec<Area> {
    let mut areas: Vec<Area> = Vec::new();
    for (index, item) in items.iter().enumerate() {
        let name = string(item, "area");
        let position = areas
            .iter()
            .position(|area| area.name == name)
            .unwrap_or_else(|| {
                areas.push(Area {
                    name: name.to_string(),
                    sum: 0.0,
                    weight: 0,
                    indices: Vec::new(),
                });
                areas.len() - 1
            });
        let area = &mut areas[position];
        area.indices.push(index);
        if let Some(score) = points(string(item, "status")) {
            let weight = item.get("peso").and_then(Value::as_i64).unwrap_or(1);
            area.sum += score * weight as f64;
            area.weight += weight;
        }
    }
    areas
}

fn percent(sum: f64, weight: i64) -> f64 {
    if weight == 0 {
        0.0
    } else {
        100.0 * sum / weight as f64
    }
}

fn optional<'a>(value: &'a Value, key: &str) -> Option<&'a str> {
    value.get(key).and_then(Value::as_str)
}

fn write_db(path: &Path, items: &[Value]) -> Result<(), String> {
    if !path.exists() {
        return Ok(());
    }
    let mut connection = Connection::open(path).map_err(|error| error.to_string())?;
    let transaction = connection
        .transaction()
        .map_err(|error| error.to_string())?;
    transaction.execute_batch("DROP TABLE IF EXISTS parametros;
        CREATE TABLE parametros (id TEXT PRIMARY KEY, area TEXT, parametro TEXT, apple TEXT,
        hyprmac TEXT, status TEXT, prioridade TEXT, peso INT, onde TEXT, fonte TEXT, medir TEXT, nota TEXT);")
        .map_err(|error| error.to_string())?;
    {
        let mut statement = transaction
            .prepare("INSERT INTO parametros VALUES (?,?,?,?,?,?,?,?,?,?,?,?)")
            .map_err(|error| error.to_string())?;
        for item in items {
            statement
                .execute(params![
                    string(item, "id"),
                    string(item, "area"),
                    string(item, "parametro"),
                    string(item, "apple"),
                    string(item, "hyprmac"),
                    string(item, "status"),
                    string(item, "prioridade"),
                    item.get("peso").and_then(Value::as_i64).unwrap_or(1),
                    optional(item, "onde"),
                    optional(item, "fonte"),
                    optional(item, "medir"),
                    optional(item, "nota"),
                ])
                .map_err(|error| error.to_string())?;
        }
    }
    transaction.commit().map_err(|error| error.to_string())
}

fn report(root: &Path, items: &[Value], areas: &[Area], total: f64) -> Result<(), String> {
    let mut out = vec![
        "# Matriz de comparação — hyprmac × Apple (macOS Tahoe/27)".to_string(),
        "".into(),
        "Gerada por `ferramentas/comparar.py` a partir de `comparacao/parametros.json`. Valores marcados com 📏 foram **lidos do código agora**; os outros foram avaliados à mão.".into(),
        "".into(),
        "Legenda: ✅ conforme · 🟡 próximo · 🔴 diverge · ⬜ ausente · ➖ limitação do Linux (não conta). Prioridade: **P1** visível/perigoso · **P2** notável · **P3** detalhe.".into(),
        "".into(),
        format!("## Nota geral: **{total:.0}%**"),
        "".into(),
        "| Área | Nota | ✅ | 🟡 | 🔴 | ⬜ |".into(),
        "|---|---|---|---|---|---|".into(),
    ];
    for area in areas {
        let count = |status: &str| {
            area.indices
                .iter()
                .filter(|&&index| string(&items[index], "status") == status)
                .count()
        };
        out.push(format!(
            "| {} | {:.0}% | {} | {} | {} | {} |",
            area.name,
            percent(area.sum, area.weight),
            count("conforme"),
            count("proximo"),
            count("diverge"),
            count("ausente")
        ));
    }
    out.extend(["", "## Pendências P1", ""].map(str::to_string));
    for item in items {
        let status = string(item, "status");
        if string(item, "prioridade") == "P1" && status != "conforme" && status != "limitacao" {
            out.push(format!(
                "- {} **{} {}** — Apple: {}; hyprmac: {}",
                icon(status),
                string(item, "id"),
                string(item, "parametro"),
                string(item, "apple"),
                string(item, "hyprmac")
            ));
        }
    }
    for area in areas {
        out.extend([
            "".to_string(),
            format!("## {} — {:.0}%", area.name, percent(area.sum, area.weight)),
            "".into(),
            "| ID | Parâmetro | Apple | hyprmac | | Prio | Onde | Fonte |".into(),
            "|---|---|---|---|---|---|---|---|".into(),
        ]);
        for &index in &area.indices {
            let item = &items[index];
            let measured = if item.get("medido").and_then(Value::as_bool).unwrap_or(false) {
                " 📏"
            } else {
                ""
            };
            let note = optional(item, "nota")
                .filter(|value| !value.is_empty())
                .map(|value| format!("<br>_{value}_"))
                .unwrap_or_default();
            out.push(format!(
                "| {} | {} | {} | {}{}{} | {} | {} | `{}` | {} |",
                string(item, "id"),
                string(item, "parametro"),
                string(item, "apple"),
                string(item, "hyprmac"),
                measured,
                note,
                icon(string(item, "status")),
                string(item, "prioridade"),
                string(item, "onde"),
                string(item, "fonte")
            ));
        }
    }
    out.extend(["", "## Como medir cada um", ""].map(str::to_string));
    for item in items {
        out.push(format!(
            "- **{}** — {}",
            string(item, "id"),
            string(item, "medir")
        ));
    }
    let matrix = root.join("BaseConhecimento/comparacao/MATRIZ.md");
    fs::write(&matrix, out.join("\n") + "\n").map_err(|error| error.to_string())?;
    write_db(&root.join("BaseConhecimento/base.db"), items)?;
    println!(
        "{} parâmetros · nota geral {total:.0}% → {}",
        items.len(),
        matrix.display()
    );
    Ok(())
}

fn run(root: &Path, args: &[String]) -> Result<(), String> {
    let file = root.join("BaseConhecimento/comparacao/parametros.json");
    let content = fs::read_to_string(file).map_err(|error| error.to_string())?;
    let document: Value = serde_json::from_str(&content).map_err(|error| error.to_string())?;
    let mut items = document["parametros"]
        .as_array()
        .ok_or("parametros ausentes")?
        .clone();
    for (index, item) in items.iter_mut().enumerate() {
        let missing: Vec<_> = ["id", "area", "parametro", "apple", "prioridade"]
            .into_iter()
            .filter(|key| item.get(*key).is_none())
            .collect();
        if !missing.is_empty() {
            return Err(format!(
                "parametros.json: registro {index} sem {}",
                missing.join(", ")
            ));
        }
        evaluate(item, root);
    }
    let areas = areas_for(&items);
    let sum: f64 = areas.iter().map(|area| area.sum).sum();
    let weight: i64 = areas.iter().map(|area| area.weight).sum();
    let total = percent(sum, weight);
    if args.iter().any(|arg| arg == "--resumo") {
        for area in &areas {
            println!(
                "{:<28} {:>5.0}%  ({} parâmetros)",
                area.name,
                percent(area.sum, area.weight),
                area.indices.len()
            );
        }
        println!("{:<28} {:>5.0}%", "TOTAL", total);
    } else if args.iter().any(|arg| arg == "--pendentes") {
        for priority in ["P1", "P2", "P3"] {
            for item in &items {
                let status = string(item, "status");
                if string(item, "prioridade") == priority
                    && status != "conforme"
                    && status != "limitacao"
                {
                    println!(
                        "{priority} {} {:<8} {} — Apple: {} · hyprmac: {}",
                        icon(status),
                        string(item, "id"),
                        string(item, "parametro"),
                        string(item, "apple"),
                        string(item, "hyprmac")
                    );
                }
            }
        }
    } else {
        report(root, &items, &areas, total)?;
    }
    Ok(())
}

fn main() {
    let root = env::var_os("HYPRMAC_REPO_ROOT")
        .map(PathBuf::from)
        .unwrap_or_else(|| PathBuf::from("."));
    let args: Vec<_> = env::args().skip(1).collect();
    if let Err(error) = run(&root, &args) {
        eprintln!("{error}");
        std::process::exit(1);
    }
}
