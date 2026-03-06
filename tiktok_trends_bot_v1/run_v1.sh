#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
set -a
source .env
set +a
python3 collect_trends.py
python3 score_trends.py
python3 daily_report.py
