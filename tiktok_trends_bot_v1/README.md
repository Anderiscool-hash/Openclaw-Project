# TikTok Trends Bot v1

Purpose: track viral sounds/hashtags/products and rank monetization opportunities.

## Files
- `collect_trends.py` → gather candidates into `raw_trends.csv`
- `score_trends.py` → compute monetization score into `scored_trends.csv`
- `daily_report.py` → output top list to `report_top_trends.csv` and `.txt`
- `run_v1.sh` → one-shot run
- `run_every_10m.sh` → loop every 10 minutes

## Setup
```bash
cd tiktok_trends_bot_v1
cp .env.example .env
pip install -r requirements.txt
```

## Run once
```bash
./run_v1.sh
```

## Run every 10 minutes
```bash
./run_every_10m.sh
```

## Notes
- v1 uses public-page best-effort extraction and heuristics.
- For stronger reliability, v2 should add stable data providers/APIs and historical growth tracking.
- Respect platform terms and rate limits.
