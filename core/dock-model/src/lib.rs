//! Conteúdo e política do Dock, sem GTK, ícones ou socket do compositor.
use serde_json::{json, Value};
use std::collections::{HashMap, HashSet};
use std::ffi::{c_char, CStr};

pub fn needs_refresh(line: &str) -> bool {
    matches!(
        line.split_once(">>").map_or(line, |(event, _)| event),
        "openwindow"
            | "closewindow"
            | "movewindowv2"
            | "activewindowv2"
            | "windowtitlev2"
            | "changefloatingmode"
            | "fullscreen"
    )
}

pub fn build_plan(clients: &[Value], pinned: &[Value]) -> Value {
    let mut groups: Vec<(String, Vec<usize>)> = Vec::new();
    let mut group_indices = HashMap::new();
    for (index, client) in clients.iter().enumerate() {
        let class = client.get("class").and_then(Value::as_str).unwrap_or("");
        if class.is_empty() || class == "hyprmac-shell" {
            continue;
        }
        let Some(key) = client.get("key").and_then(Value::as_str) else {
            continue;
        };
        let group = *group_indices.entry(key.to_owned()).or_insert_with(|| {
            groups.push((key.to_owned(), Vec::new()));
            groups.len() - 1
        });
        groups[group].1.push(index);
    }
    let shown = pinned
        .iter()
        .filter_map(|item| item.get("key").and_then(Value::as_str))
        .collect::<HashSet<_>>();
    let mut plan = Vec::new();
    for (index, item) in pinned.iter().enumerate() {
        let key = item.get("key").and_then(Value::as_str).unwrap_or("");
        let windows = if item.get("kind").and_then(Value::as_str) == Some("sep") {
            Vec::new()
        } else {
            groups
                .iter()
                .find(|(group, _)| group == key)
                .map(|(_, windows)| windows.clone())
                .unwrap_or_default()
        };
        plan.push(json!({"type":"pinned","index":index,"windows":windows}));
    }
    for (key, windows) in &groups {
        if shown.contains(key.as_str()) {
            continue;
        }
        if !plan.iter().any(|entry| entry["type"] == "sep")
            && !pinned
                .iter()
                .any(|item| item.get("kind").and_then(Value::as_str) == Some("sep"))
        {
            plan.push(json!({"type":"sep","key":"hyprmac:sep-recent"}));
        }
        let first = windows[0];
        plan.push(json!({"type":"recent","key":key,"first":first,"windows":windows}));
    }
    plan.push(json!({"type":"sep","key":"hyprmac:sep"}));
    for (index, client) in clients.iter().enumerate() {
        if client.get("workspace").and_then(Value::as_str) == Some("special:minimized") {
            plan.push(json!({"type":"minimized","index":index}));
        }
    }
    plan.push(json!({"type":"downloads"}));
    plan.push(json!({"type":"trash"}));
    json!(plan)
}

pub fn reorder(items: &[Value], pinned: &[Value], source: isize, target: isize) -> Value {
    let len = items.len() as isize;
    if source < 0 || target < 0 || source >= len || target >= len || source == target {
        return json!({"changed":false});
    }
    let movable = |item: &Value| {
        item.get("pin")
            .and_then(Value::as_str)
            .is_some_and(|pin| !pin.is_empty() && pin != "hyprmac:finder")
    };
    let source_item = &items[source as usize];
    let target_item = &items[target as usize];
    if !movable(source_item) || !movable(target_item) {
        return json!({"changed":false});
    }
    let Some(pin) = source_item.get("pin").and_then(Value::as_str) else {
        return json!({"changed":false});
    };
    let Some(target_pin) = target_item.get("pin").and_then(Value::as_str) else {
        return json!({"changed":false});
    };
    let Some(destination) = pinned
        .iter()
        .position(|value| value.as_str() == Some(target_pin))
    else {
        return json!({"changed":false});
    };
    let Some(old) = pinned.iter().position(|value| value.as_str() == Some(pin)) else {
        return json!({"changed":false});
    };
    let mut next = pinned.to_vec();
    next.remove(old);
    next.insert(destination.min(next.len()), json!(pin));
    json!({"changed":true,"pinned":next})
}

