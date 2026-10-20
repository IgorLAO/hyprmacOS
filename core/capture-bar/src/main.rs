//! Barra de captura ⇧⌘5. A interface e suas opções executam em Rust.
use gtk::cairo::{Context, Operator};
use gtk::gdk;
use gtk::glib::{self, ControlFlow};
use gtk::prelude::*;
use gtk_layer_shell::{Edge, KeyboardMode, Layer, LayerShell};
use serde_json::{Map, Value};
use std::cell::RefCell;
use std::env;
use std::fs;
use std::os::unix::process::CommandExt;
use std::path::{Path, PathBuf};
use std::process::Command;
use std::rc::Rc;
use std::time::Duration;

const MODES: [(&str, &str); 6] = [
    ("screen", "Capture Entire Screen"),
    ("pick", "Capture Selected Window"),
    ("region", "Capture Selected Portion"),
    ("rec-screen", "Record Entire Screen"),
    ("rec-pick", "Record Selected Window"),
    ("rec-region", "Record Selected Portion"),
];
const DESTINATIONS: [(&str, &str); 4] = [
    ("desktop", "Desktop"),
    ("documents", "Documents"),
    ("screenshots", "Screenshots"),
    ("clipboard", "Clipboard"),
];
const TIMERS: [(u64, &str); 3] = [(0, "None"), (5, "5 Seconds"), (10, "10 Seconds")];

#[derive(Clone, Debug)]
struct Options {
    destination: String,
    delay: u64,
    thumbnail: bool,
    microphone: bool,
    cursor: bool,
    mode: String,
    extra: Map<String, Value>,
}

#[derive(Clone, Copy)]
enum ToggleOption {
    FloatingThumbnail,
    RecordMicrophone,
    MousePointer,
}

impl ToggleOption {
    fn label(self) -> &'static str {
        match self {
            Self::FloatingThumbnail => "Show Floating Thumbnail",
            Self::RecordMicrophone => "Record Microphone",
            Self::MousePointer => "Show Mouse Pointer",
        }
    }

    fn selected(self, options: &Options) -> bool {
        match self {
            Self::FloatingThumbnail => options.thumbnail,
            Self::RecordMicrophone => options.microphone,
            Self::MousePointer => options.cursor,
        }
    }

    fn toggle(self, options: &mut Options) {
        let setting = match self {
            Self::FloatingThumbnail => &mut options.thumbnail,
            Self::RecordMicrophone => &mut options.microphone,
            Self::MousePointer => &mut options.cursor,
        };
        *setting = !*setting;
    }
}

impl Default for Options {
    fn default() -> Self {
        Self {
            destination: "desktop".into(),
            delay: 0,
            thumbnail: true,
            microphone: false,
            cursor: false,
            mode: "region".into(),
            extra: Map::new(),
        }
    }
}

impl Options {
    fn from_json(value: Value) -> Self {
        let mut options = Self::default();
        let Value::Object(mut data) = value else {
            return options;
        };
        options.destination = data
            .remove("destino")
            .and_then(|v| v.as_str().map(str::to_owned))
            .filter(|v| DESTINATIONS.iter().any(|(key, _)| key == v))
            .unwrap_or(options.destination);
        options.delay = data
            .remove("tempo")
            .and_then(|v| v.as_u64())
            .filter(|v| TIMERS.iter().any(|(delay, _)| delay == v))
            .unwrap_or(options.delay);
        options.thumbnail = data
            .remove("miniatura")
            .and_then(|v| v.as_bool())
            .unwrap_or(options.thumbnail);
        options.microphone = data
            .remove("microfone")
            .and_then(|v| v.as_bool())
            .unwrap_or(options.microphone);
        options.cursor = data
            .remove("ponteiro")
            .and_then(|v| v.as_bool())
            .unwrap_or(options.cursor);
        options.mode = data
            .remove("modo")
            .and_then(|v| v.as_str().map(str::to_owned))
            .filter(|v| MODES.iter().any(|(key, _)| key == v))
            .unwrap_or(options.mode);
        options.extra = data;
        options
    }

    fn to_json(&self) -> Value {
        let mut data = self.extra.clone();
        data.insert("destino".into(), self.destination.clone().into());
        data.insert("tempo".into(), self.delay.into());
        data.insert("miniatura".into(), self.thumbnail.into());
        data.insert("microfone".into(), self.microphone.into());
        data.insert("ponteiro".into(), self.cursor.into());
        data.insert("modo".into(), self.mode.clone().into());
        Value::Object(data)
    }
}

