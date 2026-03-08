#!/usr/bin/env python3
"""One-time interactive DraftKings login to save browser session state."""
from pathlib import Path
import time
from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent
STATE = ROOT / "dk_state.json"


def main(wait_seconds: int = 120):
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        ctx = browser.new_context()
        page = ctx.new_page()
        page.goto("https://sportsbook.draftkings.com/leagues/basketball/nba", wait_until="domcontentloaded")
        print("Login in the opened browser. Complete MFA if prompted.")
        print(f"Keeping browser open {wait_seconds}s, then saving session -> {STATE}")
        time.sleep(wait_seconds)
        ctx.storage_state(path=str(STATE))
        browser.close()
    print(f"Saved: {STATE}")


if __name__ == "__main__":
    main()
