#!/usr/bin/env bash
# Check an already-patched exact PhotoCraft checkout; no services or deployment.
set -euo pipefail
source_dir=${1:?usage: check-gr076-photocraft.sh /path/to/patched-photocraft}
cd "$source_dir"
test "$(git rev-parse HEAD)" = a02f2ee41059d3312e7ff24a5af5edcac7b6435a
cargo +1.95.0 fmt --all -- --check
cargo +1.95.0 test --locked -p photocraft-engine --lib saved_snapshot_tests
cargo +1.95.0 test --locked -p photocraft-ui-egui --lib host_
cargo +1.95.0 test --locked -p photocraft-ui-egui --lib file_open::tests::
cargo +1.95.0 test --locked -p photocraft-web host_inbox::tests::
cargo +1.95.0 check --locked -p photocraft-web --target wasm32-unknown-unknown
git diff --check
