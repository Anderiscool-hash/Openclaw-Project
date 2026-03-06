# Brightspace → Notion Reminder v1

v1/v1.1 includes scripts:

1. `auth_playwright.py` (v1.1 preferred)
   - Opens interactive browser login and saves `brightspace_state.json`
2. `sync_brightspace_session.py` (v1.1 preferred)
   - Uses saved session state to pull assignment/task-like items into `brightspace_tasks.csv`
3. `sync_brightspace.py` (legacy cookie mode)
   - Pulls assignment/task-like items via `BRIGHTSPACE_COOKIE`
4. `sync_notion.py`
   - Pushes CSV rows into a Notion database
5. `reminder_runner.py`
   - Scans due dates and emits reminders to `reminder_log.csv`

## Setup

1. Copy env template:
   ```bash
   cp .env.example .env
   ```
2. Fill values in `.env`:
   - `BRIGHTSPACE_BASE_URL`
   - `BRIGHTSPACE_COOKIE`
   - `NOTION_TOKEN`
   - `NOTION_DATABASE_ID`
3. Install deps:
   ```bash
   pip install -r requirements.txt
   ```

## Run

### Preferred (interactive login session)
```bash
set -a; source .env; set +a
python3 auth_playwright.py
python3 sync_brightspace_session.py
python3 sync_notion.py
python3 reminder_runner.py
```

### Legacy (cookie mode)
```bash
set -a; source .env; set +a
python3 sync_brightspace.py
python3 sync_notion.py
python3 reminder_runner.py
```

## Notes

- This is a pragmatic v1 parser (HTML-based).
- Some Brightspace themes/pages may require custom selectors.
- Notion database should have properties:
  - `Task` (title)
  - `Course` (rich_text)
  - `Status` (select)
  - `Priority` (select)
  - `Source` (url)
  - `Due Raw` (rich_text)
