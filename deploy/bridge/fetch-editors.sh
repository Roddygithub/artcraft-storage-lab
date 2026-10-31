#!/usr/bin/env bash
# Fetch upstream Craft web release bundles into ./editors/<app>/, verifying SHA-256.
# Usage: fetch-editors.sh wordcraft v0.13.2 <sha256> [gridcraft v0.14.2 <sha256> ...]
# The SHA-256 of a release asset: shasum -a 256 <zip>, or the lab's static/*-PROVENANCE.txt.
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT="$(cd "$HERE/../.." && pwd)"
[[ $# -gt 0 && $(($# % 3)) -eq 0 ]] || { echo "usage: $0 APP TAG SHA256 [...]" >&2; exit 2; }
mkdir -p "$HERE/editors"
tmp=$(mktemp -d); trap 'rm -rf "$tmp"' EXIT
while (($#)); do
  app=$1; tag=$2; sha=$3; shift 3
  [[ "$app" =~ ^[a-z]+$ && "$tag" =~ ^v[0-9][0-9.]*$ && "$sha" =~ ^[0-9a-f]{64}$ ]] || { echo "bad args for $app" >&2; exit 2; }
  asset="$app-web-${tag#v}.zip"
  url="https://github.com/storytold/$app/releases/download/$tag/$asset"
  echo "==> $url"
  python3 -I "$ROOT/scripts/craft_web_zip.py" download "$url" "$tmp/$asset"
  echo "$sha  $tmp/$asset" | shasum -a 256 --check --status || { echo "SHA-256 mismatch for $asset" >&2; exit 1; }
  root=$(python3 -I "$ROOT/scripts/craft_web_zip.py" extract "$tmp/$asset" "$tmp/$app")
  rm -rf "$HERE/editors/$app"
  mv "$tmp/$app/$root" "$HERE/editors/$app"
  printf 'repository: storytold/%s\nrelease_tag: %s\nasset: %s\nsha256: %s\n' "$app" "$tag" "$asset" "$sha" > "$HERE/editors/$app/PROVENANCE.txt"
done
echo "done: $(ls "$HERE/editors")"
