#!/usr/bin/env python3
import csv
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INP = ROOT / 'nba_picks_today.csv'
OUT2 = ROOT / 'parlays_2leg.csv'
OUT3 = ROOT / 'parlays_3leg.csv'


def to_decimal(american):
    a = float(american)
    if a > 0:
        return 1 + (a / 100.0)
    return 1 + (100.0 / abs(a))


def to_american(decimal_odds):
    if decimal_odds >= 2:
        return round((decimal_odds - 1) * 100)
    return round(-100 / (decimal_odds - 1))


def load_picks():
    rows = list(csv.DictReader(INP.open())) if INP.exists() else []
    # only keep strongest side per matchup+market to avoid opposite-side collisions
    best = {}
    for r in rows:
        key = (r['matchup'], r['market'])
        edge = float(r.get('edge_pct') or 0)
        if key not in best or edge > float(best[key].get('edge_pct') or 0):
            best[key] = r
    return list(best.values())


def build(rows, legs=2):
    # prefer unique matchups in a parlay
    out = []
    for combo in combinations(rows, legs):
        matchups = [c['matchup'] for c in combo]
        if len(set(matchups)) < legs:
            continue
        dec = 1.0
        edge_sum = 0.0
        for c in combo:
            dec *= to_decimal(float(c['price']))
            edge_sum += float(c.get('edge_pct') or 0)
        out.append({
            'legs': legs,
            'bets': ' | '.join([f"{c['matchup']}:{c['market']}:{c['selection']} {c.get('point','')} @{c['price']}" for c in combo]),
            'combined_decimal_odds': round(dec, 3),
            'combined_american_odds': to_american(dec),
            'combined_edge_pct': round(edge_sum, 3),
        })
    out.sort(key=lambda r: r['combined_edge_pct'], reverse=True)
    return out


def save(path, rows):
    with path.open('w', newline='') as f:
        fields = ['legs', 'bets', 'combined_decimal_odds', 'combined_american_odds', 'combined_edge_pct']
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader(); w.writerows(rows)


def main():
    picks = load_picks()
    p2 = build(picks, legs=2)
    p3 = build(picks, legs=3)
    save(OUT2, p2)
    save(OUT3, p3)
    print(f'Wrote {len(p2)} 2-leg parlays -> {OUT2}')
    print(f'Wrote {len(p3)} 3-leg parlays -> {OUT3}')


if __name__ == '__main__':
    main()
