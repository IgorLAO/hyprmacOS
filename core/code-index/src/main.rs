//! Índice leve de código para busca progressiva dos componentes.
use regex::Regex;
use serde_json::{json, Value};
use sha2::{Digest, Sha256};
use std::fs;
use std::path::{Path, PathBuf};
use walkdir::WalkDir;

const ROOTS: [&str; 12] = [
    "core", "cursores", "ghostty", "gtk", "hypr", "kde", "kitty", "scripts", "shell", "tests",
    "waybar", "wofi",
];
const SKIP: [&str; 11] = [
    ".git",
    ".obsidian",
    "__pycache__",
    ".venv",
    ".backups",
    "models",
    "base.db",
    "backup",
    "video",
    "images",
    "target",
];

fn language(path: &Path, bytes: &[u8]) -> Option<&'static str> {
    let ext = path
        .extension()
        .and_then(|value| value.to_str())
        .unwrap_or("")
        .to_lowercase();
    // Os caminhos históricos .py dos geradores migrados são invólucros Bash.
    if ext == "py" && bytes.starts_with(b"#!/usr/bin/env bash") {
        return Some("bash");
    }
    match ext.as_str() {
        "py" => Some("python"),
        "lua" => Some("lua"),
        "css" => Some("css"),
        "sh" => Some("bash"),
        "json" => Some("json"),
        "jsonc" => Some("jsonc"),
        "js" => Some("javascript"),
        "md" => Some("markdown"),
        "rs" => Some("rust"),
        "" => {
            let first = bytes.split(|byte| *byte == b'\n').next().unwrap_or(&[]);
            if !first.starts_with(b"#!") {
                return None;
            }
            let first = String::from_utf8_lossy(&first[..first.len().min(160)]).to_lowercase();
            if first.contains("python") {
                Some("python")
            } else if first.contains("bash") || first.contains("/sh") {
                Some("bash")
            } else {
                None
            }
        }
        _ => None,
    }
}

fn symbol_pattern(language: &str) -> Option<&'static str> {
    match language {
        "python" => Some(r"^\s*(?:async\s+)?(?:def|class)\s+([A-Za-z_]\w*)"),
        "lua" => Some(r"^\s*(?:local\s+)?function\s+([A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*)"),
        "bash" => Some(r"^\s*(?:function\s+)?([A-Za-z_]\w*)\s*\(\)\s*\{?"),
        "css" => Some(r"^\s*([^/@][^{]{1,100})\s*\{"),
        "rust" => Some(
            r"^\s*(?:pub(?:\([^)]*\))?\s+)?(?:async\s+)?(?:fn|struct|enum|trait)\s+([A-Za-z_]\w*)",
        ),
        _ => None,
    }
}

