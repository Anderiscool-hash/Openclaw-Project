#!/usr/bin/env python3
import json
import os
import time
from pathlib import Path
import requests

ROOT = Path(__file__).resolve().parent
STATE_FILE = ROOT / "live_stats_state.json"
CACHE_FILE = ROOT / "live_stats_last_sent.json"


def load_env():
    env = ROOT / ".env"
    if env.exists():
        for line in env.read_text().splitlines():
            if not line or line.startswith('#') or '=' not in line:
                continue
            k, v = line.split('=', 1)
            os.environ.setdefault(k.strip(), v.strip())


def send_webhook(url, content):
    r = requests.post(url, json={"content": content[:1900]}, timeout=20)
    r.raise_for_status()


def summarize(rows):
    lines = ["📊 Live Slip Update"]
    for r in rows:
        lines.append(f"• {r['matchup']}: {r['status']} | {r['score']} | {r['note']}")
    return "\n".join(lines)


def key(rows):
    # compare matchup + score + status
    compact = [{"m": r.get("matchup"), "s": r.get("score"), "st": r.get("status")} for r in rows]
    return json.dumps(compact, sort_keys=True)


def main():
    load_env()
    webhook = os.getenv("DISCORD_WEBHOOK_URL", "").strip()
    poll_sec = int(os.getenv("WEBHOOK_POLL_SEC", "30"))
    if not webhook:
        raise SystemExit("Missing DISCORD_WEBHOOK_URL in .env")

    last = ""
    if CACHE_FILE.exists():
        try:
            last = CACHE_FILE.read_text().strip()
        except Exception:
            last = ""

    while True:
        try:
            if not STATE_FILE.exists():
                time.sleep(poll_sec)
                continue
            rows = json.loads(STATE_FILE.read_text())
            k = key(rows)
            if k and k != last:
                msg = summarize(rows)
                send_webhook(webhook, msg)
                last = k
                CACHE_FILE.write_text(last)
        except Exception:
            pass
        time.sleep(poll_sec)


if __name__ == "__main__":
    main()
