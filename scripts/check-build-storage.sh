#!/usr/bin/env bash
set -euo pipefail

cache_root="${HOME}/.cache"
expected_target="${cache_root}/cargo-target"
expected_tmp="${cache_root}/cargo-tmp"
mkdir -p "$expected_target" "$expected_tmp"

target_dir="$(cargo metadata --no-deps --format-version 1 | python3 -c 'import json,sys; print(json.load(sys.stdin)["target_directory"])')"
if [[ "$target_dir" != "$expected_target" ]]; then
  printf 'Cargo target-dir mismatch: %s\n' "$target_dir" >&2
  exit 1
fi

configured_tmp="$(python3 - <<'PY'
import os, pathlib, tomllib
config = pathlib.Path.home() / ".cargo/config.toml"
data = tomllib.loads(config.read_text())
print(data["env"]["TMPDIR"]["value"])
PY
)"
if [[ "$configured_tmp" != "$expected_tmp" ]]; then
  printf 'Cargo TMPDIR config mismatch: %s\n' "$configured_tmp" >&2
  exit 1
fi

probe="$(TMPDIR="$expected_tmp" mktemp -d "${expected_tmp}/cargo-env-check.XXXXXX")"
cleanup() {
  python3 -c 'import pathlib,shutil,sys; shutil.rmtree(pathlib.Path(sys.argv[1]))' "$probe"
}
trap cleanup EXIT
mkdir -p "$probe/src"
cat > "$probe/Cargo.toml" <<'EOF'
[package]
name = "cargo-storage-env-check"
version = "0.1.0"
edition = "2024"
EOF
cat > "$probe/src/main.rs" <<'EOF'
fn main() {
    println!("{}", std::env::var("TMPDIR").unwrap_or_default());
}
EOF

observed_tmp="$(cargo run --quiet --offline --manifest-path "$probe/Cargo.toml")"
if [[ "$observed_tmp" != "$expected_tmp" ]]; then
  printf 'Cargo child TMPDIR mismatch: %s\n' "$observed_tmp" >&2
  exit 1
fi

printf 'Cargo target-dir: %s\nCargo child TMPDIR: %s\n' "$target_dir" "$observed_tmp"
