#!/usr/bin/env python3
"""
Fetch Brightspace pages using saved Playwright session state.
Writes extracted tasks to brightspace_tasks.csv
"""
import csv
import re
import os
from pathlib import Path
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "brightspace_tasks.csv"
STATE = ROOT / "brightspace_state.json"


def extract_tasks_from_html(base_url: str, html: str):
    tasks = []
    for m in re.finditer(r'<a[^>]+href="([^"]+)"[^>]*>(.*?)</a>', html, re.I | re.S):
        href, text = m.groups()
        title = re.sub(r"<.*?>", " ", text)
        title = " ".join(title.split())
        if not title:
            continue
        low = title.lower()
        if not any(k in low for k in ["assignment", "quiz", "discussion", "dropbox", "homework", "due"]):
            continue
        snippet = html[max(0, m.start()-250): m.end()+250]
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
    dedup = {}
    for t in tasks:
        dedup[(t['task'], t['source_url'])] = t
    return list(dedup.values())


def main():
    base = os.getenv("BRIGHTSPACE_BASE_URL", "https://brightspace.cuny.edu")
    if not STATE.exists():
        raise SystemExit(f"Missing {STATE}. Run auth_playwright.py first.")

    urls = [
        f"{base.rstrip('/')}/d2l/home",
        f"{base.rstrip('/')}/d2l/le/calendar",
        f"{base.rstrip('/')}/d2l/lms/dropbox/user/folders_list.d2l",
    ]

    tasks = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(storage_state=str(STATE))
        page = context.new_page()
        for url in urls:
            try:
                page.goto(url, wait_until="domcontentloaded", timeout=30000)
                html = page.content()
                tasks.extend(extract_tasks_from_html(base, html))
            except Exception:
                continue
        browser.close()

    fields = ["task", "course", "due_date", "status", "priority", "source_url", "source"]
    with OUT.open("w", newline="") as f:
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(tasks)

    print(f"Wrote {len(tasks)} tasks -> {OUT}")


if __name__ == "__main__":
    main()
