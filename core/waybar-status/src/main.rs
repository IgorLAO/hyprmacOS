use chrono::{Datelike, Local, Timelike};
use regex::Regex;
use serde_json::{json, Value};
use std::env;
use std::fs;
use std::io::{self, Read, Write};
use std::os::fd::AsRawFd;
use std::os::unix::net::UnixStream;
use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};
use std::time::Duration;

mod menu_extras;

fn runtime_path(name: &str) -> PathBuf {
    Path::new(&env::var("XDG_RUNTIME_DIR").unwrap_or_else(|_| "/tmp".into())).join(name)
}

fn config_path(name: &str) -> PathBuf {
    Path::new(&env::var("HOME").unwrap_or_default())
        .join(".config/hyprmac")
        .join(name)
}

fn read_json(path: &Path) -> Option<Value> {
    serde_json::from_slice(&fs::read(path).ok()?).ok()
}

fn visible(key: &str) -> bool {
    read_json(&config_path("barra.json"))
        .and_then(|v| v.get("hidden")?.as_array().cloned())
        .map(|list| !list.iter().any(|item| item.as_str() == Some(key)))
        .unwrap_or(false)
}

fn status(on: bool, active_text: &str, tooltip: &str) -> Value {
    json!({"text": if on {active_text} else {""}, "class": if on {"on"} else {"off"}, "tooltip": if on {tooltip} else {""}})
}

fn process_exists(pid: i32) -> bool {
    if pid <= 0 {
        return false;
    }
    let result = unsafe { libc::kill(pid, 0) };
    result == 0 || io::Error::last_os_error().raw_os_error() == Some(libc::EPERM)
}

fn active_class() -> String {
    if let Some(state) = read_json(&runtime_path("hyprmac-active-class.json")) {
        if let (Some(pid), Some(class)) = (state["pid"].as_i64(), state["class"].as_str()) {
            if i32::try_from(pid).ok().is_some_and(process_exists) {
                return class.to_owned();
            }
        }
    }
    // Keep the fallback bounded if Hyprland is unresponsive.
    let output = Command::new("timeout")
        .args(["2", "hyprctl", "activewindow", "-j"])
        .stdout(Stdio::piped())
        .stderr(Stdio::null())
        .output();
    output
        .ok()
        .and_then(|out| serde_json::from_slice::<Value>(&out.stdout).ok())
        .and_then(|v| v["class"].as_str().map(str::to_owned))
        .unwrap_or_default()
}

fn menu(args: &[String]) -> Result<Value, String> {
    if args.len() != 2 {
        return Err("uso: hyprmac-waybar app-menu <rótulo> <regex de classe>".into());
    }
    let re = Regex::new(&args[1]).map_err(|e| e.to_string())?;
    Ok(json!({"text": if re.is_match(&active_class()) {&args[0]} else {""}}))
}

fn headphones() -> Value {
    let out = Command::new("timeout")
        .args(["2", "wpctl", "inspect", "@DEFAULT_AUDIO_SINK@"])
        .stdout(Stdio::piped())
        .stderr(Stdio::null())
        .output();
    let text = out
        .ok()
        .map(|out| String::from_utf8_lossy(&out.stdout).to_lowercase())
        .unwrap_or_default();
    let on = visible("headphones")
        && ["bluez_output", "headphones", "headset", "earbuds"]
            .iter()
            .any(|word| text.contains(word));
    status(on, "󰋋", "Headphones · Sound Outputs")
}

fn layout_status(devices: &Value) -> Option<Value> {
    let keyboards = devices.get("keyboards")?.as_array()?;
    let keyboard = keyboards
        .iter()
        .find(|item| item["main"] == true)
        .or_else(|| keyboards.first())?;
    let layouts = keyboard["layout"].as_str()?.split(',').collect::<Vec<_>>();
    let index = keyboard["active_layout_index"].as_u64().unwrap_or(0) as usize;
    let layout = layouts
        .get(index.min(layouts.len() - 1))?
        .trim()
        .to_uppercase();
    Some(json!({"text": layout, "tooltip": keyboard["active_keymap"].as_str().unwrap_or("")}))
}

