#!/usr/bin/env python3
"""
Auto-increment TD row creator for TECH_DEBT.md

Usage examples:
  # Print next row only (no write)
  python tools/td_auto_add.py --desc "GitHub Action: promote plan.yml current_day on merge" --when "Day 10" --status Pending --no-write

  # Insert into TECH_DEBT.md in-place
  python tools/td_auto_add.py --desc "Add live CI badges to README via GHA" --when "Day 10" --status Pending

Notes:
- Auto-detects last TD id (e.g., TD21 -> TD22)
- Writes a Markdown table row like:
  | TD22 | Add live CI badges to README via GHA | Day 10 | Pending |
- When writing, appends as the **last TD row** in the main table (before the --- separator)
"""
from __future__ import annotations
import argparse, re, sys
from pathlib import Path

TD_FILE = Path("TECH_DEBT.md")

STATUS_MAP = {
    "pending": "Pending",
    "in-progress": "In-Progress 🔧",
    "in_progress": "In-Progress 🔧",
    "inprogress": "In-Progress 🔧",
    "resolved": "✅ Resolved",
    "✅ resolved": "✅ Resolved",
    "resolved ✅": "✅ Resolved",
}

def normalize_status(s: str) -> str:
    key = s.strip().lower()
    return STATUS_MAP.get(key, s.strip())

def parse_args():
    ap = argparse.ArgumentParser(description="Auto-add next TD row to TECH_DEBT.md")
    ap.add_argument("--desc", required=True, help="Description column text")
    ap.add_argument("--when", required=True, help='e.g., "Day 10"')
    ap.add_argument("--status", default="Pending", help='Pending | In-Progress | Resolved (default: Pending)')
    ap.add_argument("--no-write", action="store_true", help="Do not modify TECH_DEBT.md; print row for copy/paste")
    return ap.parse_args()

def read_td_lines() -> list[str]:
    try:
        return TD_FILE.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        print("ERROR: TECH_DEBT.md not found at repo root.", file=sys.stderr)
        sys.exit(2)

def next_td_id(lines: list[str]) -> int:
    last = 0
    for ln in lines:
        m = re.match(r'^\|\s*TD(\d+)\s*\|', ln)
        if m:
            n = int(m.group(1))
            if n > last:
                last = n
    return last + 1 if last > 0 else 1

def find_table_insert_index(lines: list[str]) -> int:
    """
    Return the index where a new TD row should be inserted.
    Strategy:
      - Find the main table header separator line (e.g., '|------|')
      - Scan forward through lines that start with '|' (table rows)
      - Stop before the first non-table line or '---' section break
    Insert **after** the last TD row (i.e., at the boundary index).
    """
    if not lines:
        return len(lines)

    # Find header separator (---- line) – start of data rows follows it.
    sep_idx = -1
    for i, ln in enumerate(lines):
        if ln.strip().startswith("|------"):
            sep_idx = i
            break
    if sep_idx == -1:
        # fallback: append near top if no header found
        return len(lines)

    # Walk forward to end of table rows
    j = sep_idx + 1
    while j < len(lines):
        s = lines[j].strip()
        if s.startswith("|"):
            j += 1
            continue
        if s.startswith("---"):
            break
        # first non-table line → stop here
        break
    return j

def build_row(td_num: int, desc: str, when: str, status: str) -> str:
    # Minimal clean spacing; Markdown table doesn’t require exact column widths.
    return f"| TD{td_num} | {desc} | {when} | {status} |"

def main():
    args = parse_args()
    status = normalize_status(args.status)

    lines = read_td_lines()
    td_num = next_td_id(lines)
    row = build_row(td_num, args.desc.strip(), args.when.strip(), status)

    if args.no_write:
        print(row)
        print("\nCopy/paste the row above into the TECH_DEBT table (before the '---' line).")
        sys.exit(0)

    ins = find_table_insert_index(lines)
    new_lines = lines[:ins] + [row] + lines[ins:]
    TD_FILE.write_text("\n".join(new_lines) + "\n", encoding="utf-8")

    print(f"✅ Added TD{td_num} to TECH_DEBT.md")
    print(row)

if __name__ == "__main__":
    main()
