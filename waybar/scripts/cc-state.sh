#!/usr/bin/env bash
# Estado do ícone da Central de Controle: "active" enquanto o painel está aberto.
osd="${XDG_RUNTIME_DIR:-/tmp}/hyprmac-osd-active"
if [ -e "$osd" ]; then
  kind=$(cat "$osd")
  case "$kind" in
    volume) echo '{"text":"      ","class":"volume"}' ;;
    brightness) echo '{"text":"      ","class":"brightness"}' ;;
    *) echo '{"text":"      ","class":""}' ;;
  esac
elif [ -e "${XDG_RUNTIME_DIR:-/tmp}/hyprmac-cc-open" ]; then
  echo '{"text":"      ","class":"active"}'
else
  echo '{"text":"      ","class":""}'
fi
