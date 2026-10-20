//! Capturas do shell: preserva os modos e as opções do comando scripts/screenshot.
use serde_json::Value;
use std::collections::HashSet;
use std::env;
use std::fs::{self, File};
use std::io::Write;
use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};
use std::thread;
use std::time::Duration;

const SLURP_ARGS: &[&str] = &[
    "-d",
    "-b",
    "#0000004d",
    "-c",
    "#ffffffd9",
    "-s",
    "#ffffff14",
    "-w",
    "1",
    "-F",
    "Inter Variable",
];

fn output(program: &str, args: &[&str]) -> Result<String, String> {
    let out = Command::new(program)
        .args(args)
        .output()
        .map_err(|error| format!("{program}: {error}"))?;
    if !out.status.success() {
        return Err(format!(
            "{program} falhou: {}",
            String::from_utf8_lossy(&out.stderr)
        ));
    }
    Ok(String::from_utf8_lossy(&out.stdout)
        .trim_end_matches('\n')
        .to_string())
}

fn hypr_json(name: &str) -> Result<Value, String> {
    serde_json::from_str(&output("hyprctl", &[name, "-j"])?).map_err(|error| error.to_string())
}

fn point_size(client: &Value) -> Option<String> {
    let at = client.get("at")?.as_array()?;
    let size = client.get("size")?.as_array()?;
    Some(format!(
        "{},{} {}x{}",
        at.first()?.as_i64()?,
        at.get(1)?.as_i64()?,
        size.first()?.as_i64()?,
        size.get(1)?.as_i64()?
    ))
}

fn visible_rectangles(monitors: &Value, clients: &Value) -> Vec<String> {
    let active: HashSet<i64> = monitors
        .as_array()
        .into_iter()
        .flatten()
        .flat_map(|monitor| {
            [
                monitor
                    .pointer("/activeWorkspace/id")
                    .and_then(Value::as_i64),
                monitor
                    .pointer("/specialWorkspace/id")
                    .and_then(Value::as_i64),
            ]
            .into_iter()
            .flatten()
        })
        .collect();
    clients
        .as_array()
        .into_iter()
        .flatten()
        .filter(|client| {
            client.get("mapped").and_then(Value::as_bool) == Some(true)
                && client.get("hidden").and_then(Value::as_bool) == Some(false)
                && client
                    .pointer("/workspace/id")
                    .and_then(Value::as_i64)
                    .is_some_and(|id| active.contains(&id))
        })
        .filter_map(point_size)
        .collect()
}

fn select_rectangle(rectangles: Option<&[String]>) -> Result<Option<String>, String> {
    let mut command = Command::new("slurp");
    if rectangles.is_some() {
        command.arg("-r");
    }
    command.args(SLURP_ARGS).stdout(Stdio::piped());
    if rectangles.is_some() {
        command.stdin(Stdio::piped());
    }
    let mut child = command.spawn().map_err(|error| format!("slurp: {error}"))?;
    if let Some(rectangles) = rectangles {
        let Some(mut stdin) = child.stdin.take() else {
            return Err("slurp sem stdin".into());
        };
        let data = rectangles.join("\n") + "\n";
        if let Err(error) = stdin.write_all(data.as_bytes()) {
            if error.kind() != std::io::ErrorKind::BrokenPipe {
                return Err(error.to_string());
            }
        }
    }
    let result = child
        .wait_with_output()
        .map_err(|error| error.to_string())?;
    if !result.status.success() {
        return Ok(None);
    }
    let geometry = String::from_utf8_lossy(&result.stdout).trim().to_owned();
    Ok((!geometry.is_empty()).then_some(geometry))
}

fn capture(file: &Path, mode: &str, delay: u64, cursor: bool) -> Result<bool, String> {
    let destination = file.to_string_lossy().to_string();
    let mut args: Vec<String> = match mode {
        "pick" => {
            let rectangles = visible_rectangles(&hypr_json("monitors")?, &hypr_json("clients")?);
            let Some(geometry) = select_rectangle(Some(&rectangles))? else {
                return Ok(false);
            };
            vec!["-g".into(), geometry, destination]
        }
        "region" => {
            let Some(geometry) = select_rectangle(None)? else {
                return Ok(false);
            };
            vec!["-g".into(), geometry, destination]
        }
        "screen" => {
            let monitors = hypr_json("monitors")?;
            let monitor = monitors
                .as_array()
                .into_iter()
                .flatten()
                .find(|monitor| monitor.get("focused").and_then(Value::as_bool) == Some(true))
                .and_then(|monitor| monitor.get("name"))
                .and_then(Value::as_str)
                .ok_or("monitor em foco ausente")?;
            vec!["-o".into(), monitor.into(), destination]
        }
        "window" => {
            let Some(geometry) = point_size(&hypr_json("activewindow")?) else {
                return Ok(false);
            };
            vec!["-g".into(), geometry, destination]
        }
        _ => return Err("uso: screenshot [region|screen|window|pick]".into()),
    };
    if cursor {
        args.insert(0, "-c".into());
    }
    if delay > 0 {
        thread::sleep(Duration::from_secs(delay));
    }
    let status = Command::new("grim")
        .args(args)
        .status()
        .map_err(|error| format!("grim: {error}"))?;
    if !status.success() {
        return Err(format!("grim encerrou com {status}"));
    }
    Ok(true)
}

