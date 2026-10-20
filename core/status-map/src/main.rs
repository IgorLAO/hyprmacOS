//! Gera os mapas SVG e o bloco de status do README a partir dos dados curados.
use regex::Regex;
use serde_json::Value;
use std::fs;
use std::path::{Path, PathBuf};

type Item = (String, &'static str);
type Areas = Vec<(String, Vec<Item>)>;

const STATES: [&str; 6] = ["feito", "parcial", "inicio", "diverge", "falta", "fora"];

fn color(state: &str) -> &'static str {
    match state {
        "feito" => "#3fb44b",
        "parcial" => "#9bc53d",
        "inicio" => "#d6a531",
        "diverge" => "#d0583c",
        "falta" => "#7b7d86",
        _ => "#4a4c55",
    }
}

fn label(state: &str) -> &'static str {
    match state {
        "feito" => "feito",
        "parcial" => "parcial testado",
        "inicio" => "parcial/relatado",
        "diverge" => "diverge",
        "falta" => "a fazer",
        _ => "não conta",
    }
}

fn weight(state: &str) -> f64 {
    match state {
        "feito" => 1.0,
        "parcial" => 0.5,
        "inicio" => 0.25,
        _ => 0.0,
    }
}

fn xml(s: &str) -> String {
    s.replace('&', "&amp;")
        .replace('<', "&lt;")
        .replace('>', "&gt;")
        .replace('"', "&quot;")
        .replace('\'', "&#x27;")
}

fn add(areas: &mut Areas, area: &str, id: String, state: &'static str) {
    if let Some((_, items)) = areas.iter_mut().find(|(name, _)| name == area) {
        items.push((id, state));
    } else {
        areas.push((area.to_string(), vec![(id, state)]));
    }
}

fn behaviors(root: &Path) -> Result<Areas, String> {
    let content = read(&root.join("BaseConhecimento/LISTA-DE-DESEJOS.md"))?;
    let re = Regex::new(r"(?m)^\| ([A-Z]{3})-(\d+) \| P\d \| [^|]*\| ([A-Z_]+) \| ([A-Z_]+) \|")
        .unwrap();
    let mut areas = Areas::new();
    for capture in re.captures_iter(&content) {
        let area = match &capture[1] {
            "DCK" => "Dock",
            "BAR" => "Barra",
            "GLS" => "Vidro",
            "WIN" => "Janelas",
            "SPT" => "Spotlight",
            "MSC" => "Mission Ctrl",
            "CCN" => "Central",
            "FIL" => "Finder",
            "MIC" => "Microinterações",
            "INT" => "Integrações",
            _ => continue,
        };
        let implementation = &capture[3];
        let validation = &capture[4];
        let state = if implementation == "IMPLEMENTADO" && validation != "NAO_AVALIADO" {
            "feito"
        } else if ["IMPLEMENTADO", "PARCIAL"].contains(&implementation)
            && validation != "NAO_AVALIADO"
        {
            "parcial"
        } else if ["IMPLEMENTADO", "PARCIAL", "RELATADO_PARCIAL"].contains(&implementation) {
            "inicio"
        } else if implementation == "DIVERGE" {
            "diverge"
        } else {
            "falta"
        };
        add(
            &mut areas,
            area,
            format!("{}-{}", &capture[1], &capture[2]),
            state,
        );
    }
    Ok(areas)
}

fn parameters(root: &Path) -> Result<Areas, String> {
    let content = read(&root.join("BaseConhecimento/comparacao/MATRIZ.md"))?;
    let re = Regex::new(r"^\| ([A-Z]{2,5}-\d+) \|").unwrap();
    let mut areas = Areas::new();
    let mut area = String::new();
    for line in content.lines() {
        if line.starts_with("## ") && line.contains('—') {
            area = line[3..].split('—').next().unwrap_or("").trim().to_string();
            continue;
        }
        if let Some(capture) = re.captures(line) {
            if area.is_empty() {
                continue;
            }
            let cells: Vec<_> = line.trim_matches('|').split('|').map(str::trim).collect();
            let state = cells
                .iter()
                .skip(4)
                .find_map(|cell| match *cell {
                    "✅" => Some("feito"),
                    "🟡" => Some("parcial"),
                    "🔴" => Some("diverge"),
                    "⬜" => Some("falta"),
                    "➖" => Some("fora"),
                    _ => None,
                })
                .unwrap_or("falta");
            add(&mut areas, &area, capture[1].to_string(), state);
        }
    }
    Ok(areas)
}

