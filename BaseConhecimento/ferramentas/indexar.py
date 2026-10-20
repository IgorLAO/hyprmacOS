#!/usr/bin/env bash
# Preserva o caminho operacional da indexação incremental via Rust.
set -euo pipefail
root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
export HYPRMAC_BASE_DIR="$root/BaseConhecimento"
exec cargo run --quiet --locked --manifest-path "$root/core/knowledge-index/Cargo.toml" -- "$@"
