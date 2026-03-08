#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
set -a
source .env
set +a
python3 nba_collect.py
python3 nba_model.py
python3 nba_picks_today.py
