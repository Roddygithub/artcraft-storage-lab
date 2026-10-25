#!/bin/sh
set -eu

ROOT=/home/roddy/.t3/worktrees/artcraft-storage-lab/t3-4d53dbd5
SOURCE=/home/roddy/.cache/artcraft-storage-lab/gr056-source/gridcraft
PATCH="$ROOT/docs/reviews/GR-016/patches/gridcraft-shared-transport.patch"
DIST=/home/roddy/.cache/artcraft-storage-lab/gr056-gridcraft-static/gridcraft

# If starting fresh, use a clean local clone of the public-origin checkout
# recorded in the report, then detach at the exact source commit.
if [ ! -d "$SOURCE/.git" ]; then
  git clone --no-hardlinks --no-checkout /home/roddy/Projects/gridcraft "$SOURCE"
  git -C "$SOURCE" remote set-url origin https://github.com/storytold/gridcraft.git
  git -C "$SOURCE" checkout --detach 06920de8da609c19de7446945cfc62b844691efd
fi
test "$(git -C "$SOURCE" rev-parse HEAD)" = 06920de8da609c19de7446945cfc62b844691efd
sha256sum "$PATCH"
if ! git -C "$SOURCE" apply --reverse --check "$PATCH" >/dev/null 2>&1; then
  git -C "$SOURCE" apply --check "$PATCH"
  git -C "$SOURCE" apply "$PATCH"
fi
grep -n 'craft-platform' "$SOURCE/Cargo.toml" "$SOURCE/Cargo.lock"
if ! grep -q 'data-wasm-opt="0"' "$SOURCE/apps/gridcraft-web/index.html"; then
  sed -i 's/data-wasm-opt="z"/data-wasm-opt="0"/' "$SOURCE/apps/gridcraft-web/index.html"
fi
sha256sum "$SOURCE/apps/gridcraft-web/index.html"
RUSTUP_TOOLCHAIN=1.95.0 rustc --version
RUSTUP_TOOLCHAIN=1.95.0 cargo --version
trunk --version
test "$TMPDIR" = /home/roddy/.cache/cargo-tmp
printf 'TMPDIR=%s\n' "$TMPDIR"
printf 'CARGO_TARGET_DIR=%s\n' "${CARGO_TARGET_DIR:-<unset>}"
mkdir -p "$(dirname "$DIST")"
(cd "$SOURCE/apps/gridcraft-web" && RUSTUP_TOOLCHAIN=1.95.0 \
  trunk build --release --locked --dist "$DIST")
python3 "$ROOT/docs/reviews/GR-056/verify_candidate.py"