fn apps(root: &Path) -> Result<Areas, String> {
    let content = read(&root.join("BaseConhecimento/referencias/hyprmac-apps-progress.json"))?;
    let data: Value = serde_json::from_str(&content).map_err(|error| error.to_string())?;
    let mut areas = Areas::new();
    for app in data["apps"].as_array().ok_or("apps inválido")? {
        let functionality = app["functionality"].as_str().unwrap_or("");
        let fidelity = app["fidelity"].as_str().unwrap_or("");
        let state = if fidelity.starts_with("verified") || fidelity == "certified" {
            "feito"
        } else if functionality == "unverified" {
            "inicio"
        } else if functionality.contains("verified") || functionality.contains("tested") {
            "parcial"
        } else {
            "falta"
        };
        let group = match app["group"].as_str().unwrap_or("?") {
            "A" => "Grupo A",
            "B" => "Grupo B",
            "C" => "Grupo C",
            "D" => "Grupo D",
            other => other,
        };
        add(
            &mut areas,
            group,
            app["name"].as_str().unwrap_or("?").to_string(),
            state,
        );
    }
    Ok(areas)
}

fn worst(row: &[f64], side: f64) -> f64 {
    let sum: f64 = row.iter().sum();
    row.iter()
        .map(|value| (side * side * value / (sum * sum)).max(sum * sum / (side * side * value)))
        .fold(0.0, f64::max)
}

fn squarify(
    weights: &[usize],
    mut x: f64,
    mut y: f64,
    mut w: f64,
    mut h: f64,
) -> Vec<(f64, f64, f64, f64)> {
    let total: usize = weights.iter().sum();
    if total == 0 {
        return Vec::new();
    }
    let scale = w * h / total as f64;
    let remaining: Vec<f64> = weights.iter().map(|value| *value as f64 * scale).collect();
    let mut rects = Vec::new();
    let mut index = 0;
    while index < remaining.len() {
        let side = w.min(h);
        let mut row = vec![remaining[index]];
        index += 1;
        while index < remaining.len() {
            let mut next = row.clone();
            next.push(remaining[index]);
            if worst(&next, side) > worst(&row, side) {
                break;
            }
            row.push(remaining[index]);
            index += 1;
        }
        let sum: f64 = row.iter().sum();
        if w >= h {
            let width = sum / h;
            let mut yy = y;
            for value in row {
                let height = value / width;
                rects.push((x, yy, width, height));
                yy += height;
            }
            x += width;
            w -= width;
        } else {
            let height = sum / w;
            let mut xx = x;
            for value in row {
                let width = value / height;
                rects.push((xx, y, width, height));
                xx += width;
            }
            y += height;
            h -= height;
        }
    }
    rects
}

fn grid(n: usize, w: f64, h: f64) -> (usize, usize) {
    let mut best = (1, n);
    let mut lowest = f64::INFINITY;
    for cols in 1..=n {
        let rows = n.div_ceil(cols);
        let cw = w / cols as f64;
        let ch = h / rows as f64;
        let cost = (cw / ch).max(ch / cw) + (cols * rows - n) as f64 * 0.02;
        if cost < lowest {
            lowest = cost;
            best = (cols, rows);
        }
    }
    best
}

fn score(items: &[Item]) -> f64 {
    let valid: Vec<_> = items.iter().filter(|(_, state)| *state != "fora").collect();
    if valid.is_empty() {
        return 0.0;
    }
    100.0 * valid.iter().map(|(_, state)| weight(state)).sum::<f64>() / valid.len() as f64
}

