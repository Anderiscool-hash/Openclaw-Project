#!/usr/bin/env python3
import csv
import os
import time
from pathlib import Path
from datetime import datetime
import requests

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "latest_top10.csv"
OFFSET_FILE = ROOT / "offset.txt"

QUERIES = {
    "sounds": [("song", "tiktok trending songs today"), ("song", "tiktok viral sounds this week")],
    "hashtags": [("hashtag", "tiktok trending hashtags today"), ("hashtag", "best tiktok hashtags for views")],
    "products": [("product", "tiktok made me buy it trending products"), ("product", "viral tiktok shop products today")],
    "trends": [("trend", "tiktok viral trends right now"), ("trend", "tiktok content trends 2026")],
}


def load_env(path: Path):
    if not path.exists():
        return
    for line in path.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith('#') or '=' not in line:
            continue
        k, v = line.split('=', 1)
        os.environ.setdefault(k.strip(), v.strip())


def tg_api(method, token, params=None):
    url = f"https://api.telegram.org/bot{token}/{method}"
    r = requests.get(url, params=params or {}, timeout=60)
    r.raise_for_status()
    return r.json()


def send_message(token, chat_id, text):
    tg_api("sendMessage", token, {"chat_id": chat_id, "text": text[:4000]})


def searx_search(q: str):
    base = os.getenv("SEARXNG_URL", "http://127.0.0.1:8080/search")
    r = requests.get(base, params={"q": q, "format": "json"}, timeout=25)
    r.raise_for_status()
    return r.json().get("results", [])


def collect_top10():
    rows = []
    for kind, qs in QUERIES.items():
        for _, q in qs:
            try:
                results = searx_search(q)
            except Exception:
                continue
            for r in results[:12]:
                title = (r.get("title") or "").strip()
                url = (r.get("url") or "").strip()
                if not title or not url:
                    continue
                score = 50
                low = title.lower()
                if kind == "products" and any(x in low for x in ["buy", "shop", "amazon", "product", "made me"]):
                    score += 30
                if kind == "hashtags" and "#" in low:
                    score += 20
                if kind == "sounds" and any(x in low for x in ["sound", "song", "music"]):
                    score += 20
                if kind == "trends" and any(x in low for x in ["trend", "viral", "challenge"]):
                    score += 15
                rows.append({"type": kind, "title": title[:160], "url": url, "score": score})

    dedup = {}
    for r in rows:
        dedup[(r["type"], r["title"].lower())] = r
    rows = sorted(dedup.values(), key=lambda x: x["score"], reverse=True)

    top_n = int(os.getenv("TOP_N", "10"))
    top = rows[:top_n]
    with DATA.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["rank", "type", "title", "score", "url", "updated_at"])
        w.writeheader()
        for i, r in enumerate(top, 1):
            w.writerow({"rank": i, **r, "updated_at": datetime.now().isoformat(timespec="seconds")})
    return top


def read_latest():
    if not DATA.exists():
        return []
    return list(csv.DictReader(DATA.open()))


def fmt(rows, filter_type=None):
    if filter_type:
        rows = [r for r in rows if r["type"] == filter_type]
    if not rows:
        return "No data yet. Use /refresh first."
    return "\n".join([f"{r['rank']}. [{r['type']}] {r['title']} (score {r['score']})" for r in rows[:10]])


def handle_command(token, chat_id, text):
    cmd = text.strip().split()[0].lower()
    if cmd == '/start':
        send_message(token, chat_id, "TikTok Trends Bot live. Commands: /refresh /top10 /sounds /hashtags /products /trends")
    elif cmd == '/refresh':
        top = collect_top10()
        send_message(token, chat_id, f"Refreshed {len(top)} items. Use /top10")
    elif cmd == '/top10':
        send_message(token, chat_id, fmt(read_latest()))
    elif cmd == '/sounds':
        send_message(token, chat_id, fmt(read_latest(), 'sounds'))
    elif cmd == '/hashtags':
        send_message(token, chat_id, fmt(read_latest(), 'hashtags'))
    elif cmd == '/products':
        send_message(token, chat_id, fmt(read_latest(), 'products'))
    elif cmd == '/trends':
        send_message(token, chat_id, fmt(read_latest(), 'trends'))


def load_offset():
    if OFFSET_FILE.exists():
        try:
            return int(OFFSET_FILE.read_text().strip())
        except Exception:
            return 0
    return 0


def save_offset(v):
    OFFSET_FILE.write_text(str(v))


def main():
    load_env(ROOT / '.env')
    token = os.getenv('TELEGRAM_BOT_TOKEN', '')
    if not token:
        raise SystemExit('Missing TELEGRAM_BOT_TOKEN')

    print('Bot running (polling)...')
    offset = load_offset()
    while True:
        try:
            data = tg_api('getUpdates', token, {'timeout': 30, 'offset': offset + 1})
            if data.get('ok'):
                for upd in data.get('result', []):
                    offset = max(offset, upd['update_id'])
                    msg = upd.get('message') or {}
                    text = msg.get('text', '')
                    chat_id = msg.get('chat', {}).get('id')
                    if text.startswith('/') and chat_id:
                        handle_command(token, chat_id, text)
                save_offset(offset)
        except Exception:
            time.sleep(2)


if __name__ == '__main__':
    main()