fn show_layout() -> Result<(), String> {
    let output = Command::new("timeout")
        .args(["2", "hyprctl", "devices", "-j"])
        .stdout(Stdio::piped())
        .stderr(Stdio::null())
        .output()
        .map_err(|e| e.to_string())?;
    if let Ok(devices) = serde_json::from_slice::<Value>(&output.stdout) {
        if let Some(status) = layout_status(&devices) {
            println!("{status}");
            io::stdout().flush().map_err(|e| e.to_string())?;
        }
    }
    Ok(())
}

fn layout_events() -> Result<(), String> {
    let signature = env::var("HYPRLAND_INSTANCE_SIGNATURE").map_err(|e| e.to_string())?;
    let socket_path = runtime_path("hypr").join(signature).join(".socket2.sock");
    let mut socket = UnixStream::connect(&socket_path).map_err(|e| e.to_string())?;
    show_layout()?;
    let mut pending = Vec::new();
    let mut chunk = [0_u8; 65536];
    loop {
        let mut fds = [
            libc::pollfd {
                fd: socket.as_raw_fd(),
                events: libc::POLLIN,
                revents: 0,
            },
            libc::pollfd {
                fd: libc::STDOUT_FILENO,
                events: 0,
                revents: 0,
            },
        ];
        let count = unsafe { libc::poll(fds.as_mut_ptr(), fds.len() as libc::nfds_t, -1) };
        if count < 0 {
            if io::Error::last_os_error().kind() == io::ErrorKind::Interrupted {
                continue;
            }
            return Err(io::Error::last_os_error().to_string());
        }
        if fds[1].revents != 0 || fds[0].revents & (libc::POLLHUP | libc::POLLERR) != 0 {
            return Ok(());
        }
        if fds[0].revents & libc::POLLIN == 0 {
            continue;
        }
        let size = socket.read(&mut chunk).map_err(|e| e.to_string())?;
        if size == 0 {
            return Ok(());
        }
        pending.extend_from_slice(&chunk[..size]);
        let mut refresh = false;
        while let Some(end) = pending.iter().position(|byte| *byte == b'\n') {
            let line = pending.drain(..=end).collect::<Vec<_>>();
            refresh |= line.starts_with(b"activelayout>>");
        }
        if refresh {
            show_layout()?;
        }
        // Hyprland lines are short; bound memory if an invalid peer never sends a newline.
        if pending.len() > 65536 {
            pending.clear();
        }
    }
}

fn about_message(class: &str, executable: Option<&Path>, package: Option<&str>) -> String {
    let mut lines = Vec::new();
    if let Some(package) = package {
        if let Some((name, version)) = package.split_once(' ') {
            lines.push(format!("Versão: {version}"));
            lines.push(format!("Pacote: {name}"));
        }
    }
    lines.push(format!("Classe: {class}"));
    if let Some(path) = executable {
        lines.push(format!("Programa: {}", path.display()));
    }
    lines.join("\n")
}

