use image::{imageops::FilterType, GenericImageView, ImageFormat};
use serde_json::{json, Value};
use sha1::{Digest, Sha1};
use std::env;
use std::fs;
use std::io::{self, Read};
use std::os::unix::ffi::OsStrExt;
use std::os::unix::process::CommandExt;
use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};
use std::time::{SystemTime, UNIX_EPOCH};

const KEEP_SECONDS: f64 = 8.0 * 3600.0;
const MAX_ITEMS: usize = 100;
const MAX_TEXT: usize = 1 << 20;

fn cache_dir() -> PathBuf {
    Path::new(&env::var("HOME").unwrap_or_default()).join(".cache/hyprmac/clipboard")
}

fn index_path() -> PathBuf {
    cache_dir().join("index.json")
}

fn now() -> f64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap_or_default()
        .as_secs_f64()
}

fn capture(args: &[&str], seconds: u32) -> Vec<u8> {
    Command::new("timeout")
        .arg(seconds.to_string())
        .args(args)
        .stdout(Stdio::piped())
        .stderr(Stdio::null())
        .output()
        .ok()
        .filter(|output| output.status.success())
        .map(|output| output.stdout)
        .unwrap_or_default()
}

fn forget_files(item: &Value) {
    for key in ["file", "thumb"] {
        if let Some(path) = item[key].as_str() {
            let _ = fs::remove_file(path);
        }
    }
}

fn retained(items: Vec<Value>, timestamp: f64) -> Vec<Value> {
    let mut keep = Vec::new();
    for item in items {
        let fresh = item["t"]
            .as_f64()
            .is_some_and(|saved| timestamp - saved < KEEP_SECONDS);
        if fresh && keep.len() < MAX_ITEMS {
            keep.push(item);
        } else {
            forget_files(&item);
        }
    }
    keep
}

fn load() -> Vec<Value> {
    let items = fs::read(index_path())
        .ok()
        .and_then(|data| serde_json::from_slice::<Value>(&data).ok())
        .and_then(|value| value.as_array().cloned())
        .unwrap_or_default();
    retained(items, now())
}

fn save(items: &[Value]) -> Result<(), String> {
    let directory = cache_dir();
    fs::create_dir_all(&directory).map_err(|e| e.to_string())?;
    let temporary = directory.join(format!("index.json.{}.tmp", std::process::id()));
    let data = serde_json::to_vec(items).map_err(|e| e.to_string())?;
    fs::write(&temporary, data).map_err(|e| e.to_string())?;
    fs::rename(temporary, index_path()).map_err(|e| e.to_string())
}

fn digest(data: &[u8]) -> String {
    format!("{:x}", Sha1::digest(data))
}

fn image_item(data: &[u8], directory: &Path) -> Option<Value> {
    let id = digest(data);
    let path = directory.join(format!("{id}.png"));
    let thumb = directory.join(format!("{id}-thumb.png"));
    let image = image::load_from_memory(data).ok()?;
    let (width, height) = image.dimensions();
    if width == 0 || height == 0 {
        return None;
    }
    if !path.exists() {
        image.save_with_format(&path, ImageFormat::Png).ok()?;
        let scale = 96.0 / width.max(height) as f64;
        let tw = (width as f64 * scale).round().max(1.0) as u32;
        let th = (height as f64 * scale).round().max(1.0) as u32;
        if image
            .resize_exact(tw, th, FilterType::Triangle)
            .save_with_format(&thumb, ImageFormat::Png)
            .is_err()
        {
            let _ = fs::remove_file(&path);
            return None;
        }
    }
    Some(json!({"kind":"image","id":id,"file":path,"w":width,"h":height,"thumb":thumb}))
}

fn text_item(data: &[u8], files: bool) -> Option<Value> {
    if data.len() > MAX_TEXT || data.iter().all(u8::is_ascii_whitespace) {
        return None;
    }
    let text = String::from_utf8_lossy(data).to_string();
    if text.trim().is_empty() {
        return None;
    }
    let id = digest(text.trim().as_bytes());
    Some(json!({"kind":if files {"files"} else {"text"},"id":id,"text":text}))
}

