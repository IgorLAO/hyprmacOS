//! Pequenas consultas de estado usadas pelos scripts do compositor.
use serde_json::Value;
use std::env;
use std::fs;
use std::path::{Path, PathBuf};
use std::process::Command;

fn config_path() -> Result<PathBuf, String> {
    Ok(PathBuf::from(env::var_os("HOME").ok_or("HOME ausente")?)
        .join(".config/hyprmac/config.json"))
}

fn config_value(key: &str, default: &str) -> Result<String, String> {
    let data = fs::read_to_string(config_path()?)
        .ok()
        .and_then(|text| serde_json::from_str::<Value>(&text).ok());
    let value = data.as_ref().and_then(|data| data.get(key));
    Ok(match value {
        Some(Value::Bool(value)) => if *value { "True" } else { "False" }.into(),
        Some(Value::String(value)) => value.clone(),
        Some(Value::Number(value)) => value.to_string(),
        _ => default.into(),
    })
}

fn scratchpad_count() -> Result<i64, String> {
    let output = Command::new("hyprctl")
        .args(["workspaces", "-j"])
        .output()
        .map_err(|error| error.to_string())?;
    if !output.status.success() {
        return Err(String::from_utf8_lossy(&output.stderr).into());
    }
    let data: Value = serde_json::from_slice(&output.stdout).map_err(|error| error.to_string())?;
    Ok(data
        .as_array()
        .into_iter()
        .flatten()
        .filter(|workspace| workspace.get("name").and_then(Value::as_str) == Some("special:magic"))
        .map(|workspace| {
            workspace
                .get("windows")
                .and_then(Value::as_i64)
                .unwrap_or(0)
        })
        .sum())
}

fn lock_ready(pidfile: &Path, executable: &Path) -> bool {
    let Some(pid) = fs::read_to_string(pidfile)
        .ok()
        .and_then(|text| text.trim().parse::<u32>().ok())
    else {
        return false;
    };
    if pid == 0 {
        return false;
    }
    // /proc/<pid>/cmdline only exists while the process is alive and is readable to this user.
    let Some(args) = fs::read(format!("/proc/{pid}/cmdline")).ok() else {
        return false;
    };
    let expected = executable.as_os_str().as_encoded_bytes();
    args.split(|byte| *byte == 0).any(|arg| arg == expected)
}

fn main() {
    let args = env::args().skip(1).collect::<Vec<_>>();
    let result = match args.as_slice() {
        [command, key, default] if command == "config" => config_value(key, default).map(|value| { println!("{value}"); 0 }),
        [command] if command == "scratchpad-count" => scratchpad_count().map(|count| { println!("{count}"); 0 }),
        [command, pidfile, executable] if command == "lock-ready" => Ok(if lock_ready(Path::new(pidfile), Path::new(executable)) { 0 } else { 1 }),
        _ => Err("uso: hyprmac-runtime config <chave> <padrão> | scratchpad-count | lock-ready <pidfile> <executável>".into()),
    };
    match result {
        Ok(code) => std::process::exit(code),
        Err(error) => {
            eprintln!("{error}");
            std::process::exit(2);
        }
    }
}
