#!/usr/bin/env bash
# Fetch upstream Craft web release bundles into ./editors/<app>/, verifying SHA-256.
# Usage: fetch-editors.sh wordcraft v0.13.2 <sha256> [gridcraft v0.14.2 <sha256> ...]
# The SHA-256 of a release asset: shasum -a 256 <zip>, or the lab's static/*-PROVENANCE.txt.
# Options:
#   --dry-run     Show what would be done without downloading
#   --parallel N  Download N bundles in parallel (default: 1)
set -euo pipefail

DRY_RUN=false
PARALLEL=1

# Parse options
while [[ $# -gt 0 ]]; do
  case "$1" in
    --dry-run) DRY_RUN=true; shift ;;
    --parallel) PARALLEL="${2:-1}"; shift 2 ;;
    --) shift; break ;;
    -*) echo "Unknown option: $1" >&2; exit 2 ;;
    *) break ;;
  esac
done

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
[[ $# -gt 0 && $(($# % 3)) -eq 0 ]] || { echo "usage: $0 [--dry-run] [--parallel N] APP TAG SHA256 [...]" >&2; exit 2; }

mkdir -p "$HERE/editors"
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT

fetch_one() {
  local app=$1 tag=$2 sha=$3
  [[ "$app" =~ ^[a-z]+$ && "$tag" =~ ^v[0-9][0-9.]*$ && "$sha" =~ ^[0-9a-f]{64}$ ]] || { echo "bad args for $app" >&2; return 1; }
  local asset="$app-web-${tag#v}.zip"
  local url="https://github.com/storytold/$app/releases/download/$tag/$asset"

  echo "==> [$app] $url"
  if [[ "$DRY_RUN" == true ]]; then
    echo "    (dry-run) would download, verify SHA-256, extract to editors/$app/"
    return 0
  fi

  python3 -I "$ROOT/scripts/craft_web_zip.py" download "$url" "$tmp/$asset"
  echo "$sha  $tmp/$asset" | shasum -a 256 --check --status || { echo "SHA-256 mismatch for $asset" >&2; return 1; }
  local root
  root=$(python3 -I "$ROOT/scripts/craft_web_zip.py" extract "$tmp/$asset" "$tmp/$app")
  rm -rf "$HERE/editors/$app"
  mv "$tmp/$app/$root" "$HERE/editors/$app"
  printf 'repository: storytold/%s\nrelease_tag: %s\nasset: %s\nsha256: %s\n' "$app" "$tag" "$asset" "$sha" > "$HERE/editors/$app/PROVENANCE.txt"
  echo "    ✓ $app installed"
}

# Run fetches in parallel using xargs
printf '%s\0' "$@" | xargs -0 -n 3 -P "$PARALLEL" bash -c 'fetch_one "$@"' _

echo "done: $(ls "$HERE/editors")"
