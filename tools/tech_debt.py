#!/usr/bin/env python3
"""
CourtIQ Tech Debt CLI

Automations for TECH_DEBT.md:
- Parse/update the main Markdown table
- Resolve/add items quickly
- Sync with meta/plan.yml (resolve/add for current day)

Usage examples:
  # View table
  python tools/tech_debt.py list

  # Resolve a TD
  python tools/tech_debt.py resolve TD2

  # Add a new TD row
  python tools/tech_debt.py add --id TD19 --desc "Normalize error envelope to arrays" --when "Day 11" --status Pending

  # Set explicit status
  python tools/tech_debt.py set-status TD2 Resolved

  # Sync from plan.yml (applies tech_debt_resolve/add for current_day)
  python tools/tech_debt.py sync --plan meta/plan.yml

  # Preview changes only
  python tools/tech_debt.py sync --dry-run
"""
from __future__ import annotations
import argparse
import copy
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Optional, Tuple

try:
    import yaml  # PyYAML
except Exception:
    yaml = None  # only required for 'sync' command


TECH_DEBT_PATH = Path("TECH_DEBT.md")

# Acceptable status tokens and their display strings
STATUS_CANON = {
    "PENDING": "Pending",
    "IN-PROGRESS": "In-Progress",
    "INPROGRESS": "In-Progress",
    "WIP": "In-Progress",
    "RESOLVED": "✅ Resolved",
    "DONE": "✅ Resolved",
    "FIXED": "✅ Resolved",
    "P": "Pending",
    "IP": "In-Progress",
    "R": "✅ Resolved",
}

TABLE_HEADER = "| ID   | Description                                                                                                                                            | When to Address | Status    |"
TABLE_SEPARATOR = "|------|--------------------------------------------------------------------------------------------------------------------------------------------------------|-----------------|-----------|"

@dataclass
class TDRow:
    id: str
    description: str
    when: str
    status: str

    def clone(self) -> "TDRow":
        return copy.deepcopy(self)

def _read_file(path: Path) -> str:
    return path.read_text(encoding="utf-8")

def _write_file(path: Path, text: str) -> None:
    path.write_text(text, encoding="utf-8")

def _find_table_block(md: str) -> Tuple[int, int]:
    """
    Return (start_idx, end_idx) of the main TD table (inclusive slice for lines).
    Raises if header not found.
    """
    lines = md.splitlines()
    start = end = -1
    for i, line in enumerate(lines):
        if line.strip() == TABLE_HEADER.strip():
            # Next line should be separator
            if i + 1 < len(lines) and lines[i + 1].strip().startswith("|---"):
                start = i
                break
    if start == -1:
        raise RuntimeError("Could not find TECH_DEBT table header in TECH_DEBT.md")

    # Find end: table ends when a line is not a table-row (not starting with '|')
    end = start + 1
    while end + 1 < len(lines) and lines[end + 1].lstrip().startswith("|"):
        end += 1
    return start, end

def _parse_table(md: str) -> Tuple[List[TDRow], int, int]:
    start, end = _find_table_block(md)
    lines = md.splitlines()
    table_lines = lines[start:end+1]
    rows: List[TDRow] = []
    for i, line in enumerate(table_lines):
        if i < 2:  # header + separator
            continue
        parts = [p.strip() for p in line.strip().split("|")[1:-1]]
        if len(parts) != 4:
            # Skip malformed lines silently
            continue
        rows.append(TDRow(id=parts[0], description=parts[1], when=parts[2], status=parts[3]))
    return rows, start, end

def _format_table(rows: List[TDRow]) -> List[str]:
    out = [TABLE_HEADER, TABLE_SEPARATOR]
    for r in rows:
        out.append(f"| {r.id}  | {r.description} | {r.when} | {r.status} |")
    return out

def _normalize_status(s: str) -> str:
    key = s.strip().upper()
    return STATUS_CANON.get(key, s.strip())

def list_rows(md: str) -> List[TDRow]:
    rows, *_ = _parse_table(md)
    return rows

def get_row_map(rows: List[TDRow]) -> Dict[str, TDRow]:
    return {r.id.strip(): r for r in rows}

def set_status(rows: List[TDRow], td_id: str, status: str) -> bool:
    m = get_row_map(rows)
    if td_id not in m:
        return False
    m[td_id].status = _normalize_status(status)
    return True

def resolve_row(rows: List[TDRow], td_id: str) -> bool:
    return set_status(rows, td_id, "✅ Resolved")

def add_row(rows: List[TDRow], td_id: str, desc: str, when: str, status: str = "Pending") -> bool:
    m = get_row_map(rows)
    if td_id in m:
        return False
    rows.append(TDRow(id=td_id, description=desc, when=when, status=_normalize_status(status)))
    return True

def ensure_row(rows: List[TDRow], td_id: str, default_desc: str, default_when: str, default_status: str = "Pending") -> TDRow:
    m = get_row_map(rows)
    if td_id in m:
        return m[td_id]
    r = TDRow(id=td_id, description=default_desc, when=default_when, status=_normalize_status(default_status))
    rows.append(r)
    return r

def replace_table(md: str, new_rows: List[TDRow]) -> str:
    rows, start, end = _parse_table(md)
    lines = md.splitlines()
    new_table_lines = _format_table(new_rows)
    new_lines = lines[:start] + new_table_lines + lines[end+1:]
    return "\n".join(new_lines) + ("\n" if md.endswith("\n") else "")

def load_plan(plan_path: Path) -> dict:
    if yaml is None:
        raise RuntimeError("PyYAML is required for 'sync'. Install with: pip install pyyaml")
    return yaml.safe_load(plan_path.read_text(encoding="utf-8")) or {}

