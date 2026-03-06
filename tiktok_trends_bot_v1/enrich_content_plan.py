#!/usr/bin/env python3
"""
Create a creator-ready plan from scored trends.
Outputs:
- top10_creator_pack.csv
- top10_creator_pack.txt

This script does not require external APIs; it transforms scored trend rows
into actionable video ideas (hook/angle/CTA/hashtag bundle).
"""
import csv
import os
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent
INP = ROOT / "scored_trends.csv"
OUT_CSV = ROOT / "top10_creator_pack.csv"
OUT_TXT = ROOT / "top10_creator_pack.txt"

ANGLE_MAP = {
    "song": "Use this sound with a fast 3-cut transformation",
    "hashtag": "Join the hashtag with your niche-specific twist",
    "product": "Demo + problem/solution + before/after",
    "creator": "Remix the format with your brand voice",
}


def make_hook(name: str, trend_type: str) -> str:
    if trend_type == "song":
        return f"POV: this sound instantly upgrades your video style ({name})"
    if trend_type == "hashtag":
        return f"I tested {name} in my niche so you don\'t have to"
    if trend_type == "product":
        return f"This product is blowing up for a reason — here\'s what happened"
    return f"Tried this viral trend: {name}"


def make_cta(trend_type: str) -> str:
    if trend_type == "product":
        return "Comment 'LINK' and I\'ll send details"
    return "Follow for daily viral trend breakdowns"


def hashtag_bundle(name: str, trend_type: str) -> str:
    base = ["#fyp", "#viral", "#tiktoktrend", "#contentcreator"]
    if trend_type == "product":
        base += ["#tiktokmademebuyit", "#amazonfinds", "#musthave"]
    if trend_type == "song":
        base += ["#viralsound", "#musictrend"]
    if trend_type == "hashtag" and name.startswith("#"):
        base.insert(0, name.lower())
    return " ".join(base[:8])


def main():
    if not INP.exists():
        raise SystemExit("Missing scored_trends.csv; run collect_trends.py and score_trends.py first.")

    top_n = int(os.getenv("TOP_N", "10"))
    rows = list(csv.DictReader(INP.open()))[:top_n]

    pack = []
    for i, r in enumerate(rows, 1):
        t = (r.get("trend_type") or "").lower()
        name = r.get("name", "")
        pack.append({
            "rank": i,
            "trend_type": t,
            "name": name,
            "score": r.get("monetization_score", ""),
            "hook": make_hook(name, t),
            "angle": ANGLE_MAP.get(t, "Repurpose trend with your niche context"),
            "cta": make_cta(t),
            "hashtags": hashtag_bundle(name, t),
            "source_url": r.get("source_url", ""),
        })

    fields = ["rank", "trend_type", "name", "score", "hook", "angle", "cta", "hashtags", "source_url"]
    with OUT_CSV.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(pack)

    lines = [f"TikTok Creator Pack ({datetime.now().strftime('%Y-%m-%d %H:%M')})", ""]
    for p in pack:
        lines += [
            f"{p['rank']}. [{p['trend_type']}] {p['name']} (score {p['score']})",
            f"   Hook: {p['hook']}",
            f"   Angle: {p['angle']}",
            f"   CTA: {p['cta']}",
            f"   Hashtags: {p['hashtags']}",
            f"   Source: {p['source_url']}",
            "",
        ]
    OUT_TXT.write_text("\n".join(lines))
    print(f"Wrote {len(pack)} rows -> {OUT_CSV} and {OUT_TXT}")


if __name__ == "__main__":
    main()
