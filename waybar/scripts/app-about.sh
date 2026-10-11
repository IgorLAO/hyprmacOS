#!/usr/bin/env bash
# "About <App>" do menu do app: mostra nome, versão e pacote do app em foco
# numa notificação (o Linux não tem uma janela "Sobre" padrão para todo app).
# A versão vem do pacote dono do executável (pacman -Qo).
set -uo pipefail
win=$(hyprctl activewindow -j 2>/dev/null) || exit 0
read -r cls pid < <(printf '%s' "$win" | python3 -c '
import json, sys
try:
    w = json.load(sys.stdin) or {}
except ValueError:
    w = {}
print(w.get("class") or "-", w.get("pid") or 0)')
[ "$cls" = "-" ] && exit 0

# nome bonito: o mesmo "rewrite" da barra para os casos comuns
nome=${cls##*.}
nome=${nome^}

exe=$(readlink -f "/proc/$pid/exe" 2>/dev/null)
pacote=""
if [ -n "$exe" ] && command -v pacman >/dev/null; then
  pacote=$(pacman -Qo "$exe" 2>/dev/null | sed -E 's/.* is owned by //')
fi

corpo="Classe: $cls"
[ -n "$pacote" ] && corpo="Versão: ${pacote#* }"$'\n'"Pacote: ${pacote% *}"$'\n'"$corpo"
[ -n "$exe" ] && corpo+=$'\n'"Programa: $exe"

notify-send -a "$nome" -i "$cls" "About $nome" "$corpo"