fn config_sound(home: &Path) -> bool {
    let path = home.join(".config/hyprmac/config.json");
    let data = fs::read_to_string(path)
        .ok()
        .and_then(|text| serde_json::from_str::<Value>(&text).ok());
    data.as_ref()
        .and_then(|data| data.get("ui_sound_effects"))
        .and_then(Value::as_bool)
        .unwrap_or(true)
}

fn command_exists(name: &str) -> bool {
    env::split_paths(&env::var_os("PATH").unwrap_or_default()).any(|dir| dir.join(name).is_file())
}

fn main_result() -> Result<(), String> {
    let mode = env::args().nth(1).unwrap_or_else(|| "region".into());
    if !["region", "screen", "window", "pick"].contains(&mode.as_str()) {
        return Err("uso: screenshot [region|screen|window|pick]".into());
    }
    let home = PathBuf::from(env::var_os("HOME").ok_or("HOME ausente")?);
    let dir = env::var_os("HYPRMAC_SCREENSHOT_DIR")
        .map(PathBuf::from)
        .unwrap_or_else(|| home.join("Desktop"));
    fs::create_dir_all(&dir).map_err(|error| error.to_string())?;
    let clipboard_only = env::var("HYPRMAC_SHOT_CLIPBOARD").as_deref() == Ok("1");
    let file = if clipboard_only {
        PathBuf::from(env::var_os("XDG_RUNTIME_DIR").unwrap_or_else(|| "/tmp".into()))
            .join("hyprmac-captura.png")
    } else {
        let stamp = output("date", &["+%Y-%m-%d às %H.%M.%S"])?;
        dir.join(format!("Captura de Tela {stamp}.png"))
    };
    let delay = env::var("HYPRMAC_SHOT_DELAY")
        .ok()
        .and_then(|value| value.parse::<u64>().ok())
        .unwrap_or(0);
    let cursor = env::var("HYPRMAC_SHOT_CURSOR").as_deref() == Ok("1");
    if !capture(&file, &mode, delay, cursor)? {
        return Ok(());
    }
    let nonempty = fs::metadata(&file).is_ok_and(|metadata| metadata.len() > 0);
    if nonempty && config_sound(&home) {
        let _ = Command::new("setsid")
            .args([
                "-f",
                "canberra-gtk-play",
                "-i",
                "screen-capture",
                "-d",
                "hyprmac-ui",
            ])
            .stdout(Stdio::null())
            .stderr(Stdio::null())
            .status();
    }
    if command_exists("wl-copy") {
        if let Ok(input) = File::open(&file) {
            let _ = Command::new("wl-copy")
                .args(["--type", "image/png"])
                .stdin(input)
                .status();
        }
    }
    if clipboard_only {
        fs::remove_file(&file).map_err(|error| error.to_string())?;
        return Ok(());
    }
    if env::var("HYPRMAC_SHOT_THUMB").as_deref() == Ok("0") {
        return Ok(());
    }
    let thumbnail = home.join(".local/bin/hyprmac-captura-miniatura");
    let status = Command::new("setsid")
        .args(["-f", &thumbnail.to_string_lossy(), &file.to_string_lossy()])
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .status();
    if !status.is_ok_and(|status| status.success()) {
        let display_dir =
            dir.to_string_lossy()
                .replacen(&home.to_string_lossy().to_string(), "~", 1);
        let _ = Command::new("notify-send")
            .args([
                "-a",
                "Captura de Tela",
                "-i",
                &file.to_string_lossy(),
                "-t",
                "3000",
                "Captura de Tela",
                &format!("Salva em {display_dir}"),
            ])
            .status();
    }
    Ok(())
}

fn main() {
    if let Err(error) = main_result() {
        eprintln!("{error}");
        std::process::exit(1);
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use serde_json::json;

    #[test]
    fn pick_uses_only_visible_clients_on_active_workspaces() {
        let monitors = json!([{"activeWorkspace":{"id":2},"specialWorkspace":{"id":99}}]);
        let clients = json!([
            {"mapped":true,"hidden":false,"workspace":{"id":2},"at":[10,20],"size":[300,200]},
            {"mapped":true,"hidden":false,"workspace":{"id":99},"at":[1,2],"size":[20,30]},
            {"mapped":true,"hidden":true,"workspace":{"id":2},"at":[0,0],"size":[1,1]},
            {"mapped":true,"hidden":false,"workspace":{"id":3},"at":[0,0],"size":[1,1]}
        ]);
        assert_eq!(
            visible_rectangles(&monitors, &clients),
            ["10,20 300x200", "1,2 20x30"]
        );
    }
}
