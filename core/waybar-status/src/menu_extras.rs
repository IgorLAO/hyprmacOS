//! Persistência das preferências SNI da barra, compartilhada com o script de diagnóstico.

use serde_json::{json, Value};
use std::env;
use std::fs::{self, OpenOptions};
use std::io::Write;
use std::os::fd::AsRawFd;
use std::os::unix::fs::OpenOptionsExt;
use std::path::{Path, PathBuf};

fn config_path() -> Result<PathBuf, String> {
    if let Some(path) = env::var_os("HYPRMAC_MENU_EXTRAS_CONFIG") {
        return Ok(PathBuf::from(path));
    }
    let base = env::var_os("XDG_CONFIG_HOME")
        .map(PathBuf::from)
        .or_else(|| env::var_os("HOME").map(|home| PathBuf::from(home).join(".config")))
        .ok_or("HOME e XDG_CONFIG_HOME ausentes")?;
    Ok(base.join("hyprmac/menu-extras.json"))
}

fn validate(data: &Value) -> Result<(), String> {
    let tray = data
        .as_object()
        .and_then(|root| root.get("tray"))
        .filter(|tray| tray.is_object());
    if !data.is_object() || data.get("tray").is_some() && tray.is_none() {
        return Err("Configuração de extras inválida".into());
    }
    for key in ["hidden-items", "order-items"] {
        if let Some(value) = tray.and_then(|tray| tray.get(key)) {
            if !value
                .as_array()
                .is_some_and(|values| values.iter().all(Value::is_string))
            {
                return Err(format!("Lista inválida: {key}"));
            }
        }
    }
    Ok(())
}

fn update(mut data: Value, action: &str, identities: &[String]) -> Result<Value, String> {
    validate(&data)?;
    let root = data
        .as_object_mut()
        .ok_or("Configuração de extras inválida")?;
    let tray = root.entry("tray").or_insert_with(|| json!({}));
    let tray = tray
        .as_object_mut()
        .ok_or("Configuração de extras inválida")?;
    match action {
        "order" => {
            let mut ordered = Vec::new();
            for identity in identities {
                if !ordered.contains(identity) {
                    ordered.push(identity.clone());
                }
            }
            tray.insert("order-items".into(), json!(ordered));
        }
        "hide" | "show" => {
            let identity = identities.first().ok_or("identidade ausente")?;
            if identities.len() != 1 {
                return Err("uso: hide|show <identidade>".into());
            }
            let mut hidden: Vec<String> = tray
                .get("hidden-items")
                .and_then(Value::as_array)
                .into_iter()
                .flatten()
                .filter_map(|item| item.as_str().map(str::to_owned))
                .collect();
            hidden.retain(|item| item != identity);
            if action == "hide" {
                hidden.push(identity.clone());
            }
            hidden.sort();
            hidden.dedup();
            tray.insert("hidden-items".into(), json!(hidden));
        }
        _ => return Err(format!("comando desconhecido: {action}")),
    }
    Ok(data)
}

fn save(path: &Path, data: &Value) -> Result<(), String> {
    let parent = path.parent().ok_or("caminho de configuração inválido")?;
    let bytes = format!(
        "{}\n",
        serde_json::to_string_pretty(data).map_err(|error| error.to_string())?
    );
    for attempt in 0..20 {
        let temp = parent.join(format!(".menu-extras-{}-{attempt}", std::process::id()));
        match OpenOptions::new()
            .write(true)
            .create_new(true)
            .mode(0o600)
            .open(&temp)
        {
            Ok(mut file) => {
                let result = file
                    .write_all(bytes.as_bytes())
                    .and_then(|()| file.sync_all())
                    .and_then(|()| fs::rename(&temp, path));
                if result.is_err() {
                    let _ = fs::remove_file(&temp);
                }
                return result.map_err(|error| error.to_string());
            }
            Err(error) if error.kind() == std::io::ErrorKind::AlreadyExists => continue,
            Err(error) => return Err(error.to_string()),
        }
    }
    Err("não foi possível criar arquivo temporário".into())
}

pub fn run(args: &[String]) -> Result<(), String> {
    let (action, identities) = args
        .split_first()
        .ok_or("uso: menu-extras-pref hide|show|order")?;
    let path = config_path()?;
    let parent = path.parent().ok_or("caminho de configuração inválido")?;
    fs::create_dir_all(parent).map_err(|error| error.to_string())?;
    let lock_path = path.with_extension("lock");
    let lock = OpenOptions::new()
        .append(true)
        .create(true)
        .open(lock_path)
        .map_err(|error| error.to_string())?;
    if unsafe { libc::flock(lock.as_raw_fd(), libc::LOCK_EX) } != 0 {
        return Err(std::io::Error::last_os_error().to_string());
    }
    let data = match fs::read_to_string(&path) {
        Ok(text) => serde_json::from_str(&text).map_err(|error| error.to_string())?,
        Err(error) if error.kind() == std::io::ErrorKind::NotFound => {
            json!({"tray":{"hidden-items":[],"order-items":[]}})
        }
        Err(error) => return Err(error.to_string()),
    };
    save(&path, &update(data, action, identities)?)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn preserves_unknown_fields_and_order() {
        let state = json!({"tray":{"order-items":["vlc"],"show-passive-items":false},"other":true});
        let hidden = update(state, "hide", &["title:Application with spaces".into()]).unwrap();
        assert_eq!(
            hidden["tray"]["hidden-items"],
            json!(["title:Application with spaces"])
        );
        assert_eq!(hidden["tray"]["order-items"], json!(["vlc"]));
        assert_eq!(hidden["other"], true);
        let shown = update(hidden, "show", &["title:Application with spaces".into()]).unwrap();
        assert_eq!(shown["tray"]["hidden-items"], json!([]));
    }

    #[test]
    fn deduplicates_order_and_rejects_invalid_state() {
        let ordered = update(
            json!({}),
            "order",
            &["nm".into(), "vlc".into(), "nm".into()],
        )
        .unwrap();
        assert_eq!(ordered["tray"]["order-items"], json!(["nm", "vlc"]));
        assert!(update(json!({"tray": []}), "hide", &["vlc".into()]).is_err());
        assert!(update(
            json!({"tray":{"hidden-items":[1]}}),
            "show",
            &["vlc".into()]
        )
        .is_err());
    }
}
