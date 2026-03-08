#!/usr/bin/env python3
"""Strict DK market filter: keep only clean core markets and player props.

Input: draftkings_nba_markets_clean.csv
Output: draftkings_nba_markets_strict.csv
"""
import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INP = ROOT / "draftkings_nba_markets_clean.csv"
OUT = ROOT / "draftkings_nba_markets_strict.csv"

ALLOW_MARKETS = {"moneyline", "spread", "total", "player_prop", "player_total"}

BAD_TOKENS = [
    "bonus", "crowd", "popular", "warm up", "raising", "covering", "up up",
    "same game", "sponsored", "featured", "most bet", "placed this bet", "boost",
    "1st points scorer", "first points scorer", "race", "special"
]

TEAM_SHORT = [
    "hawks", "76ers", "celtics", "cavaliers", "knicks", "lakers", "nets", "pistons",
    "bucks", "jazz", "clippers", "grizzlies", "thunder", "warriors", "mavericks",
    "raptors", "wizards", "pelicans", "rockets", "spurs", "bulls", "kings", "pacers",
    "trail blazers", "hornets", "suns"
]

PRICE_RE = re.compile(r"^[+-]\d{2,4}$")


def looks_real_selection(sel: str, mtype: str) -> bool:
    s = (sel or "").strip().lower()
    if not s:
        return False
    if any(b in s for b in BAD_TOKENS):
        return False

    if mtype in {"spread", "total"}:
        # expect over/under or team names
        return ("over" in s or "under" in s or any(t in s for t in TEAM_SHORT))

    if mtype == "moneyline":
        return any(t in s for t in TEAM_SHORT)

    if mtype in {"player_prop", "player_total"}:
        # likely has player-like text and metric hint
        return any(k in s for k in ["points", "rebounds", "assists", "pra", "threes", "3pt", "over", "under"])

    return False


def main():
    if not INP.exists():
        raise SystemExit(f"Missing {INP}")

    strict = []
    with INP.open() as f:
        for r in csv.DictReader(f):
            mtype = (r.get("market_type") or "").strip()
            sel = (r.get("selection") or "").strip()
            price = (r.get("price") or "").strip()

            if mtype not in ALLOW_MARKETS:
                continue
            if not PRICE_RE.match(price):
                continue
            if not looks_real_selection(sel, mtype):
                continue

            strict.append(r)

    # de-dupe
    dedup = {}
    for r in strict:
        k = (r['event_url'], r['market_type'], r['selection'], r.get('line', ''), r['price'])
        dedup[k] = r
    strict = list(dedup.values())

    with OUT.open('w', newline='') as f:
        fields = ['event_url', 'market_raw', 'market_type', 'selection', 'line', 'price', 'raw_text']
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(strict)

    print(f"Wrote {len(strict)} strict rows -> {OUT}")


if __name__ == '__main__':
    main()
