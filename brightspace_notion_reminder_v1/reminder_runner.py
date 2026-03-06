#!/usr/bin/env python3
import csv
import os
from datetime import datetime, timedelta
from pathlib import Path

from dateutil import parser as dateparser

ROOT = Path(__file__).resolve().parent
TASKS = ROOT / "brightspace_tasks.csv"
LOG = ROOT / "reminder_log.csv"


def load_tasks():
    if not TASKS.exists():
        return []
    with TASKS.open() as f:
        return list(csv.DictReader(f))


def parse_due(value: str):
    if not value:
        return None
    try:
        return dateparser.parse(value)
    except Exception:
        return None


def should_alert(due: datetime, now: datetime, hours):
    delta = due - now
    for h in hours:
        window = timedelta(minutes=20)
        target = timedelta(hours=h)
        if target - window <= delta <= target + window:
            return True, f"due in ~{h}h"
    if due < now:
        return True, "overdue"
    return False, ""


def main():
    hrs = [int(x.strip()) for x in os.getenv("REMINDER_HOURS", "24,6,1").split(",") if x.strip()]
    now = datetime.now()

    alerts = []
    for t in load_tasks():
        due = parse_due(t.get("due_date", ""))
        if not due:
            continue
        ok, reason = should_alert(due, now, hrs)
        if ok:
            alerts.append({
                "timestamp": now.isoformat(timespec="seconds"),
                "task": t.get("task", ""),
                "course": t.get("course", ""),
                "due_date": t.get("due_date", ""),
                "reason": reason,
                "source_url": t.get("source_url", ""),
            })

    if alerts:
        write_header = not LOG.exists()
        with LOG.open("a", newline="") as f:
            w = csv.DictWriter(f, fieldnames=list(alerts[0].keys()))
            if write_header:
                w.writeheader()
            w.writerows(alerts)

        print("ALERTS")
        for a in alerts:
            print(f"- {a['task']} ({a['course']}) | {a['due_date']} | {a['reason']}")
    else:
        print("NO_ALERTS")


if __name__ == "__main__":
    main()
