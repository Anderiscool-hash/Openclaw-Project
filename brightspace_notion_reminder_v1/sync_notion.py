#!/usr/bin/env python3
import csv
import os
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parent
IN_CSV = ROOT / "brightspace_tasks.csv"


def notion_headers(token: str):
    return {
        "Authorization": f"Bearer {token}",
        "Notion-Version": "2022-06-28",
        "Content-Type": "application/json",
    }


def create_page(token: str, database_id: str, row: dict):
    url = "https://api.notion.com/v1/pages"
    payload = {
        "parent": {"database_id": database_id},
        "properties": {
            "Task": {"title": [{"text": {"content": row.get("task", "")[:2000]}}]},
            "Course": {"rich_text": [{"text": {"content": row.get("course", "")[:2000]}}]},
            "Status": {"select": {"name": row.get("status", "Not started")}},
            "Priority": {"select": {"name": row.get("priority", "Medium")}},
            "Source": {"url": row.get("source_url", "") or None},
        },
    }
    # Due date best-effort as text fallback if not ISO
    due = row.get("due_date", "").strip()
    if due:
        payload["properties"]["Due Raw"] = {"rich_text": [{"text": {"content": due[:2000]}}]}

    r = requests.post(url, headers=notion_headers(token), json=payload, timeout=30)
    if r.status_code >= 300:
        return False, r.text
    return True, r.json().get("id", "")


def main():
    token = os.getenv("NOTION_TOKEN", "")
    db = os.getenv("NOTION_DATABASE_ID", "")
    if not token or not db:
        raise SystemExit("Missing NOTION_TOKEN or NOTION_DATABASE_ID")
    if not IN_CSV.exists():
        raise SystemExit(f"Missing input CSV: {IN_CSV}")

    ok = 0
    fail = 0
    with IN_CSV.open() as f:
        for row in csv.DictReader(f):
            success, _ = create_page(token, db, row)
            if success:
                ok += 1
            else:
                fail += 1

    print(f"Notion sync complete: success={ok}, failed={fail}")


if __name__ == "__main__":
    main()
