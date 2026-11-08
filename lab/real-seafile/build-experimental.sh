#!/usr/bin/env bash
# Build experimental Rust/WASM Craft ports in the Lima VM.
# Run INSIDE the Lima VM (limactl shell seafile-lab).
# Requires: rustup, trunk, ~6 GiB RAM, ~10 GiB disk per app during build.

set -euo pipefail

APPS=(deckcraft soundcraft photocraft designcraft)
# Pin exact upstream commits from the upstream-drafts README
# These must match the apply.py patches
declare -A COMMITS=(
    ["deckcraft"]="a3fbf02"   # v0.13.1
    ["soundcraft"]="0d8b7e3"  # v0.15.0
    ["photocraft"]="1e8f9a2"  # v0.18.0
    ["designcraft"]="7c4e1b5" # v0.15.2
)

ROOT="$HOME/build"
mkdir -p "$ROOT"

clone_and_patch() {
    local app=$1
    local commit=${COMMITS[$app]}
    local repo_url="https://github.com/storytold/$app"
    local build_dir="$ROOT/$app"

    echo "=== Building $app ==="
    if [[ -d "$build_dir" ]]; then
        echo "Directory exists, pulling latest..."
        cd "$build_dir" && git fetch origin && git reset --hard "$commit"
    else
        echo "Cloning $repo_url at $commit..."
        git clone --depth 1 --branch main "$repo_url" "$build_dir"
        cd "$build_dir" && git fetch origin "$commit" && git reset --hard "$commit"
    fi

    # Apply the host bridge patch
    local apply_script="/opt/seafile/seafile-lab/app/docs/upstream-drafts/${app}-host-bridge/apply.py"
    if [[ -f "$apply_script" ]]; then
        echo "Applying host bridge patch..."
        python3 "$apply_script" "$build_dir"
    else
        echo "ERROR: apply.py not found at $apply_script" >&2
        return 1
    fi

    # Build
    echo "Building WASM with trunk (release)..."
    cd "$build_dir/apps/${app}-web"
    # Stop other containers to free RAM
    if command -v docker &> /dev/null; then
        docker compose -f ~/seafile-lab/compose.yml stop 2>/dev/null || true
    fi

    # trunk build needs lots of RAM; set CARGO_BUILD_JOBS=2 to limit parallelism
    CARGO_BUILD_JOBS=2 trunk build --release --public-url "/editors/$app/" 2>&1 | tee "$build_dir/build.log"

    echo "Build complete: $build_dir/dist/web/"
    ls -la "$build_dir/dist/web/"
}

# Build all apps sequentially (parallel builds OOM)
for app in "${APPS[@]}"; do
    clone_and_patch "$app" || { echo "FAILED: $app"; exit 1; }
done

echo "All experimental ports built. Next steps:"
echo "  1. Run wire-built-bundle.sh for each app from the host"
echo "  2. Copy editors.experimental.json and seahub_settings.experimental.py to the lab"
echo "  3. Run lab/real-seafile/up.sh browser with BROWSER_ONLY_EDITOR set per app"