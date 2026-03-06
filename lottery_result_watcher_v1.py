#!/usr/bin/env python3
import csv, json, re, requests
from datetime import datetime
from itertools import combinations
from pathlib import Path

BASE='https://www.conectate.com.do/loterias/'
GAMES=[
 ('Gana Mas','nacional/gana-mas','Tarde'),('Loteria Nacional','nacional/quiniela','Noche'),('Quiniela Leidsa','leidsa/quiniela-pale','Noche'),('Quiniela Real','loto-real/quiniela','Noche'),('Quiniela Loteka','loteka/quiniela-mega-decenas','Noche'),('La Primera Dia','la-primera/quiniela-medio-dia','Mediodia'),('La Primera Noche','la-primera/quiniela-noche','Noche'),('La Suerte MD','la-suerte-dominicana/quiniela','Mediodia'),('La Suerte 6PM','la-suerte-dominicana/quiniela-tarde','6:00 PM'),('Anguila 10:00 AM','anguilla/anguila-10-am','10:00 AM'),('Anguila 1:00 PM','anguilla/anguila-12-pm','1:00 PM'),('Anguila 6:00 PM','anguilla/anguila-5-pm','6:00 PM'),('Anguila 9:00 PM','anguilla/anguila-9-pm','9:00 PM')
]
ROOT=Path('/home/ander/.openclaw/workspace')
PRED=ROOT/'lottery_edge_predictions_v1.csv'
STATE=ROOT/'lottery_result_state.json'
OUT=ROOT/'lottery_new_results.csv'


def parse_top(html):
    m=re.search(r'<div class="game-block[^>]*>(.*?)<div class="game-scores ball-mode">(.*?)</div>',html,re.S)
    if not m: return None,None
    info,scores=m.groups()
    dm=re.search(r'session-date[^>]*>\s*([0-9]{2}-[0-9]{2})\s*<',info,re.S)
    ym=re.search(r"today:\s*'([0-9]{2}-[0-9]{2}-[0-9]{4})'",html)
    if not dm or not ym: return None,None
    draw_date=f"{dm.group(1)}-{ym.group(1).split('-')[-1]}"
    nums=[x.strip('+=!?') for x in re.findall(r'<span class="score[^>]*>\s*([+!=?]?\d{1,2})\s*</span>',scores,re.S)]
    nums=[int(x) for x in nums if x.isdigit()]
    if not nums: return None,None
    return draw_date, nums

pred={}
if PRED.exists():
    with PRED.open() as f:
        for r in csv.DictReader(f):
            singles=[int(x) for x in r['top_singles'].split() if x.isdigit()]
            pales=[]
            for p in r['top_pales'].split(','):
                p=p.strip()
                if '-' in p:
                    a,b=p.split('-')
                    if a.isdigit() and b.isdigit(): pales.append((int(a),int(b)))
            pred[r['game']]={'singles':singles,'pales':pales}

state={}
if STATE.exists():
    state=json.loads(STATE.read_text())

new_rows=[]
for g,path,time_lbl in GAMES:
    html=requests.get(BASE+path,timeout=20).text
    draw_date,nums=parse_top(html)
    if not draw_date: continue
    key=f"{draw_date}|{'-'.join(f'{n:02d}' for n in nums)}"
    if state.get(g)==key:
        continue
    state[g]=key
    p=pred.get(g,{'singles':[],'pales':[]})
    s_hits=sorted(set(nums).intersection(p['singles']))
    rp=set(combinations(sorted(set(nums)),2))
    p_hits=[ab for ab in p['pales'] if ab in rp]
    new_rows.append({
      'timestamp':datetime.now().isoformat(timespec='seconds'),
      'game':g,'draw_time':time_lbl,'draw_date':draw_date,
      'result':' '.join(f'{n:02d}' for n in nums),
      'single_hits':' '.join(f'{n:02d}' for n in s_hits),
      'pale_hits':', '.join(f'{a:02d}-{b:02d}' for a,b in p_hits),
      'single_status':'HIT' if s_hits else 'MISS',
      'pale_status':'HIT' if p_hits else 'MISS'
    })

STATE.write_text(json.dumps(state,indent=2))
if new_rows:
    write_header=not OUT.exists()
    with OUT.open('a',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(new_rows[0].keys()))
        if write_header: w.writeheader()
        w.writerows(new_rows)
    for r in new_rows:
        print(f"NEW {r['game']} {r['draw_date']} res={r['result']} single={r['single_status']} pale={r['pale_status']}")
else:
    print('NO_NEW_RESULTS')
