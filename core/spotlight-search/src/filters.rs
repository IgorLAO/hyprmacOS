//! Categorias e seletores do Spotlight. Ordem e nomes são os do módulo GTK atual.
use serde_json::{json, Value};

use crate::fold;

const CATEGORIES: &[(&str, &[&str])] = &[
    (
        "Productivity & Finance",
        &[
            "Office",
            "Finance",
            "ProjectManagement",
            "Calendar",
            "ContactManagement",
            "WordProcessor",
            "Spreadsheet",
            "Presentation",
            "Email",
        ],
    ),
    (
        "Social",
        &[
            "InstantMessaging",
            "Chat",
            "IRCClient",
            "VideoConference",
            "Telephony",
        ],
    ),
    (
        "Entertainment",
        &["Audio", "Music", "Player", "TV", "AudioVideo"],
    ),
    (
        "Photo & Video",
        &[
            "Photography",
            "ImageViewer",
            "Video",
            "AudioVideoEditing",
            "Recorder",
        ],
    ),
    (
        "Creativity",
        &[
            "Graphics",
            "2DGraphics",
            "VectorGraphics",
            "RasterGraphics",
            "3DGraphics",
            "Art",
            "Publishing",
        ],
    ),
    (
        "Developer Tools",
        &["Development", "IDE", "Debugger", "RevisionControl"],
    ),
    ("Games", &["Game"]),
    ("Education", &["Education", "Science", "Math"]),
    (
        "Information & Reading",
        &[
            "News",
            "Dictionary",
            "Literature",
            "Documentation",
            "Feed",
            "Maps",
        ],
    ),
    (
        "Utilities",
        &[
            "Utility",
            "System",
            "Settings",
            "Accessories",
            "FileManager",
            "TerminalEmulator",
            "Network",
            "WebBrowser",
            "Archiving",
            "Monitor",
        ],
    ),
];

const FILTERS: &[(&str, &str, &str, &str)] = &[
    ("apps", "Applications", "Apps", "system-software-install"),
    ("folders", "Folders", "Folders", "folder"),
    ("settings", "Settings", "Settings", "preferences-system"),
    ("actions", "Actions", "Actions", "system-run-symbolic"),
];

pub fn app_category(input: &str) -> Option<&'static str> {
    let have = input.split(';').collect::<Vec<_>>();
    CATEGORIES
        .iter()
        .find(|(_, keys)| keys.iter().any(|key| have.contains(key)))
        .map(|(label, _)| *label)
}

pub fn filter_command(input: &str) -> Option<&'static str> {
    let text = input.trim();
    let name = text.strip_prefix('/')?.trim();
    match fold(name).as_str() {
        "apps" | "applications" => Some("apps"),
        "folders" => Some("folders"),
        "settings" | "system settings" => Some("settings"),
        "actions" => Some("actions"),
        _ => None,
    }
}

pub fn filter_results(input: &str, include_sources: bool) -> Option<Value> {
    let text = input.trim();
    let prefix = text.strip_prefix('/')?;
    if !prefix
        .chars()
        .all(|ch| ch.is_ascii_alphabetic() || ch == ' ')
    {
        return None;
    }
    let prefix = fold(prefix.trim());
    let sources = [
        ("files", "Files", "Files", "text-x-generic-symbolic"),
        ("clipboard", "Clipboard", "Clipboard", "edit-paste-symbolic"),
    ];
    let mut filters = Vec::new();
    filters.push(FILTERS[0]);
    if include_sources {
        filters.push(sources[0]);
    }
    filters.extend_from_slice(&FILTERS[1..]);
    if include_sources {
        filters.push(sources[1]);
    }
    let matches = filters
        .into_iter()
        .filter(|(key, label, token, _)| {
            fold(label).starts_with(&prefix)
                || fold(token).starts_with(&prefix)
                || (*key == "settings" && "system settings".starts_with(&prefix))
        })
        .map(|(key, label, _token, icon)| {
            json!({
                "kind":"filter", "name":label, "id":format!("filter:{key}"),
                "key":key, "icons":[icon], "sub":"Filter results"
            })
        })
        .collect::<Vec<_>>();
    Some(json!(matches))
}

pub fn dispatch(request: &Value) -> Value {
    let input = request.get("text").and_then(Value::as_str).unwrap_or("");
    match request.get("op").and_then(Value::as_str).unwrap_or("") {
        "category" => json!(app_category(input)),
        "command" => json!(filter_command(input)),
        "results" => filter_results(
            input,
            request
                .get("include_sources")
                .and_then(Value::as_bool)
                .unwrap_or(false),
        )
        .unwrap_or(Value::Null),
        _ => Value::Null,
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn category_uses_first_matching_group() {
        assert_eq!(
            app_category("Office;Email;Game;"),
            Some("Productivity & Finance")
        );
        assert_eq!(app_category("Unknown;"), None);
    }
    #[test]
    fn selectors_keep_scope_and_order() {
        assert_eq!(filter_command(" /Applications "), Some("apps"));
        assert_eq!(filter_command("/pdf"), None);
        let results = filter_results("/f", true).unwrap();
        assert_eq!(
            results
                .as_array()
                .unwrap()
                .iter()
                .map(|item| item["key"].as_str().unwrap())
                .collect::<Vec<_>>(),
            vec!["files", "folders"]
        );
        assert_eq!(filter_results("/tmp/report.pdf", false), None);
    }
}