fn repo_root() -> PathBuf {
    PathBuf::from(env!("CARGO_MANIFEST_DIR")).join("../..")
}

fn config_file() -> PathBuf {
    let base = env::var_os("XDG_CONFIG_HOME")
        .map(PathBuf::from)
        .unwrap_or_else(|| PathBuf::from(env::var_os("HOME").unwrap_or_default()).join(".config"));
    base.join("hyprmac/captura.json")
}

fn pid_file() -> PathBuf {
    PathBuf::from(env::var_os("XDG_RUNTIME_DIR").unwrap_or_else(|| "/tmp".into()))
        .join("hyprmac-captura.pid")
}

fn load_options(path: &Path) -> Options {
    fs::read_to_string(path)
        .ok()
        .and_then(|text| serde_json::from_str(&text).ok())
        .map(Options::from_json)
        .unwrap_or_default()
}

fn save_options(path: &Path, options: &Options) -> Result<(), String> {
    let parent = path.parent().ok_or("caminho de configuração inválido")?;
    fs::create_dir_all(parent).map_err(|error| error.to_string())?;
    let text =
        serde_json::to_string_pretty(&options.to_json()).map_err(|error| error.to_string())?;
    let temporary = parent.join(format!(".captura-{}.tmp", std::process::id()));
    fs::write(&temporary, format!("{text}\n")).map_err(|error| error.to_string())?;
    fs::rename(temporary, path).map_err(|error| error.to_string())
}

fn toggle_previous(path: &Path) -> bool {
    let Some(pid) = fs::read_to_string(path)
        .ok()
        .and_then(|s| s.trim().parse::<i32>().ok())
    else {
        return false;
    };
    let Some(cmdline) = fs::read(format!("/proc/{pid}/cmdline")).ok() else {
        return false;
    };
    if !cmdline
        .windows(b"hyprmac-capture-bar".len())
        .any(|part| part == b"hyprmac-capture-bar")
    {
        return false;
    }
    unsafe { libc::kill(pid, libc::SIGTERM) == 0 }
}

fn dark_theme() -> bool {
    Command::new("gsettings")
        .args(["get", "org.gnome.desktop.interface", "color-scheme"])
        .output()
        .is_ok_and(|out| String::from_utf8_lossy(&out.stdout).contains("prefer-dark"))
}

fn glass_loaded() -> bool {
    Command::new("hyprctl")
        .args(["plugin", "list"])
        .output()
        .is_ok_and(|out| String::from_utf8_lossy(&out.stdout).contains("hyprglass"))
}

fn accent_color(dark: bool) -> String {
    let fallback = if dark { "#0091FF" } else { "#0088FF" };
    let Ok(css) = fs::read_to_string(repo_root().join("gtk/accent3.css")) else {
        return fallback.into();
    };
    css.lines()
        .find_map(|line| {
            let parts: Vec<_> = line.split_whitespace().collect();
            (parts.len() >= 3 && parts[0] == "@define-color" && parts[1] == "mac_accent")
                .then(|| parts[2].trim_end_matches(';'))
                .filter(|color| {
                    color.len() == 7
                        && color.starts_with('#')
                        && color[1..].bytes().all(|byte| byte.is_ascii_hexdigit())
                })
                .map(str::to_owned)
        })
        .unwrap_or_else(|| fallback.into())
}