fn app_about() -> Result<(), String> {
    let output = Command::new("timeout")
        .args(["2", "hyprctl", "activewindow", "-j"])
        .stdout(Stdio::piped())
        .stderr(Stdio::null())
        .output()
        .map_err(|e| e.to_string())?;
    let window: Value = match serde_json::from_slice(&output.stdout) {
        Ok(value) => value,
        Err(_) => return Ok(()),
    };
    let Some(class) = window["class"].as_str().filter(|s| !s.is_empty()) else {
        return Ok(());
    };
    let pid = window["pid"].as_i64().unwrap_or(0);
    let executable = fs::canonicalize(format!("/proc/{pid}/exe")).ok();
    let package = executable.as_ref().and_then(|exe| {
        Command::new("timeout")
            .args(["2", "pacman", "-Qo"])
            .arg(exe)
            .stdout(Stdio::piped())
            .stderr(Stdio::null())
            .output()
            .ok()
            .filter(|out| out.status.success())
            .and_then(|out| String::from_utf8(out.stdout).ok())
            .and_then(|text| {
                text.trim()
                    .split_once(" is owned by ")
                    .map(|(_, tail)| tail.to_owned())
            })
    });
    let name = class.rsplit('.').next().unwrap_or(class);
    let mut chars = name.chars();
    let display_name = chars
        .next()
        .map(|first| first.to_uppercase().collect::<String>() + chars.as_str())
        .unwrap_or_default();
    let body = about_message(class, executable.as_deref(), package.as_deref());
    Command::new("notify-send")
        .args([
            "-a",
            &display_name,
            "-i",
            class,
            &format!("About {display_name}"),
            &body,
        ])
        .status()
        .map_err(|e| e.to_string())?;
    Ok(())
}

const DAYS: [&str; 7] = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
const LONG_DAYS: [&str; 7] = [
    "Monday",
    "Tuesday",
    "Wednesday",
    "Thursday",
    "Friday",
    "Saturday",
    "Sunday",
];
const MONTHS: [&str; 12] = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
];
const LONG_MONTHS: [&str; 12] = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
];

fn pref_bool(prefs: &Value, key: &str, default: bool) -> bool {
    prefs.get(key).and_then(Value::as_bool).unwrap_or(default)
}

fn clock_text(now: chrono::DateTime<Local>, prefs: &Value, h24: bool) -> String {
    let mut parts = Vec::new();
    let day = now.weekday().num_days_from_monday() as usize;
    let month = now.month0() as usize;
    if pref_bool(prefs, "show_day_of_week", true) {
        parts.push(DAYS[day].to_owned());
    }
    if prefs["show_date"].as_str() == Some("always") {
        parts.push(format!("{} {}", MONTHS[month], now.day()));
    }
    let sep = if pref_bool(prefs, "flash_separators", false) && now.second() % 2 == 1 {
        "<span alpha=\"1\">:</span>"
    } else {
        ":"
    };
    let hour = if h24 {
        now.hour()
    } else {
        (now.hour() + 11) % 12 + 1
    };
    let mut time = format!("{hour}{sep}{:02}", now.minute());
    if pref_bool(prefs, "show_seconds", false) {
        time.push_str(&format!("{sep}{:02}", now.second()));
    }
    if !h24 && pref_bool(prefs, "show_ampm", true) {
        time.push_str(if now.hour() < 12 { " AM" } else { " PM" });
    }
    parts.push(time);
    parts.join(" ")
}

fn clock_line() -> Value {
    let prefs = read_json(&config_path("relogio.json")).unwrap_or(Value::Null);
    let h24 = read_json(&config_path("ajustes.json"))
        .and_then(|v| v.get("clock_24h").and_then(Value::as_bool))
        .unwrap_or(true);
    let now = Local::now();
    let tooltip = format!(
        "{}, {} {}, {}",
        LONG_DAYS[now.weekday().num_days_from_monday() as usize],
        LONG_MONTHS[now.month0() as usize],
        now.day(),
        now.year()
    );
    json!({"text": clock_text(now, &prefs, h24), "tooltip": tooltip})
}

