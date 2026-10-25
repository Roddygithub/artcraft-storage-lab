#!/usr/bin/env bash
set -eu

# Exact source checkout and stored host-ack patch application.
mkdir -p /home/roddy/.cache/artcraft-storage-lab/gr057-source
git clone https://github.com/storytold/pdfcraft.git /home/roddy/.cache/artcraft-storage-lab/gr057-source/pdfcraft
git -C /home/roddy/.cache/artcraft-storage-lab/gr057-source/pdfcraft fetch origin 57e531ccca0047597809748b5cb4276336d6051a
git -C /home/roddy/.cache/artcraft-storage-lab/gr057-source/pdfcraft checkout --detach 57e531ccca0047597809748b5cb4276336d6051a
git -C /home/roddy/.cache/artcraft-storage-lab/gr057-source/pdfcraft rev-parse HEAD
sha256sum /home/roddy/.t3/worktrees/artcraft-storage-lab/t3-52de755b/docs/reviews/GR-017/patches/pdfcraft-durable-host-ack.patch
git -C /home/roddy/.cache/artcraft-storage-lab/gr057-source/pdfcraft apply --check /home/roddy/.t3/worktrees/artcraft-storage-lab/t3-52de755b/docs/reviews/GR-017/patches/pdfcraft-durable-host-ack.patch
git -C /home/roddy/.cache/artcraft-storage-lab/gr057-source/pdfcraft apply /home/roddy/.t3/worktrees/artcraft-storage-lab/t3-52de755b/docs/reviews/GR-017/patches/pdfcraft-durable-host-ack.patch

# Documented build-only functional overlay; this does not alter the stored patch.
cd /home/roddy/.cache/artcraft-storage-lab/gr057-source/pdfcraft
sed -i 's/data-wasm-opt="z"/data-wasm-opt="0"/' apps/pdfcraft-web/index.html
sha256sum apps/pdfcraft-web/index.html
sha256sum Cargo.lock

# Release bundle outside integration/static and dispatch.
cd apps/pdfcraft-web
CARGO_TARGET_DIR=/home/roddy/.cache/cargo-target \
TMPDIR=/home/roddy/.cache/cargo-tmp \
CARGO_BUILD_JOBS=2 \
CARGO_PROFILE_RELEASE_DEBUG=0 \
CARGO_INCREMENTAL=0 \
RUSTUP_TOOLCHAIN=1.95.0 \
trunk build --release --locked \
  --dist /home/roddy/.cache/artcraft-storage-lab/gr057-pdfcraft-static/pdfcraft --verbose

# Candidate verifier and actual-built-WASM Chromium smoke.
cd /home/roddy/.t3/worktrees/artcraft-storage-lab/t3-52de755b
python3 docs/reviews/GR-057/verify_candidate.py
uv run --with playwright --python 3.14 -- python -u docs/reviews/GR-057/runtime/test_pdfcraft_host_roundtrip.py \
  --candidate /home/roddy/.cache/artcraft-storage-lab/gr057-pdfcraft-static/pdfcraft \
  --fixture /home/roddy/.cache/artcraft-storage-lab/gr057-source/pdfcraft/crates/ui-egui/tests/data/form.pdf \
  --evidence-dir docs/reviews/GR-057/runtime
