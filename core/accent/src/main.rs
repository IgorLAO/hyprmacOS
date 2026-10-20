use serde_json::Value;
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

fn palette() -> Vec<Value> {
    serde_json::from_str(include_str!("../palette.json")).expect("valid palette")
}

fn colors(name: &str, dark: bool) -> Option<[u8; 3]> {
    let item = palette().into_iter().find(|item| item["name"] == name)?;
    let hex = item[if dark { "dark" } else { "light" }]
        .as_str()?
        .trim_start_matches('#');
    if hex.len() != 6 {
        return None;
    }
    Some([
        u8::from_str_radix(&hex[0..2], 16).ok()?,
        u8::from_str_radix(&hex[2..4], 16).ok()?,
        u8::from_str_radix(&hex[4..6], 16).ok()?,
    ])
}

fn hex(color: [u8; 3]) -> String {
    format!("#{:02X}{:02X}{:02X}", color[0], color[1], color[2])
}

fn mix(first: [u8; 3], second: [u8; 3], fraction: f64) -> [u8; 3] {
    std::array::from_fn(|index| {
        (first[index] as f64 + (second[index] as f64 - first[index] as f64) * fraction)
            .round()
            .clamp(0.0, 255.0) as u8
    })
}

fn current() -> String {
    let out = Command::new("gsettings")
        .args(["get", "org.gnome.desktop.interface", "accent-color"])
        .stdout(Stdio::piped())
        .stderr(Stdio::null())
        .output();
    let raw = out
        .ok()
        .map(|out| {
            String::from_utf8_lossy(&out.stdout)
                .trim()
                .trim_matches('\'')
                .to_owned()
        })
        .unwrap_or_default();
    let name = match raw.as_str() {
        "slate" => "graphite",
        "teal" => "blue",
        _ => &raw,
    };
    if colors(name, true).is_some() {
        name.to_owned()
    } else {
        "blue".to_owned()
    }
}

fn dark_mode() -> bool {
    Command::new("gsettings")
        .args(["get", "org.gnome.desktop.interface", "color-scheme"])
        .stdout(Stdio::piped())
        .stderr(Stdio::null())
        .output()
        .ok()
        .is_some_and(|out| String::from_utf8_lossy(&out.stdout).contains("prefer-dark"))
}

fn write_if_changed(path: &Path, content: &str) -> Result<(), String> {
    if fs::read_to_string(path).ok().as_deref() == Some(content) {
        return Ok(());
    }
    fs::write(path, content).map_err(|e| e.to_string())
}

fn generated(name: &str, dark: bool) -> Result<Vec<(&'static str, String)>, String> {
    let base = colors(name, dark).ok_or("cor desconhecida")?;
    let accent = hex(base);
    let highlight = hex(mix(base, [255, 255, 255], 0.2));
    let selection = if name == "blue" {
        "#0069F9".to_owned()
    } else {
        hex(mix(base, [0, 0, 0], 0.16))
    };
    let mode = if dark { "escuro" } else { "claro" };
    let header = format!("/* gerado por scripts/accent — cor de destaque: {name} ({mode}) */\n");
    let gtk = format!("{header}@define-color mac_accent      {accent};\n@define-color mac_accent_hi   {highlight};\n@define-color mac_selection   {selection};\n@define-color theme_selected_bg_color {accent};\n@define-color accent_color    {};\n@define-color accent_bg_color {accent};\n",if dark {&highlight} else {&accent});
    let gtk4 = format!(
        "{gtk}:root {{\n  --accent-bg-color: {accent};\n  --accent-color: {};\n}}\n",
        if dark { &highlight } else { &accent }
    );
    let waybar = format!("{header}@define-color accent         {accent};\n@define-color menu-selection {selection};\n");
    let wofi = format!("{header}@define-color accent {accent};\n");
    Ok(vec![
        ("gtk/accent3.css", gtk),
        ("gtk/accent4.css", gtk4),
        ("waybar/accent.css", waybar),
        ("wofi/accent.css", wofi),
    ])
}

fn apply(name: &str) -> Result<(), String> {
    let dark = dark_mode();
    for (path, content) in generated(name, dark)? {
        write_if_changed(&root().join(path), &content)?;
    }
    let gnome = if name == "graphite" { "slate" } else { name };
    let _ = Command::new("gsettings")
        .args(["set", "org.gnome.desktop.interface", "accent-color", gnome])
        .stderr(Stdio::null())
        .status();
    let [r, g, b] = colors(name, dark).ok_or("cor desconhecida")?;
    let rgb = format!("{r},{g},{b}");
    let _ = Command::new("kwriteconfig6")
        .args([
            "--file",
            "kdeglobals",
            "--group",
            "General",
            "--key",
            "AccentColor",
            &rgb,
        ])
        .stderr(Stdio::null())
        .status();
    let _ = Command::new("pkill")
        .args(["-SIGUSR2", "-x", "waybar"])
        .stderr(Stdio::null())
        .status();
    Ok(())
}

fn run() -> Result<(), String> {
    let argument = env::args().nth(1);
    if argument.as_deref() == Some("list") {
        for item in palette() {
            println!("{}", item["name"].as_str().unwrap_or(""));
        }
        return Ok(());
    }
    let name = argument.unwrap_or_else(current);
    if colors(&name, true).is_none() {
        return Err(format!("cor desconhecida: {name}"));
    }
    apply(&name)
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
    fn palette_contains_all_eight_tahoe_colors() {
        assert_eq!(palette().len(), 8);
        assert_eq!(colors("blue", true), Some([0, 122, 255]));
        assert_eq!(colors("graphite", false), Some([152, 152, 152]));
    }

    #[test]
    fn generated_css_uses_same_accent_across_toolkits() {
        let css = generated("purple", false).unwrap();
        for (_, content) in css {
            assert!(content.contains("#953D96"));
        }
    }
}
