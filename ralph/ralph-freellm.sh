#!/usr/bin/env bash
# Ralph Loop para Claude Code + FreeLLMAPI (Linux / Bash)
# Uso: ./ralph-freellm.sh [PROMPT.md] [MAX_ITERACOES]
# MAX_ITERACOES=0 executa sem limite; Ctrl+C para parar.
set -Eeuo pipefail
umask 077

PROJECT_DIR="${RALPH_PROJECT:-$PWD}"
cd "$PROJECT_DIR"
PROMPT_FILE="${1:-RALPH_PROMPT.md}"
MAX_ITERATIONS="${2:-20}"
BASE_URL="${FREELLMAPI_URL:-http://localhost:3001}"
MAX_TURNS="${RALPH_MAX_TURNS:-20}"
TIMEOUT_SECONDS="${RALPH_TIMEOUT_SECONDS:-1800}"
DELAY_SECONDS="${RALPH_DELAY_SECONDS:-3}"
FAIL_LIMIT="${RALPH_FAIL_LIMIT:-3}"
STATE_DIR="${RALPH_STATE_DIR:-.ralph}"

abort() { printf '[ralph] ERRO: %s\n' "$*" >&2; exit 1; }
for dep in claude jq timeout; do command -v "$dep" >/dev/null 2>&1 || abort "Instale '$dep' e tente novamente."; done
for val in MAX_ITERATIONS MAX_TURNS TIMEOUT_SECONDS DELAY_SECONDS FAIL_LIMIT; do
    [[ "${!val}" =~ ^[0-9]+$ ]] || abort "$val deve ser um numero inteiro nao negativo."
