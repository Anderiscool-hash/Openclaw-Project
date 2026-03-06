#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
set -a
source .env
set +a

while true; do
  echo "[$(date)] cycle start"
  python3 sync_brightspace_session.py || echo "sync_brightspace_session failed"
  python3 sync_notion.py || echo "sync_notion failed"
  python3 reminder_runner.py || echo "reminder_runner failed"
  echo "[$(date)] sleeping 10 minutes"
  sleep 600
done
