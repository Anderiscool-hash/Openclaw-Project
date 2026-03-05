#!/usr/bin/env python3
"""
Generate top-10 number probabilities per game from a lottery CSV.

Usage:
  python3 predict_lottery_top10.py \
    --input dominican_lottery_data.csv \
    --output dominican_lottery_top10_predictions.csv
"""
import csv, math, argparse
from collections import defaultdict, Counter
from datetime import datetime


def load_rows(path):
    rows=[]
    with open(path,newline='') as f:
        for r in csv.DictReader(f):
            try:
                d=datetime.strptime(r['draw_date'],'%d-%m-%Y')
            except Exception:
                continue
            nums=[int(x) for x in r.get('numbers_drawn','').split() if x.isdigit()]
            if nums:
                rows.append((r['game'],d,nums))
    return rows


def predict(rows):
    by=defaultdict(list)
    for g,d,nums in rows:
        by[g].append((d,nums))

    out=[]
    for g,items in by.items():
        latest=max(d for d,_ in items)
        score=Counter()
        for d,nums in items:
            age=max((latest-d).days,0)
            w=math.exp(-age/365)
            for n in nums:
                score[n]+=w
        total=sum(score.values()) or 1
        for rank,(n,s) in enumerate(score.most_common(10),1):
            out.append({
                'game':g,
                'rank':rank,
                'number':n,
                'probability':round(s/total,6),
                'raw_score':round(s,4)
            })
    return out


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--input',required=True)
    ap.add_argument('--output',required=True)
    args=ap.parse_args()

    rows=load_rows(args.input)
    pred=predict(rows)
    with open(args.output,'w',newline='') as f:
        w=csv.DictWriter(f,fieldnames=['game','rank','number','probability','raw_score'])
        w.writeheader(); w.writerows(pred)
    print(f'Wrote {len(pred)} prediction rows to {args.output}')

if __name__=='__main__':
    main()
