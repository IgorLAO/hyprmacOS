#!/usr/bin/env bash
# Câmera em uso → cápsula verde com o ícone da câmera na barra (o indicador de
# privacidade do macOS; o módulo "privacy" do Waybar não conhece câmera).
# Confere a cada 2 s quem tem /dev/video* aberto; sem câmera em uso, o módulo some.
ultimo=""
while :; do
  if fuser /dev/video* >/dev/null 2>&1; then
    apps=$(fuser /dev/video* 2>/dev/null | tr -s ' ' '\n' | grep -E '^[0-9]+$' | sort -u \
           | xargs -r -n1 -I{} cat /proc/{}/comm 2>/dev/null | sort -u | paste -sd, -)
    agora="{\"text\":\"󰄀\",\"class\":\"on\",\"tooltip\":\"Câmera em uso: ${apps}\"}"
  else
    agora='{"text":""}'
  fi
  [ "$agora" != "$ultimo" ] && { echo "$agora"; ultimo="$agora"; }
  sleep 2
done
