#!/usr/bin/env bash
# Preserva o caminho operacional enquanto executa a auditoria Rust.
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
export HYPRMAC_REPO_ROOT="$root"
exec cargo run --quiet --locked --manifest-path "$root/core/audit/Cargo.toml" -- "$@"
