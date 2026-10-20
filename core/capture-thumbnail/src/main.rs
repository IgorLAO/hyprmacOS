//! Miniatura flutuante de captura. Medidas herdadas do kit macOS 27,
//! ainda sem conferência visual com Tahoe 26.
use gdk_pixbuf::{InterpType, Pixbuf};
use gtk::gdk::{self, prelude::GdkContextExt};
use gtk::glib::{self, ControlFlow, Propagation, SourceId};
use gtk::prelude::*;
use gtk_layer_shell::{Edge, Layer, LayerShell};
use std::cell::RefCell;
use std::env;
use std::f64::consts::PI;
use std::path::{Path, PathBuf};
use std::process::{Command, Stdio};
use std::rc::Rc;
use std::time::Duration;

const MAX_SIZE: i32 = 220;
const MARGIN: i32 = 20;
const SHADOW: i32 = 16;
const RADIUS: f64 = 12.0;
const LIFETIME: Duration = Duration::from_secs(5);

#[derive(Default)]
struct State {
    timer: Option<SourceId>,
    dragged: bool,
}

fn thumbnail_size(width: i32, height: i32) -> (i32, i32) {
    let mut w = width.min(MAX_SIZE);
    let mut h = ((height as f64 * w as f64 / width as f64).round() as i32).max(1);
    if h > MAX_SIZE {
        h = MAX_SIZE;
        w = ((width as f64 * h as f64 / height as f64).round() as i32).max(1);
    }
    (w, h)
}

fn rounded(cr: &gtk::cairo::Context, w: f64, h: f64, r: f64) {
    cr.new_sub_path();
    cr.arc(w - r, r, r, -PI / 2.0, 0.0);
    cr.arc(w - r, h - r, r, 0.0, PI / 2.0);
    cr.arc(r, h - r, r, PI / 2.0, PI);
    cr.arc(r, r, r, PI, 3.0 * PI / 2.0);
    cr.close_path();
}

fn open_target(path: &Path) {
    let path = path.to_string_lossy();
    let video = [".mp4", ".mkv", ".webm", ".mov"]
        .iter()
        .any(|ext| path.to_ascii_lowercase().ends_with(ext));
    let commands: Vec<(&str, Vec<&str>)> = if video {
        vec![("xdg-open", vec![&path])]
    } else {
        vec![
            ("spectacle", vec!["--edit-existing", &path]),
            ("gwenview", vec![&path]),
            ("xdg-open", vec![&path]),
        ]
    };
    for (program, args) in commands {
        if Command::new(program)
            .args(args)
            .stdin(Stdio::null())
            .stdout(Stdio::null())
            .stderr(Stdio::null())
            .spawn()
            .is_ok()
        {
            break;
        }
    }
}

fn arm(state: &Rc<RefCell<State>>) {
    if let Some(timer) = state.borrow_mut().timer.take() {
        timer.remove();
    }
    state.borrow_mut().timer = Some(glib::timeout_add_local(LIFETIME, || {
        gtk::main_quit();
        ControlFlow::Break
    }));
}

