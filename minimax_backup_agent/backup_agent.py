#!/usr/bin/env python3
import os
import requests
import sys
from pathlib import Path


def load_env(path: Path):
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line=line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        k,v=line.split('=',1)
        os.environ.setdefault(k.strip(), v.strip())


def call_minimax(prompt: str):
    key=os.getenv('MINIMAX_API_KEY','')
    if not key:
        raise RuntimeError('Missing MINIMAX_API_KEY')
    base=os.getenv('MINIMAX_BASE_URL','https://api.minimax.chat').rstrip('/')
    model=os.getenv('MINIMAX_MODEL','MiniMax-Text-01')

    url=f"{base}/v1/text/chatcompletion_v2"
    payload={
        'model': model,
        'messages': [
            {'role':'system','content':'You are the backup agent. Be concise and practical.'},
            {'role':'user','content': prompt}
        ]
    }
    headers={
        'Authorization': f'Bearer {key}',
        'Content-Type': 'application/json'
    }
    r=requests.post(url, json=payload, headers=headers, timeout=60)
    r.raise_for_status()
    return r.json()


def main():
    load_env(Path(__file__).resolve().parent / '.env')
    prompt=' '.join(sys.argv[1:]).strip() or 'Health check: reply with backup agent online.'
    out=call_minimax(prompt)
    print(out)

if __name__=='__main__':
    main()
