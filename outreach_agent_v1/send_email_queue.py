#!/usr/bin/env python3
import csv
import os
import smtplib
from email.message import EmailMessage

QUEUE='/home/ander/.openclaw/workspace/outreach_agent_v1/outreach_queue.csv'

SMTP_HOST=os.getenv('SMTP_HOST','smtp.gmail.com')
SMTP_PORT=int(os.getenv('SMTP_PORT','587'))
SMTP_USER=os.getenv('SMTP_USER','')
SMTP_PASS=os.getenv('SMTP_PASS','')
FROM_EMAIL=os.getenv('FROM_EMAIL', SMTP_USER)
DRY_RUN=os.getenv('DRY_RUN','1')=='1'
MAX_SEND=int(os.getenv('MAX_SEND','20'))


def main():
    if not os.path.exists(QUEUE):
        print('queue missing'); return

    rows=[]
    with open(QUEUE,'r',encoding='utf-8') as f:
        rows=list(csv.DictReader(f))

    sent=0
    server=None
    if not DRY_RUN:
        if not (SMTP_USER and SMTP_PASS and FROM_EMAIL):
            raise SystemExit('Missing SMTP env vars')
        server=smtplib.SMTP(SMTP_HOST,SMTP_PORT)
        server.starttls(); server.login(SMTP_USER,SMTP_PASS)

    for r in rows:
        if sent>=MAX_SEND: break
        if r.get('status')!='draft' or r.get('channel')!='email' or not r.get('email_to'):
            continue

        if DRY_RUN:
            r['status']='approved_pending_send'
            sent+=1
            continue

        msg=EmailMessage()
        msg['From']=FROM_EMAIL
        msg['To']=r['email_to']
        msg['Subject']=r['subject']
        msg.set_content(r['body'])
        server.send_message(msg)
        r['status']='sent'
        sent+=1

    if server:
        server.quit()

    with open(QUEUE,'w',newline='',encoding='utf-8') as f:
        w=csv.DictWriter(f,fieldnames=rows[0].keys())
        w.writeheader(); w.writerows(rows)

    print(f'processed={sent} dry_run={DRY_RUN}')

if __name__=='__main__':
    main()
