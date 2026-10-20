//! Teclas rápidas personalizáveis do Spotlight, sem GTK e sem estado global.
use regex::Regex;
use serde::Serialize;
use serde_json::{json, Map, Value};
use std::collections::HashSet;
use std::ffi::{c_char, CStr};
use std::fs;
use std::path::Path;
use std::sync::LazyLock;

static WORDS: LazyLock<Regex> = LazyLock::new(|| Regex::new(r"[0-9A-Za-zÀ-ÿ]+").unwrap());
const MAX_LEN: usize = 8;

pub fn normalize(input: &str) -> String {
    input.to_lowercase().chars().filter(|ch| ch.is_ascii_lowercase() || ch.is_ascii_digit() || ('à'..='ÿ').contains(ch)).take(MAX_LEN).collect()
}

pub fn suggest(label: &str, taken: &HashSet<String>) -> String {
    let words = WORDS.find_iter(label).map(|match_| match_.as_str()).collect::<Vec<_>>();
    if words.is_empty() { return String::new(); }
    let initials = words.iter().filter_map(|word| word.chars().next()).collect::<String>();
    let mut base = normalize(&initials);
    if base.chars().count() == 1 && words[0].chars().count() > 1 {
        base = normalize(&words[0].chars().take(2).collect::<String>());
    }
    let mut key = base.clone();
    let extra = normalize(&words.last().unwrap().chars().skip(1).collect::<String>());
    for ch in extra.chars() {
        if !taken.contains(&key) { break; }
        key.push(ch);
        key = key.chars().take(MAX_LEN).collect();
    }
    let mut suffix = 2;
    while taken.contains(&key) {
        key = format!("{base}{suffix}");
        suffix += 1;
    }
    key
}

fn as_string(value: &Value) -> String {
    match value {
        Value::String(text) => text.clone(),
        Value::Bool(boolean) => if *boolean { "True" } else { "False" }.into(),
        Value::Null => "None".into(),
        other => other.to_string(),
    }
}
fn object(value: &Value) -> Map<String, Value> { value.as_object().cloned().unwrap_or_default() }

pub fn effective(actions: &Value, overrides: &Value) -> Value {
    let mut result = Map::new();
    for action in actions.as_array().into_iter().flatten() {
        let Some(id) = action.get("id").and_then(Value::as_str) else { continue; };
        let key = overrides.get(id).unwrap_or_else(|| action.get("key").unwrap_or(&Value::Null));
        if !key.is_null() && key != "" && key != false { result.insert(id.into(), key.clone()); }
    }
    Value::Object(result)
}

pub fn assign(overrides: &Value, action_id: &str, key: &str, keys: &Value) -> Value {
    let key = normalize(key);
    let mut result = object(overrides);
    if !key.is_empty() {
        for (other, existing) in keys.as_object().into_iter().flat_map(|map| map.iter()) {
            if existing.as_str() == Some(&key) && other != action_id { result.insert(other.clone(), Value::String(String::new())); }
        }
    }
    result.insert(action_id.into(), Value::String(key));
    Value::Object(result)
}

pub fn after_run(overrides: &Value, action: &Value, keys: &Value) -> (bool, Value) {
    let Some(id) = action.get("id").and_then(Value::as_str) else { return (false, overrides.clone()); };
    if overrides.get(id).is_some() || keys.get(id).is_some_and(|value| !value.is_null() && value != "" && value != false) {
        return (false, overrides.clone());
    }
    let label = action.get("label").and_then(Value::as_str).filter(|value| !value.is_empty())
        .or_else(|| action.get("name").and_then(Value::as_str)).unwrap_or("");
    let taken = keys.as_object().into_iter().flat_map(|map| map.values()).filter_map(Value::as_str).map(str::to_string).collect();
    let key = suggest(label, &taken);
    if key.is_empty() { return (false, overrides.clone()); }
    let mut result = object(overrides);
    result.insert(id.into(), Value::String(key));
    (true, Value::Object(result))
}

fn load(path: &Path) -> Value {
    let Some(value) = fs::read_to_string(path).ok().and_then(|text| serde_json::from_str::<Value>(&text).ok()) else { return json!({}); };
    let Some(map) = value.as_object() else { return json!({}); };
    Value::Object(map.iter().map(|(key, value)| (key.clone(), Value::String(as_string(value)))).collect())
}
fn save(path: &Path, overrides: &Value) -> Result<(), String> {
    let parent = path.parent().ok_or("caminho sem diretório")?;
    fs::create_dir_all(parent).map_err(|error| error.to_string())?;
    let mut output = Vec::new();
    let formatter = serde_json::ser::PrettyFormatter::with_indent(b" ");
    let mut serializer = serde_json::Serializer::with_formatter(&mut output, formatter);
    overrides.serialize(&mut serializer).map_err(|error| error.to_string())?;
    let temporary = format!("{}.tmp", path.display());
    fs::write(&temporary, output).map_err(|error| error.to_string())?;
    fs::rename(&temporary, path).map_err(|error| error.to_string())
}

pub fn dispatch(input: &Value) -> Value {
    let op = input.get("op").and_then(Value::as_str).unwrap_or("");
    match op {
        "normalize" => json!(normalize(input.get("text").and_then(Value::as_str).unwrap_or(""))),
        "suggest" => {
            let taken = input.get("taken").and_then(Value::as_array).into_iter().flatten().filter_map(Value::as_str).map(str::to_string).collect();
            json!(suggest(input.get("label").and_then(Value::as_str).unwrap_or(""), &taken))
        }
        "effective" => effective(&input["actions"], &input["overrides"]),
        "assign" => assign(&input["overrides"], input.get("action_id").and_then(Value::as_str).unwrap_or(""), input.get("key").and_then(Value::as_str).unwrap_or(""), &input["keys"]),
        "after_run" => { let (changed, value) = after_run(&input["overrides"], &input["action"], &input["keys"]); json!({"changed":changed,"value":value}) }
        "load" => load(Path::new(input.get("path").and_then(Value::as_str).unwrap_or(""))),
        "save" => match save(Path::new(input.get("path").and_then(Value::as_str).unwrap_or("")), &input["overrides"]) { Ok(()) => Value::Null, Err(error) => json!({"error":error}) },
        _ => json!({"error":"operação desconhecida"}),
    }
}

/// # Safety
/// `input` must be a valid NUL-terminated UTF-8 string. `output` must reference
/// `capacity` writable bytes when non-null. Returns the required output length.
#[no_mangle]
pub unsafe extern "C" fn hyprmac_quickkeys(input: *const c_char, output: *mut c_char, capacity: usize) -> usize {
    if input.is_null() { return 0; }
    let Ok(text) = (unsafe { CStr::from_ptr(input) }).to_str() else { return 0; };
    let Ok(request) = serde_json::from_str::<Value>(text) else { return 0; };
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
    fn collision_moves_previous_owner() {
        let result = assign(&json!({}), "m:facetime", "NT", &json!({"q:nt":"nt"}));
        assert_eq!(result, json!({"m:facetime":"nt","q:nt":""}));
    }
    #[test]
    fn suggestion_only_after_first_run() {
        let action = json!({"id":"m:facetime","label":"Start FaceTime Call"});
        let (changed, overrides) = after_run(&json!({}), &action, &json!({}));
        assert!(changed);
        assert_eq!(overrides["m:facetime"], "sfc");
        assert!(!after_run(&overrides, &action, &json!({})).0);
    }
}
