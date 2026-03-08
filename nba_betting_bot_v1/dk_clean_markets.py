#!/usr/bin/env python3
"""Clean DK deep market rows into structured betting markets.

Input: draftkings_nba_markets_raw.csv
Output: draftkings_nba_markets_clean.csv
"""
import csv
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INP = ROOT / "draftkings_nba_markets_raw.csv"
OUT = ROOT / "draftkings_nba_markets_clean.csv"

BAD_MARKET_HINTS = [
    'bonus', 'crowd', 'popular', 'warm up', 'raising', 'covering', 'up up', 'game parlay',
    'same game parlay', 'sponsored', 'featured', 'most bet', 'people placed', 'boost'
]

GOOD_MARKET_HINTS = [
    'moneyline', 'spread', 'total', 'over', 'under',
    'player points', 'points', 'rebounds', 'assists',
    'threes', '3pt', 'pra', 'double double', 'triple double'
]

ODDS_RE = re.compile(r'([+-]\d{2,4})')
LINE_RE = re.compile(r'(\d+(?:\.\d+)?)')


def classify_market(market: str, selection: str):
    m = (market or '').lower()
    s = (selection or '').lower()
    text = f"{m} {s}"

    if any(b in text for b in BAD_MARKET_HINTS):
        return None

    if 'moneyline' in text or ('ml' in text and 'player' not in text):
        return 'moneyline'
    if 'spread' in text:
        return 'spread'
    if 'total' in text or ('over' in text or 'under' in text):
        # could be game total or player total, keep broad
        if 'player' in text:
            return 'player_total'
        return 'total'

    if 'player' in text and ('points' in text or 'rebounds' in text or 'assists' in text or 'threes' in text or 'pra' in text):
        return 'player_prop'

    # fallback heuristic
    if any(g in text for g in GOOD_MARKET_HINTS):
        return 'other_market'

    return None


def clean_row(r):
    market = (r.get('market') or '').strip()
    selection = (r.get('selection') or '').strip()
    price = (r.get('price') or '').strip()
    url = (r.get('event_url') or '').strip()

    if not ODDS_RE.fullmatch(price):
        return None

    mtype = classify_market(market, selection)
    if not mtype:
        return None

    # line extraction from either dedicated line column or selection text
    line = (r.get('line') or '').strip()
    if not line:
        lm = LINE_RE.search(selection)
        line = lm.group(1) if lm else ''

    return {
        'event_url': url,
        'market_raw': market,
        'market_type': mtype,
        'selection': selection,
        'line': line,
        'price': price,
        'raw_text': (r.get('raw_text') or '')[:220],
    }


def main():
    if not INP.exists():
        raise SystemExit(f"Missing {INP}; run dk_deep_run.sh first")

    cleaned = []
    with INP.open() as f:
        for r in csv.DictReader(f):
            c = clean_row(r)
            if c:
                cleaned.append(c)

    # dedupe
    dedup = {}
    for c in cleaned:
        k = (c['event_url'], c['market_type'], c['selection'], c['line'], c['price'])
        dedup[k] = c
    cleaned = list(dedup.values())

    with OUT.open('w', newline='') as f:
        fields = ['event_url', 'market_raw', 'market_type', 'selection', 'line', 'price', 'raw_text']
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(cleaned)

    print(f"Wrote {len(cleaned)} clean rows -> {OUT}")


if __name__ == '__main__':
    main()
