#!/usr/bin/env python3
"""Deep DraftKings scraper: visits each NBA event page and extracts market-level rows.

Output:
- draftkings_nba_markets_raw.csv
Columns:
  matchup,event_url,market,selection,line,price,raw_text
"""
from pathlib import Path
import csv
import re
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
STATE = ROOT / "dk_state.json"
EVENTS = ROOT / "draftkings_nba_odds.csv"
OUT = ROOT / "draftkings_nba_markets_raw.csv"

ODDS_RE = re.compile(r"([+-]\d{2,4})")
LINE_RE = re.compile(r"\b(\d+(?:\.\d+)?)\b")


def extract_rows(page, event_url):
    rows = []
    # Best-effort: capture visible text blocks that include american odds
    blocks = page.query_selector_all("section, div")
    for b in blocks:
        try:
            txt = (b.inner_text() or "").strip()
        except Exception:
            continue
        if not txt or len(txt) < 4:
            continue
        if not ODDS_RE.search(txt):
            continue

        lines = [x.strip() for x in txt.split("\n") if x.strip()]
        if len(lines) < 2:
            continue

        market = lines[0][:120]
        # pull likely outcomes from lines containing american odds
        for line in lines[1:20]:
            m = ODDS_RE.search(line)
            if not m:
                continue
            price = m.group(1)
            # remove odds token to get selection text
            selection = line.replace(price, "").strip(" -|:")[:140]
            # optional line number (spread/total/prop line)
            lm = LINE_RE.search(selection)
            line_val = lm.group(1) if lm else ""
            rows.append({
                "matchup": "",
                "event_url": event_url,
                "market": market,
                "selection": selection,
                "line": line_val,
                "price": price,
                "raw_text": line[:220],
            })
    return rows


def load_event_urls():
    urls = []
    if not EVENTS.exists():
        return urls
    with EVENTS.open() as f:
        for r in csv.DictReader(f):
            u = (r.get("event_url") or "").strip()
            if u and u not in urls and "/event/" in u:
                urls.append(u)
    return urls


def main():
    if not STATE.exists():
        raise SystemExit(f"Missing {STATE}. Run dk_auth.py first.")

    event_urls = load_event_urls()
    if not event_urls:
        raise SystemExit("No event URLs found. Run dk_scrape_nba.py first.")

    all_rows = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(storage_state=str(STATE))
        page = ctx.new_page()

        for u in event_urls:
            try:
                page.goto(u, wait_until="domcontentloaded", timeout=90000)
                page.wait_for_timeout(3500)
                all_rows.extend(extract_rows(page, u))
            except Exception:
                continue

        browser.close()

    # basic dedupe
    dedup = {}
    for r in all_rows:
        k = (r["event_url"], r["market"], r["selection"], r["price"])
        dedup[k] = r
    rows = list(dedup.values())

    with OUT.open("w", newline="") as f:
        fields = ["matchup", "event_url", "market", "selection", "line", "price", "raw_text"]
        w = csv.DictWriter(f, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)

    print(f"Wrote {len(rows)} deep market rows -> {OUT}")


if __name__ == "__main__":
    main()