def find_current_day_obj(plan: dict) -> dict:
    current = plan.get("current_day")
    days = plan.get("days", []) or []
    def norm(x):
        try: return int(x)
        except Exception: return x
    tgt = norm(current)
    for d in days:
        if norm(d.get("day")) == tgt:
            return d
    return {}

def cmd_list(args):
    md = _read_file(TECH_DEBT_PATH)
    rows = list_rows(md)
    for r in rows:
        print(f"{r.id:>4} | {r.when:<6} | {r.status:<12} | {r.description}")

def cmd_set_status(args):
    md = _read_file(TECH_DEBT_PATH)
    rows, *_ = _parse_table(md)
    ok = set_status(rows, args.id, args.status)
    if not ok:
        print(f"ERROR: TD '{args.id}' not found.", file=sys.stderr)
        sys.exit(1)
    new_md = replace_table(md, rows)
    if args.dry_run:
        print(new_md)
    else:
        _write_file(TECH_DEBT_PATH, new_md)
        print(f"Updated {args.id} → { _normalize_status(args.status) }")

def cmd_resolve(args):
    md = _read_file(TECH_DEBT_PATH)
    rows, *_ = _parse_table(md)
    ok = resolve_row(rows, args.id)
    if not ok:
        print(f"ERROR: TD '{args.id}' not found.", file=sys.stderr)
        sys.exit(1)
    new_md = replace_table(md, rows)
    if args.dry_run:
        print(new_md)
    else:
        _write_file(TECH_DEBT_PATH, new_md)
        print(f"Resolved {args.id}")

def cmd_add(args):
    md = _read_file(TECH_DEBT_PATH)
    rows, *_ = _parse_table(md)
    ok = add_row(rows, args.id, args.desc, args.when, args.status)
    if not ok:
        print(f"ERROR: TD '{args.id}' already exists.", file=sys.stderr)
        sys.exit(1)
    new_md = replace_table(md, rows)
    if args.dry_run:
        print(new_md)
    else:
        _write_file(TECH_DEBT_PATH, new_md)
        print(f"Added {args.id}")

def cmd_sync(args):
    md = _read_file(TECH_DEBT_PATH)
    rows, *_ = _parse_table(md)
    plan = load_plan(Path(args.plan))
    day = find_current_day_obj(plan)
    day_num = day.get("day", plan.get("current_day"))
    td_resolve = [str(x).strip() for x in (day.get("tech_debt_resolve", []) or [])]
    td_add = [str(x).strip() for x in (day.get("tech_debt_add", []) or [])]

    changed = False

    # Resolve listed items
    for td in td_resolve:
        ok = resolve_row(rows, td)
        if not ok:
            print(f"WARNING: '{td}' not found to resolve; skipping.", file=sys.stderr)
        else:
            changed = True

    # Ensure "add" items exist (Pending if missing)
    for td in td_add:
        if td not in get_row_map(rows):
            # Best-effort defaults; user can edit description later
            ensure_row(
                rows,
                td_id=td,
                default_desc=f"(From plan Day {day_num})",
                default_when=f"Day {day_num}",
                default_status="Pending",
            )
            print(f"Created missing {td} as Pending (Day {day_num})")
            changed = True

    if not changed:
        print("No changes required (TECH_DEBT is already aligned with plan).")
        return

    new_md = replace_table(md, rows)
    if args.dry_run:
        print(new_md)
    else:
        _write_file(TECH_DEBT_PATH, new_md)
        print("TECH_DEBT.md updated from plan.yml")

def main():
    ap = argparse.ArgumentParser(description="CourtIQ Tech Debt CLI")
    sub = ap.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("list", help="List TD rows")
    sp.set_defaults(func=cmd_list)

    sp = sub.add_parser("set-status", help="Set a TD status (Pending, In-Progress, ✅ Resolved)")
    sp.add_argument("id", help="e.g., TD2")
    sp.add_argument("status", help="Pending | In-Progress | ✅ Resolved")
    sp.add_argument("--dry-run", action="store_true", help="Print file with changes instead of writing")
    sp.set_defaults(func=cmd_set_status)

    sp = sub.add_parser("resolve", help="Mark a TD as ✅ Resolved")
    sp.add_argument("id", help="e.g., TD2")
    sp.add_argument("--dry-run", action="store_true", help="Print file with changes instead of writing")
    sp.set_defaults(func=cmd_resolve)

    sp = sub.add_parser("add", help="Add a new TD row")
    sp.add_argument("--id", required=True, help="New TD id, e.g., TD19")
    sp.add_argument("--desc", required=True, help="Description")
    sp.add_argument("--when", required=True, help='When to Address, e.g., "Day 12"')
    sp.add_argument("--status", default="Pending", help='Initial status (default "Pending")')
    sp.add_argument("--dry-run", action="store_true", help="Print file with changes instead of writing")
    sp.set_defaults(func=cmd_add)

    sp = sub.add_parser("sync", help="Align TECH_DEBT.md with meta/plan.yml (current_day)")
    sp.add_argument("--plan", default="meta/plan.yml", help="Path to plan.yml")
    sp.add_argument("--dry-run", action="store_true", help="Print file with changes instead of writing")
    sp.set_defaults(func=cmd_sync)

    args = ap.parse_args()
    try:
        args.func(args)
    except FileNotFoundError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(2)
    except RuntimeError as e:
        print(f"ERROR: {e}", file=sys.stderr)
        sys.exit(3)

if __name__ == "__main__":
    sys.exit(main())