fn style(dark: bool) -> String {
    let colors = if dark {
        [
            (
                "cap_bg",
                if glass_loaded() {
                    "rgba(8, 8, 10, 0.76)"
                } else {
                    "rgba(30, 30, 34, 0.80)"
                },
            ),
            ("cap_rim", "rgba(255, 255, 255, 0.14)"),
            ("cap_hover", "rgba(255, 255, 255, 0.08)"),
            ("cap_sel", "rgba(255, 255, 255, 0.14)"),
            ("cap_dim", "rgba(255, 255, 255, 0.55)"),
            ("cap_x", "rgba(255, 255, 255, 0.30)"),
            ("cap_xfg", "rgba(30, 30, 34, 0.90)"),
            ("cap_sep", "rgba(255, 255, 255, 0.14)"),
            ("cap_tip", "rgba(40, 40, 44, 0.96)"),
        ]
    } else {
        [
            (
                "cap_bg",
                if glass_loaded() {
                    "rgba(255, 255, 255, 0.66)"
                } else {
                    "rgba(236, 236, 238, 0.82)"
                },
            ),
            ("cap_rim", "rgba(255, 255, 255, 0.60)"),
            ("cap_hover", "rgba(0, 0, 0, 0.05)"),
            ("cap_sel", "rgba(0, 0, 0, 0.08)"),
            ("cap_dim", "rgba(0, 0, 0, 0.45)"),
            ("cap_x", "rgba(0, 0, 0, 0.45)"),
            ("cap_xfg", "rgba(255, 255, 255, 0.95)"),
            ("cap_sep", "rgba(0, 0, 0, 0.10)"),
            ("cap_tip", "rgba(236, 236, 238, 0.96)"),
        ]
    };
    let mut css = String::new();
    for (name, color) in colors {
        css.push_str(&format!("@define-color {name} {color};\n"));
    }
    css.push_str(&format!(
        "@define-color cap_accent {};\n",
        accent_color(dark)
    ));
    css.push_str(include_str!("style.css"));
    css
}

fn rounded(cr: &Context, x: f64, y: f64, w: f64, h: f64, r: f64) {
    cr.new_sub_path();
    cr.arc(x + w - r, y + r, r, -std::f64::consts::FRAC_PI_2, 0.0);
    cr.arc(x + w - r, y + h - r, r, 0.0, std::f64::consts::FRAC_PI_2);
    cr.arc(
        x + r,
        y + h - r,
        r,
        std::f64::consts::FRAC_PI_2,
        std::f64::consts::PI,
    );
    cr.arc(
        x + r,
        y + r,
        r,
        std::f64::consts::PI,
        std::f64::consts::PI * 1.5,
    );
    cr.close_path();
}

fn icon(mode: &str, dark: bool) -> gtk::DrawingArea {
    let area = gtk::DrawingArea::new();
    let recording = mode.starts_with("rec-");
    let base = mode.trim_start_matches("rec-").to_owned();
    area.set_size_request(if recording { 48 } else { 46 }, 37);
    area.connect_draw(move |area, cr| {
        let (w, h) = (28.0, 21.0);
        let x = (area.allocated_width() as f64 - w) / 2.0 - if recording { 4.0 } else { 0.0 };
        let y = (area.allocated_height() as f64 - h) / 2.0;
        let (r, g, b) = if dark {
            (1.0, 1.0, 1.0)
        } else {
            (0.42, 0.48, 0.50)
        };
        let opacity = if dark { 0.85 } else { 0.95 };
        cr.set_source_rgba(r, g, b, opacity);
        cr.set_line_width(1.7);
        cr.set_line_join(gtk::cairo::LineJoin::Round);
        if base == "region" {
            cr.set_dash(&[3.6, 2.6], 0.0);
            rounded(cr, x + 0.85, y + 0.85, w - 1.7, h - 1.7, 3.5);
            let _ = cr.stroke();
            cr.set_dash(&[], 0.0);
        } else {
            rounded(cr, x + 0.85, y + 0.85, w - 1.7, h - 1.7, 4.0);
            let _ = cr.stroke();
            if base == "screen" {
                cr.rectangle(x + 4.0, y + h - 7.5, w - 8.0, 3.4);
                let _ = cr.fill();
            } else {
                for n in 0..3 {
                    cr.arc(x + 5.0 + n as f64 * 3.2, y + 5.0, 0.95, 0.0, 6.3);
                    let _ = cr.fill();
                }
            }
        }
        if recording {
            let (cx, cy) = (x + w + 1.0, y + h - 1.0);
            cr.set_operator(Operator::Clear);
            cr.arc(cx, cy, 7.2, 0.0, 6.3);
            let _ = cr.fill();
            cr.set_operator(Operator::Over);
            cr.set_source_rgba(r, g, b, opacity);
            cr.set_line_width(1.5);
            cr.arc(cx, cy, 5.6, 0.0, 6.3);
            let _ = cr.stroke();
            cr.arc(cx, cy, 3.6, 0.0, 6.3);
            let _ = cr.fill();
        }
        glib::Propagation::Stop
    });
    area
}

