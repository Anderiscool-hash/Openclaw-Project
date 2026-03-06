#!/usr/bin/env python3
"""
Create a concise daily short-list from scored_trends.csv.
Output: report_top_trends.txt + report_top_trends.csv
"""
import csv
import os
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent
INP = ROOT / "scored_trends.csv"
TXT = ROOT / "report_top_trends.txt"
CSV_OUT = ROOT / "report_top_trends.csv"


def main():
    if not INP.exists():
        raise SystemExit(f"Missing {INP}. Run score_trends.py first.")

    top_n = int(os.getenv("TOP_N", "20"))

    rows = []
    with INP.open() as f:
        rows = list(csv.DictReader(f))

    top = rows[:top_n]

    with CSV_OUT.open("w", newline="") as f:
        fields = ["trend_type", "name", "monetization_score", "source_url"]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for r in top:
            w.writerow({k: r.get(k, "") for k in fields})

    lines = [f"TikTok Trends Daily Report ({datetime.now().strftime('%Y-%m-%d %H:%M')})", ""]
    for i, r in enumerate(top, 1):
        lines.append(
            f"{i}. [{r.get('trend_type','')}] {r.get('name','')} | score={r.get('monetization_score','')} | {r.get('source_url','')}"
        )

    TXT.write_text("\n".join(lines))
    print(f"Wrote {len(top)} top trends -> {CSV_OUT} and {TXT}")


if __name__ == "__main__":
    main()
