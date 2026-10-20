#!/usr/bin/env bash
# Preserva o caminho operacional enquanto atualiza o índice com Rust.
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
export HYPRMAC_REPO_ROOT="$root"
exec cargo run --quiet --locked --manifest-path "$root/core/code-index/Cargo.toml" -- "$@"