fn import_pattern(language: &str) -> Option<&'static str> {
    match language {
        "python" => Some(r"^\s*(?:from\s+([^\s]+)\s+import|import\s+([^\s#]+))"),
        "lua" => Some(r#"require\s*[\("]([^\)"]+)"#),
        "javascript" => Some(r#"(?:from|require\s*\()\s*["']([^"']+)"#),
        "css" => Some(r#"@import\s+["']([^"']+)"#),
        "rust" => Some(r"^\s*use\s+([^;]+);"),
        _ => None,
    }
}

fn unique_values(
    text: &str,
    language: &str,
    pattern: Option<&str>,
    limit: usize,
    css: bool,
) -> Vec<String> {
    let Some(pattern) = pattern else {
        return Vec::new();
    };
    let regex = Regex::new(pattern).unwrap();
    let spaces = Regex::new(r"\s+").unwrap();
    let mut values = Vec::new();
    for line in text.lines() {
        if let Some(capture) = regex.captures(line) {
            let value = capture.iter().skip(1).flatten().next().unwrap().as_str();
            let candidates: Vec<String> = if css && language == "css" {
                value
                    .split(',')
                    .map(|part| spaces.replace_all(part, " ").trim().to_string())
                    .collect()
            } else {
                vec![value.trim().to_string()]
            };
            for candidate in candidates {
                if !candidate.is_empty() && !values.contains(&candidate) && values.len() < limit {
                    values.push(
                        candidate
                            .chars()
                            .take(if css { 100 } else { usize::MAX })
                            .collect(),
                    );
                }
            }
        }
    }
    values
}

fn summary(text: &str, path: &Path) -> String {
    let comments = Regex::new(r"^\s*(#|//|--|/\*+|\*+)\s?").unwrap();
    let mut useful = Vec::new();
    for line in text.lines() {
        if line.trim().is_empty() || line.trim_start().starts_with("#!") {
            continue;
        }
        let stripped = comments.replace(line, "").trim().to_string();
        if ["#!", "{", "}", "import ", "from "]
            .iter()
            .any(|prefix| stripped.starts_with(prefix))
        {
            continue;
        }
        useful.push(stripped);
        if useful.len() == 2 {
            break;
        }
    }
    let text = if useful.is_empty() {
        path.file_name().unwrap().to_string_lossy().into_owned()
    } else {
        useful.join(" ")
    };
    text.chars().take(280).collect()
}

fn tags(path: &Path, text: &str) -> Vec<String> {
    let mut out: Vec<String> = Vec::new();
    for tag in [
        "shell", "hypr", "waybar", "scripts", "tests", "gtk", "kde", "kitty", "ghostty", "wofi",
    ] {
        if path
            .components()
            .any(|component| component.as_os_str() == tag)
        {
            out.push(tag.into());
        }
    }
    let low = format!("{} {text}", path.file_name().unwrap().to_string_lossy()).to_lowercase();
    for word in [
        "dock",
        "control center",
        "spotlight",
        "notification",
        "lock",
        "menu",
        "glass",
        "theme",
        "window",
    ] {
        if low.contains(word) && !out.iter().any(|tag| tag == word) {
            out.push(word.into());
        }
    }
    if ["central de controle", "hyprmac-cc", ".cc", "control center"]
        .iter()
        .any(|word| low.contains(word))
    {
        for word in ["control", "center", "control_center"] {
            if !out.iter().any(|tag| tag == word) {
                out.push(word.into());
            }
        }
    }
    out
}

fn collect(root: &Path) -> Result<Vec<Value>, String> {
    let mut out = Vec::new();
    for name in ROOTS {
        let dir = root.join(name);
        if !dir.exists() {
            continue;
        }
        let mut paths: Vec<PathBuf> = WalkDir::new(dir)
            .into_iter()
            .filter_map(Result::ok)
            .filter(|entry| entry.file_type().is_file())
            .map(|entry| entry.into_path())
            .collect();
        paths.sort();
        for path in paths {
            if path
                .components()
                .any(|part| SKIP.iter().any(|skip| part.as_os_str() == *skip))
            {
                continue;
            }
            let bytes = fs::read(&path).map_err(|error| error.to_string())?;
            let Some(lang) = language(&path, &bytes) else {
                continue;
            };
            let text = String::from_utf8_lossy(&bytes);
            let rel = path.strip_prefix(root).map_err(|error| error.to_string())?;
            let rel = rel
                .to_string_lossy()
                .replace(std::path::MAIN_SEPARATOR, "/");
            let syms = unique_values(&text, lang, symbol_pattern(lang), 120, true);
            let imports = unique_values(&text, lang, import_pattern(lang), 40, false);
            out.push(json!({
                "path": rel, "language": lang, "bytes": bytes.len(), "lines": text.lines().count(),
                "summary": summary(&text, &path), "symbols": syms, "imports": imports,
                "tags": tags(&path, &text), "sha256": hex::encode(Sha256::digest(&bytes)),
            }));
        }
    }
    Ok(out)
}

fn markdown(items: &[Value]) -> String {
    let mut lines: Vec<String> = [
        "# Índice de código para agentes",
        "",
        "Metadados para localizar candidatos antes de ler arquivos completos.",
        "",
        "| Caminho | Linguagem | Linhas | Tags | Resumo |",
        "|---|---|---:|---|---|",
    ]
    .into_iter()
    .map(str::to_string)
    .collect();
    for item in items {
        let tags = item["tags"]
            .as_array()
            .unwrap()
            .iter()
            .take(6)
            .filter_map(Value::as_str)
            .collect::<Vec<_>>()
            .join(", ");
        lines.push(format!(
            "| `{}` | {} | {} | {} | {} |",
            item["path"].as_str().unwrap(),
            item["language"].as_str().unwrap(),
            item["lines"].as_u64().unwrap(),
            tags,
            item["summary"].as_str().unwrap().replace('|', "/")
        ));
    }
    lines.extend(
        [
            "",
            "## Recuperação progressiva",
            "",
            "1. filtre por caminho, linguagem ou tag;",
            "2. leia `summary` e `symbols`;",
            "3. recupere um trecho relevante;",
            "4. carregue o arquivo completo somente quando necessário.",
            "",
        ]
        .map(str::to_string),
    );
    lines.join("\n")
}

fn run(root: &Path) -> Result<(), String> {
    let items = collect(root)?;
    let base = root.join("BaseConhecimento");
    let output = base.join("codigo.json");
    let data = json!({"schema": 1, "items": items});
    fs::write(&output, serde_json::to_string_pretty(&data).unwrap() + "\n")
        .map_err(|error| error.to_string())?;
    fs::write(
        base.join("INDICE-CODIGO-AGENTES.md"),
        markdown(data["items"].as_array().unwrap()),
    )
    .map_err(|error| error.to_string())?;
    println!(
        "{} arquivos indexados → {}",
        data["items"].as_array().unwrap().len(),
        output.display()
    );
    Ok(())
}

fn main() {
    let root = std::env::var_os("HYPRMAC_REPO_ROOT")
        .map(PathBuf::from)
        .unwrap_or_else(|| PathBuf::from("."));
    if let Err(error) = run(&root) {
        eprintln!("{error}");
        std::process::exit(1);
    }
}
