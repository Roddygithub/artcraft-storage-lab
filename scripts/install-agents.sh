#!/usr/bin/env bash
# Install the OpenCode agent definitions into the global agent directory so that
# automatic model routing works in every session, including sessions started
# outside this repository.
#
# Usage: ./scripts/install-agents.sh [--check]
#   --check  verify the installed copies match the repo copies, install nothing.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SRC_DIR="$REPO_ROOT/config/opencode/agents"
# OpenCode reads global agents from "$XDG_CONFIG_HOME/opencode/agents" (or
# ~/.config/opencode/agents). Note the "/opencode" segment: XDG_CONFIG_HOME is
# the *config root*, not the OpenCode directory.
CONFIG_ROOT="${XDG_CONFIG_HOME:-$HOME/.config}"
DEST_DIR="$CONFIG_ROOT/opencode/agents"

CHECK_ONLY=0
[[ "${1:-}" == "--check" ]] && CHECK_ONLY=1

if [[ ! -d "$SRC_DIR" ]]; then
  echo "error: source agent directory not found: $SRC_DIR" >&2
  exit 1
fi

mkdir -p "$DEST_DIR"

status=0
for src in "$SRC_DIR"/*.md; do
  name="$(basename "$src")"
  dest="$DEST_DIR/$name"
  if [[ -f "$dest" ]] && diff -q "$src" "$dest" >/dev/null 2>&1; then
    echo "  up to date: $name"
    continue
  fi
  if [[ $CHECK_ONLY -eq 1 ]]; then
    echo "  OUT OF SYNC: $name"
    status=1
    continue
  fi
  cp "$src" "$dest"
  echo "  installed:  $name -> $dest"
done

if [[ $CHECK_ONLY -eq 1 && $status -ne 0 ]]; then
  echo
  echo "agents are out of sync; run: $0"
  exit 1
fi

echo
echo "agent definitions live in: $DEST_DIR"
echo "verify with: opencode api get '/api/agent?directory=$REPO_ROOT'"
