#!/usr/bin/env python3
"""
Collect TikTok trend candidates via SearXNG JSON endpoint.
Requires:
- SEARXNG_URL (e.g. http://127.0.0.1:8080/search)
Outputs raw_trends.csv
"""
import csv
import os
from datetime import datetime
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "raw_trends.csv"


QUERIES = [
    ("song", "tiktok trending songs today"),
    ("song", "tiktok viral sounds this week"),
    ("hashtag", "tiktok trending hashtags today"),
    ("hashtag", "best tiktok hashtags for views"),
    ("product", "tiktok made me buy it trending products"),
    ("product", "viral tiktok shop products today"),
    ("trend", "tiktok viral trends right now"),
    ("trend", "tiktok content trends 2026"),
]


def search(searx_url: str, q: str):
    r = requests.get(searx_url, params={"q": q, "format": "json"}, timeout=25)
    r.raise_for_status()
    data = r.json()
    return data.get("results", [])


def classify_name(title: str, trend_type: str):
    # Keep titles as candidate trend names in v1.2
    return " ".join(title.split())[:160]


def main():
    searx = os.getenv("SEARXNG_URL", "http://127.0.0.1:8080/search")
    rows = []

    for trend_type, q in QUERIES:
        try:
            results = search(searx, q)
        except Exception:
            continue
        for r in results[:25]:
            title = (r.get("title") or "").strip()
            url = (r.get("url") or "").strip()
            if not title or not url:
                continue
            rows.append({
                "trend_type": trend_type,
                "name": classify_name(title, trend_type),
                "source_url": url,
                "metric_hint": "",
                "captured_at": datetime.utcnow().isoformat(timespec="seconds"),
            })

    # dedupe by title/url
    dedup = {}
    for row in rows:
        dedup[(row["trend_type"], row["name"].lower(), row["source_url"])] = row
    rows = list(dedup.values())

    with OUT.open("w", newline="") as f:
        fields = ["trend_type", "name", "source_url", "metric_hint", "captured_at"]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    print(f"Wrote {len(rows)} raw trends via SearXNG -> {OUT}")


if __name__ == "__main__":
    main()