fn run() -> Result<(), String> {
    let args: Vec<_> = env::args_os().collect();
    let Some(image_arg) = args.get(1) else {
        return Err("uso: hyprmac-captura-miniatura <imagem.png> [--abrir <arquivo>]".into());
    };
    let image = PathBuf::from(image_arg)
        .canonicalize()
        .map_err(|e| e.to_string())?;
    let mut target = image.clone();
    if let Some(index) = args.iter().position(|arg| arg == "--abrir") {
        if let Some(arg) = args.get(index + 1) {
            if let Ok(path) = PathBuf::from(arg).canonicalize() {
                target = path;
            }
        }
    }
    let pixbuf = Pixbuf::from_file(&image).map_err(|e| e.to_string())?;
    let (w, h) = thumbnail_size(pixbuf.width(), pixbuf.height());
    let thumb = pixbuf
        .scale_simple(w, h, InterpType::Hyper)
        .ok_or("falha ao escalar miniatura")?;
    let drag_icon = thumb.scale_simple((w / 2).max(1), (h / 2).max(1), InterpType::Bilinear);

    gtk::init().map_err(|e| e.to_string())?;
    let provider = gtk::CssProvider::new();
    provider
        .load_from_data(b"window { background: transparent; }")
        .map_err(|e| e.to_string())?;
    if let Some(screen) = gdk::Screen::default() {
        gtk::StyleContext::add_provider_for_screen(
            &screen,
            &provider,
            gtk::STYLE_PROVIDER_PRIORITY_APPLICATION,
        );
    }
    let window = gtk::Window::new(gtk::WindowType::Toplevel);
    if let Some(visual) =
        gtk::prelude::WidgetExt::screen(&window).and_then(|screen| screen.rgba_visual())
    {
        window.set_visual(Some(&visual));
    }
    window.set_app_paintable(true);
    window.init_layer_shell();
    window.set_namespace("hyprmac-captura");
    window.set_layer(Layer::Overlay);
    window.set_anchor(Edge::Bottom, true);
    window.set_anchor(Edge::Right, true);
    window.set_layer_shell_margin(Edge::Bottom, MARGIN - SHADOW);
    window.set_layer_shell_margin(Edge::Right, MARGIN - SHADOW);
    window.connect_destroy(|_| gtk::main_quit());

    let area = gtk::DrawingArea::new();
    area.set_size_request(w + 2 * SHADOW, h + 2 * SHADOW);
    area.connect_draw(move |_, cr| {
        let (w, h) = (w as f64, h as f64);
        for i in (1..=SHADOW).rev().step_by(2) {
            let i = i as f64;
            let _ = cr.save();
            cr.translate(SHADOW as f64 - i, SHADOW as f64 - i + 5.0);
            rounded(cr, w + 2.0 * i, h + 2.0 * i, RADIUS + i);
            cr.set_source_rgba(0.0, 0.0, 0.0, 0.035);
            let _ = cr.fill();
            let _ = cr.restore();
        }
        cr.translate(SHADOW as f64, SHADOW as f64);
        let _ = cr.save();
        cr.translate(-1.0, -1.0);
        rounded(cr, w + 2.0, h + 2.0, RADIUS + 1.0);
        cr.set_source_rgba(0.0, 0.0, 0.0, 0.55);
        let _ = cr.fill();
        let _ = cr.restore();
        rounded(cr, w, h, RADIUS);
        cr.clip();
        cr.set_source_pixbuf(&thumb, 0.0, 0.0);
        let _ = cr.paint();
        rounded(cr, w - 1.0, h - 1.0, RADIUS - 0.5);
        cr.translate(0.5, 0.5);
        cr.set_source_rgba(1.0, 1.0, 1.0, 0.20);
        cr.set_line_width(1.0);
        let _ = cr.stroke();
        Propagation::Proceed
    });

    let events = gtk::EventBox::new();
    events.add(&area);
    events.add_events(
        gdk::EventMask::BUTTON_PRESS_MASK
            | gdk::EventMask::BUTTON_RELEASE_MASK
            | gdk::EventMask::ENTER_NOTIFY_MASK
            | gdk::EventMask::LEAVE_NOTIFY_MASK,
    );
    window.add(&events);
    let state = Rc::new(RefCell::new(State::default()));
    let release_state = Rc::clone(&state);
    let release_target = target.clone();
    events.connect_button_release_event(move |_, event| {
        if release_state.borrow().dragged {
            return Propagation::Proceed;
        }
        if event.button() == 1 {
            open_target(&release_target);
        }
        gtk::main_quit();
        Propagation::Stop
    });
    let enter_state = Rc::clone(&state);
    events.connect_enter_notify_event(move |_, _| {
        if let Some(timer) = enter_state.borrow_mut().timer.take() {
            timer.remove();
        }
        Propagation::Proceed
    });
    let leave_state = Rc::clone(&state);
    events.connect_leave_notify_event(move |_, event| {
        if event.detail() != gdk::NotifyType::Inferior {
            arm(&leave_state);
        }
        Propagation::Proceed
    });

    events.drag_source_set(gdk::ModifierType::BUTTON1_MASK, &[], gdk::DragAction::COPY);
    events.drag_source_add_uri_targets();
    if let Some(icon) = drag_icon {
        events.drag_source_set_icon_pixbuf(&icon);
    }
    let drag_state = Rc::clone(&state);
    events.connect_drag_begin(move |_, _| drag_state.borrow_mut().dragged = true);
    let uri = glib::filename_to_uri(&target, None).map_err(|e| e.to_string())?;
    events.connect_drag_data_get(move |_, _, data, _, _| {
        data.set_uris(&[uri.as_str()]);
    });
    events.connect_drag_end(|_, _| gtk::main_quit());

    window.show_all();
    arm(&state);
    gtk::main();
    Ok(())
}

fn main() {
    if let Err(error) = run() {
        eprintln!("{error}");
        std::process::exit(1);
    }
}

#[cfg(test)]
mod tests {
    use super::thumbnail_size;

    #[test]
    fn thumbnail_fits_both_axes_and_preserves_portrait() {
        assert_eq!(thumbnail_size(440, 220), (220, 110));
        assert_eq!(thumbnail_size(100, 400), (55, 220));
        assert_eq!(thumbnail_size(1, 1), (1, 1));
    }
}
