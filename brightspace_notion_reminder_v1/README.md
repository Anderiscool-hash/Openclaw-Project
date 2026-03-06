# Brightspace → Notion Reminder v1

v1 includes 3 scripts:

1. `sync_brightspace.py`
   - Pulls assignment/task-like items from Brightspace pages into `brightspace_tasks.csv`
2. `sync_notion.py`
   - Pushes CSV rows into a Notion database
3. `reminder_runner.py`
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