fn clock() -> Result<(), String> {
    let mut set = unsafe { std::mem::zeroed::<libc::sigset_t>() };
    unsafe {
        libc::sigemptyset(&mut set);
        libc::sigaddset(&mut set, libc::SIGUSR1);
        libc::pthread_sigmask(libc::SIG_BLOCK, &set, std::ptr::null_mut());
    }
    loop {
        println!("{}", clock_line());
        io::stdout().flush().map_err(|e| e.to_string())?;
        let prefs = read_json(&config_path("relogio.json")).unwrap_or(Value::Null);
        let now = Local::now();
        let seconds_tick = pref_bool(&prefs, "show_seconds", false)
            || pref_bool(&prefs, "flash_separators", false);
        let wait_secs = if seconds_tick { 1 } else { 60 - now.second() };
        let wait = Duration::from_secs(wait_secs as u64)
            .saturating_sub(Duration::from_nanos(now.nanosecond() as u64));
        let timeout = libc::timespec {
            tv_sec: wait.as_secs() as libc::time_t,
            tv_nsec: wait.subsec_nanos() as libc::c_long,
        };
        unsafe {
            libc::sigtimedwait(&set, std::ptr::null_mut(), &timeout);
        }
    }
}

fn run() -> Result<(), String> {
    let mut args = env::args().skip(1);
    let command = args.next().ok_or(
        "uso: hyprmac-waybar <app-menu|add-controls|recording|headphones|sleep-focus|clock|input-source|app-about|menu-extras-pref>",
    )?;
    if command == "clock" {
        return clock();
    }
    if command == "input-source" {
        return layout_events();
    }
    if command == "app-about" {
        return app_about();
    }
    if command == "menu-extras-pref" {
        return menu_extras::run(&args.collect::<Vec<_>>());
    }
    let result = match command.as_str() {
        "app-menu" => menu(&args.collect::<Vec<_>>())?,
        "add-controls" => status(
            runtime_path("hyprmac-cc-edit").exists(),
            "+",
            "Add Controls to Menu Bar",
        ),
        "recording" => {
            let on = fs::read_to_string(runtime_path("hyprmac-gravacao.pid"))
                .ok()
                .and_then(|s| s.trim().parse::<i32>().ok())
                .is_some_and(process_exists);
            status(on, "   ", "Stop Screen Recording")
        }
        "headphones" => headphones(),
        "sleep-focus" => {
            let on = visible("sleep")
                && fs::read_to_string(runtime_path("hyprmac-dnd"))
                    .is_ok_and(|s| s.trim() == "sleep");
            status(on, "󰒲", "Sleep Focus")
        }
        _ => return Err(format!("comando desconhecido: {command}")),
    };
    println!("{result}");
    Ok(())
}

fn main() {
    if let Err(error) = run() {
        eprintln!("{error}");
        std::process::exit(2);
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use chrono::TimeZone;

    #[test]
    fn clock_options() {
        let dt = Local.with_ymd_and_hms(2026, 10, 11, 17, 5, 9).unwrap();
        assert_eq!(clock_text(dt, &json!({}), true), "Sun 17:05");
        assert_eq!(
            clock_text(
                dt,
                &json!({"show_date":"always","show_seconds":true}),
                false
            ),
            "Sun Oct 11 5:05:09 PM"
        );
        assert_eq!(
            clock_text(dt, &json!({"flash_separators":true}), true),
            "Sun 17<span alpha=\"1\">:</span>05"
        );
    }

    #[test]
    fn missing_config_hides_optional_items() {
        assert!(!visible("sleep"));
        assert!(!visible("headphones"));
    }

    #[test]
    fn layout_uses_main_keyboard_and_active_index() {
        let devices = json!({"keyboards": [
            {"main":false,"layout":"us","active_layout_index":0,"active_keymap":"English"},
            {"main":true,"layout":"us,br","active_layout_index":1,"active_keymap":"Portuguese (Brazil)"}
        ]});
        assert_eq!(
            layout_status(&devices),
            Some(json!({"text":"BR","tooltip":"Portuguese (Brazil)"}))
        );
    }

    #[test]
    fn about_formats_package_and_executable() {
        assert_eq!(
            about_message(
                "dev.hyprmac.Notes",
                Some(Path::new("/usr/bin/notes")),
                Some("notes 1.2")
            ),
            "Versão: 1.2\nPacote: notes\nClasse: dev.hyprmac.Notes\nPrograma: /usr/bin/notes"
        );
    }
}
