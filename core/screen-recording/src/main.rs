//! Gravação de tela ⇧⌘5; processo wf-recorder e controle GTK/LayerShell.
mod hypr;
mod process_control;
mod ui;

use gtk::glib::{self, ControlFlow};
use hypr::{focused_monitor, window_rectangles};
use process_control::{recording_delay, runtime_file, stop_existing};
use std::cell::RefCell;
use std::env;
use std::fs;
use std::path::{Path, PathBuf};
use std::process::{Child, Command, Stdio};
use std::rc::Rc;
use std::time::{Duration, Instant};

struct Recorder {
    child: Child,
    file: PathBuf,
    started: Instant,
    pidfile: PathBuf,
    filemark: PathBuf,
    loop_: glib::MainLoop,
    stopped: bool,
}

fn notify_missing(tool: &str) {
    let message = format!("Instale o {tool} para gravar a tela (ex.: pacman -S {tool}).");
    let _ = Command::new("notify-send")
        .args(["-a", "Gravação de Tela", "Gravação de Tela", &message])
        .spawn();
}

fn destination() -> Result<PathBuf, String> {
    let folder = env::var_os("HYPRMAC_REC_DIR")
        .filter(|value| !value.is_empty())
        .map(PathBuf::from)
        .or_else(|| glib::user_special_dir(glib::UserDirectory::Videos))
        .unwrap_or_else(|| PathBuf::from(env::var_os("HOME").unwrap_or_default()).join("Movies"));
    fs::create_dir_all(&folder).map_err(|error| error.to_string())?;
    Ok(folder)
}

fn file_name() -> Result<String, String> {
    let now = glib::DateTime::now_local().map_err(|error| error.to_string())?;
    now.format("Gravação de Tela %Y-%m-%d às %H.%M.%S.mp4")
        .map(|name| name.to_string())
        .map_err(|error| error.to_string())
}

fn pick_geometry(mode: &str) -> Result<Option<String>, String> {
    let mut cmd = Command::new("slurp");
    cmd.args([
        "-b",
        "#0000004d",
        "-c",
        "#ffffffd9",
        "-s",
        "#ffffff14",
        "-w",
        "1",
    ]);
    if mode == "pick" {
        cmd.arg("-r").stdin(Stdio::piped());
    }
    cmd.stdout(Stdio::piped()).stderr(Stdio::piped());
    let mut child = cmd.spawn().map_err(|error| {
        if error.kind() == std::io::ErrorKind::NotFound {
            notify_missing("slurp");
        }
        error.to_string()
    })?;
    if mode == "pick" {
        use std::io::Write;
        if let Some(mut stdin) = child.stdin.take() {
            stdin
                .write_all(window_rectangles().as_bytes())
                .map_err(|error| error.to_string())?;
        }
    }
    let output = child
        .wait_with_output()
        .map_err(|error| error.to_string())?;
    let geometry = String::from_utf8_lossy(&output.stdout).trim().to_owned();
    Ok((!geometry.is_empty()).then_some(geometry))
}

fn signal_bar() {
    let _ = Command::new("pkill")
        .args(["-RTMIN+13", "-x", "waybar"])
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .status();
}

fn thumbnail(file: &Path) {
    if env::var("HYPRMAC_SHOT_THUMB").ok().as_deref() == Some("0") {
        return;
    }
    if !file.exists() {
        return;
    }
    let poster = PathBuf::from(format!("{}.png", file.display()));
    let success = Command::new("ffmpeg")
        .args(["-y", "-i"])
        .arg(file)
        .args(["-vframes", "1"])
        .arg(&poster)
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .spawn()
        .ok()
        .is_some_and(|mut child| {
            let deadline = Instant::now() + Duration::from_secs(10);
            while Instant::now() < deadline {
                if let Ok(Some(status)) = child.try_wait() {
                    return status.success();
                }
                std::thread::sleep(Duration::from_millis(50));
            }
            let _ = child.kill();
            let _ = child.wait();
            false
        });
    if success && poster.exists() {
        let tool = PathBuf::from(env::var_os("HOME").unwrap_or_default())
            .join(".local/bin/hyprmac-captura-miniatura");
        let _ = Command::new(tool)
            .arg(&poster)
            .arg("--abrir")
            .arg(file)
            .stdout(Stdio::null())
            .stderr(Stdio::null())
            .spawn();
    } else {
        let home = env::var("HOME").unwrap_or_default();
        let shown = file.to_string_lossy().replace(&home, "~");
        let _ = Command::new("notify-send")
            .args([
                "-a",
                "Gravação de Tela",
                "Gravação de Tela",
                &format!("Salva em {shown}"),
            ])
            .spawn();
    }
}

