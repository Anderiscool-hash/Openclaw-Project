#!/usr/bin/env python3
import csv
from datetime import datetime

LEADS = '/home/ander/.openclaw/workspace/outreach_agent_v1/leads_50.csv'
OUT = '/home/ander/.openclaw/workspace/outreach_agent_v1/outreach_queue.csv'


def main():
    rows=[]
    with open(LEADS,'r',encoding='utf-8') as f:
      for r in csv.DictReader(f):
        owner='team'
        subj=f"quick growth idea for {r['business_name']}"
        body=(
          f"Hi {owner},\\n\\n"
          f"I’m local and I put together quick AI-powered growth audits for neighborhood businesses. "
          f"I checked {r['business_name']} and I can send a short report with practical fixes "
          f"(SEO + visibility + conversion ideas) you can use right away.\\n\\n"
          f"If you want, I’ll send a free 3-point preview first.\\n\\n"
          f"— Ander\\n"
          f"ayalaander323@gmail.com"
        )
        rows.append({
          'created_at': datetime.now().isoformat(),
          'business_name': r['business_name'],
          'email_to': r.get('email',''),
          'subject': subj,
          'body': body,
          'status': 'draft',
          'channel': 'email' if r.get('email') else 'manual_dm',
          'website': r.get('website',''),
          'phone': r.get('phone','')
        })

    with open(OUT,'w',newline='',encoding='utf-8') as f:
      w=csv.DictWriter(f,fieldnames=list(rows[0].keys()))
      w.writeheader(); w.writerows(rows)
    print(f'wrote {OUT} rows={len(rows)}')

if __name__=='__main__':
  main()
