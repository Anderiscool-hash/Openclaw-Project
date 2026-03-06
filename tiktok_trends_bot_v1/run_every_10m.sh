#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
set -a
source .env
set +a
while true; do
  echo "[$(date)] TikTok trends cycle"
  python3 collect_trends_searxng.py || echo "collect failed"
  python3 score_trends.py || echo "score failed"
  python3 daily_report.py || echo "report failed"
  python3 enrich_content_plan.py || echo "creator pack failed"
  sleep 600
done
