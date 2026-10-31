#!/usr/bin/env bash
# Take a bundle built in the lab VM (~/build/<app>/dist/web, from an upstream clone plus our
# host-bridge port) into the lab's editors, record provenance, save the port diff under
# docs/upstream-drafts/<app>-host-bridge/, and free the VM's build target directory.
# Usage: lab/real-seafile/wire-built-bundle.sh <app>
set -euo pipefail
VM=${VM:-seafile-lab}
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
app=$1
[[ "$app" =~ ^[a-z]+$ ]] || { echo "bad app name" >&2; exit 2; }
vm() { limactl shell "$VM" -- bash -lc "$*"; }
home=$(vm 'echo $HOME')
vm "test -f ~/build/$app/dist/web/index.html" || { echo "no built bundle for $app in the VM" >&2; exit 1; }
commit=$(vm "cd ~/build/$app && git rev-parse --short HEAD")
version=$(vm "cd ~/build/$app && grep -m1 '^version' Cargo.toml | sed 's/.*\"\\(.*\\)\"/\\1/'")
vm "cd ~/build/$app && git add -N . && git diff > ~/build/$app-host-bridge.diff"
limactl copy "$VM:$home/build/$app-host-bridge.diff" "$HERE/docs/upstream-drafts/$app-host-bridge/$app-host-bridge.diff"
# into the VM's lab copy (served by the bridge container) and the local lab tree (gitignored)
vm "rm -rf ~/seafile-lab/app/lab/real-seafile/static/$app && cp -R ~/build/$app/dist/web ~/seafile-lab/app/lab/real-seafile/static/$app"
rm -rf "$HERE/lab/real-seafile/static/$app"
mkdir -p "$HERE/lab/real-seafile/static/$app"
limactl copy -r "$VM:$home/build/$app/dist/web/." "$HERE/lab/real-seafile/static/$app/" 2>/dev/null || true
cat > "$HERE/lab/real-seafile/static/$app-PROVENANCE.txt" <<P
repository: storytold/$app
built_from: $commit (v$version, shallow clone of main)
asset: built in the lab VM with trunk build --release (not an upstream release asset)
patched: yes -- host bridge port, see docs/upstream-drafts/$app-host-bridge/ ($app-host-bridge.diff); nothing else changed
EOF_MARK
P
sed -i '' '/^EOF_MARK$/d' "$HERE/lab/real-seafile/static/$app-PROVENANCE.txt"
grep -q "static/$app/" "$HERE/lab/real-seafile/.gitignore" || echo "static/$app/" >> "$HERE/lab/real-seafile/.gitignore"
vm "rm -rf ~/build/$app/target"
echo "wired $app ($commit v$version); diff: $(wc -l < "$HERE/docs/upstream-drafts/$app-host-bridge/$app-host-bridge.diff") lines"
