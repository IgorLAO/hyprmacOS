use serde_json::{json, Value};
use std::env;
use std::fs;
use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};

fn root() -> PathBuf {
    env::var_os("HYPRMAC_ROOT")
        .map(PathBuf::from)
        .unwrap_or_else(|| {
            Path::new(&env::var("HOME").unwrap_or_default()).join("Projects/hyprmac")
        })
}

fn config_path() -> PathBuf {
    Path::new(&env::var("HOME").unwrap_or_default()).join(".config/hyprmac/acessibilidade.json")
}

fn load() -> Value {
    let data = fs::read(config_path())
        .ok()
        .and_then(|bytes| serde_json::from_slice::<Value>(&bytes).ok())
        .unwrap_or(Value::Null);
    json!({"reduce_transparency": data["reduce_transparency"].as_bool().unwrap_or(false),
           "increase_contrast": data["increase_contrast"].as_bool().unwrap_or(false)})
}

fn write_if_changed(path: &Path, content: &str) -> Result<(), String> {
    if fs::read_to_string(path).ok().as_deref() == Some(content) {
        return Ok(());
    }
    fs::write(path, content).map_err(|e| e.to_string())
}

fn css(options: &Value, dark: bool) -> (String, String) {
    let header = "/* gerado por scripts/acessibilidade */\n";
    let mut bar = header.to_owned();
    let mut gtk = header.to_owned();
    if options["reduce_transparency"].as_bool().unwrap_or(false) {
        let (background, text, menu, popover, tooltip) = if dark {
            (
                "rgb(36, 36, 40)",
                "#ffffff",
                "rgb(40, 40, 44)",
                "rgb(40, 40, 43)",
                "rgb(44, 44, 47)",
            )
        } else {
            (
                "rgb(236, 236, 236)",
                "#000000",
                "rgb(246, 246, 246)",
                "rgb(250, 250, 250)",
                "rgb(250, 250, 250)",
            )
        };
        bar.push_str(&format!(
            "window#waybar.top {{ background: {background}; }}\n"
        ));
        bar.push_str(&format!(
            "window#waybar.top label {{ color: {text}; text-shadow: none; }}\n"
        ));
        bar.push_str(&format!(
            "window#waybar.top menu, window#waybar.top tooltip {{ background: {menu}; }}\n"
        ));
        gtk.push_str(&format!("@define-color mac_menu    {menu};\n@define-color mac_popover {popover};\n@define-color mac_tooltip {tooltip};\n"));
    }
    if options["increase_contrast"].as_bool().unwrap_or(false) {
        let border = if dark {
            "rgba(255, 255, 255, 0.70)"
        } else {
            "rgba(0, 0, 0, 0.60)"
        };
        bar.push_str(&format!(
            "window#waybar.top {{ border-bottom: 1px solid {border}; }}\n"
        ));
        gtk.push_str(&format!(
            "@define-color mac_stroke    {border};\n@define-color mac_separator {border};\n"
        ));
    }
    (bar, gtk)
}

fn apply(options: &Value) -> Result<(), String> {
    let output = Command::new("gsettings")
        .args(["get", "org.gnome.desktop.interface", "color-scheme"])
        .stdout(Stdio::piped())
        .stderr(Stdio::null())
        .output()
        .map_err(|e| e.to_string())?;
    let dark = String::from_utf8_lossy(&output.stdout).contains("prefer-dark");
    let (bar, gtk) = css(options, dark);
    let root = root();
    write_if_changed(&root.join("waybar/a11y.css"), &bar)?;
    write_if_changed(&root.join("gtk/a11y3.css"), &gtk)?;
    write_if_changed(&root.join("gtk/a11y4.css"), &gtk)?;
    let _ = Command::new("pkill")
        .args(["-SIGUSR2", "-x", "waybar"])
        .stderr(Stdio::null())
        .status();
    let _ = Command::new(root.join("scripts/vidro"))
        .arg("recarregar")
        .stdout(Stdio::null())
        .stderr(Stdio::null())
        .status();
    Ok(())
}

fn run() -> Result<(), String> {
    let mut args = env::args().skip(1);
    let mut options = load();
    if let Some(feature) = args.next() {
        let key = match feature.as_str() {
            "transparency" => "reduce_transparency",
            "contrast" => "increase_contrast",
            _ => {
                return Err(
                    "uso: hyprmac-acessibilidade [transparency|contrast] [on|off|toggle]".into(),
                )
            }
        };
        let action = args.next().unwrap_or_else(|| "toggle".into());
        let current = options[key].as_bool().unwrap_or(false);
        options[key] = json!(match action.as_str() {
            "toggle" => !current,
            "on" => true,
            _ => false,
        });
        let path = config_path();
        fs::create_dir_all(path.parent().ok_or("configuração inválida")?)
            .map_err(|e| e.to_string())?;
        fs::write(
            path,
            serde_json::to_vec_pretty(&options).map_err(|e| e.to_string())?,
        )
        .map_err(|e| e.to_string())?;
    }
    apply(&options)
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

    #[test]
    fn solid_and_high_contrast_css_use_dark_values() {
        let (bar, gtk) = css(
            &json!({"reduce_transparency":true,"increase_contrast":true}),
            true,
        );
        assert!(bar.contains("background: rgb(36, 36, 40)"));
        assert!(bar.contains("border-bottom: 1px solid rgba(255, 255, 255, 0.70)"));
        assert!(gtk.contains("@define-color mac_menu    rgb(40, 40, 44)"));
    }
}