fn svg_map(title: &str, areas: &Areas) -> (String, f64) {
    let (width, height, top) = (520.0, 260.0, 26.0);
    let items: Vec<Item> = areas
        .iter()
        .flat_map(|(_, items)| items.iter().cloned())
        .collect();
    let pct = score(&items);
    let complete = items.iter().filter(|(_, state)| *state == "feito").count();
    let mut names: Vec<_> = areas.iter().collect();
    names.sort_by_key(|(_, items)| std::cmp::Reverse(items.len()));
    let rects = squarify(
        &names
            .iter()
            .map(|(_, items)| items.len())
            .collect::<Vec<_>>(),
        0.0,
        top,
        width,
        height - top,
    );
    let mut parts = vec![
        format!("<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"520\" height=\"260\" viewBox=\"0 0 520 260\" font-family=\"Inter,Segoe UI,Helvetica,Arial,sans-serif\">"),
        "<rect width=\"520\" height=\"260\" fill=\"#1f2026\"/>".to_string(),
        format!("<text x=\"4\" y=\"17\" font-size=\"13\" fill=\"#e6e6ea\">{}: {:.1}% ({}/{} feitos)</text>", xml(title), pct, complete, items.len()),
    ];
    for ((name, items), (x, y, w, h)) in names.into_iter().zip(rects) {
        let mut cells = items.clone();
        cells.sort_by_key(|(_, state)| {
            STATES
                .iter()
                .position(|candidate| candidate == state)
                .unwrap()
        });
        let (cols, _) = grid(cells.len(), w - 2.0, h - 2.0);
        let cw = (w - 2.0) / cols as f64;
        let rows = cells.len().div_ceil(cols);
        let ch = (h - 2.0) / rows as f64;
        parts.push(format!(
            "<g><title>{} — {:.0}%</title>",
            xml(name),
            score(&cells)
        ));
        parts.push(format!(
            "<rect x=\"{x:.1}\" y=\"{y:.1}\" width=\"{w:.1}\" height=\"{h:.1}\" fill=\"#16171c\"/>"
        ));
        for (index, (ident, state)) in cells.iter().enumerate() {
            let cx = x + 1.0 + (index % cols) as f64 * cw;
            let cy = y + 1.0 + (index / cols) as f64 * ch;
            parts.push(format!("<rect x=\"{:.1}\" y=\"{:.1}\" width=\"{:.1}\" height=\"{:.1}\" fill=\"{}\"><title>{}: {}</title></rect>", cx + 0.5, cy + 0.5, (cw - 1.0).max(0.5), (ch - 1.0).max(0.5), color(state), xml(ident), label(state)));
        }
        if w > 34.0 && h > 14.0 {
            let max_chars = (((w - 6.0) / 6.2) as usize).max(3);
            let display = if name.chars().count() as f64 * 6.2 < w - 6.0 {
                name.to_string()
            } else {
                name.chars().take(max_chars).collect()
            };
            parts.push(format!("<text x=\"{:.1}\" y=\"{:.1}\" font-size=\"10.5\" fill=\"#fff\" stroke=\"#000\" stroke-opacity=\".55\" stroke-width=\"2.4\" paint-order=\"stroke\">{}</text>", x + 3.0, y + 12.0, xml(&display)));
        }
        parts.push("</g>".to_string());
    }
    parts.push("</svg>".to_string());
    (parts.join("\n") + "\n", pct)
}

fn legend() -> String {
    let mut x = 4.0;
    let mut parts = String::new();
    for (index, state) in STATES.into_iter().enumerate() {
        let position = if index == 0 {
            "4".to_string()
        } else {
            format!("{x:?}")
        };
        let text_position = if index == 0 {
            "20".to_string()
        } else {
            format!("{:?}", x + 16.0)
        };
        parts.push_str(&format!("<rect x=\"{position}\" y=\"5\" width=\"12\" height=\"12\" fill=\"{}\"/><text x=\"{text_position}\" y=\"15\" font-size=\"11\" fill=\"#c9c9d0\">{}</text>", color(state), label(state)));
        x += 22.0 + label(state).chars().count() as f64 * 6.3;
    }
    let width = x as i32;
    format!("<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"{width}\" height=\"22\" font-family=\"Inter,Segoe UI,Helvetica,Arial,sans-serif\"><rect width=\"{width}\" height=\"22\" fill=\"#1f2026\"/>{parts}</svg>\n")
}

