#!/usr/bin/env python3
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SCORES = ROOT / 'model_scores_v3.csv'
STRAT = ROOT / 'strategy_v3.csv'
OUT = ROOT / 'ticket_v3.csv'


def main():
    rows = list(csv.DictReader(SCORES.open()))
    strat = {r['game']: r for r in csv.DictReader(STRAT.open())}
    games = sorted(strat.keys())

    out = []
    for g in games:
        sr = strat[g]
        singles = [r for r in rows if r['game'] == g and r['kind'] == 'single']
        pales = [r for r in rows if r['game'] == g and r['kind'] == 'pale']

        if sr['strategy'] == 'A_top3_singles':
            pick_s = [r['value'] for r in singles[:3]]
            pick_p = []
        elif sr['strategy'] == 'B_top5_singles':
            pick_s = [r['value'] for r in singles[:5]]
            pick_p = []
        else:
            pick_s = [r['value'] for r in singles[:3]]
            pick_p = [pales[0]['value']] if pales else []

        out.append({
            'game': g,
            'strategy': sr['strategy'],
            'singles': ' '.join(f"{int(x):02d}" for x in pick_s),
            'pales': ', '.join(pick_p),
            'top3_prob_%': round(float(sr['top3_prob']) * 100, 2),
            'top5_prob_%': round(float(sr['top5_prob']) * 100, 2),
            'best_pale_prob_%': round(float(sr['best_pale_prob']) * 100, 2),
        })

    with OUT.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['game', 'strategy', 'singles', 'pales', 'top3_prob_%', 'top5_prob_%', 'best_pale_prob_%'])
        w.writeheader(); w.writerows(out)

    print(f'Wrote {len(out)} rows -> {OUT}')


if __name__ == '__main__':
    main()
