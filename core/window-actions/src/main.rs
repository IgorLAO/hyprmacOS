use serde_json::Value;
use std::env;
use std::process::{Command, Stdio};

fn hypr(args: &[&str]) -> String {
    Command::new("hyprctl")
        .args(args)
        .stdout(Stdio::piped())
        .stderr(Stdio::null())
        .output()
        .ok()
        .map(|output| String::from_utf8_lossy(&output.stdout).into_owned())
        .unwrap_or_default()
}

fn snapshot(name: &str, fallback: &str) -> Value {
    serde_json::from_str(&hypr(&[name, "-j"]))
        .unwrap_or_else(|_| serde_json::from_str(fallback).expect("valid fallback"))
}

fn field<'a>(item: &'a Value, key: &str) -> &'a str {
    item.get(key).and_then(Value::as_str).unwrap_or("")
}

fn workspace_id(item: &Value) -> i64 {
    item["workspace"]["id"].as_i64().unwrap_or(0)
}

fn address(item: &Value) -> &str {
    field(item, "address")
}

fn next_window<'a>(windows: &'a [&Value], current: Option<&str>, step: i32) -> Option<&'a Value> {
    let mut sorted = windows.to_vec();
    sorted.sort_by(|a, b| {
        field(a, "stableId")
            .cmp(field(b, "stableId"))
            .then_with(|| address(a).cmp(address(b)))
    });
    if sorted.is_empty() {
        return None;
    }
    let index = current.and_then(|addr| sorted.iter().position(|item| address(item) == addr));
    let target = match index {
        Some(i) if step > 0 => (i + 1) % sorted.len(),
        Some(i) => (i + sorted.len() - 1) % sorted.len(),
        None if step > 0 => 0,
        None => sorted.len() - 1,
    };
    Some(sorted[target])
}

fn move_window(address: &str, workspace: &str) -> String {
    format!("hl.dsp.window.move({{ workspace = {workspace}, follow = false, window = \"address:{address}\" }})")
}

fn plan(
    command: &str,
    active: &Value,
    clients: &[Value],
    current_workspace: i64,
    monitors: &Value,
) -> Result<Vec<String>, String> {
    let class = field(active, "class");
    let current = address(active);
    let mut actions = Vec::new();
    match command {
        "quit-app" if !class.is_empty() => {
            for client in clients.iter().filter(|item| field(item, "class") == class) {
                actions.push(format!(
                    "hl.dsp.window.close({{ window = \"address:{}\" }})",
                    address(client)
                ));
            }
        }
        "hide-app" if !class.is_empty() => {
            for client in clients.iter().filter(|item| {
                field(item, "class") == class
                    && !field(&item["workspace"], "name").starts_with("special")
            }) {
                actions.push(move_window(address(client), "\"special:magic\""));
            }
        }
        "hide-others" if !class.is_empty() => {
            let workspace = workspace_id(active);
            for client in clients
                .iter()
                .filter(|item| field(item, "class") != class && workspace_id(item) == workspace)
            {
                actions.push(move_window(address(client), "\"special:magic\""));
            }
        }
        "show-all" => {
            for client in clients
                .iter()
                .filter(|item| field(&item["workspace"], "name") == "special:magic")
            {
                actions.push(move_window(address(client), &current_workspace.to_string()));
            }
        }
        "show-desktop" => {
            let saved_name = format!("special:mesa{current_workspace}");
            let saved = clients
                .iter()
                .filter(|item| field(&item["workspace"], "name") == saved_name)
                .collect::<Vec<_>>();
            if saved.is_empty() {
                for client in clients
                    .iter()
                    .filter(|item| workspace_id(item) == current_workspace)
                {
                    actions.push(move_window(address(client), &format!("\"{saved_name}\"")));
                }
            } else {
                for client in saved {
                    actions.push(move_window(address(client), &current_workspace.to_string()));
                }
            }
        }
        "next-window" | "prev-window" if !class.is_empty() => {
            let same = clients
                .iter()
                .filter(|item| {
                    field(item, "class") == class
                        && !field(&item["workspace"], "name").starts_with("special")
                })
                .collect::<Vec<_>>();
            if same.len() > 1 {
                if let Some(target) = next_window(
                    &same,
                    Some(current),
                    if command == "next-window" { 1 } else { -1 },
                ) {
                    actions.push(format!(
                        "hl.dsp.focus({{ window = \"address:{}\" }})",
                        address(target)
                    ));
                }
            }
        }
        "next-any" | "prev-any" => {
            let visible = monitors
                .as_array()
                .map(|list| {
                    list.iter()
                        .filter_map(|item| item["activeWorkspace"]["id"].as_i64())
                        .collect::<Vec<_>>()
                })
                .unwrap_or_default();
            let windows = clients
                .iter()
                .filter(|item| {
                    visible.contains(&workspace_id(item))
                        && item["mapped"].as_bool().unwrap_or(true)
                })
                .collect::<Vec<_>>();
            let current = if current.is_empty() {
                None
            } else {
                Some(current)
            };
            if let Some(target) = next_window(
                &windows,
                current,
                if command == "next-any" { 1 } else { -1 },
            ) {
                actions.push(format!(
                    "hl.dsp.focus({{ window = \"address:{}\" }})",
                    address(target)
                ));
            }
        }
        "quit-app" | "hide-app" | "hide-others" | "next-window" | "prev-window" => {}
        _ => return Err(format!("comando desconhecido: {command}")),
    }
    Ok(actions)
}

