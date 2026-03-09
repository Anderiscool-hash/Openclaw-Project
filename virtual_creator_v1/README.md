# Virtual Creator v1 (JSON2Video)

This starter uses JSON2Video to render reel-style vertical videos programmatically.

## Security first
Your API key was posted publicly in chat. Rotate it before production use.

## Setup
```bash
cd virtual_creator_v1
cp .env.example .env
# set JSON2VIDEO_API_KEY in .env
pip install -r requirements.txt
```

## Render first reel
```bash
python3 render_reel.py
```

Outputs:
- `outputs/create_response.json`
- `outputs/status_response.json`

If render succeeds, the output video URL appears in `status_response.json`.

## How to scale to your goal
- Keep one persona style guide (voice, hooks, colors, captions)
- Generate 5-10 scripts/day
- Render each via JSON2Video payload templates
- Save metadata (caption, hashtags, CTA) beside each video
- Upload manually/approved APIs
