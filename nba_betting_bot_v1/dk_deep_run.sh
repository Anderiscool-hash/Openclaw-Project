#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
python3 dk_scrape_nba.py
python3 dk_scrape_deep.py