fn run() -> Result<(), String> {
    let command = env::args().nth(1).ok_or("uso: hyprmac-janela <ação>")?;
    let active = snapshot("activewindow", "{}");
    let clients = snapshot("clients", "[]")
        .as_array()
        .cloned()
        .unwrap_or_default();
    let workspace = if command == "show-all" || command == "show-desktop" {
        snapshot("activeworkspace", "{}")["id"]
            .as_i64()
            .unwrap_or(1)
    } else {
        1
    };
    let monitors = if command == "next-any" || command == "prev-any" {
        snapshot("monitors", "[]")
    } else {
        Value::Null
    };
    for action in plan(&command, &active, &clients, workspace, &monitors)? {
        hypr(&["dispatch", &action]);
    }
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
    use serde_json::json;

    #[test]
    fn opening_order_wraps_in_both_directions() {
        let values = [
            json!({"address":"0xc","stableId":"3"}),
            json!({"address":"0xa","stableId":"1"}),
            json!({"address":"0xb","stableId":"2"}),
        ];
        let refs = values.iter().collect::<Vec<_>>();
        assert_eq!(address(next_window(&refs, Some("0xa"), 1).unwrap()), "0xb");
        assert_eq!(address(next_window(&refs, Some("0xc"), 1).unwrap()), "0xa");
        assert_eq!(address(next_window(&refs, Some("0xa"), -1).unwrap()), "0xc");
        assert_eq!(address(next_window(&refs, None, -1).unwrap()), "0xc");
    }

    #[test]
    fn desktop_toggle_round_trip_preserves_workspace() {
        let active = json!({});
        let visible = [json!({"address":"0xa","workspace":{"id":2,"name":"2"}})];
        assert_eq!(plan("show-desktop",&active,&visible,2,&Value::Null).unwrap(),
            vec!["hl.dsp.window.move({ workspace = \"special:mesa2\", follow = false, window = \"address:0xa\" })"]);
        let saved = [json!({"address":"0xa","workspace":{"id":-1,"name":"special:mesa2"}})];
        assert_eq!(
            plan("show-desktop", &active, &saved, 2, &Value::Null).unwrap(),
            vec!["hl.dsp.window.move({ workspace = 2, follow = false, window = \"address:0xa\" })"]
        );
    }

    #[test]
    fn visible_window_cycle_skips_hidden_and_unmapped() {
        let clients = [
            json!({"address":"0xa","stableId":"1","workspace":{"id":1},"mapped":true}),
            json!({"address":"0xb","stableId":"2","workspace":{"id":2},"mapped":true}),
            json!({"address":"0xc","stableId":"3","workspace":{"id":1},"mapped":false}),
        ];
        let monitors = json!([{"activeWorkspace":{"id":1}}]);
        assert_eq!(
            plan(
                "next-any",
                &json!({"address":"0xa"}),
                &clients,
                1,
                &monitors
            )
            .unwrap(),
            vec!["hl.dsp.focus({ window = \"address:0xa\" })"]
        );
    }
}