done
(( MAX_TURNS > 0 && TIMEOUT_SECONDS > 0 && FAIL_LIMIT > 0 )) || abort 'MAX_TURNS, TIMEOUT_SECONDS e FAIL_LIMIT devem ser maiores que zero.'
[[ -f "$PROMPT_FILE" && -r "$PROMPT_FILE" ]] || abort "Arquivo de prompt nao encontrado: $PROMPT_FILE"
[[ "$BASE_URL" =~ ^https?:// ]] || abort 'FREELLMAPI_URL deve iniciar com http:// ou https://.'

# Não carrega automaticamente ~/.zshrc ou altera a configuração normal do Claude.
# Se não houver chave exportada, pede sem exibi-la no terminal.
GATEWAY_KEY="${FREELLMAPI_KEY:-${FREELLMAPI_API_KEY:-}}"
if [[ -z "$GATEWAY_KEY" ]]; then
    [[ -t 0 ]] || abort 'Defina FREELLMAPI_KEY para execucao nao interativa.'
    read -r -s -p 'Chave unificada FreeLLMAPI: ' GATEWAY_KEY
    printf '\n'
fi
[[ -n "$GATEWAY_KEY" ]] || abort 'Chave vazia.'

mkdir -p "$STATE_DIR/logs"
[[ -f "$STATE_DIR/progress.md" ]] || cat > "$STATE_DIR/progress.md" <<'EOF'
# Progresso do Ralph Loop

O agente atualiza este arquivo a cada ciclo com o que mudou, o que foi testado e o proximo passo.
EOF
# Ignora saídas possivelmente sensíveis/pesadas, mas mantém progress.md versionável.
[[ -f "$STATE_DIR/.gitignore" ]] || printf 'logs/\n*.json\nhistory.tsv\n' > "$STATE_DIR/.gitignore"

BASE_PROMPT="$(cat "$PROMPT_FILE")"
PROMPT="$BASE_PROMPT

---
INSTRUCOES DO EXECUTOR RALPH (seguir a cada execucao):
- Voce esta em uma NOVA execucao; leia os arquivos atuais e $STATE_DIR/progress.md antes de agir.
- Cada execucao deve realizar uma melhoria pequena e verificavel, priorizando impacto real e evitando refazer trabalho concluido.
- Pode editar codigo e criar testes neste repositorio. Nao altere segredos, arquivos fora do repositorio, nem execute destruicao irreversivel.
- Execute testes pertinentes e registre resultado, arquivos alterados e proxima prioridade em $STATE_DIR/progress.md.
- Caso ainda exista qualquer requisito nao concluido, NAO produza a marca de conclusao.
- SOMENTE quando TODOS os criterios objetivos do arquivo de prompt estiverem satisfeitos e testados, encerre sua ULTIMA linha com EXATAMENTE:
<promise>RALPH_DONE</promise>
- Se uma acao estiver bloqueada, explique no registro de progresso e escolha outra tarefa possivel.
"

args=(--print --output-format json --max-turns "$MAX_TURNS")
if [[ -n "${RALPH_MODEL:-}" ]]; then args+=(--model "$RALPH_MODEL"); fi
if [[ "${RALPH_UNSAFE:-0}" == '1' ]]; then
    # APENAS em repositorio/VM/sandbox de confianca: permite Bash e edicoes sem prompts.
    args+=(--dangerously-skip-permissions)
else
    # Permite editar arquivos, mas outras ferramentas podem exigir autorizacao.
    args+=(--permission-mode acceptEdits)
fi

printf '\n[ralph] Projeto: %s\n' "$PWD"
printf '[ralph] Gateway: %s | ciclos: %s | turns/ciclo: %s\n' "$BASE_URL" "$MAX_ITERATIONS" "$MAX_TURNS"
printf '[ralph] Logs: %s/logs | Interromper: Ctrl+C\n' "$STATE_DIR"
[[ "${RALPH_UNSAFE:-0}" == '1' ]] && printf '[ralph] ATENCAO: execucao SEM prompts de permissao ativada.\n'

stopping=0
trap 'stopping=1; printf "\\n[ralph] Interrompido pelo usuario.\\n" >&2; exit 130' INT TERM

# Faz a contagem continuar após reiniciar o script, sem reaproveitar contexto da conversa.
i=0
failures=0
while (( MAX_ITERATIONS == 0 || i < MAX_ITERATIONS )); do
    ((i+=1))
    stamp="$(date +%Y%m%d-%H%M%S)"
    prefix="$STATE_DIR/logs/${stamp}-$(printf '%04d' "$i")"
    printf '\n[ralph] ===== Ciclo %d =====\n' "$i"

    rc=0
    timeout --signal=TERM --kill-after=10s "${TIMEOUT_SECONDS}s" \
        env -u ANTHROPIC_API_KEY \
            ANTHROPIC_BASE_URL="$BASE_URL" \
            ANTHROPIC_AUTH_TOKEN="$GATEWAY_KEY" \
            claude "${args[@]}" "$PROMPT" \
            > "${prefix}.json" 2> "${prefix}.stderr" || rc=$?

    printf '%s\t%s\t%s\n' "$(date -Is)" "$i" "$rc" >> "$STATE_DIR/history.tsv"
    if (( rc != 0 )); then
        printf '[ralph] Falha (codigo %d). Verifique: %s.stderr\n' "$rc" "$prefix" >&2
        tail -n 10 "${prefix}.stderr" >&2 || true
        if grep -Eiq 'cooldown|rate.?limit|429|403|forbidden|model agreement|quota|invalid.api.key|unauthoriz' "${prefix}.stderr" "${prefix}.json"; then
            abort 'Erro de chave, quota, licenca ou cooldown: parei para evitar chamadas repetidas.'
        fi
        ((failures+=1))
        if (( failures >= FAIL_LIMIT )); then abort "${failures} ciclos seguidos falharam; parei."; fi
        sleep "$DELAY_SECONDS"
        continue
    fi

    if ! jq -e . "${prefix}.json" >/dev/null 2>&1; then
        printf '[ralph] Resposta nao e JSON valido: %s.json\n' "$prefix" >&2
        ((failures+=1))
        if (( failures >= FAIL_LIMIT )); then abort 'Muitas respostas invalidas; confira o gateway e o modelo.'; fi
        sleep "$DELAY_SECONDS"
        continue
    fi
    if [[ "$(jq -r '.is_error // false' "${prefix}.json")" == 'true' ]]; then
        printf '[ralph] O agente retornou is_error=true: %s.json\n' "$prefix" >&2
        if grep -Eiq 'cooldown|rate.?limit|429|403|forbidden|model agreement|quota|invalid.api.key|unauthoriz' "${prefix}.stderr" "${prefix}.json"; then
            abort 'Erro de chave, quota, licenca ou cooldown: parei para evitar chamadas repetidas.'
        fi
        ((failures+=1))
        if (( failures >= FAIL_LIMIT )); then abort 'Muitos erros retornados pelo agente.'; fi
        sleep "$DELAY_SECONDS"
        continue
    fi
    result="$(jq -r '.result // empty' "${prefix}.json")"
    if [[ -z "$result" ]]; then
        printf '[ralph] Resposta sem campo result: %s.json\n' "$prefix" >&2
        ((failures+=1))
        if (( failures >= FAIL_LIMIT )); then abort 'Muitas respostas vazias.'; fi
        sleep "$DELAY_SECONDS"
        continue
    fi
    failures=0
    printf '%s\n' "$result" | tail -n 25
    printf '[ralph] Registro: %s.json\n' "$prefix"

    last_line="$(printf '%s\n' "$result" | sed '/^[[:space:]]*$/d' | tail -n 1 | tr -d '\r')"
    if [[ "$last_line" == '<promise>RALPH_DONE</promise>' ]]; then
        if [[ -n "${RALPH_VERIFY_CMD:-}" ]]; then
            printf '[ralph] Executando verificacao final: %s\n' "$RALPH_VERIFY_CMD"
            if ! bash -lc "$RALPH_VERIFY_CMD" > "${prefix}.verify.log" 2>&1; then
                printf '[ralph] Verificacao falhou. Detalhes: %s.verify.log\n' "$prefix" >&2
                tail -n 20 "${prefix}.verify.log" >&2 || true
                sleep "$DELAY_SECONDS"
                continue
            fi
        fi
        printf '\n[ralph] Concluido: criterios sinalizados pelo agente no ciclo %d.\n' "$i"
        exit 0
    fi
    sleep "$DELAY_SECONDS"
done
printf '\n[ralph] Limite de %s ciclos atingido. Estado salvo em %s/progress.md.\n' "$MAX_ITERATIONS" "$STATE_DIR"
exit 0
