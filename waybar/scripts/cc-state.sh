#!/usr/bin/env bash
# Estado do ícone da Central de Controle: "active" enquanto o painel está aberto.
if [ -e "${XDG_RUNTIME_DIR:-/tmp}/hyprmac-cc-open" ]; then
  echo '{"text":"      ","class":"active"}'
else
  echo '{"text":"      ","class":""}'
fi
