#!/usr/bin/env python3
import csv, math
from collections import defaultdict, Counter
from datetime import datetime
from itertools import combinations
from pathlib import Path

ROOT = Path(__file__).resolve().parent
DATA = Path('/home/ander/.openclaw/workspace/dominican_lottery_data.csv')
OUT = ROOT / 'model_scores_v3.csv'


def load_history():
    by = defaultdict(list)
    with DATA.open() as f:
        for r in csv.DictReader(f):
            try:
                d = datetime.strptime(r['draw_date'], '%d-%m-%Y')
            except Exception:
                continue
            nums = [int(x) for x in r['numbers_drawn'].split() if x.isdigit()]
            if len(nums) >= 3:
                by[r['game']].append((d, nums))
    for g in by:
        by[g].sort(key=lambda x: x[0])
    return by


def score_game(items, decay_days=365):
    latest = max(d for d, _ in items)
    single = Counter()
    first = Counter()
    second = Counter()
    third = Counter()
    pair = Counter()

    for d, nums in items:
        w = math.exp(-max((latest - d).days, 0) / decay_days)
        single[nums[0]] += w
        if len(nums) > 1:
            single[nums[1]] += w
            second[nums[1]] += w
        if len(nums) > 2:
            single[nums[2]] += w
            third[nums[2]] += w
        first[nums[0]] += w
        for a, b in combinations(sorted(set(nums)), 2):
            pair[(a, b)] += w

    return single, first, second, third, pair


def main():
    by = load_history()
    rows = []

    for game, items in by.items():
        if len(items) < 40:
            continue

        single, first, second, third, pair = score_game(items, decay_days=365)
        st = sum(single.values()) or 1
        p1 = sum(first.values()) or 1
        p2 = sum(second.values()) or 1
        p3 = sum(third.values()) or 1
        pt = sum(pair.values()) or 1

        top_s = single.most_common(10)
        top_p = pair.most_common(10)

        for rank, (n, s) in enumerate(top_s, 1):
            rows.append({
                'game': game,
                'kind': 'single',
                'rank': rank,
                'value': str(n),
                'prob': round(s / st, 6),
                'p_first': round(first[n] / p1, 6),
                'p_second': round(second[n] / p2, 6),
                'p_third': round(third[n] / p3, 6),
            })

        for rank, ((a, b), s) in enumerate(top_p, 1):
            rows.append({
                'game': game,
                'kind': 'pale',
                'rank': rank,
                'value': f'{a:02d}-{b:02d}',
                'prob': round(s / pt, 6),
                'p_first': '',
                'p_second': '',
                'p_third': '',
            })

    with OUT.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['game', 'kind', 'rank', 'value', 'prob', 'p_first', 'p_second', 'p_third'])
        w.writeheader()
        w.writerows(rows)

    print(f'Wrote {len(rows)} rows -> {OUT}')


if __name__ == '__main__':
    main()