fn folder(destination: &str, video: bool) -> PathBuf {
    let home = PathBuf::from(env::var_os("HOME").unwrap_or_default());
    let (kind, fallback) = match destination {
        "desktop" => (glib::UserDirectory::Desktop, "Desktop"),
        "documents" => (glib::UserDirectory::Documents, "Documents"),
        _ if video => (glib::UserDirectory::Videos, "Movies"),
        _ => return home.join("Pictures/Screenshots"),
    };
    glib::user_special_dir(kind).unwrap_or_else(|| home.join(fallback))
}

fn launch(options: &Options) -> Result<(), String> {
    let root = repo_root();
    let recording = options.mode.starts_with("rec-");
    let base = options.mode.trim_start_matches("rec-");
    let program = root.join(if recording {
        "scripts/gravacao"
    } else {
        "scripts/screenshot"
    });
    let mut command = Command::new(program);
    command.arg(base);
    if recording {
        command.env("HYPRMAC_REC_DIR", folder(&options.destination, true));
        command.env(
            "HYPRMAC_REC_AUDIO",
            if options.microphone { "1" } else { "0" },
        );
        command.env("HYPRMAC_REC_DELAY", options.delay.to_string());
    } else {
        command.env(
            "HYPRMAC_SCREENSHOT_DIR",
            folder(&options.destination, false),
        );
        command.env(
            "HYPRMAC_SHOT_CLIPBOARD",
            if options.destination == "clipboard" {
                "1"
            } else {
                "0"
            },
        );
        command.env("HYPRMAC_SHOT_DELAY", options.delay.to_string());
        command.env(
            "HYPRMAC_SHOT_CURSOR",
            if options.cursor { "1" } else { "0" },
        );
    }
    command.env(
        "HYPRMAC_SHOT_THUMB",
        if options.thumbnail { "1" } else { "0" },
    );
    unsafe {
        command.pre_exec(|| {
            if libc::setsid() < 0 {
                Err(std::io::Error::last_os_error())
            } else {
                Ok(())
            }
        });
    }
    command
        .spawn()
        .map(|_| ())
        .map_err(|error| error.to_string())
}

fn begin_capture(window: &gtk::Window, options: &Rc<RefCell<Options>>, path: &Path) {
    let selected = options.borrow().clone();
    if let Err(error) = save_options(path, &selected) {
        eprintln!("captura: {error}");
    }
    window.hide();
    glib::timeout_add_local(Duration::from_millis(250), move || {
        if let Err(error) = launch(&selected) {
            eprintln!("captura: {error}");
        }
        gtk::main_quit();
        ControlFlow::Break
    });
}

fn menu_item<F: Fn() + 'static>(menu: &gtk::Menu, title: &str, checked: bool, action: F) {
    let item =
        gtk::MenuItem::with_label(&format!("{}{}", if checked { "✓ " } else { "    " }, title));
    item.connect_activate(move |_| action());
    menu.append(&item);
}

fn options_menu(button: &gtk::Button, options: &Rc<RefCell<Options>>, path: &Path) {
    let menu = gtk::Menu::new();
    menu.set_reserve_toggle_size(false);
    menu.style_context().add_class("hyprmac-menu");
    let heading = |title: &str| {
        let item = gtk::MenuItem::with_label(title);
        item.set_sensitive(false);
        menu.append(&item);
    };
    heading("Save to");
    for (key, name) in DESTINATIONS {
        let state = Rc::clone(options);
        let config = path.to_path_buf();
        let selected = options.borrow().destination == key;
        menu_item(&menu, name, selected, move || {
            state.borrow_mut().destination = key.into();
            let _ = save_options(&config, &state.borrow());
        });
    }
    menu.append(&gtk::SeparatorMenuItem::new());
    heading("Timer");
    for (seconds, name) in TIMERS {
        let state = Rc::clone(options);
        let config = path.to_path_buf();
        let selected = options.borrow().delay == seconds;
        menu_item(&menu, name, selected, move || {
            state.borrow_mut().delay = seconds;
            let _ = save_options(&config, &state.borrow());
        });
    }
    menu.append(&gtk::SeparatorMenuItem::new());
    heading("Options");
    let recording = options.borrow().mode.starts_with("rec-");
    for choice in if recording {
        [
            ToggleOption::FloatingThumbnail,
            ToggleOption::RecordMicrophone,
        ]
    } else {
        [ToggleOption::FloatingThumbnail, ToggleOption::MousePointer]
    } {
        let state = Rc::clone(options);
        let config = path.to_path_buf();
        let selected = choice.selected(&options.borrow());
        menu_item(&menu, choice.label(), selected, move || {
            let mut value = state.borrow_mut();
            choice.toggle(&mut value);
            let _ = save_options(&config, &value);
        });
    }
    menu.show_all();
    menu.popup_at_widget(
        button,
        gdk::Gravity::NorthWest,
        gdk::Gravity::SouthWest,
        None,
    );
}

