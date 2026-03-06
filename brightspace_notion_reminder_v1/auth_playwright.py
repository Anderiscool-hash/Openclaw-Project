#!/usr/bin/env python3
"""
Interactive login bootstrap for Brightspace session.
Opens a real browser so user can enter credentials + MFA directly.
Saves Playwright storage state to ./brightspace_state.json
"""
from pathlib import Path
from playwright.sync_api import sync_playwright
import os

ROOT = Path(__file__).resolve().parent
STATE = ROOT / "brightspace_state.json"


def main():
    base = os.getenv("BRIGHTSPACE_BASE_URL", "https://brightspace.cuny.edu")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False)
        context = browser.new_context()
        page = context.new_page()
        page.goto(base, wait_until="domcontentloaded")
        print("\nLogin in the opened browser (including MFA).")
        print("After you land on Brightspace home/course page, come back and press Enter.\n")
        input("Press Enter after login completes...")
        context.storage_state(path=str(STATE))
        browser.close()
    print(f"Saved session state: {STATE}")


if __name__ == "__main__":
    main()