fn store() -> Result<(), String> {
    let mut forwarded = Vec::new();
    io::stdin()
        .read_to_end(&mut forwarded)
        .map_err(|e| e.to_string())?;
    if ["sensitive", "clear", "nil"]
        .contains(&env::var("CLIPBOARD_STATE").unwrap_or_default().as_str())
    {
        return Ok(());
    }
    let types = String::from_utf8_lossy(&capture(&["wl-paste", "--list-types"], 3))
        .split_whitespace()
        .map(str::to_owned)
        .collect::<Vec<_>>();
    if types.is_empty() || types.iter().any(|item| item == "x-kde-passwordManagerHint") {
        return Ok(());
    }
    let directory = cache_dir();
    fs::create_dir_all(&directory).map_err(|e| e.to_string())?;
    let selected_image = ["image/png", "image/jpeg", "image/webp"]
        .iter()
        .find(|candidate| types.iter().any(|item| item == **candidate))
        .copied();
    let mut item = if let Some(format) = selected_image {
        let data = capture(&["wl-paste", "--type", format], 5);
        if data.is_empty() {
            return Ok(());
        }
        match image_item(&data, &directory) {
            Some(item) => item,
            None => return Ok(()),
        }
    } else {
        let data = capture(&["wl-paste", "--no-newline", "--type", "text"], 3);
        match text_item(&data, types.iter().any(|item| item == "text/uri-list")) {
            Some(item) => item,
            None => return Ok(()),
        }
    };
    item["t"] = json!(now());
    let mut items = load();
    items.retain(|old| old["id"] != item["id"]);
    items.insert(0, item);
    for old in items.iter().skip(MAX_ITEMS) {
        forget_files(old);
    }
    items.truncate(MAX_ITEMS);
    save(&items)
}

fn clear() -> Result<(), String> {
    for item in load() {
        forget_files(&item);
    }
    save(&[])
}

fn pick() -> Result<(), String> {
    Command::new("gdbus")
        .args([
            "call",
            "--session",
            "--dest",
            "dev.hyprmac.Shell",
            "--object-path",
            "/dev/hyprmac/Shell",
            "--method",
            "dev.hyprmac.Shell.Command",
            "toggle-clipboard",
        ])
        .stdout(Stdio::null())
        .status()
        .map_err(|e| e.to_string())?;
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
        let args = command.split(|byte| *byte == 0).collect::<Vec<_>>();
        if args.len() >= 4
            && Path::new(std::ffi::OsStr::from_bytes(args[0])).file_name()
                == Some(std::ffi::OsStr::new("wl-paste"))
            && args[1] == b"--watch"
            && args[3] == b"store"
            && (args[2].ends_with(b"/scripts/clipboard")
                || args[2].ends_with(b"/hyprmac-clipboard"))
        {
            unsafe {
                libc::kill(pid, libc::SIGTERM);
            }
        }
    }
}

fn watch() -> Result<(), String> {
    stop_previous_watchers();
    let binary =
        Path::new(&env::var("HOME").unwrap_or_default()).join(".local/bin/hyprmac-clipboard");
    let error = Command::new("wl-paste")
        .arg("--watch")
        .arg(binary)
        .arg("store")
        .exec();
    Err(error.to_string())
}

fn main() {
    let result = match env::args().nth(1).as_deref().unwrap_or("pick") {
        "store" => store(),
        "watch" => watch(),
        "pick" => pick(),
        "clear" => clear(),
        _ => Err("uso: hyprmac-clipboard [store|watch|pick|clear]".into()),
    };
    if let Err(error) = result {
        eprintln!("{error}");
        std::process::exit(2);
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::io::Cursor;

    #[test]
    fn text_dedup_ignores_edge_whitespace_and_preserves_kind() {
        let first = text_item(b"hello\n", false).unwrap();
        let second = text_item(b" hello ", true).unwrap();
        assert_eq!(first["id"], second["id"]);
        assert_eq!(first["kind"], "text");
        assert_eq!(second["kind"], "files");
    }

    #[test]
    fn old_entries_expire() {
        let items = vec![json!({"id":"old","t":0}), json!({"id":"new","t":30000})];
        let kept = retained(items, 30001.0);
        assert_eq!(kept.len(), 1);
        assert_eq!(kept[0]["id"], "new");
    }

    #[test]
    fn image_is_normalized_and_thumbnail_is_bounded() {
        let directory =
            env::temp_dir().join(format!("hyprmac-clipboard-test-{}", std::process::id()));
        fs::create_dir_all(&directory).unwrap();
        let image = image::DynamicImage::new_rgba8(200, 100);
        let mut png = Cursor::new(Vec::new());
        image.write_to(&mut png, ImageFormat::Png).unwrap();
        let item = image_item(&png.into_inner(), &directory).unwrap();
        assert_eq!(item["w"], 200);
        assert_eq!(item["h"], 100);
        let thumb = image::open(item["thumb"].as_str().unwrap()).unwrap();
        assert_eq!(thumb.dimensions(), (96, 48));
        forget_files(&item);
        fs::remove_dir(directory).unwrap();
    }
}
