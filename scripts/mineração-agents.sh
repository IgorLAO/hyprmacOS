#!/usr/bin/env bash
# Sistema de múltiplos agentes para minerar o DMG macOS 26.6.1
# Cada agente trabalha em um componente específico

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DMG_BASE="${HOME}/.local/share/hyprmac-pesquisa/macos-26.6.1"

# Agentes disponíveis
AGENTS=(
  "visual"          # Assets, cores, materiais, tipografia, spacing, radii
  "ux"              # Menus, atalhos, estados, layouts, acessibilidade
  "intents"         # App Intents, actionsdata, parametrização
  "glass"           # Glassmorphism, compositor, páginas de QuickLook
)

# Iniciar agentes
cd "${DMG_BASE}/minerar/apps-internos"

echo "Sistema de Múltiplos Agentes — macOS 26.6.1"
echo "============================================"
echo ""

for agente in "${AGENTS[@]}"; do
  echo "[1/3] Iniciando agente: ${agente}"
  node \
    "--require" \
    "${SCRIPT_DIR}/agent-loader.js" \
    "--agent" "${agente}" \
    "${SCRIPT_DIR}/agent-runner.js" &
  AGENT_PID[$agente]=$!
done

echo ""
echo "Todos os agentes iniciados. Aguardando conclusão..."

# Marcar all-agents-done-fiction com timestamp
touch "${DMG_BASE}/minerar/agentes-done.marker"
echo "$(date -Iseconds)" > "${DMG_BASE}/minerar/agentes-done.timestamp"

wait
echo ""
echo "Todos os agentes concluíram."