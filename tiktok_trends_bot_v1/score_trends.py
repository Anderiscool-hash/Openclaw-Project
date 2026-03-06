#!/usr/bin/env python3
"""
Score trend opportunities for monetization.
Input: raw_trends.csv
Output: scored_trends.csv
"""
import csv
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INP = ROOT / "raw_trends.csv"
OUT = ROOT / "scored_trends.csv"


def score_row(row, product_keywords):
    name = row["name"].lower()
    ttype = row["trend_type"].lower()

    # Base by trend type
    base = {
        "hashtag": 55,
        "song": 60,
        "creator": 45,
        "product": 70,
    }.get(ttype, 50)

    # Product intent boost
    pboost = 0
    for kw in product_keywords:
        if kw and kw in name:
            pboost += 12

    # Naming heuristics
    if re.search(r"\b(must have|deal|amazon|shop|buy|finds|gadget|viral|review)\b", name):
        pboost += 10

    # Freshness placeholder (v1 has no historical growth yet)
    freshness = 8

    # Competition proxy
    competition = 20 if len(name) < 10 else 12

    score = max(0, min(100, base + pboost + freshness - competition))
    return score, pboost, competition


def main():
    if not INP.exists():
        raise SystemExit(f"Missing input: {INP}. Run collect_trends.py first.")

    keywords = [k.strip().lower() for k in os.getenv("PRODUCT_KEYWORDS", "").split(",") if k.strip()]

    scored = []
    with INP.open() as f:
        for row in csv.DictReader(f):
            score, pboost, competition = score_row(row, keywords)
            row["monetization_score"] = score
            row["product_intent_boost"] = pboost
            row["competition_penalty"] = competition
            scored.append(row)

    scored.sort(key=lambda r: int(r["monetization_score"]), reverse=True)

    fields = [
        "trend_type", "name", "source_url", "metric_hint", "captured_at",
        "monetization_score", "product_intent_boost", "competition_penalty",
    ]
    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(scored)

    print(f"Wrote {len(scored)} scored trends -> {OUT}")


if __name__ == "__main__":
    main()
