#!/usr/bin/env bash
# Mantém o caminho operacional da matriz enquanto executa o gerador Rust.
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
export HYPRMAC_REPO_ROOT="$root"
exec cargo run --quiet --locked --manifest-path "$root/core/comparison/Cargo.toml" -- "$@"
