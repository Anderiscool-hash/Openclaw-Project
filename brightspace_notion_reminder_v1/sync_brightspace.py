#!/usr/bin/env python3
import csv
import os
import re
from datetime import datetime
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "brightspace_tasks.csv"


def fetch_assignments(base_url: str, cookie: str):
    # v1: tries common Brightspace pages and parses assignment links/titles/dates from HTML
    session = requests.Session()
    headers = {
        "User-Agent": "Mozilla/5.0",
        "Cookie": cookie,
    }
    candidates = [
        f"{base_url.rstrip('/')}/d2l/home",
        f"{base_url.rstrip('/')}/d2l/le/calendar",
        f"{base_url.rstrip('/')}/d2l/lms/dropbox/user/folders_list.d2l",
    ]

    tasks = []
    for url in candidates:
        try:
            html = session.get(url, headers=headers, timeout=20).text
        except Exception:
            continue

        # very lightweight parsing for v1
        for m in re.finditer(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', html, re.I | re.S):
            href, text = m.groups()
            title = re.sub(r"<.*?>", " ", text)
            title = " ".join(title.split())
            if not title:
                continue
            low = title.lower()
            if not any(k in low for k in ["assignment", "quiz", "discussion", "dropbox", "homework", "due"]):
                continue

            # guess due date near link
            snippet = html[max(0, m.start() - 250): m.end() + 250]
            dmatch = re.search(r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}(?:\s+\d{1,2}:\d{2}\s*(?:AM|PM)?)?)', snippet, re.I)
            due = dmatch.group(1) if dmatch else ""

            full = href if href.startswith("http") else f"{base_url.rstrip('/')}{href if href.startswith('/') else '/' + href}"
            tasks.append({
                "task": title,
                "course": "",
                "due_date": due,
                "status": "Not started",
                "priority": "Medium",
                "source_url": full,
                "source": "Brightspace",
            })

    # de-dupe by task+url
    dedup = {}
    for t in tasks:
        key = (t["task"], t["source_url"])
        dedup[key] = t
    return list(dedup.values())


def main():
    base = os.getenv("BRIGHTSPACE_BASE_URL", "")
    cookie = os.getenv("BRIGHTSPACE_COOKIE", "")
    if not base or not cookie:
        raise SystemExit("Missing BRIGHTSPACE_BASE_URL or BRIGHTSPACE_COOKIE in environment")

    tasks = fetch_assignments(base, cookie)
    fields = ["task", "course", "due_date", "status", "priority", "source_url", "source"]
    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(tasks)

    print(f"Wrote {len(tasks)} tasks -> {OUT}")


if __name__ == "__main__":
    main()
