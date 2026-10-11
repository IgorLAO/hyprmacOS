/* hyprmac — "Tocando Agora" na barra (módulo CFFI do Waybar)
 *
 * Fica à direita do botão play/pause (módulo mpris): nome da música que está
 * tocando (desliza se passar de 250 px) + três barrinhas verdes que sobem e descem
 * com o áudio de verdade (captura do monitor da saída que está tocando, via
 * pw-record — nem sempre é a saída padrão).
 * Sem nada tocando, o nome encolhe para dentro do play/pause, que desliza de
 * volta ao seu lugar (a barra é alinhada à direita).
 * Clique: abre/fecha o player do hyprmac-shell (dev.hyprmac.Shell toggle-media).
 *
 * Compilar: make -C ~/Projects/hyprmac/waybar/cffi
 */
#include <gtk/gtk.h>
#include <errno.h>
#include <math.h>
#include <playerctl/playerctl.h>
#include <signal.h>
#include <stdint.h>
#include <string.h>
#include <glib-unix.h>
#include <unistd.h>

const size_t wbcffi_version = 2;

typedef struct wbcffi_module wbcffi_module;
typedef struct {
  wbcffi_module *obj;
  const char *waybar_version;
  GtkContainer *(*get_root_widget)(wbcffi_module *obj);
  void (*queue_update)(wbcffi_module *);
} wbcffi_init_info;
typedef struct {
  const char *key;
  const char *value;
} wbcffi_config_entry;

#define MAX_TEXT 250.0   /* acima disso o nome desliza */
#define PAD_L 1.0
#define GAP 6.0          /* entre o nome e as barras */
#define PAD_R 8.0
#define BAR_W 2.4
#define BAR_GAP 2.2
#define BAR_MAX 11.0
#define LOOP_GAP 36.0    /* espaço entre o fim do nome e o recomeço */
#define SCROLL_PX_S 24.0
#define SCROLL_PAUSE 2.2 /* segundos parado no início de cada volta */
#define FADE 10.0
#define RATE 8000
#define NBARS 3
/* mesma cor do ponto verde de notificações (@green da barra) */
#define BAR_R (0x30 / 255.0)
#define BAR_G (0xd1 / 255.0)
#define BAR_B (0x58 / 255.0)

typedef struct {
  GtkWidget *area;
  PlayerctlPlayerManager *mgr;
  guint sync_id;

  char *title;
  gboolean playing;
  double text_w, text_h;
  PangoLayout *layout;

  double width, alpha;   /* animados */
  double scroll, pause;  /* letreiro */
  gint64 last_us;
  guint tick_id;

  GPid cap_pid;
  char *cap_sink;        /* saída capturada agora */
  guint sink_check;
  int cap_fd;
  guint cap_watch;
  guint8 carry[2];
  gsize ncarry;
  double lp1, lp2, env[NBARS], avg[NBARS], peak[NBARS], level[NBARS], bar[NBARS];
} NP;

/* ───────────── medidas ───────────── */

static double view_w(NP *np) { return MIN(np->text_w, MAX_TEXT); }

static double full_w(NP *np) {
  if (!np->title || !*np->title) return 0;
  return PAD_L + view_w(np) + GAP + NBARS * BAR_W + (NBARS - 1) * BAR_GAP + PAD_R;
}

static void measure(NP *np, const char *title) {
  if (!np->layout) np->layout = gtk_widget_create_pango_layout(np->area, NULL);
  pango_layout_set_text(np->layout, title ? title : "", -1);
  PangoRectangle log;
  pango_layout_get_extents(np->layout, NULL, &log);
  np->text_w = log.width / (double)PANGO_SCALE;
  np->text_h = log.height / (double)PANGO_SCALE;
}

static void set_title(NP *np, const char *title) {
  if (g_strcmp0(title, np->title) == 0) return;
  g_free(np->title);
  np->title = g_strdup(title);
  measure(np, title);
  np->scroll = 0;
  np->pause = SCROLL_PAUSE;
}

/* fonte da barra mudou (tema/CSS recarregado): mede de novo */
static void on_style(GtkWidget *w, gpointer data) {
  NP *np = data;
  if (np->layout) pango_layout_context_changed(np->layout);
  if (np->title) measure(np, np->title);
}

/* ───────────── áudio ───────────── */

