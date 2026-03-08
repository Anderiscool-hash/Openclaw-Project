#!/usr/bin/env python3
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
INP = ROOT / 'model_scores_v3.csv'
OUT = ROOT / 'strategy_v3.csv'


def main():
    rows = list(csv.DictReader(INP.open()))
    games = sorted(set(r['game'] for r in rows))
    out = []

    for g in games:
        s = [r for r in rows if r['game'] == g and r['kind'] == 'single']
        p = [r for r in rows if r['game'] == g and r['kind'] == 'pale']

        top3_sum = sum(float(r['prob']) for r in s[:3])
        top5_sum = sum(float(r['prob']) for r in s[:5])
        best_pale = float(p[0]['prob']) if p else 0.0

        # simple selector: prefer top3 singles by default; allow 1 pale only if strong
        strategy = 'A_top3_singles'
        if best_pale >= 0.01 and top3_sum >= 0.08:
            strategy = 'C_top3_plus_1_pale'
        elif top5_sum - top3_sum > 0.03:
            strategy = 'B_top5_singles'

        out.append({
            'game': g,
            'strategy': strategy,
            'top3_prob': round(top3_sum, 6),
            'top5_prob': round(top5_sum, 6),
            'best_pale_prob': round(best_pale, 6),
        })

    with OUT.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['game', 'strategy', 'top3_prob', 'top5_prob', 'best_pale_prob'])
        w.writeheader(); w.writerows(out)

    print(f'Wrote {len(out)} rows -> {OUT}')


if __name__ == '__main__':
    main()
