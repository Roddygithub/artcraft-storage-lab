#!/usr/bin/env bash
# Bring up the real-Seafile slice inside the dedicated Lima VM (default name: seafile-lab).
# Usage: lab/real-seafile/up.sh [up|configure|slice|down|logs]
set -euo pipefail
VM=${VM:-seafile-lab}
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
REMOTE='~/seafile-lab'
cmd=${1:-up}

vm() { limactl shell "$VM" -- bash -lc "$*"; }

sync_files() {
  vm "mkdir -p $REMOTE/app $REMOTE/results"
  limactl copy -r "$HERE/bridge" "$VM:$REMOTE/app/"
  limactl copy -r "$HERE/lab" "$VM:$REMOTE/app/"
  limactl copy "$HERE/lab/real-seafile/compose.yml" "$VM:$REMOTE/compose.yml"
  if ! vm "test -f $REMOTE/.env"; then
    vm "cd $REMOTE && {
      echo SEAFILE_MYSQL_DB_PASSWORD=\$(openssl rand -hex 16)
      echo INIT_SEAFILE_MYSQL_ROOT_PASSWORD=\$(openssl rand -hex 16)
      echo REDIS_PASSWORD=\$(openssl rand -hex 16)
      echo JWT_PRIVATE_KEY=\$(openssl rand -hex 32)
      echo ONLYOFFICE_JWT_SECRET=\$(openssl rand -hex 24)
      echo ADMIN_EMAIL=admin@lab.test
      echo ADMIN_PASSWORD=\$(openssl rand -hex 12)
    } > .env && chmod 600 .env"
  fi
}

case "$cmd" in
  up)
    sync_files
    vm "cd $REMOTE && docker compose up -d db redis seafile onlyoffice bridge"
    ;;
  configure)
    # (Re)apply the managed settings block once Seafile has written its config, then restart.
    sync_files
    vm "cd $REMOTE && set -a && . ./.env && set +a
        conf=data/seafile/seafile/conf/seahub_settings.py
        for i in \$(seq 1 60); do sudo test -f \$conf && break; sleep 5; done
        sudo test -f \$conf || { echo 'seahub_settings.py never appeared' >&2; exit 1; }
        sudo sed -i '/^# >>> artcraft-lab/,/^# <<< artcraft-lab/d' \$conf
        sed \"s|__ONLYOFFICE_JWT_SECRET__|\$ONLYOFFICE_JWT_SECRET|\" app/lab/real-seafile/seahub_settings.extra.py | sudo tee -a \$conf >/dev/null
        docker compose restart seafile >/dev/null 2>&1
        sudo grep -E 'FILE_EXTENSION' \$conf"
    ;;
  slice)
    sync_files
    vm "cd $REMOTE && docker compose --profile test run --rm slice"
    vm "cat $REMOTE/results/slice.json" > "$HERE/lab/real-seafile/results/slice.json" 2>/dev/null || true
    ;;
  logs) vm "cd $REMOTE && docker compose logs --tail=100 ${2:-}" ;;
  down) vm "cd $REMOTE && docker compose --profile test down" ;;
  *) echo "unknown command $cmd" >&2; exit 2 ;;
esac
