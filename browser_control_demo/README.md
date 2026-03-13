# Browser Control Demo (School Project)

This demo shows AI-like browser control with Playwright on a safe demo e-commerce site.

## What it does
- Opens Chromium visibly
- Navigates to a safe demo store
- Adds/removes cart items
- Logs each action to `logs/actions.jsonl`
- Saves screenshots to `artifacts/`
- Supports multi-account simulation mode

## Run (single account demo)
```bash
cd browser_control_demo
npm install
npx playwright install chromium
npm start
```

## Run multi-account simulation
```bash
node demo.js --multi
```

Edit `accounts_demo.json` to change simulated account labels.

## Target site
Uses a public demo store:
- https://www.saucedemo.com/
- Demo credentials are public on the login page.