fn stop(state: &Rc<RefCell<Recorder>>) {
    let mut recorder = state.borrow_mut();
    if recorder.stopped {
        return;
    }
    recorder.stopped = true;
    if recorder.child.try_wait().ok().flatten().is_none() {
        unsafe {
            libc::kill(recorder.child.id() as i32, libc::SIGINT);
        }
        let deadline = Instant::now() + Duration::from_secs(5);
        while Instant::now() < deadline {
            if recorder.child.try_wait().ok().flatten().is_some() {
                break;
            }
            std::thread::sleep(Duration::from_millis(50));
        }
        if recorder.child.try_wait().ok().flatten().is_none() {
            let _ = recorder.child.kill();
        }
        let _ = recorder.child.wait();
    }
    let _ = fs::remove_file(&recorder.pidfile);
    let _ = fs::remove_file(&recorder.filemark);
    signal_bar();
    thumbnail(&recorder.file);
    recorder.loop_.quit();
}

fn run() -> Result<(), String> {
    let args = env::args().collect::<Vec<_>>();
    let mode = args.get(1).map(String::as_str).unwrap_or("screen");
    let pidfile = runtime_file("hyprmac-gravacao.pid");
    let filemark = runtime_file("hyprmac-gravacao.arquivo");
    if mode == "stop" {
        if !stop_existing(&pidfile) {
            eprintln!("nenhuma gravação em andamento");
        }
        return Ok(());
    }
    if stop_existing(&pidfile) {
        std::thread::sleep(Duration::from_millis(300));
        return Ok(());
    }
    let file = destination()?.join(file_name()?);
    let mut cmd = Command::new("wf-recorder");
    cmd.arg("-f").arg(&file);
    if env::var("HYPRMAC_REC_AUDIO").ok().as_deref() == Some("1") {
        cmd.arg("-a");
    }
    if mode == "region" || mode == "pick" {
        let Some(geometry) = pick_geometry(mode)? else {
            return Ok(());
        };
        cmd.arg("-g").arg(geometry);
    } else if let Some(monitor) = focused_monitor() {
        cmd.arg("-o").arg(monitor);
    }
    let delay = recording_delay(env::var("HYPRMAC_REC_DELAY").ok().as_deref());
    if delay > 0 {
        std::thread::sleep(Duration::from_secs(delay));
    }
    let child = cmd
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .spawn()
        .map_err(|error| {
            if error.kind() == std::io::ErrorKind::NotFound {
                notify_missing("wf-recorder");
            }
            error.to_string()
        })?;
    fs::write(&pidfile, std::process::id().to_string()).map_err(|error| error.to_string())?;
    fs::write(&filemark, file.to_string_lossy().as_bytes()).map_err(|error| error.to_string())?;
    let loop_ = glib::MainLoop::new(None, false);
    let state = Rc::new(RefCell::new(Recorder {
        child,
        file,
        started: Instant::now(),
        pidfile,
        filemark,
        loop_: loop_.clone(),
        stopped: false,
    }));
    let waybar = Command::new("pgrep")
        .args(["-x", "waybar"])
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .status()
        .is_ok_and(|status| status.success());
    if waybar {
        signal_bar();
    } else if let Err(error) = ui::show(&state) {
        stop(&state);
        return Err(error);
    }
    for signal in [libc::SIGINT, libc::SIGTERM] {
        let state = Rc::clone(&state);
        glib::source::unix_signal_add_local(signal, move || {
            stop(&state);
            ControlFlow::Break
        });
    }
    let watcher = Rc::clone(&state);
    glib::timeout_add_seconds_local(1, move || {
        let ended = watcher
            .borrow_mut()
            .child
            .try_wait()
            .ok()
            .flatten()
            .is_some();
        if ended {
            stop(&watcher);
            ControlFlow::Break
        } else {
            ControlFlow::Continue
        }
    });
    loop_.run();
    Ok(())
}

fn main() {
    if let Err(error) = run() {
        eprintln!("{error}");
        std::process::exit(1);
    }
}
