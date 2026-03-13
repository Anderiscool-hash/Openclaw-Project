# Browser Control Demo (School Project)

This demo shows AI-like browser control with Playwright on a safe demo e-commerce site.

## What it does
- Opens Chromium visibly
- Navigates to a demo store
- Searches products
- Adds/removes cart items
- Logs each action to `logs/actions.jsonl`
- Saves screenshots to `artifacts/`

## Run
```bash
cd browser_control_demo
npm install
npx playwright install chromium
npm start
```

## Target site
Uses a public demo store:
- https://www.saucedemo.com/
- Demo credentials are public on the login page.
