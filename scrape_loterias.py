import csv,re,requests
from datetime import datetime
BASE='https://www.conectate.com.do/loterias/'
GAMES=[
('Gana Mas','nacional/gana-mas'),('Loteria Nacional','nacional/quiniela'),('Quiniela Leidsa','leidsa/quiniela-pale'),('Quiniela Real','loto-real/quiniela'),('Quiniela Loteka','loteka/quiniela-mega-decenas'),('La Primera Dia','la-primera/quiniela-medio-dia'),('La Primera Noche','la-primera/quiniela-noche'),('La Suerte MD','la-suerte-dominicana/quiniela'),('La Suerte 6PM','la-suerte-dominicana/quiniela-tarde'),('Anguila 10:00 AM','anguilla/anguila-10-am'),('Anguila 1:00 PM','anguilla/anguila-12-pm'),('Anguila 6:00 PM','anguilla/anguila-5-pm'),('Anguila 9:00 PM','anguilla/anguila-9-pm')
]

def parse_game(name,path):
    url=BASE+path
    html=requests.get(url,timeout=25).text
    # extract year context from page (today date dd-mm-yyyy)
    m=re.search(r"today:\s*'([0-9]{2}-[0-9]{2}-[0-9]{4})'",html)
    year='2026'
    if m: year=m.group(1).split('-')[-1]
    rows=[]
    blocks=re.findall(r'<div class="game-block[^>]*>(.*?)<div class="game-scores ball-mode">(.*?)</div>',html,re.S)
    for info,scores in blocks:
        dm=re.search(r'session-date[^>]*>\s*([0-9]{2}-[0-9]{2})\s*<',info,re.S)
        if not dm: continue
        date=f"{dm.group(1)}-{year}"
        nums=re.findall(r'<span class="score[^>]*>\s*([+!=?]?\d{1,2})\s*</span>',scores,re.S)
        if not nums:
            nums=re.findall(r'>(\d{1,2})<',scores)
        nums_clean=[n.strip('+=!?') for n in nums if n.strip('+=!?').isdigit()]
        if not nums_clean: continue
        rows.append({
            'game':name,
            'draw_date':date,
            'numbers_drawn':' '.join(nums_clean),
            'extras':'',
            'jackpot':'',
            'source_url':url,
            'notes':'parsed from page history cards'
        })
    return rows

all_rows=[]
for n,p in GAMES:
    try:
        all_rows.extend(parse_game(n,p))
    except Exception as e:
        all_rows.append({'game':n,'draw_date':'','numbers_drawn':'','extras':'','jackpot':'','source_url':BASE+p,'notes':f'error:{e}'})

# dedupe
uniq=[]
seen=set()
for r in all_rows:
    k=(r['game'],r['draw_date'],r['numbers_drawn'])
    if k in seen: continue
    seen.add(k); uniq.append(r)

out='/home/ander/.openclaw/workspace/dominican_lottery_data.csv'
with open(out,'w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=['game','draw_date','numbers_drawn','extras','jackpot','source_url','notes'])
    w.writeheader(); w.writerows(uniq)
print('rows',len(uniq),'->',out)

# predictions top10 by frequency weighted recency (within this extracted set)
from collections import defaultdict,Counter
import math
by_game=defaultdict(list)
for r in uniq:
    try:
        d=datetime.strptime(r['draw_date'],'%d-%m-%Y')
    except: continue
    nums=[int(x) for x in r['numbers_drawn'].split() if x.isdigit()]
    if nums: by_game[r['game']].append((d,nums))

pred=[]
for g,items in by_game.items():
    if not items: continue
    latest=max(d for d,_ in items)
    score=Counter()
    for d,nums in items:
        age=max((latest-d).days,0)
        w=math.exp(-age/180)
        for n in nums: score[n]+=w
    total=sum(score.values()) or 1
    top=score.most_common(10)
    rank=1
    for n,s in top:
        pred.append({'game':g,'rank':rank,'number':n,'probability':round(s/total,6),'raw_score':round(s,4)})
        rank+=1

pout='/home/ander/.openclaw/workspace/dominican_lottery_top10_predictions.csv'
with open(pout,'w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=['game','rank','number','probability','raw_score'])
    w.writeheader(); w.writerows(pred)
print('pred rows',len(pred),'->',pout)
