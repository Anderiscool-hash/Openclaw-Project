#!/usr/bin/env python3
import json, math, os, csv
from pathlib import Path
from datetime import datetime

ROOT = Path(__file__).resolve().parent
RAW = ROOT / 'odds_raw.json'
MODELED = ROOT / 'modeled_edges.csv'


def implied_prob_american(odds):
    try:
        odds = float(odds)
    except Exception:
        return None
    if odds > 0:
        return 100.0 / (odds + 100.0)
    return (-odds) / ((-odds) + 100.0)


def estimate_fair_prob(market_outcomes):
    probs = []
    for o in market_outcomes:
        p = implied_prob_american(o.get('price'))
        if p is not None:
            probs.append((o, p))
    s = sum(p for _, p in probs)
    if s <= 0:
        return []
    # remove vig by normalization
    return [(o, p / s) for o, p in probs]


def kelly_fraction(edge, odds_american):
    # simple fractional Kelly basis
    o = float(odds_american)
    b = (o / 100.0) if o > 0 else (100.0 / (-o))
    if b <= 0:
        return 0.0
    p = edge['our_prob']
    q = 1 - p
    f = (b * p - q) / b
    return max(0.0, f)


def load_env():
    env = ROOT / '.env'
    if env.exists():
        for line in env.read_text().splitlines():
            if not line or line.startswith('#') or '=' not in line:
                continue
            k, v = line.split('=', 1)
            os.environ.setdefault(k.strip(), v.strip())


def main():
    load_env()
    if not RAW.exists():
        raise SystemExit('Missing odds_raw.json, run nba_collect.py first')

    data = json.loads(RAW.read_text())
    rows = []

    for event in data:
        home = event.get('home_team', '')
        away = event.get('away_team', '')
        commence = event.get('commence_time', '')

        for book in event.get('bookmakers', []):
            book_key = book.get('key', '')
            for market in book.get('markets', []):
                mkey = market.get('key', '')
                fair = estimate_fair_prob(market.get('outcomes', []))
                for o, fair_prob in fair:
                    price = o.get('price')
                    implied = implied_prob_american(price)
                    if implied is None:
                        continue

                    # naive edge: fair_prob - implied_prob
                    edge = fair_prob - implied
                    rows.append({
                        'commence_time': commence,
                        'matchup': f"{away} @ {home}",
                        'bookmaker': book_key,
                        'market': mkey,
                        'selection': o.get('name', ''),
                        'point': o.get('point', ''),
                        'price': price,
                        'implied_prob': round(implied * 100, 3),
                        'our_prob': round(fair_prob * 100, 3),
                        'edge_pct': round(edge * 100, 3),
                        'kelly_frac': round(kelly_fraction({'our_prob': fair_prob}, price), 4),
                    })

    with MODELED.open('w', newline='') as f:
        fields = ['commence_time', 'matchup', 'bookmaker', 'market', 'selection', 'point', 'price', 'implied_prob', 'our_prob', 'edge_pct', 'kelly_frac']
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(rows)

    print(f'Wrote modeled edges -> {MODELED} ({len(rows)} rows)')


if __name__ == '__main__':
    main()
