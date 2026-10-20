#!/usr/bin/env bash
# Preserva o caminho operacional para buscas na base por meio do executável Rust.
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
export HYPRMAC_REPO_ROOT="$root"
exec cargo run --quiet --locked --manifest-path "$root/core/query/Cargo.toml" -- "$@"
