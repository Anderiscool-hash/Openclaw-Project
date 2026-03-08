#!/usr/bin/env python3
import csv, os
from pathlib import Path

ROOT = Path(__file__).resolve().parent
MODELED = ROOT / 'modeled_edges.csv'
OUT = ROOT / 'nba_picks_today.csv'
TXT = ROOT / 'nba_picks_today.txt'


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
    if not MODELED.exists():
        raise SystemExit('Missing modeled_edges.csv; run nba_model.py first')

    max_bets = int(float(os.getenv('MAX_BETS', '10')))
    min_edge = float(os.getenv('MIN_EDGE_PCT', '2.0'))
    bankroll = float(os.getenv('BANKROLL', '1000'))
    profile = os.getenv('RISK_PROFILE', 'medium').lower()

    mult = 0.25 if profile == 'conservative' else (0.75 if profile == 'aggressive' else 0.5)

    rows = list(csv.DictReader(MODELED.open()))
    rows = [r for r in rows if float(r.get('edge_pct') or 0) >= min_edge]
    rows.sort(key=lambda r: float(r['edge_pct']), reverse=True)
    picks = rows[:max_bets]

    for p in picks:
        kelly = float(p.get('kelly_frac') or 0)
        stake = bankroll * kelly * mult
        p['stake_$'] = round(max(0, stake), 2)

    fields = ['commence_time', 'matchup', 'bookmaker', 'market', 'selection', 'point', 'price', 'edge_pct', 'kelly_frac', 'stake_$']
    with OUT.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        for p in picks:
            w.writerow({k: p.get(k, '') for k in fields})

    lines = ['NBA v1 Picks', '']
    for i, p in enumerate(picks, 1):
        lines.append(f"{i}. {p['matchup']} | {p['market']} {p['selection']} {p.get('point','')} @ {p['price']} | edge {p['edge_pct']}% | stake ${p['stake_$']}")
    TXT.write_text('\n'.join(lines))

    print(f'Wrote picks -> {OUT} and {TXT} (count={len(picks)})')


if __name__ == '__main__':
    main()
