//! Consultas pontuais ao compositor para escolher monitor e janela de gravação.
use serde_json::Value;
use std::process::Command;

fn run_output(program: &str, args: &[&str]) -> Option<String> {
    let output = Command::new(program).args(args).output().ok()?;
    Some(String::from_utf8_lossy(&output.stdout).into_owned())
}

pub(crate) fn focused_monitor() -> Option<String> {
    let monitors: Value =
        serde_json::from_str(&run_output("hyprctl", &["monitors", "-j"])?).ok()?;
    monitors
        .as_array()?
        .iter()
        .find(|monitor| monitor["focused"] == true)?["name"]
        .as_str()
        .map(str::to_owned)
}

fn visible_windows(monitors: &Value, clients: &Value) -> String {
    let Some(monitors) = monitors.as_array() else {
        return String::new();
    };
    let Some(clients) = clients.as_array() else {
        return String::new();
    };
    let active = monitors
        .iter()
        .flat_map(|monitor| {
            [
                monitor["activeWorkspace"]["id"].as_i64(),
                monitor["specialWorkspace"]["id"].as_i64(),
            ]
        })
        .flatten()
        .collect::<Vec<_>>();
    let rows = clients
        .iter()
        .filter_map(|client| {
            if client["mapped"] != true
                || client["hidden"] == true
                || !client["workspace"]["id"]
                    .as_i64()
                    .is_some_and(|id| active.contains(&id))
            {
                return None;
            }
            let at = client["at"].as_array()?;
            let size = client["size"].as_array()?;
            Some(format!(
                "{},{} {}x{}",
                at.first()?,
                at.get(1)?,
                size.first()?,
                size.get(1)?
            ))
        })
        .collect::<Vec<_>>();
    format!("{}\n", rows.join("\n"))
}

pub(crate) fn window_rectangles() -> String {
    let Some(monitors) = run_output("hyprctl", &["monitors", "-j"])
        .and_then(|text| serde_json::from_str::<Value>(&text).ok())
    else {
        return String::new();
    };
    let Some(clients) = run_output("hyprctl", &["clients", "-j"])
        .and_then(|text| serde_json::from_str::<Value>(&text).ok())
    else {
        return String::new();
    };
    visible_windows(&monitors, &clients)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn visible_workspaces_filter_hidden_clients() {
        let monitors =
            serde_json::json!([{"activeWorkspace":{"id":1},"specialWorkspace":{"id":7}}]);
        let clients = serde_json::json!([
            {"mapped":true,"hidden":false,"workspace":{"id":1},"at":[10,20],"size":[300,200]},
            {"mapped":true,"hidden":true,"workspace":{"id":1},"at":[0,0],"size":[1,1]},
            {"mapped":true,"hidden":false,"workspace":{"id":2},"at":[0,0],"size":[1,1]}
        ]);
        assert_eq!(visible_windows(&monitors, &clients), "10,20 300x200\n");
    }
}
