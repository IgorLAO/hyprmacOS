/* hyprmac-ocioso — vigia de inatividade (ext-idle-notify-v1), no lugar do hypridle.
 *
 *   hyprmac-ocioso SEGUNDOS COMANDO_AO_FICAR_OCIOSO [COMANDO_AO_VOLTAR]
 *
 * Usa get_idle_notification, que respeita os inibidores (vídeo tocando, jogo em tela
 * cheia…), como o Mac não apaga a tela durante um filme. Os comandos rodam com sh -c.
 * Compilar: make -C shell/ocioso
 */
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/wait.h>
#include <signal.h>
#include <wayland-client.h>
#include "ext-idle-notify-v1-client-protocol.h"

static struct wl_seat *seat;
static struct ext_idle_notifier_v1 *notifier;
static const char *on_idle, *on_resume;

static void run(const char *cmd) {
    if (!cmd || !*cmd) return;
    pid_t p = fork();
    if (p == 0) {
        setsid();
        execl("/bin/sh", "sh", "-c", cmd, (char *)NULL);
        _exit(127);
    }
}

static void idled(void *data, struct ext_idle_notification_v1 *n) { run(on_idle); }
static void resumed(void *data, struct ext_idle_notification_v1 *n) { run(on_resume); }
static const struct ext_idle_notification_v1_listener idle_listener = { idled, resumed };

static void global(void *data, struct wl_registry *reg, uint32_t name, const char *iface, uint32_t ver) {
    if (strcmp(iface, wl_seat_interface.name) == 0 && !seat)
        seat = wl_registry_bind(reg, name, &wl_seat_interface, 1);
    else if (strcmp(iface, ext_idle_notifier_v1_interface.name) == 0)
        notifier = wl_registry_bind(reg, name, &ext_idle_notifier_v1_interface, 1);
}
static void global_remove(void *data, struct wl_registry *reg, uint32_t name) {}
static const struct wl_registry_listener reg_listener = { global, global_remove };

int main(int argc, char **argv) {
    if (argc < 3) {
        fprintf(stderr, "uso: %s SEGUNDOS COMANDO_OCIOSO [COMANDO_VOLTAR]\n", argv[0]);
        return 2;
    }
    signal(SIGCHLD, SIG_IGN);              /* sem zumbis */
    long secs = atol(argv[1]);
    on_idle = argv[2];
    on_resume = argc > 3 ? argv[3] : NULL;
    struct wl_display *d = wl_display_connect(NULL);
    if (!d) { fprintf(stderr, "sem Wayland\n"); return 1; }
    struct wl_registry *reg = wl_display_get_registry(d);
    wl_registry_add_listener(reg, &reg_listener, NULL);
    wl_display_roundtrip(d);
    if (!seat || !notifier) { fprintf(stderr, "o compositor não tem ext-idle-notify-v1\n"); return 1; }
    struct ext_idle_notification_v1 *n =
        ext_idle_notifier_v1_get_idle_notification(notifier, (uint32_t)(secs * 1000), seat);
    ext_idle_notification_v1_add_listener(n, &idle_listener, NULL);
    while (wl_display_dispatch(d) != -1) {}
    return 0;
}