static gboolean on_audio(int fd, GIOCondition cond, gpointer data) {
  NP *np = data;
  /* passa-baixas de 1 polo: graves (<180 Hz), médios (180–1500 Hz) e agudos */
  const double a1 = 1.0 - exp(-2.0 * M_PI * 180.0 / RATE);
  const double a2 = 1.0 - exp(-2.0 * M_PI * 1500.0 / RATE);
  const double ae = 1.0 - exp(-1.0 / (0.025 * RATE));   /* envelope de ~25 ms */
  size_t total = 0;
  for (;;) {   /* drena o pipe: sempre analisa o som de agora, sem fila */
    int16_t buf[1024];
    memcpy(buf, np->carry, np->ncarry);
    ssize_t r = read(fd, (guint8 *)buf + np->ncarry, sizeof buf - np->ncarry);
    if (r < 0 && errno == EINTR) continue;
    if (r < 0 && errno == EAGAIN) break;
    if (r <= 0) {
      np->cap_watch = 0;
      return G_SOURCE_REMOVE;
    }
    gsize n = np->ncarry + r;
    np->ncarry = n % 2;   /* o pipe pode cortar uma amostra ao meio */
    if (np->ncarry) memcpy(np->carry, (guint8 *)buf + n - 1, 1);
    size_t cnt = n / 2;
    for (size_t i = 0; i < cnt; i++) {
      double x = buf[i] / 32768.0;
      np->lp1 += a1 * (x - np->lp1);
      np->lp2 += a2 * (x - np->lp2);
      double band[NBARS] = {np->lp1, np->lp2 - np->lp1, x - np->lp2};
      for (int k = 0; k < NBARS; k++) np->env[k] += ae * (band[k] * band[k] - np->env[k]);
    }
    total += cnt;
  }
  if (!total) return G_SOURCE_CONTINUE;
  double dt = total / (double)RATE;
  for (int k = 0; k < NBARS; k++) {
    double rms = sqrt(np->env[k]);
    /* ganho automático: as batidas são o que passa da média recente */
    np->avg[k] += (rms - np->avg[k]) * (1.0 - exp(-dt / 0.8));
    np->peak[k] = MAX(rms, MAX(np->peak[k] * exp(-dt / 1.5), 0.004));
    double base = 0.55 * np->avg[k];
    double v = (rms - base) / MAX(np->peak[k] - base, 1e-4);
    np->level[k] = CLAMP(v, 0.0, 1.0);
  }
  return G_SOURCE_CONTINUE;
}

static void stop_capture(NP *np) {
  if (np->cap_watch) g_source_remove(np->cap_watch);
  np->cap_watch = 0;
  if (np->cap_fd > 0) close(np->cap_fd);
  np->cap_fd = -1;
  np->ncarry = 0;
  if (np->cap_pid) kill(np->cap_pid, SIGTERM);
  if (np->sink_check && !np->playing) {
    g_source_remove(np->sink_check);
    np->sink_check = 0;
  }
  np->cap_pid = 0;
  memset(np->level, 0, sizeof np->level);
}

/* A saída que está tocando (estado RUNNING); prefere a padrão. */
static char *pick_sink(void) {
  char *def = NULL, *list = NULL, *pick = NULL;
  g_spawn_command_line_sync("pactl get-default-sink", &def, NULL, NULL, NULL);
  g_spawn_command_line_sync("pactl list short sinks", &list, NULL, NULL, NULL);
  if (def) g_strstrip(def);
  char **lines = g_strsplit(list ? list : "", "\n", -1);
  for (char **l = lines; *l; l++) {
    char **f = g_strsplit(*l, "\t", -1);
    if (g_strv_length(f) >= 5 && strcmp(f[4], "RUNNING") == 0) {
      if (def && strcmp(f[1], def) == 0) {
        g_free(pick);
        pick = g_strdup(def);
        g_strfreev(f);
        break;
      }
      if (!pick) pick = g_strdup(f[1]);
    }
    g_strfreev(f);
  }
  g_strfreev(lines);
  if (!pick && def && *def) pick = g_strdup(def);
  g_free(def);
  g_free(list);
  return pick;
}

static void start_capture(NP *np);

