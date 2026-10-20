//! Histórico dos modos do Spotlight, independente da view GTK e do lançador.
use serde::Serialize;
use serde_json::{json, Map, Value};
use std::ffi::{c_char, CStr};
use std::fs;
use std::path::Path;

pub fn load(path: &Path) -> Value {
    fs::read_to_string(path)
        .ok()
        .and_then(|text| serde_json::from_str::<Value>(&text).ok())
        .filter(Value::is_object)
        .unwrap_or_else(|| json!({}))
}

pub fn ids(data: &Value, mode: &str) -> Value {
    let values = data
        .get(mode)
        .and_then(Value::as_array)
        .into_iter()
        .flatten()
        .filter_map(|entry| entry.get("id"))
        .filter(|id| match id {
            Value::Null => false,
            Value::Bool(value) => *value,
            Value::String(value) => !value.is_empty(),
            Value::Number(value) => value.as_f64().is_some_and(|number| number != 0.0),
            Value::Array(value) => !value.is_empty(),
            Value::Object(value) => !value.is_empty(),
        })
        .cloned()
        .collect::<Vec<_>>();
    json!(values)
}

pub fn record(data: &Value, mode: &str, item_id: &Value, label: &Value, timestamp: i64) -> Value {
    let mut result = data.as_object().cloned().unwrap_or_else(Map::new);
    let mut entries = result
        .get(mode)
        .and_then(Value::as_array)
        .cloned()
        .unwrap_or_default();
    entries.retain(|entry| entry.get("id") != Some(item_id));
    entries.insert(0, json!({"id":item_id,"label":label,"t":timestamp}));
    entries.truncate(20);
    result.insert(mode.to_owned(), Value::Array(entries));
    Value::Object(result)
}

pub fn save(path: &Path, data: &Value) -> Result<(), String> {
    let parent = path.parent().ok_or("caminho sem diretório")?;
    fs::create_dir_all(parent).map_err(|error| error.to_string())?;
    let mut output = Vec::new();
    let formatter = serde_json::ser::PrettyFormatter::with_indent(b" ");
    let mut serializer = serde_json::Serializer::with_formatter(&mut output, formatter);
    data.serialize(&mut serializer)
        .map_err(|error| error.to_string())?;
    let temporary = format!("{}.tmp", path.display());
    fs::write(&temporary, output).map_err(|error| error.to_string())?;
    fs::rename(&temporary, path).map_err(|error| error.to_string())
}

pub fn read_drun_cache(path: &Path) -> Value {
    let mut counts = Map::new();
    if let Ok(contents) = fs::read_to_string(path) {
        for line in contents.lines() {
            let Some((number, desktop)) = line.split_once(' ') else {
                continue;
            };
            if desktop.is_empty() || !number.chars().all(|ch| ch.is_ascii_digit()) {
                continue;
            }
            if let Ok(number) = number.parse::<u64>() {
                let old = counts.get(desktop).and_then(Value::as_u64).unwrap_or(0);
                counts.insert(desktop.to_owned(), json!(old.saturating_add(number)));
            }
        }
    }
    Value::Object(counts)
}

pub fn write_drun_cache(path: &Path, counts: &Value) -> Result<(), String> {
    let parent = path.parent().ok_or("caminho sem diretório")?;
    fs::create_dir_all(parent).map_err(|error| error.to_string())?;
    let mut output = String::new();
    if let Some(counts) = counts.as_object() {
        for (desktop, count) in counts {
            let number = count.as_u64().ok_or("contagem inválida")?;
            output.push_str(&format!("{number} {desktop}\n"));
        }
    }
    let temporary = format!("{}.tmp", path.display());
    fs::write(&temporary, output).map_err(|error| error.to_string())?;
    fs::rename(&temporary, path).map_err(|error| error.to_string())
}

pub fn dispatch(request: &Value) -> Value {
    let path = Path::new(request.get("path").and_then(Value::as_str).unwrap_or(""));
    let mode = request.get("mode").and_then(Value::as_str).unwrap_or("");
    match request.get("op").and_then(Value::as_str).unwrap_or("") {
        "load" => load(path),
        "ids" => ids(&load(path), mode),
        "record" => {
            let data = record(
                &load(path),
                mode,
                &request["id"],
                &request["label"],
                request
                    .get("timestamp")
                    .and_then(Value::as_i64)
                    .unwrap_or(0),
            );
            match save(path, &data) {
                Ok(()) => Value::Null,
                Err(error) => json!({"error":error}),
            }
        }
        "read_drun_cache" => read_drun_cache(path),
        "write_drun_cache" => match write_drun_cache(path, &request["counts"]) {
            Ok(()) => Value::Null,
            Err(error) => json!({"error":error}),
        },
        _ => json!({"error":"operação desconhecida"}),
    }
}

/// # Safety
/// `input` must be a valid NUL-terminated UTF-8 string. `output` must reference
/// `capacity` writable bytes when non-null. Returns the required output length.
#[no_mangle]
pub unsafe extern "C" fn hyprmac_spotlight_history(
    input: *const c_char,
    output: *mut c_char,
    capacity: usize,
) -> usize {
    if input.is_null() {
        return 0;
    }
    let Ok(text) = (unsafe { CStr::from_ptr(input) }).to_str() else {
        return 0;
    };
    let Ok(request) = serde_json::from_str::<Value>(text) else {
        return 0;
    };
    let result = dispatch(&request).to_string();
    let bytes = result.as_bytes();
    if !output.is_null() && capacity > bytes.len() {
        unsafe {
            std::ptr::copy_nonoverlapping(bytes.as_ptr(), output.cast::<u8>(), bytes.len());
            *output.add(bytes.len()) = 0;
        }
    }
    bytes.len()
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn recent_entry_replaces_old_and_preserves_other_modes() {
        let previous = json!({"apps":[{"id":"one"},{"id":"two"}],"files":[{"id":"x"}]});
        let next = record(&previous, "apps", &json!("two"), &json!("Two"), 42);
        assert_eq!(ids(&next, "apps"), json!(["two", "one"]));
        assert_eq!(ids(&next, "files"), json!(["x"]));
        assert_eq!(next["apps"][0]["t"], 42);
    }

    #[test]
    fn cache_sums_duplicate_desktop_entries() {
        let path = std::env::temp_dir().join(format!("hyprmac-drun-{}", std::process::id()));
        fs::write(
            &path,
            "2 app.desktop\n3 app.desktop\nnope other.desktop\n4 next.desktop\n",
        )
        .unwrap();
        let counts = read_drun_cache(&path);
        assert_eq!(counts, json!({"app.desktop":5,"next.desktop":4}));
        write_drun_cache(&path, &counts).unwrap();
        assert_eq!(
            fs::read_to_string(&path).unwrap(),
            "5 app.desktop\n4 next.desktop\n"
        );
        fs::remove_file(&path).unwrap();
    }
}
