use chrono::{Local, Timelike};
use serde_json::Value;
use std::env;
use std::fs;
use std::os::unix::ffi::OsStrExt;
use std::os::unix::fs::symlink;
use std::os::unix::process::CommandExt;
use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};

const WATCHER: &str = "hyprmac-aparencia-ocioso";

fn root() -> PathBuf {
    env::var_os("HYPRMAC_ROOT")
        .map(PathBuf::from)
        .unwrap_or_else(|| {
            Path::new(&env::var("HOME").unwrap_or_default()).join("Projects/hyprmac")
        })
}

fn wanted(mode: &str, hour: u32) -> Option<&'static str> {
    if mode != "auto" {
        return None;
    }
    Some(if (7..19).contains(&hour) {
        "light"
    } else {
        "dark"
    })
}

fn mode() -> String {
    let path = Path::new(&env::var("HOME").unwrap_or_default()).join(".config/hyprmac/config.json");
    fs::read(path)
        .ok()
        .and_then(|data| serde_json::from_slice::<Value>(&data).ok())
        .and_then(|value| value["appearance_mode"].as_str().map(str::to_owned))
        .unwrap_or_else(|| "dark".to_owned())
}

fn current() -> String {
    let output = Command::new("gsettings")
        .args(["get", "org.gnome.desktop.interface", "color-scheme"])
        .stdout(Stdio::piped())
        .stderr(Stdio::null())
        .output();
    match output {
        Ok(output) if String::from_utf8_lossy(&output.stdout).contains("dark") => "dark".to_owned(),
        _ => "light".to_owned(),
    }
}

fn check() -> Result<(), String> {
    let Some(theme) = wanted(&mode(), Local::now().hour()) else {
        return Ok(());
    };
    if theme != current() {
        Command::new(root().join("scripts/theme"))
            .arg(theme)
            .status()
            .map_err(|e| e.to_string())?;
    }
    Ok(())
}

fn stop_previous_watchers() {
    let Ok(entries) = fs::read_dir("/proc") else {
        return;
    };
    for entry in entries.flatten() {
        let Some(pid) = entry
            .file_name()
            .to_str()
            .and_then(|name| name.parse::<i32>().ok())
        else {
            continue;
        };
        if pid == std::process::id() as i32 {
            continue;
        }
        let Ok(command) = fs::read(entry.path().join("cmdline")) else {
            continue;
        };
        let Some(first) = command.split(|byte| *byte == 0).next() else {
            continue;
        };
        if Path::new(std::ffi::OsStr::from_bytes(first)).file_name()
            == Some(std::ffi::OsStr::new(WATCHER))
        {
            unsafe {
                libc::kill(pid, libc::SIGTERM);
            }
        }
    }
}

fn start() -> Result<(), String> {
    let root = root();
    let binary = root.join("shell/ocioso/hyprmac-ocioso");
    if !binary.exists() {
        let status = Command::new("make")
            .args(["-s", "-C"])
            .arg(binary.parent().ok_or("caminho do vigia inválido")?)
            .status()
            .map_err(|e| e.to_string())?;
        if !status.success() {
            return Err("não foi possível compilar o vigia de inatividade".into());
        }
    }
    let runtime = env::var("XDG_RUNTIME_DIR").unwrap_or_else(|_| "/tmp".into());
    let link = Path::new(&runtime).join(WATCHER);
    if fs::symlink_metadata(&link).is_ok() {
        fs::remove_file(&link).map_err(|e| e.to_string())?;
    }
    symlink(&binary, &link).map_err(|e| e.to_string())?;
    stop_previous_watchers();
    let check_command = format!(
        "{}/.local/bin/hyprmac-aparencia check",
        env::var("HOME").unwrap_or_default()
    );
    let error = Command::new(&link).args(["60", &check_command]).exec();
    Err(error.to_string())
}

fn main() {
    let result = match env::args().nth(1).as_deref().unwrap_or("check") {
        "check" => check(),
        "start" => start(),
        _ => Err("uso: hyprmac-aparencia [start|check]".into()),
    };
    if let Err(error) = result {
        eprintln!("{error}");
        std::process::exit(2);
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn automatic_schedule() {
        assert_eq!(wanted("auto", 6), Some("dark"));
        assert_eq!(wanted("auto", 7), Some("light"));
        assert_eq!(wanted("auto", 18), Some("light"));
        assert_eq!(wanted("auto", 19), Some("dark"));
        assert_eq!(wanted("light", 23), None);
        assert_eq!(wanted("dark", 12), None);
    }

    #[test]
    fn watcher_name_is_distinct_from_screen_idle_service() {
        assert_ne!(WATCHER, "hyprmac-ocioso");
    }
}