pub fn pin_slot(items: &[Value], pinned: &[Value], x: f64, origin_x: f64, icon: f64) -> usize {
    let mut slot = 0;
    for item in items {
        if !pinned.contains(&item["pin"]) {
            break;
        }
        let position = item.get("x").and_then(Value::as_f64).unwrap_or(0.0);
        if x < origin_x + position + icon / 2.0 {
            break;
        }
        slot += 1;
    }
    slot.max(usize::from(
        pinned.first().and_then(Value::as_str) == Some("hyprmac:finder"),
    ))
}

pub fn insert_pin(pinned: &[Value], pin: &str, slot: isize) -> Value {
    if pin.is_empty() || pin == "hyprmac:finder" {
        return json!({"changed":false});
    }
    let mut next = pinned.to_vec();
    let mut slot = slot;
    if let Some(old) = next.iter().position(|value| value.as_str() == Some(pin)) {
        next.remove(old);
        if (old as isize) < slot {
            slot -= 1;
        }
    }
    let floor = usize::from(next.first().and_then(Value::as_str) == Some("hyprmac:finder"));
    let destination = (slot.max(floor as isize) as usize).min(next.len());
    next.insert(destination, json!(pin));
    json!({"changed":next != pinned,"pinned":next})
}

pub fn dispatch(request: &Value) -> Value {
    let items = request
        .get("items")
        .and_then(Value::as_array)
        .map(Vec::as_slice)
        .unwrap_or(&[]);
    let pinned = request
        .get("pinned")
        .and_then(Value::as_array)
        .map(Vec::as_slice)
        .unwrap_or(&[]);
    match request.get("op").and_then(Value::as_str).unwrap_or("") {
        "needs_refresh" => json!(needs_refresh(
            request.get("line").and_then(Value::as_str).unwrap_or("")
        )),
        "build_plan" => build_plan(
            request
                .get("clients")
                .and_then(Value::as_array)
                .map(Vec::as_slice)
                .unwrap_or(&[]),
            pinned,
        ),
        "reorder" => reorder(
            items,
            pinned,
            request.get("source").and_then(Value::as_i64).unwrap_or(-1) as isize,
            request.get("target").and_then(Value::as_i64).unwrap_or(-1) as isize,
        ),
        "pin_slot" => json!(pin_slot(
            items,
            pinned,
            request.get("x").and_then(Value::as_f64).unwrap_or(0.0),
            request
                .get("origin_x")
                .and_then(Value::as_f64)
                .unwrap_or(0.0),
            request.get("icon").and_then(Value::as_f64).unwrap_or(0.0)
        )),
        "insert_pin" => insert_pin(
            pinned,
            request.get("pin").and_then(Value::as_str).unwrap_or(""),
            request.get("slot").and_then(Value::as_i64).unwrap_or(0) as isize,
        ),
        _ => Value::Null,
    }
}

/// # Safety
/// `input` points to NUL-terminated JSON. `output`, when non-null, references
/// `capacity` writable bytes. Returns the required result length.
#[no_mangle]
pub unsafe extern "C" fn hyprmac_dock_model(
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
    fn sections_keep_focus_order_and_minimized() {
        let clients = vec![
            json!({"class":"recent","key":"recent","workspace":"special:minimized"}),
            json!({"class":"fixed","key":"fixed","workspace":"1"}),
            json!({"class":"other","key":"other","workspace":"1"}),
        ];
        let plan = build_plan(&clients, &[json!({"key":"fixed","kind":"app"})]);
        assert_eq!(
            plan.as_array()
                .unwrap()
                .iter()
                .map(|entry| entry["type"].as_str().unwrap())
                .collect::<Vec<_>>(),
            [
                "pinned",
                "sep",
                "recent",
                "recent",
                "sep",
                "minimized",
                "downloads",
                "trash"
            ]
        );
        assert_eq!(plan[2]["windows"], json!([0]));
    }
    #[test]
    fn finder_cannot_move() {
        let items = vec![
            json!({"pin":"hyprmac:finder"}),
            json!({"pin":"one"}),
            json!({"pin":"two"}),
        ];
        let pinned = vec![json!("hyprmac:finder"), json!("one"), json!("two")];
        assert!(!reorder(&items, &pinned, 0, 2)["changed"].as_bool().unwrap());
        assert_eq!(
            insert_pin(&pinned, "two", 1)["pinned"],
            json!(["hyprmac:finder", "two", "one"])
        );
    }
}