/* o som mudou de saída? reinicia a captura nela */
static gboolean check_sink(gpointer data) {
  NP *np = data;
  char *sink = pick_sink();
  if (sink && g_strcmp0(sink, np->cap_sink) != 0) {
    stop_capture(np);
    start_capture(np);
  }
  g_free(sink);
  return G_SOURCE_CONTINUE;
}

static void start_capture(NP *np) {
  if (np->cap_pid) return;
  g_free(np->cap_sink);
  np->cap_sink = pick_sink();
  if (!np->cap_sink) return;
  if (!np->sink_check) np->sink_check = g_timeout_add_seconds(3, check_sink, np);
  /* stream.monitor = true: o indicador de privacidade não acusa "microfone" */
  char *argv[] = {"pw-record", "--rate", "8000", "--channels", "1", "--format", "s16",
                  "--latency", "15ms", "--raw", "--target", np->cap_sink, "-P",
                  "{ stream.capture.sink = true, stream.monitor = true, "
                  "node.name = hyprmac-visualizer, media.name = \"hyprmac visualizer\" }",
                  "-", NULL};
  int out;
  if (!g_spawn_async_with_pipes(NULL, argv, NULL, G_SPAWN_SEARCH_PATH | G_SPAWN_DO_NOT_REAP_CHILD |
                                    G_SPAWN_STDERR_TO_DEV_NULL,
                                NULL, NULL, &np->cap_pid, NULL, &out, NULL, NULL)) {
    np->cap_pid = 0;
    return;
  }
  g_child_watch_add(np->cap_pid, (GChildWatchFunc)g_spawn_close_pid, NULL);
  np->cap_fd = out;
  g_unix_set_fd_nonblocking(out, TRUE, NULL);
  np->cap_watch = g_unix_fd_add(out, G_IO_IN | G_IO_HUP | G_IO_ERR, on_audio, np);
}

/* ───────────── animação ───────────── */

static gboolean tick(GtkWidget *w, GdkFrameClock *clock, gpointer data) {
  NP *np = data;
  gint64 now = gdk_frame_clock_get_frame_time(clock);
  double dt = np->last_us ? (now - np->last_us) / 1e6 : 0.016;
  dt = CLAMP(dt, 0.0, 0.1);
  np->last_us = now;

  double target_w = np->playing ? full_w(np) : 0;
  double k = 1.0 - exp(-dt * 9.0);   /* aproximação suave, sem passar do alvo */
  np->width += (target_w - np->width) * k;
  np->alpha += ((np->playing ? 1.0 : 0.0) - np->alpha) * (1.0 - exp(-dt * 11.0));
  if (fabs(target_w - np->width) < 0.3) np->width = target_w;

  /* barras: sobem rápido, descem devagar */
  for (int i = 0; i < NBARS; i++) {
    double t = np->playing ? np->level[i] : 0;
    double rate = t > np->bar[i] ? 28.0 : 9.0;
    np->bar[i] += (t - np->bar[i]) * (1.0 - exp(-dt * rate));
  }

  /* letreiro: pausa no começo de cada volta e desliza sem emendas */
  if (np->text_w > MAX_TEXT) {
    if (np->pause > 0) {
      np->pause -= dt;
    } else {
      np->scroll += SCROLL_PX_S * dt;
      if (np->scroll >= np->text_w + LOOP_GAP) {
        np->scroll = 0;
        np->pause = SCROLL_PAUSE;
      }
    }
  }

  int req = (int)ceil(np->width);
  int cur;
  gtk_widget_get_size_request(w, &cur, NULL);
  if (req != cur) gtk_widget_set_size_request(w, req, -1);

  if (!np->playing && np->width == 0) {
    stop_capture(np);
    gtk_widget_hide(w);
    np->tick_id = 0;
    np->last_us = 0;
    return G_SOURCE_REMOVE;
  }
  gtk_widget_queue_draw(w);
  return G_SOURCE_CONTINUE;
}

static void ensure_tick(NP *np) {
  gtk_widget_show(np->area);
  if (!np->tick_id) np->tick_id = gtk_widget_add_tick_callback(np->area, tick, np, NULL);
}

