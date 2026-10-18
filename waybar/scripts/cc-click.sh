#!/usr/bin/env bash
# Quando o indicador vira alto-falante, o clique abre saídas/volume.
osd="${XDG_RUNTIME_DIR:-/tmp}/hyprmac-osd-active"
if [ -e "$osd" ] && [ "$(cat "$osd")" = volume ]; then
  action=toggle-sound
else
  action=toggle-cc
fi
gdbus call --session --dest dev.hyprmac.Shell --object-path /dev/hyprmac/Shell \
  --method dev.hyprmac.Shell.Command "$action" >/dev/null
