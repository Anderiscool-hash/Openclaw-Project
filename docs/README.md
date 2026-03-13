# Ander AI Ops Demo Site
Static site for capability showcase.

## CashClaw dashboard section
The page now reads metrics from `docs/cashclaw-metrics.json`.

Refresh that file any time with:
```bash
node /home/ander/.openclaw/workspace/cashclaw/export_metrics.js
```

## Deploy on GitHub Pages
1. Create a new GitHub repo (e.g. `ander-ai-demo`)
2. Push this folder contents to the repo root
3. In repo settings -> Pages -> Deploy from `main` branch `/root`
4. Your public URL will be:
   `https://<username>.github.io/ander-ai-demo/`
