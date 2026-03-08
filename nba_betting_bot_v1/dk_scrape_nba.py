#!/usr/bin/env python3
"""Scrape NBA lines from DraftKings pages using saved session state."""
from pathlib import Path
import csv
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
STATE = ROOT / "dk_state.json"
OUT = ROOT / "draftkings_nba_odds.csv"


def parse_cards(page):
    rows = []
    cards = page.query_selector_all('a[href*="/event/"]')
    seen = set()
    for c in cards:
        txt = (c.inner_text() or "").strip()
        if not txt or txt in seen:
            continue
        seen.add(txt)
        lines = [x.strip() for x in txt.split('\n') if x.strip()]
        href = c.get_attribute('href') or ''
        full = href if href.startswith('http') else f"https://sportsbook.draftkings.com{href}"
        rows.append({
            'raw_card_text': ' | '.join(lines),
            'event_url': full,
        })
    return rows


def main():
    if not STATE.exists():
        raise SystemExit(f"Missing {STATE}. Run dk_auth.py first.")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(storage_state=str(STATE))
        page = ctx.new_page()
        page.goto("https://sportsbook.draftkings.com/leagues/basketball/nba", wait_until="networkidle", timeout=60000)
        rows = parse_cards(page)
        browser.close()

    with OUT.open('w', newline='') as f:
        w = csv.DictWriter(f, fieldnames=['raw_card_text', 'event_url'])
        w.writeheader()
        w.writerows(rows)

    print(f"Wrote {len(rows)} rows -> {OUT}")


if __name__ == "__main__":
    main()
