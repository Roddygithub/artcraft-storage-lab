#!/usr/bin/env sh
set -eu
root=$(CDPATH= cd -- "$(dirname -- "$0")/.." && pwd)
crate="$root/integration/rust/craft-platform"
cargo metadata --locked --no-deps --format-version 1 --manifest-path "$crate/Cargo.toml" >/dev/null
cargo test --manifest-path "$crate/Cargo.toml" --locked
cargo check --manifest-path "$crate/Cargo.toml" --locked --features browser --target wasm32-unknown-unknown