fn build_ui(options: Rc<RefCell<Options>>, config: PathBuf) -> Result<(), String> {
    gtk::init().map_err(|error| error.to_string())?;
    let dark = dark_theme();
    let provider = gtk::CssProvider::new();
    provider
        .load_from_data(style(dark).as_bytes())
        .map_err(|error| error.to_string())?;
    if let Some(screen) = gdk::Screen::default() {
        gtk::StyleContext::add_provider_for_screen(
            &screen,
            &provider,
            gtk::STYLE_PROVIDER_PRIORITY_USER + 1,
        );
    }
    let window = gtk::Window::new(gtk::WindowType::Toplevel);
    window.style_context().add_class("captura");
    if let Some(visual) =
        gtk::prelude::WidgetExt::screen(&window).and_then(|screen| screen.rgba_visual())
    {
        window.set_visual(Some(&visual));
    }
    window.set_app_paintable(true);
    window.init_layer_shell();
    window.set_namespace("hyprmac-captura-barra");
    window.set_layer(Layer::Overlay);
    window.set_anchor(Edge::Bottom, true);
    window.set_layer_shell_margin(Edge::Bottom, 110);
    let preview_ms = env::var("HYPRMAC_CAPTURA_TESTE")
        .ok()
        .and_then(|text| text.parse::<u64>().ok());
    window.set_keyboard_mode(if preview_ms.is_some() {
        KeyboardMode::None
    } else {
        KeyboardMode::Exclusive
    });
    if let Some(ms) = preview_ms {
        glib::timeout_add_local(Duration::from_millis(ms), || {
            gtk::main_quit();
            ControlFlow::Break
        });
    }
    let bar = gtk::Box::new(gtk::Orientation::Horizontal, 2);
    bar.style_context().add_class("cap-bar");
    let close = gtk::Button::new();
    close.style_context().add_class("fechar");
    close.set_valign(gtk::Align::Center);
    close.set_tooltip_text(Some("Close"));
    let x = gtk::Label::new(Some("✕"));
    x.style_context().add_class("x");
    close.add(&x);
    close.connect_clicked(|_| gtk::main_quit());
    bar.pack_start(&close, false, false, 0);
    let capture = gtk::Button::with_label("Capture");
    capture.style_context().add_class("texto");
    capture.style_context().add_class("capturar");
    capture.set_valign(gtk::Align::Center);
    let mut buttons = Vec::new();
    for (index, (mode, title)) in MODES.iter().enumerate() {
        let button = gtk::Button::new();
        button.style_context().add_class("modo");
        if index == 0 {
            button.style_context().add_class("primeiro");
        }
        if index >= 3 {
            button.style_context().add_class("rec");
        }
        button.set_valign(gtk::Align::Center);
        button.add(&icon(mode, dark));
        button.set_tooltip_text(Some(title));
        let state = Rc::clone(&options);
        let action = capture.clone();
        let selected = *mode;
        button.connect_clicked(move |_| {
            state.borrow_mut().mode = selected.into();
            action.set_label(if selected.starts_with("rec-") {
                "Record"
            } else {
                "Capture"
            });
            for child in action
                .parent()
                .and_then(|parent| parent.downcast::<gtk::Box>().ok())
                .map(|bar| bar.children())
                .unwrap_or_default()
            {
                if child.style_context().has_class("modo") {
                    if child.tooltip_text().as_deref() == Some(title_for_mode(selected)) {
                        child.style_context().add_class("selected");
                    } else {
                        child.style_context().remove_class("selected");
                    }
                }
            }
        });
        if options.borrow().mode == *mode {
            button.style_context().add_class("selected");
        }
        bar.pack_start(&button, false, false, 0);
        buttons.push(button);
        if index == 2 || index == 5 {
            let separator = gtk::Box::new(gtk::Orientation::Horizontal, 0);
            separator.style_context().add_class("cap-sep");
            separator.set_valign(gtk::Align::Center);
            bar.pack_start(&separator, false, false, 0);
        }
    }
    let options_button = gtk::Button::new();
    options_button.style_context().add_class("texto");
    options_button.set_valign(gtk::Align::Center);
    let options_box = gtk::Box::new(gtk::Orientation::Horizontal, 6);
    options_box.pack_start(&gtk::Label::new(Some("Options")), false, false, 0);
    let chevron = gtk::DrawingArea::new();
    chevron.set_size_request(9, 9);
    chevron.set_valign(gtk::Align::Center);
    chevron.style_context().add_class("chev");
    chevron.connect_draw(|area, cr| {
        let color = area.style_context().color(area.state_flags());
        cr.set_source_rgba(color.red(), color.green(), color.blue(), color.alpha());
        cr.set_line_width(1.5);
        cr.set_line_cap(gtk::cairo::LineCap::Round);
        cr.move_to(1.0, 3.0);
        cr.line_to(4.5, 6.5);
        cr.line_to(8.0, 3.0);
        let _ = cr.stroke();
        glib::Propagation::Stop
    });
    options_box.pack_start(&chevron, false, false, 0);
    options_button.add(&options_box);
    let menu_options = Rc::clone(&options);
    let menu_path = config.clone();
    options_button.connect_clicked(move |button| options_menu(button, &menu_options, &menu_path));
    bar.pack_start(&options_button, false, false, 0);
    capture.set_label(if options.borrow().mode.starts_with("rec-") {
        "Record"
    } else {
        "Capture"
    });
    let launch_options = Rc::clone(&options);
    let launch_path = config.clone();
    let launch_window = window.clone();
    capture.connect_clicked(move |_| begin_capture(&launch_window, &launch_options, &launch_path));
    bar.pack_start(&capture, false, false, 0);
    window.add(&bar);
    let key_options = Rc::clone(&options);
    let key_path = config;
    window.connect_key_press_event(move |window, event| {
        if event.keyval() == gdk::keys::constants::Escape {
            gtk::main_quit();
        } else if [gdk::keys::constants::Return, gdk::keys::constants::KP_Enter]
            .contains(&event.keyval())
        {
            begin_capture(window, &key_options, &key_path);
        }
        glib::Propagation::Stop
    });
    window.show_all();
    drop(buttons);
    gtk::main();
    Ok(())
}

