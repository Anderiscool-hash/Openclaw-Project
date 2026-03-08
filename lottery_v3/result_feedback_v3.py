#!/usr/bin/env python3
import csv
from pathlib import Path

ROOT = Path(__file__).resolve().parent
TICKET = ROOT / 'ticket_v3.csv'
OUT = ROOT / 'feedback_v3.md'


def main():
    rows = list(csv.DictReader(TICKET.open()))
    lines = ["# v3 Ticket Feedback Template", "", "Use this after results post:", ""]
    for r in rows:
        lines.append(f"- {r['game']}")
        lines.append(f"  - Strategy: {r['strategy']}")
        lines.append(f"  - Played singles: {r['singles']}")
        lines.append(f"  - Played pales: {r['pales'] or '-'}")
        lines.append("  - Result: ___")
        lines.append("  - Hit: ___")
        lines.append("")

    OUT.write_text('\n'.join(lines))
    print(f'Wrote template -> {OUT}')


if __name__ == '__main__':
    main()
