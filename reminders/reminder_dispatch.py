#!/usr/bin/env python3
import json, os
from datetime import datetime
from pathlib import Path
import requests

ROOT = Path('/home/ander/.openclaw/workspace/reminders')
DB = ROOT / 'reminders.json'
WEBHOOK = os.getenv('DISCORD_WEBHOOK_URL','').strip()

if not WEBHOOK:
    # fallback to known env file from nba bot
    envp = Path('/home/ander/.openclaw/workspace/nba_betting_bot_v1/.env')
    if envp.exists():
        for line in envp.read_text().splitlines():
            if line.startswith('DISCORD_WEBHOOK_URL='):
                WEBHOOK=line.split('=',1)[1].strip()

if not DB.exists() or not WEBHOOK:
    raise SystemExit(0)

items = json.loads(DB.read_text())
now = datetime.now().astimezone()
changed = False
for it in items:
    if it.get('sent'):
        continue
    due = datetime.fromisoformat(it['due'])
    if now >= due:
        try:
            requests.post(WEBHOOK, json={'content': it['text'][:1900]}, timeout=15).raise_for_status()
            it['sent'] = True
            changed = True
        except Exception:
            pass

if changed:
    DB.write_text(json.dumps(items, indent=2))