fn title_for_mode(mode: &str) -> &'static str {
    MODES
        .iter()
        .find(|(key, _)| *key == mode)
        .map(|(_, title)| *title)
        .unwrap_or("")
}

fn main_result() -> Result<(), String> {
    let pidfile = pid_file();
    if toggle_previous(&pidfile) {
        return Ok(());
    }
    fs::write(&pidfile, std::process::id().to_string()).map_err(|error| error.to_string())?;
    let result = build_ui(
        Rc::new(RefCell::new(load_options(&config_file()))),
        config_file(),
    );
    let _ = fs::remove_file(pidfile);
    result
}

fn main() {
    if let Err(error) = main_result() {
        eprintln!("captura: {error}");
        std::process::exit(1);
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn options_round_trip_preserves_other_settings_and_validates_modes() {
        let input = serde_json::json!({"destino":"documents","tempo":5,"miniatura":false,
            "microfone":true,"ponteiro":true,"modo":"rec-pick","custom":42});
        let options = Options::from_json(input.clone());
        assert_eq!(options.to_json(), input);
        let invalid = Options::from_json(serde_json::json!({"modo":"unknown","tempo":999}));
        assert_eq!(invalid.mode, "region");
        assert_eq!(invalid.delay, 0);
        assert_eq!(invalid.destination, "desktop");
    }

    #[test]
    fn capture_and_record_destinations_keep_video_out_of_screenshots() {
        assert!(folder("screenshots", false).ends_with("Pictures/Screenshots"));
        assert!(
            folder("screenshots", true).ends_with("Movies")
                || !folder("screenshots", true).ends_with("Pictures/Screenshots")
        );
    }
}
