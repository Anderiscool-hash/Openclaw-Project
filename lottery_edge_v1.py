#!/usr/bin/env python3
import argparse
import csv
import math
import re
import requests
from collections import Counter, defaultdict
from datetime import datetime
from itertools import combinations
from pathlib import Path

BASE = 'https://www.conectate.com.do/loterias/'
GAMES = [
    ('Gana Mas', 'nacional/gana-mas', 'Tarde'),
    ('Loteria Nacional', 'nacional/quiniela', 'Noche'),
    ('Quiniela Leidsa', 'leidsa/quiniela-pale', 'Noche'),
    ('Quiniela Real', 'loto-real/quiniela', 'Noche'),
    ('Quiniela Loteka', 'loteka/quiniela-mega-decenas', 'Noche'),
    ('La Primera Dia', 'la-primera/quiniela-medio-dia', 'Mediodia'),
    ('La Primera Noche', 'la-primera/quiniela-noche', 'Noche'),
    ('La Suerte MD', 'la-suerte-dominicana/quiniela', 'Mediodia'),
    ('La Suerte 6PM', 'la-suerte-dominicana/quiniela-tarde', '6:00 PM'),
    ('Anguila 10:00 AM', 'anguilla/anguila-10-am', '10:00 AM'),
    ('Anguila 1:00 PM', 'anguilla/anguila-12-pm', '1:00 PM'),
    ('Anguila 6:00 PM', 'anguilla/anguila-5-pm', '6:00 PM'),
    ('Anguila 9:00 PM', 'anguilla/anguila-9-pm', '9:00 PM'),
]

FIELDS = ['game', 'draw_date', 'numbers_drawn', 'extras', 'jackpot', 'source_url', 'notes']


def ensure_csv(path: Path):
    if path.exists():
        return
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()


def parse_top_block(html: str):
    m = re.search(r'<div class="game-block[^>]*>(.*?)<div class="game-scores ball-mode">(.*?)</div>', html, re.S)
    if not m:
        return None, None
    info, scores = m.groups()
    dm = re.search(r'session-date[^>]*>\s*([0-9]{2}-[0-9]{2})\s*<', info, re.S)
    if not dm:
        return None, None
    ym = re.search(r"today:\s*'([0-9]{2}-[0-9]{2}-[0-9]{4})'", html)
    year = ym.group(1).split('-')[-1] if ym else str(datetime.now().year)
    draw_date = f"{dm.group(1)}-{year}"
    nums = [x.strip('+=!?') for x in re.findall(r'<span class="score[^>]*>\s*([+!=?]?\d{1,2})\s*</span>', scores, re.S)]
    nums = [x for x in nums if x.isdigit()]
    if not nums:
        return None, None
    return draw_date, ' '.join(nums)


def refresh_data(data_csv: Path):
    ensure_csv(data_csv)
    rows = []
    with data_csv.open() as f:
        rows = list(csv.DictReader(f))

    seen = {(r['game'], r['draw_date'], r['numbers_drawn']) for r in rows}
    added = 0
    for game, path, _ in GAMES:
        url = BASE + path
        html = requests.get(url, timeout=20).text
        draw_date, numbers = parse_top_block(html)
        if not draw_date:
            continue
        key = (game, draw_date, numbers)
        if key in seen:
            continue
        rows.append({
            'game': game,
            'draw_date': draw_date,
            'numbers_drawn': numbers,
            'extras': '',
            'jackpot': '',
            'source_url': url,
            'notes': 'v1 refresh top block'
        })
        seen.add(key)
        added += 1

    with data_csv.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=FIELDS)
        w.writeheader()
        w.writerows(rows)

    return added, len(rows)


def load_history(data_csv: Path):
    hist = defaultdict(list)
    with data_csv.open() as f:
        for r in csv.DictReader(f):
            try:
                d = datetime.strptime(r['draw_date'], '%d-%m-%Y')
            except Exception:
                continue
            nums = [int(x) for x in r['numbers_drawn'].split() if x.isdigit()]
            if nums:
                hist[r['game']].append((d, nums))
    return hist


