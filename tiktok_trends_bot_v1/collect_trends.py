#!/usr/bin/env python3
"""
Collect trend candidates (sounds/hashtags/products) into raw_trends.csv.

v1 sources:
- TikTok Creative Center trend pages (public HTML best-effort)
- Optional manual seed file: manual_trends.csv

Output: raw_trends.csv
Columns: trend_type,name,source_url,metric_hint,captured_at
"""
import csv
import os
import re
from datetime import datetime
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "raw_trends.csv"
MANUAL = ROOT / "manual_trends.csv"


def parse_public_tiktok_pages(region="US"):
    # Public pages; parsing is best-effort and may evolve with site changes.
    pages = [
        ("hashtag", f"https://ads.tiktok.com/business/creativecenter/inspiration/popular/hashtag/pc/{region}"),
        ("song", f"https://ads.tiktok.com/business/creativecenter/inspiration/popular/music/pc/{region}"),
        ("creator", f"https://ads.tiktok.com/business/creativecenter/inspiration/popular/creator/pc/{region}"),
    ]
    rows = []
    for trend_type, url in pages:
        try:
            html = requests.get(url, timeout=25, headers={"User-Agent": "Mozilla/5.0"}).text
        except Exception:
            continue

        # very lightweight extraction of quoted hashtag/music-like tokens
        # This is intentionally broad to keep v1 resilient.
        candidates = set()
        if trend_type == "hashtag":
            for m in re.finditer(r"#([A-Za-z0-9_]{3,40})", html):
                candidates.add("#" + m.group(1))
        else:
            for m in re.finditer(r'"title"\s*:\s*"([^"\\]{3,120})"', html):
                candidates.add(m.group(1).strip())

        for c in list(candidates)[:120]:
            rows.append({
                "trend_type": trend_type,
                "name": c,
                "source_url": url,
                "metric_hint": "",
                "captured_at": datetime.utcnow().isoformat(timespec="seconds"),
            })
    return rows


def load_manual():
    if not MANUAL.exists():
        return []
    rows = []
    with MANUAL.open() as f:
        for r in csv.DictReader(f):
            name = (r.get("name") or "").strip()
            if not name:
                continue
            rows.append({
                "trend_type": (r.get("trend_type") or "product").strip().lower(),
                "name": name,
                "source_url": (r.get("source_url") or "manual").strip(),
                "metric_hint": (r.get("metric_hint") or "").strip(),
                "captured_at": datetime.utcnow().isoformat(timespec="seconds"),
            })
    return rows


def main():
    region = os.getenv("TT_REGION", "US")
    rows = []
    rows.extend(parse_public_tiktok_pages(region=region))
    rows.extend(load_manual())

    # de-dupe by type+name
    dedup = {}
    for r in rows:
        dedup[(r["trend_type"], r["name"].lower())] = r
    rows = list(dedup.values())

    fields = ["trend_type", "name", "source_url", "metric_hint", "captured_at"]
    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    print(f"Wrote {len(rows)} raw trends -> {OUT}")


if __name__ == "__main__":
    main()
