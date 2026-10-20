use super::{stop, Recorder};
use gtk::gdk;
use gtk::glib::{self, ControlFlow};
use gtk::prelude::*;
use gtk_layer_shell::{Edge, Layer, LayerShell};
use std::cell::RefCell;
use std::rc::Rc;
use std::time::Duration;

const CSS: &[u8] = br#"
window.gravacao { background: transparent; }
.rec-pill { border-radius: 999px; background-color: rgba(30, 30, 34, 0.80);
  border: 1px solid rgba(255, 255, 255, 0.18);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.08), 0 4px 24px rgba(0, 0, 0, 0.30);
  padding: 5px 12px 5px 10px; }
.rec-pill button { min-height: 26px; min-width: 26px; padding: 0; margin: 0;
  border-radius: 999px; border: none; background: transparent; box-shadow: none; }
.rec-pill button:hover { background: rgba(255, 255, 255, 0.12); }
.rec-stop { color: #FF383C; font-size: 18px; }
.rec-tempo { font-family: "SF Pro"; font-size: 13px; font-weight: 600; color: #ffffff; margin-left: 2px; }
.rec-dot { color: #FF383C; font-size: 11px; margin-right: 2px; }
"#;

pub fn show(state: &Rc<RefCell<Recorder>>) -> Result<(), String> {
    gtk::init().map_err(|error| error.to_string())?;
    let provider = gtk::CssProvider::new();
    provider
        .load_from_data(CSS)
        .map_err(|error| error.to_string())?;
    if let Some(screen) = gdk::Screen::default() {
        gtk::StyleContext::add_provider_for_screen(
            &screen,
            &provider,
            gtk::STYLE_PROVIDER_PRIORITY_USER + 1,
        );
    }
    let window = gtk::Window::new(gtk::WindowType::Toplevel);
    window.style_context().add_class("gravacao");
    if let Some(visual) =
        gtk::prelude::WidgetExt::screen(&window).and_then(|screen| screen.rgba_visual())
    {
        window.set_visual(Some(&visual));
    }
    window.set_app_paintable(true);
    window.init_layer_shell();
    window.set_namespace("hyprmac-captura");
    window.set_layer(Layer::Overlay);
    window.set_anchor(Edge::Top, true);
    window.set_anchor(Edge::Right, true);
    window.set_layer_shell_margin(Edge::Top, 6);
    window.set_layer_shell_margin(Edge::Right, 8);
    let pill = gtk::Box::new(gtk::Orientation::Horizontal, 4);
    pill.style_context().add_class("rec-pill");
    let dot = gtk::Label::new(Some("●"));
    dot.style_context().add_class("rec-dot");
    pill.pack_start(&dot, false, false, 0);
    let timer = gtk::Label::new(Some("0:00"));
    timer.style_context().add_class("rec-tempo");
    pill.pack_start(&timer, false, false, 0);
    let button = gtk::Button::with_label("⏹");
    button.style_context().add_class("rec-stop");
    button.set_tooltip_text(Some("Parar Gravação"));
    let stop_state = Rc::clone(state);
    button.connect_clicked(move |_| stop(&stop_state));
    pill.pack_start(&button, false, false, 0);
    window.add(&pill);
    window.show_all();
    glib::timeout_add_local(Duration::from_millis(500), move || {
        dot.set_opacity(if dot.opacity() > 0.6 { 0.3 } else { 1.0 });
        ControlFlow::Continue
    });
    let started = state.borrow().started;
    glib::timeout_add_seconds_local(1, move || {
        let seconds = started.elapsed().as_secs();
        timer.set_text(&format!("{}:{:02}", seconds / 60, seconds % 60));
        ControlFlow::Continue
    });
    Ok(())
}