def build_predictions(data_csv: Path, out_csv: Path, top_singles=5, top_pales=3):
    hist = load_history(data_csv)
    out_rows = []

    for game, _, draw_time in GAMES:
        items = hist.get(game, [])
        if not items:
            continue
        latest = max(d for d, _ in items)

        single = Counter()
        pair = Counter()

        for d, nums in items:
            age = max((latest - d).days, 0)
            w = math.exp(-age / 365)
            for n in nums:
                single[n] += w
            for a, b in combinations(sorted(set(nums)), 2):
                pair[(a, b)] += w

        single_total = sum(single.values()) or 1
        pair_total = sum(pair.values()) or 1

        top_s = single.most_common(top_singles)
        top_p = pair.most_common(top_pales)

        top1 = top_s[0][1] / single_total if top_s else 0
        top5 = sum(s for _, s in top_s) / single_total if top_s else 0
        best_pair_p = top_p[0][1] / pair_total if top_p else 0
        edge_score = (top5 * 0.7) + (best_pair_p * 0.3)

        out_rows.append({
            'game': game,
            'draw_time': draw_time,
            'top_singles': ' '.join(f"{n:02d}" for n, _ in top_s),
            'top_singles_prob_%': f"{top5*100:.2f}",
            'best_single_prob_%': f"{top1*100:.2f}",
            'top_pales': ', '.join(f"{a:02d}-{b:02d}" for (a, b), _ in top_p),
            'best_pale_prob_%': f"{best_pair_p*100:.2f}",
            'edge_score_%': f"{edge_score*100:.2f}",
        })

    with out_csv.open('w', newline='') as f:
        fields = ['game', 'draw_time', 'top_singles', 'top_singles_prob_%', 'best_single_prob_%', 'top_pales', 'best_pale_prob_%', 'edge_score_%']
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(out_rows)

    return out_rows


def score_today(pred_csv: Path, score_csv: Path, date_str=None):
    if date_str is None:
        date_str = datetime.now().strftime('%d-%m-%Y')
    md = date_str[:5]

    pred = {}
    with pred_csv.open() as f:
        for r in csv.DictReader(f):
            singles = [int(x) for x in r['top_singles'].split() if x.isdigit()]
            pales = []
            for p in r['top_pales'].split(','):
                p = p.strip()
                if '-' in p:
                    a, b = p.split('-')
                    if a.isdigit() and b.isdigit():
                        pales.append((int(a), int(b)))
            pred[r['game']] = {'singles': singles, 'pales': pales, 'draw_time': r['draw_time']}

    rows = []
    s_hits = p_hits = total = 0

    for game, path, draw_time in GAMES:
        url = BASE + path
        html = requests.get(url, timeout=20).text
        draw_date, numbers = parse_top_block(html)
        if not draw_date or not numbers or not draw_date.startswith(md):
            continue
        nums = [int(x) for x in numbers.split() if x.isdigit()]
        ticket = pred.get(game, {'singles': [], 'pales': []})
        single_hits = sorted(set(nums).intersection(ticket['singles']))
        result_pairs = set(combinations(sorted(set(nums)), 2))
        pale_hits = [p for p in ticket['pales'] if p in result_pairs]

        s_hit = 1 if single_hits else 0
        p_hit = 1 if pale_hits else 0
        s_hits += s_hit
        p_hits += p_hit
        total += 1

        rows.append({
            'game': game,
            'draw_time': draw_time,
            'draw_date': draw_date,
            'result': ' '.join(f"{n:02d}" for n in nums),
            'single_hits': ' '.join(f"{n:02d}" for n in single_hits),
            'pale_hits': ', '.join(f"{a:02d}-{b:02d}" for a, b in pale_hits),
            'single_status': 'HIT' if s_hit else 'MISS',
            'pale_status': 'HIT' if p_hit else 'MISS',
        })

    with score_csv.open('w', newline='') as f:
        fields = ['game', 'draw_time', 'draw_date', 'result', 'single_hits', 'pale_hits', 'single_status', 'pale_status']
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    return {
        'games_scored': total,
        'single_hits': s_hits,
        'pale_hits': p_hits,
        'single_rate_%': round((s_hits / total * 100), 2) if total else 0,
        'pale_rate_%': round((p_hits / total * 100), 2) if total else 0,
        'combined_rate_%': round(((s_hits + p_hits) / (2 * total) * 100), 2) if total else 0,
    }


def main():
    ap = argparse.ArgumentParser(description='Lottery Edge v1 agent runner')
    ap.add_argument('--data', default='dominican_lottery_data.csv')
    ap.add_argument('--pred', default='lottery_edge_predictions_v1.csv')
    ap.add_argument('--score', default='lottery_edge_score_today_v1.csv')
    ap.add_argument('--date', default=None, help='dd-mm-yyyy for scoring (default today)')
    ap.add_argument('command', choices=['refresh', 'predict', 'score', 'run'])
    args = ap.parse_args()

    data_csv = Path(args.data)
    pred_csv = Path(args.pred)
    score_csv = Path(args.score)

    if args.command in ('refresh', 'run'):
        added, total = refresh_data(data_csv)
        print(f'[refresh] added={added} total_rows={total}')

    if args.command in ('predict', 'run'):
        rows = build_predictions(data_csv, pred_csv)
        best = sorted(rows, key=lambda r: float(r['edge_score_%']), reverse=True)[:3]
        print(f'[predict] games={len(rows)} wrote={pred_csv}')
        for b in best:
            print(f"  best: {b['game']} edge={b['edge_score_%']}% singles={b['top_singles']} pales={b['top_pales']}")

    if args.command in ('score', 'run'):
        stats = score_today(pred_csv, score_csv, args.date)
        print(f"[score] wrote={score_csv} stats={stats}")


if __name__ == '__main__':
    main()