static gboolean draw(GtkWidget *w, cairo_t *cr, gpointer data) {
  NP *np = data;
  double W = gtk_widget_get_allocated_width(w), H = gtk_widget_get_allocated_height(w);
  GtkStyleContext *ctx = gtk_widget_get_style_context(w);
  if (W < 1 || !np->layout) return FALSE;

  cairo_push_group(cr);
  gtk_render_background(ctx, cr, 0, 0, W, H);

  /* conteúdo preso à esquerda (junto do play/pause): ao encolher, entra nele */
  double x0 = 0;
  double vx = x0 + PAD_L, vw = view_w(np);
  double ty = round((H - np->text_h) / 2);

  cairo_save(cr);
  cairo_rectangle(cr, vx, 0, vw, H);
  cairo_clip(cr);
  if (np->text_w > MAX_TEXT) {
    cairo_push_group(cr);
    gtk_render_layout(ctx, cr, vx - np->scroll, ty, np->layout);
    gtk_render_layout(ctx, cr, vx - np->scroll + np->text_w + LOOP_GAP, ty, np->layout);
    cairo_pop_group_to_source(cr);
    /* bordas esmaecidas; a da esquerda só aparece depois que começa a deslizar */
    double lf = MIN(np->scroll, FADE) / FADE;
    cairo_pattern_t *m = cairo_pattern_create_linear(vx, 0, vx + vw, 0);
    cairo_pattern_add_color_stop_rgba(m, 0, 0, 0, 0, 1 - lf);
    cairo_pattern_add_color_stop_rgba(m, FADE / vw, 0, 0, 0, 1);
    cairo_pattern_add_color_stop_rgba(m, 1 - FADE / vw, 0, 0, 0, 1);
    cairo_pattern_add_color_stop_rgba(m, 1, 0, 0, 0, 0);
    cairo_mask(cr, m);
    cairo_pattern_destroy(m);
  } else {
    gtk_render_layout(ctx, cr, vx, ty, np->layout);
  }
  cairo_restore(cr);

  /* três barras verdes com a base parada: só o topo sobe e desce */
  cairo_set_source_rgb(cr, BAR_R, BAR_G, BAR_B);
  cairo_set_line_width(cr, BAR_W);
  cairo_set_line_cap(cr, CAIRO_LINE_CAP_ROUND);
  double bx = vx + vw + GAP + BAR_W / 2;
  double base_y = round(H / 2 + BAR_MAX / 2) - BAR_W / 2;
  for (int i = 0; i < NBARS; i++) {
    double len = np->bar[i] * (BAR_MAX - BAR_W);
    double x = bx + i * (BAR_W + BAR_GAP);
    cairo_move_to(cr, x, base_y);
    cairo_line_to(cr, x, base_y - len - 0.01);
    cairo_stroke(cr);
  }

  cairo_pop_group_to_source(cr);
  cairo_paint_with_alpha(cr, CLAMP(np->alpha, 0, 1));
  return FALSE;
}

/* ───────────── players (MPRIS) ───────────── */

static gboolean sync_players(gpointer data) {
  NP *np = data;
  np->sync_id = 0;
  GList *players = NULL;
  g_object_get(np->mgr, "players", &players, NULL);
  PlayerctlPlayer *active = NULL;
  for (GList *l = players; l; l = l->next) {
    PlayerctlPlaybackStatus st;
    g_object_get(l->data, "playback-status", &st, NULL);
    if (st == PLAYERCTL_PLAYBACK_STATUS_PLAYING) {
      active = l->data;
      break;
    }
  }
  if (active) {
    char *title = playerctl_player_get_title(active, NULL);
    set_title(np, title && *title ? title : "Tocando");
    g_free(title);
    np->playing = TRUE;
    start_capture(np);
    ensure_tick(np);
  } else if (np->playing) {
    np->playing = FALSE;   /* o tick encolhe, esconde e para a captura */
    ensure_tick(np);
  }
  return G_SOURCE_REMOVE;
}

static void queue_sync(NP *np) {
  if (!np->sync_id) np->sync_id = g_timeout_add(60, sync_players, np);
}

static void on_status(PlayerctlPlayer *p, PlayerctlPlaybackStatus st, gpointer data) { queue_sync(data); }
static void on_meta(PlayerctlPlayer *p, GVariant *meta, gpointer data) { queue_sync(data); }
static void on_vanished(PlayerctlPlayerManager *m, PlayerctlPlayer *p, gpointer data) { queue_sync(data); }