fn badge(name: &str, pct: f64) -> String {
    let color = if pct >= 90.0 {
        "#3fb44b"
    } else if pct >= 60.0 {
        "#9bc53d"
    } else if pct >= 25.0 {
        "#d6a531"
    } else {
        "#d0583c"
    };
    let value = format!("{pct:.1}%");
    let a = 8.0 + name.chars().count() as f64 * 6.6;
    let b = 10.0 + value.chars().count() as f64 * 7.0;
    format!("<svg xmlns=\"http://www.w3.org/2000/svg\" width=\"{:.0}\" height=\"20\" font-family=\"Verdana,DejaVu Sans,sans-serif\" font-size=\"11\"><rect width=\"{a:.0}\" height=\"20\" fill=\"#555\"/><rect x=\"{a:.0}\" width=\"{b:.0}\" height=\"20\" fill=\"{color}\"/><text x=\"{:.0}\" y=\"14\" fill=\"#fff\" text-anchor=\"middle\">{}</text><text x=\"{:.0}\" y=\"14\" fill=\"#fff\" text-anchor=\"middle\">{value}</text></svg>\n", a + b, a / 2.0, xml(name), a + b / 2.0)
}

fn read(path: &Path) -> Result<String, String> {
    fs::read_to_string(path).map_err(|error| format!("{}: {error}", path.display()))
}

fn write_if_changed(path: &Path, content: &str) -> Result<(), String> {
    if fs::read_to_string(path).ok().as_deref() == Some(content) {
        return Ok(());
    }
    if let Some(parent) = path.parent() {
        fs::create_dir_all(parent).map_err(|error| error.to_string())?;
    }
    fs::write(path, content).map_err(|error| format!("{}: {error}", path.display()))
}

fn run(root: &Path) -> Result<(), String> {
    let maps = [
        (
            "comportamentos",
            "Comportamentos Tahoe 26",
            behaviors(root)?,
        ),
        ("parametros", "Parâmetros medidos", parameters(root)?),
        ("apps", "Apps do sistema", apps(root)?),
    ];
    let output = root.join("docs/status");
    let mut badges = Vec::new();
    let mut images = Vec::new();
    for (key, title, areas) in maps {
        let (svg, pct) = svg_map(title, &areas);
        write_if_changed(&output.join(format!("{key}.svg")), &svg)?;
        write_if_changed(&output.join(format!("selo-{key}.svg")), &badge(key, pct))?;
        badges.push(format!("![{key}](docs/status/selo-{key}.svg)"));
        images.push(format!(
            "<img src=\"docs/status/{key}.svg\" width=\"49%\" alt=\"{}\">",
            xml(title)
        ));
    }
    write_if_changed(&output.join("legenda.svg"), &legend())?;
    let block = format!("<!-- status:inicio -->\n{}\n\n<p>\n{}\n</p>\n\n![legenda](docs/status/legenda.svg)\n\nCada célula é um item: um comportamento da [lista de desejos](BaseConhecimento/LISTA-DE-DESEJOS.md), um parâmetro da [matriz](BaseConhecimento/comparacao/MATRIZ.md) ou um app do inventário Tahoe 26.6.1. Nota = feito 1 · parcial testado ½ · parcial/relatado ¼. Gerado por `scripts/status-map` a cada commit; mede o que está cadastrado, não a fidelidade global ao macOS.\n<!-- status:fim -->", badges.join(" "), images.join("\n"));
    let readme = root.join("README.md");
    let current = read(&readme).unwrap_or_else(|_| "# HyprMac\n".to_string());
    let updated = if let Some(start) = current.find("<!-- status:inicio -->") {
        if let Some(end_relative) = current[start..].find("<!-- status:fim -->") {
            let end = start + end_relative + "<!-- status:fim -->".len();
            format!("{}{}{}", &current[..start], block, &current[end..])
        } else {
            return Err("marcador de fim ausente no README".into());
        }
    } else {
        format!(
            "{}\n\n## Status\n\n{block}\n",
            current.trim_end_matches('\n')
        )
    };
    write_if_changed(&readme, &updated)
}

fn main() {
    let root = std::env::args_os()
        .nth(1)
        .map(PathBuf::from)
        .unwrap_or_else(|| PathBuf::from("."));
    if let Err(error) = run(&root) {
        eprintln!("{error}");
        std::process::exit(1);
    }
}
