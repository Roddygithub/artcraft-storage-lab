#!/usr/bin/env bash
# Stage an exact upstream web release without replacing the active editor build.
# Promotion is deliberately separate and must follow a host-protocol check.
set -euo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
STATIC="$HERE/integration/static"

if [[ $# -eq 0 || $(($# % 3)) -ne 0 ]]; then
  echo "Usage: $0 APP RELEASE_TAG ASSET_SHA256 [APP RELEASE_TAG ASSET_SHA256 ...]" >&2
  echo "Stages verified releases under integration/static/candidates/; does not install them." >&2
  exit 2
fi

command -v gh >/dev/null || { echo "gh is required" >&2; exit 1; }
command -v curl >/dev/null || { echo "curl is required" >&2; exit 1; }
command -v python3 >/dev/null || { echo "python3 is required" >&2; exit 1; }

candidate_root="$STATIC/candidates"
if [[ -L "$candidate_root" ]]; then
  echo "refusing symlinked candidate root: $candidate_root" >&2
  exit 1
fi
mkdir -p "$candidate_root"
candidate_root_real=$(realpath --canonicalize-existing "$candidate_root")
tmp=""
cleanup() {
  if [[ -n "$tmp" && -d "$tmp" ]]; then rm -rf -- "$tmp"; fi
}
trap cleanup EXIT

while (($#)); do
  app=$1
  tag=$2
  expected=$3
  shift 3

  [[ "$app" =~ ^[a-z0-9]+$ ]] || { echo "invalid app name: $app" >&2; exit 2; }
  [[ "$tag" =~ ^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$ ]] || { echo "invalid release tag: $tag" >&2; exit 2; }
  [[ "$expected" =~ ^[[:xdigit:]]{64}$ ]] || { echo "expected SHA-256 must be 64 hex characters for $app" >&2; exit 2; }

  repo="storytold/$app"
  asset_output=$(gh release view "$tag" --repo "$repo" --json assets --jq '.assets[].name')
  mapfile -t assets < <(printf '%s\n' "$asset_output" | grep -E "^${app}-web-[A-Za-z0-9._-]+\.zip$" || true)
  if ((${#assets[@]} != 1)); then
    echo "expected exactly one $app-web ZIP asset in $repo@$tag; found ${#assets[@]}" >&2
    exit 1
  fi
  asset=${assets[0]}
  url="https://github.com/$repo/releases/download/$tag/$asset"
  app_root="$candidate_root/$app"
  if [[ -L "$app_root" ]]; then
    echo "refusing symlinked app candidate directory: $app_root" >&2
    exit 1
  fi
  mkdir -p "$app_root"
  app_root_real=$(realpath --canonicalize-existing "$app_root")
  if [[ "$app_root_real" != "$candidate_root_real/$app" ]]; then
    echo "candidate directory resolves outside its expected parent: $app_root" >&2
    exit 1
  fi
  candidate="$app_root/$tag-${expected,,}"
  if [[ -e "$candidate" || -L "$candidate" ]]; then
    echo "candidate already exists; refusing to overwrite: $candidate" >&2
    exit 1
  fi

  tmp=$(mktemp -d "$app_root/.stage.XXXXXX")
  echo "==> $repo@$tag/$asset"
  curl --fail --location --silent --show-error -o "$tmp/$asset" "$url"
  printf '%s  %s\n' "${expected,,}" "$tmp/$asset" | sha256sum --check --status || {
    echo "SHA-256 mismatch for $url" >&2
    exit 1
  }

  root=$(python3 - "$tmp/$asset" "$tmp/unpacked" <<'PY'
import stat
import sys
import zipfile
from pathlib import PurePosixPath

archive, destination = sys.argv[1:]
with zipfile.ZipFile(archive) as zf:
    infos = zf.infolist()
    roots = set()
    for info in infos:
        name = info.filename
        path = PurePosixPath(name)
        mode = info.external_attr >> 16
        if (not name or "\\" in name or path.is_absolute()
                or ".." in path.parts or stat.S_ISLNK(mode)):
            raise SystemExit(f"unsafe ZIP entry: {name!r}")
        if path.parts:
            roots.add(path.parts[0])
    if len(roots) != 1:
        raise SystemExit("web asset must contain exactly one top-level directory")
    root = roots.pop()
    names = {PurePosixPath(i.filename).as_posix() for i in infos}
    if f"{root}/index.html" not in names:
        raise SystemExit("web asset has no root index.html")
    if not any(n.startswith(root + "/") and n.endswith(".wasm") for n in names):
        raise SystemExit("web asset contains no WASM module")
    zf.extractall(destination)
    print(root)
PY
  )
  mv -- "$tmp/unpacked/$root" "$tmp/staged"
  cat > "$tmp/staged/ARTIFACT-PROVENANCE.txt" <<EOF
repository: $repo
release_tag: $tag
asset: $asset
asset_sha256: ${expected,,}
source_url: $url
host_protocol_compatibility: NOT VERIFIED
state: staged candidate; not installed under integration/static/<app>
EOF
  mv --no-clobber --no-target-directory -- "$tmp/staged" "$candidate"
  if [[ -e "$tmp/staged" ]]; then
    echo "candidate appeared during staging; refusing to overwrite: $candidate" >&2
    exit 1
  fi
  rm -rf -- "$tmp"
  tmp=""
  echo "    staged: ${candidate#"$HERE/"}"
  echo "    verify host protocol before promotion to integration/static/$app"
done