static void manage(NP *np, PlayerctlPlayerName *name) {
  PlayerctlPlayer *p = playerctl_player_new_from_name(name, NULL);
  if (!p) return;
  g_signal_connect(p, "playback-status", G_CALLBACK(on_status), np);
  g_signal_connect(p, "metadata", G_CALLBACK(on_meta), np);
  playerctl_player_manager_manage_player(np->mgr, p);
  g_object_unref(p);
  queue_sync(np);
}

static void on_name(PlayerctlPlayerManager *m, PlayerctlPlayerName *name, gpointer data) { manage(data, name); }

/* ───────────── clique ───────────── */

static gboolean on_press(GtkWidget *w, GdkEventButton *ev, gpointer data) {
  if (ev->type != GDK_BUTTON_PRESS || ev->button != 1) return FALSE;
  GtkWidget *top = gtk_widget_get_toplevel(w);
  double W = gtk_widget_get_allocated_width(w);
  int x = 0, y = 0;
  gtk_widget_translate_coordinates(w, top, (int)(W / 2), 0, &x, &y);
  int bar_w = gtk_widget_get_allocated_width(top);
  char *cmd = g_strdup_printf("toggle-media %d %d", x, bar_w);
  GDBusConnection *bus = g_bus_get_sync(G_BUS_TYPE_SESSION, NULL, NULL);
  if (bus) {
    g_dbus_connection_call(bus, "dev.hyprmac.Shell", "/dev/hyprmac/Shell", "dev.hyprmac.Shell",
                           "Command", g_variant_new("(s)", cmd), NULL, G_DBUS_CALL_FLAGS_NONE,
                           1000, NULL, NULL, NULL);
    g_object_unref(bus);
  }
  g_free(cmd);
  return TRUE;
}

static gboolean on_cross(GtkWidget *w, GdkEventCrossing *ev, gpointer data) {
  if (ev->detail == GDK_NOTIFY_INFERIOR) return FALSE;
  if (ev->type == GDK_ENTER_NOTIFY)
    gtk_widget_set_state_flags(w, GTK_STATE_FLAG_PRELIGHT, FALSE);
  else
    gtk_widget_unset_state_flags(w, GTK_STATE_FLAG_PRELIGHT);
  return FALSE;
}

/* ───────────── CFFI ───────────── */

void *wbcffi_init(const wbcffi_init_info *info, const wbcffi_config_entry *cfg, size_t n) {
  NP *np = g_new0(NP, 1);
  GtkContainer *root = info->get_root_widget(info->obj);

  np->cap_fd = -1;
  np->area = gtk_drawing_area_new();
  gtk_widget_set_name(np->area, "hyprmac-nowplaying");
  gtk_widget_add_events(np->area, GDK_BUTTON_PRESS_MASK | GDK_ENTER_NOTIFY_MASK |
                                      GDK_LEAVE_NOTIFY_MASK);
  gtk_widget_set_size_request(np->area, 0, -1);
  g_signal_connect(np->area, "draw", G_CALLBACK(draw), np);
  g_signal_connect(np->area, "style-updated", G_CALLBACK(on_style), np);
  g_signal_connect(np->area, "button-press-event", G_CALLBACK(on_press), np);
  g_signal_connect(np->area, "enter-notify-event", G_CALLBACK(on_cross), np);
  g_signal_connect(np->area, "leave-notify-event", G_CALLBACK(on_cross), np);
  gtk_container_add(root, np->area);
  gtk_widget_set_no_show_all(np->area, TRUE);

  np->mgr = playerctl_player_manager_new(NULL);
  if (np->mgr) {
    g_signal_connect(np->mgr, "name-appeared", G_CALLBACK(on_name), np);
    g_signal_connect(np->mgr, "player-vanished", G_CALLBACK(on_vanished), np);
    GList *names = NULL;
    g_object_get(np->mgr, "player-names", &names, NULL);
    for (GList *l = names; l; l = l->next) manage(np, l->data);
  }
  return np;
}

void wbcffi_deinit(void *instance) {
  NP *np = instance;
  np->playing = FALSE;
  stop_capture(np);
  g_free(np->cap_sink);
  if (np->sync_id) g_source_remove(np->sync_id);
  if (np->tick_id) gtk_widget_remove_tick_callback(np->area, np->tick_id);
  if (np->mgr) g_object_unref(np->mgr);
  if (np->layout) g_object_unref(np->layout);
  g_free(np->title);
  g_free(np);
}
