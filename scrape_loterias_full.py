import csv,re,requests,time
from datetime import datetime,timedelta
from collections import defaultdict,Counter
import math
BASE='https://www.conectate.com.do/loterias/'
GAMES=[
('Gana Mas','nacional/gana-mas'),('Loteria Nacional','nacional/quiniela'),('Quiniela Leidsa','leidsa/quiniela-pale'),('Quiniela Real','loto-real/quiniela'),('Quiniela Loteka','loteka/quiniela-mega-decenas'),('La Primera Dia','la-primera/quiniela-medio-dia'),('La Primera Noche','la-primera/quiniela-noche'),('La Suerte MD','la-suerte-dominicana/quiniela'),('La Suerte 6PM','la-suerte-dominicana/quiniela-tarde'),('Anguila 10:00 AM','anguilla/anguila-10-am'),('Anguila 1:00 PM','anguilla/anguila-12-pm'),('Anguila 6:00 PM','anguilla/anguila-5-pm'),('Anguila 9:00 PM','anguilla/anguila-9-pm')
]
TARGET_MIN_DATE=datetime(2023,1,1)

def parse_page(html,name,url):
    # year from page today var
    m=re.search(r"today:\s*'([0-9]{2}-[0-9]{2}-[0-9]{4})'",html)
    current_year=int(m.group(1).split('-')[-1]) if m else datetime.now().year
    rows=[]
    blocks=re.findall(r'<div class="game-block[^>]*>(.*?)<div class="game-scores ball-mode">(.*?)</div>',html,re.S)
    last_date=None
    prev_md=None
    y=current_year
    for info,scores in blocks:
        dm=re.search(r'session-date[^>]*>\s*([0-9]{2}-[0-9]{2})\s*<',info,re.S)
        if not dm:
            continue
        md=dm.group(1)
        # adjust year rollover
        if prev_md:
            pday,pmon=map(int,prev_md.split('-'))
            day,mon=map(int,md.split('-'))
            if (mon,pday) < (pmon,day):
                pass
            # if month jumps upward while going down list, crossed year boundary
            if mon > pmon:
                y -= 1
        prev_md=md
        d=datetime.strptime(f"{md}-{y}",'%d-%m-%Y')
        last_date=d
        nums=re.findall(r'<span class="score[^>]*>\s*([+!=?]?\d{1,2})\s*</span>',scores,re.S)
        nums=[n.strip('+=!?') for n in nums if n.strip('+=!?').isdigit()]
        if not nums:
            nums=re.findall(r'>(\d{1,2})<',scores)
        if not nums:
            continue
        rows.append({'game':name,'draw_date':d.strftime('%d-%m-%Y'),'numbers_drawn':' '.join(nums),'extras':'','jackpot':'','source_url':url,'notes':'parsed html history'})
    return rows,last_date

all_rows=[]
for name,path in GAMES:
    qdate=None
    seen_dates=set()
    stagnant=0
    for i in range(80):
        url=BASE+path + (f"?date={qdate}" if qdate else '')
        try:
            html=requests.get(url,timeout=25).text
        except Exception:
            break
        rows,last_date=parse_page(html,name,url)
        newc=0
        for r in rows:
            k=(r['game'],r['draw_date'],r['numbers_drawn'])
            if k in seen_dates: 
                continue
            seen_dates.add(k); all_rows.append(r); newc+=1
        if last_date is None:
            break
        if newc==0: stagnant+=1
        else: stagnant=0
        if stagnant>=3: break
        if last_date < TARGET_MIN_DATE: break
        qdate=(last_date - timedelta(days=1)).strftime('%d-%m-%Y')
        time.sleep(0.08)

# dedupe
uniq=[]; seen=set()
for r in all_rows:
    k=(r['game'],r['draw_date'],r['numbers_drawn'])
    if k in seen: continue
    seen.add(k); uniq.append(r)

# sort
uniq.sort(key=lambda r:(r['game'], datetime.strptime(r['draw_date'],'%d-%m-%Y')), reverse=True)

out='/home/ander/.openclaw/workspace/dominican_lottery_data.csv'
with open(out,'w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=['game','draw_date','numbers_drawn','extras','jackpot','source_url','notes'])
    w.writeheader(); w.writerows(uniq)

# predictions
by=defaultdict(list)
for r in uniq:
    try:d=datetime.strptime(r['draw_date'],'%d-%m-%Y')
    except:continue
    nums=[int(x) for x in r['numbers_drawn'].split() if x.isdigit()]
    if nums: by[r['game']].append((d,nums))
pred=[]
for g,items in by.items():
    latest=max(d for d,_ in items)
    score=Counter()
    for d,nums in items:
        age=max((latest-d).days,0)
        w=math.exp(-age/365)
        for n in nums: score[n]+=w
    total=sum(score.values()) or 1
    for rank,(n,s) in enumerate(score.most_common(10),1):
        pred.append({'game':g,'rank':rank,'number':n,'probability':round(s/total,6),'raw_score':round(s,4)})
pout='/home/ander/.openclaw/workspace/dominican_lottery_top10_predictions.csv'
with open(pout,'w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=['game','rank','number','probability','raw_score'])
    w.writeheader(); w.writerows(pred)

print('rows',len(uniq),'pred',len(pred))
print('games',len(by))
for g in sorted(by):
    ds=[d for d,_ in by[g]]
    print(g,len(ds),min(ds).strftime('%Y-%m-%d'),max(ds).strftime('%Y-%m-%d'))
