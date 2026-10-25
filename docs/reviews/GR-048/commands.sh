#!/usr/bin/env bash
# Reproduction commands. Run from this lab worktree; uses global persistent Cargo config.
set -euo pipefail
LAB=$PWD
SRC=/home/roddy/.cache/artcraft-figcraft-gr048
test -f "$LAB/docs/reviews/GR-019/figcraft-shared-host-save.patch"
test ! -e "$SRC" # fail safely if this reproduction checkout already exists
git clone --depth=1 https://github.com/storytold/figcraft.git "$SRC"
git -C "$SRC" fetch --depth=1 origin 8d790607ff1ad40e32343ca2116d8fdcf3244c8d
git -C "$SRC" checkout --detach 8d790607ff1ad40e32343ca2116d8fdcf3244c8d
git -C "$SRC" apply --check "$LAB/docs/reviews/GR-019/figcraft-shared-host-save.patch"
git -C "$SRC" apply "$LAB/docs/reviews/GR-019/figcraft-shared-host-save.patch"
git -C "$SRC" add -N apps/figcraft-web/src/host.rs crates/ui-egui/src/host_save_tests.rs
sha256sum "$LAB/docs/reviews/GR-019/figcraft-shared-host-save.patch"
git -C "$SRC" rev-parse HEAD
git -C "$SRC" diff --no-ext-diff --src-prefix=c/ --dst-prefix=w/ | sha256sum
git -C "$SRC" diff --check
(cd "$SRC/apps/figcraft-web" && RUSTUP_TOOLCHAIN=1.95.0 trunk build --release)
python3 "$LAB/docs/reviews/GR-048/runtime/make_fixture.py"
cp "$LAB/docs/reviews/GR-048/runtime/host.html" "$SRC/dist/web/host.html"
cp "$LAB/docs/reviews/GR-048/runtime/synthetic.figcraft" "$SRC/dist/web/synthetic.figcraft"
python3 -m http.server 18748 --bind 127.0.0.1 --directory "$SRC/dist/web"
