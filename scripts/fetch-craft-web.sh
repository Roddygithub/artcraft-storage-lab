#!/usr/bin/env bash
# Fetch the prebuilt Craft web builds and unpack them under integration/static/<app>/.
#
# The Craft apps publish their browser build in their GitHub releases
# (packaging/web/README.md: "wordcraft-web-<version>.zip (from the GitHub release)").
# Using the release build keeps this project free of a Rust/wasm toolchain.
#
# Usage: ./scripts/fetch-craft-web.sh [app ...]      (default: every app in dispatch.json)

set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STATIC="$HERE/integration/static"
DISPATCH="$HERE/integration/config/dispatch.json"

mkdir -p "$STATIC"

apps=("$@")
if [[ ${#apps[@]} -eq 0 ]]; then
  mapfile -t apps < <(python3 -c "
import json,sys
d=json.load(open('$DISPATCH'))
for v in sorted({e['app'] for e in d.values()}): print(v)
")
fi

for app in "${apps[@]}"; do
  repo="storytold/$app"
  tag=$(gh release view --repo "$repo" --json tagName --jq .tagName)
  asset=$(gh release view --repo "$repo" --json assets --jq ".assets[] | select(.name | test(\"^${app}-web-.*\\\\.zip$\")) | .name" | head -1)
  if [[ -z "$asset" ]]; then
    echo "no web asset in $repo $tag" >&2
    continue
  fi
  url="https://github.com/$repo/releases/download/$tag/$asset"
  echo "==> $app $tag  $asset"
  tmp=$(mktemp -d)
  curl -sSL -o "$tmp/$asset" "$url"
  unzip -q -o "$tmp/$asset" -d "$tmp"
  inner=$(find "$tmp" -mindepth 1 -maxdepth 1 -type d | head -1)
  rm -rf "$STATIC/$app"
  mkdir -p "$STATIC/$app"
  cp -a "$inner/." "$STATIC/$app/"
  rm -rf "$tmp"
  echo "    -> integration/static/$app/ ($(du -sh "$STATIC/$app" | cut -f1))"
done
