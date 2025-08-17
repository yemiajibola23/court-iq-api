#!/usr/bin/env python3
"""
CourtIQ Tech Debt CLI

Subcommands:
  list                List TD rows (raw table lines)
  set-status          Set a TD status (Pending | In-Progress 🔧 | ✅ Resolved)
  resolve             Convenience alias for set-status <id> "✅ Resolved"
  add                 Add a new TD row (auto-increment id)
  sync                Align TECH_DEBT.md with meta/plan.yml (current_day)

Highlights:
- `add` always auto-increments the id from the last table row (TDn -> TDn+1)
- `add` supports --preview (with optional --yes confirm), and --no-write
- Status normalization (accepts common variants for in-progress/resolved)
- `sync`:
    * For plan.days[current_day].tech_debt_resolve[] → mark as ✅ Resolved
    * For plan.days[current_day].tech_debt_add[]     → ensure present (Pending)
- Emits NEW_TD_ID=TD## after a successful `add`
"""

from __future__ import annotations
import argparse
import re
import sys
from pathlib import Path
from typing import List, Tuple, Optional

try:
    import yaml  # PyYAML
except Exception:  # pragma: no cover
    yaml = None

TD_FILE = Path("TECH_DEBT.md")

# ---------------------------- Status helpers ---------------------------------

_STATUS_MAP = {
    "pending": "Pending",
    "in-progress": "In-Progress 🔧",
    "in_progress": "In-Progress 🔧",
    "inprogress": "In-Progress 🔧",
    "in-progress": "In-Progress 🔧",  # protect weird hyphen
    "resolved": "✅ Resolved",
    "✅ resolved": "✅ Resolved",
    "resolved ✅": "✅ Resolved",
    "✅": "✅ Resolved",
}

def norm_status(s: str) -> str:
    key = (s or "").strip().lower()
    return _STATUS_MAP.get(key, s.strip())

# ----------------------------- File IO ---------------------------------------

def read_lines() -> List[str]:
    if not TD_FILE.exists():
        raise FileNotFoundError("TECH_DEBT.md not found at repo root")
    return TD_FILE.read_text(encoding="utf-8").splitlines()

def write_lines(lines: List[str]) -> None:
    TD_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")

# ------------------------- Table parsing/updating -----------------------------

# Match any 4-column TD table row, regardless of what's in the "When" column
ROW_RE = re.compile(r'^\|\s*(TD\d+)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*$')

def iter_td_rows(lines: List[str]) -> List[Tuple[int, str]]:
    """
    Return [(index, id), ...] for all table rows in order.
    """
    out = []
    for i, ln in enumerate(lines):
        m = ROW_RE.match(ln)
        if m:
            out.append((i, m.group(1)))
    return out

def last_td_number(lines: List[str]) -> int:
    """
    Robustly find the highest TD number by scanning only the first cell.
    Works even if other columns (like 'When') have unexpected content.
    """
    last = 0
    for ln in lines:
        m = re.match(r'^\|\s*TD(\d+)\b', ln)
        if m:
            n = int(m.group(1))
            if n > last:
                last = n
    return last

def build_row(tdid: str, desc: str, when: str, status: str) -> str:
    return f"| {tdid} | {desc} | {when} | {status} |"

def find_row_index(lines: List[str], tdid: str) -> Optional[int]:
    for i, ln in enumerate(lines):
        m = ROW_RE.match(ln)
        if m and m.group(1) == tdid:
            return i
    return None

def replace_status(lines: List[str], tdid: str, new_status: str) -> List[str]:
    idx = find_row_index(lines, tdid)
    if idx is None:
        raise ValueError(f"{tdid} not found in TECH_DEBT.md")
    m = ROW_RE.match(lines[idx])
    assert m
    desc, when = m.group(2), m.group(3)
    return lines[:idx] + [build_row(tdid, desc, when, new_status)] + lines[idx+1:]

def insert_index_after_table(lines: List[str]) -> int:
    """
    Find the index after the last table row (but before the --- divider section).
    Strategy:
      - Find the table header separator (line starting with '|------')
      - Scan forward while lines look like table rows ('| ... |')
      - Stop before first non-table or a line that starts with '---'
    """
    sep = -1
    for i, ln in enumerate(lines):
        if ln.strip().startswith("|------"):
            sep = i
            break
    if sep == -1:
        # No obvious table; append to end
        return len(lines)
    j = sep + 1
    while j < len(lines):
        s = lines[j].strip()
        if s.startswith("|"):
            j += 1
            continue
        if s.startswith("---"):
            break
        break
    return j

def preview_context(lines: List[str], idx: int, new_row: str, ctx: int = 2) -> str:
    start = max(0, idx - ctx)
    end = min(len(lines), idx + ctx)
    out = []
    out.extend(lines[start:idx])
    out.append(new_row + "   <-- (new)")
    out.extend(lines[idx:end])
    return "\n".join(out)

# ------------------------------- Commands -------------------------------------

def cmd_list(_args) -> None:
    lines = read_lines()
    # print table lines only for easy scanning
    printed = False
    for ln in lines:
        if ln.strip().startswith("| TD"):
            print(ln)
            printed = True
    if not printed:
        print("(no TD rows found)")

def cmd_set_status(args) -> None:
    new_status = norm_status(args.status)
    lines = read_lines()
    new_lines = replace_status(lines, args.id, new_status)
    if args.dry_run:
        print("\n".join(new_lines))
        return
    write_lines(new_lines)
    print(f"✅ {args.id} status → {new_status}")

def cmd_resolve(args) -> None:
    args.status = "✅ Resolved"
    cmd_set_status(args)

def next_tdid(lines: List[str]) -> str:
    n = last_td_number(lines)
    return f"TD{n+1 if n > 0 else 1}"

def cmd_add_auto(args) -> None:
    """
    Add a TECH_DEBT row with an automatically incremented id.

    Options:
      --preview    Show context and ask to confirm (unless --yes)
      --yes        Skip confirmation with --preview
      --no-write   Print row only (and NEW_TD_ID=...) without writing

    Output:
      Prints NEW_TD_ID=TD## on success (for Makefile to capture).
    """
    if not args.desc or not args.when:
        raise SystemExit("--desc and --when are required")

    status = norm_status(args.status or "Pending")
    lines = read_lines()
    tdid = next_tdid(lines)
    new_row = build_row(tdid, args.desc.strip(), args.when.strip(), status)

    if args.no_write:
        print(new_row)
        print(f"NEW_TD_ID={tdid}")
        return

    ins = insert_index_after_table(lines)

    if args.preview and not args.yes:
        if not sys.stdin.isatty() or not sys.stdout.isatty():
            print("Non-interactive session detected; rerun with --yes or without --preview.", file=sys.stderr)
            raise SystemExit(1)
        
        print("\nProposed TECH_DEBT row:\n")
        print(new_row)
        print("\nContext preview:\n")
        print(preview_context(lines, ins, new_row))
        try:
            resp = input("\nProceed to insert? [y/N]: ").strip().lower()
        except EOFError:
            resp = ""
        if resp not in ("y", "yes"):
            print("Aborted. Nothing written.")
            raise SystemExit(1)

    out = lines[:ins] + [new_row] + lines[ins:]
    write_lines(out)

    print(f"✅ Added {tdid} to TECH_DEBT.md")
    print(new_row)
    print(f"NEW_TD_ID={tdid}")

def cmd_sync(args) -> None:
    """
    Align TECH_DEBT.md with meta/plan.yml (current_day):
      - For `tech_debt_resolve`: mark those IDs as ✅ Resolved
      - For `tech_debt_add`: ensure those IDs exist; if missing, add as Pending
    """
    if yaml is None:
        raise SystemExit("PyYAML not installed; cannot read plan.yml")

    plan_path = Path(args.plan)
    if not plan_path.exists():
        raise SystemExit(f"{plan_path} not found")

    plan = yaml.safe_load(plan_path.read_text(encoding="utf-8"))
    current_day = int(plan.get("current_day", 0))
    days = plan.get("days", [])
    day_block = next((d for d in days if int(d.get("day", -1)) == current_day), None)

    if not day_block:
        print(f"(no day block for Day {current_day} in plan)")
        return

    want_resolve: List[str] = list(day_block.get("tech_debt_resolve", []) or [])
    want_add: List[str] = list(day_block.get("tech_debt_add", []) or [])

    lines = read_lines()
    changed = False

    # 1) Ensure all "add" items exist (as Pending) – if missing, append minimal rows.
    for tdid in want_add:
        idx = find_row_index(lines, tdid)
        if idx is None:
            # append a minimal placeholder row at the end of the table (When = Day <current_day>)
            placeholder = build_row(tdid, f"(from plan Day {current_day})", f"Day {current_day}", "Pending")
            ins = insert_index_after_table(lines)
            lines = lines[:ins] + [placeholder] + lines[ins:]
            changed = True

    # 2) Mark all "resolve" items as ✅ Resolved
    for tdid in want_resolve:
        idx = find_row_index(lines, tdid)
        if idx is None:
            # If the row doesn't exist, create it as resolved so docs remain truthful.
            placeholder = build_row(tdid, f"(resolved via plan Day {current_day})", f"Day {current_day}", "✅ Resolved")
            ins = insert_index_after_table(lines)
            lines = lines[:ins] + [placeholder] + lines[ins:]
            changed = True
        else:
            m = ROW_RE.match(lines[idx])
            assert m
            current_status = m.group(4).strip()
            if current_status != "✅ Resolved":
                lines = replace_status(lines, tdid, "✅ Resolved")
                changed = True

    if args.dry_run:
        if changed:
            print("\n".join(lines))
        else:
            print("(no changes needed)")
        return

    if changed:
        write_lines(lines)
        print("✅ TECH_DEBT.md updated from plan")
    else:
        print("✅ Already in sync with plan")

# ------------------------------- CLI wiring -----------------------------------

def main() -> None:
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

    # always-auto "add"
    sp = sub.add_parser("add", help="Add a new TECH_DEBT row (auto-increment id)")
    sp.add_argument("--desc", required=True, help="Description")
    sp.add_argument("--when", required=True, help='When to Address, e.g., "Day 12"')
    sp.add_argument("--status", default="Pending", help='Pending | In-Progress | ✅ Resolved')
    sp.add_argument("--preview", action="store_true", help="Show context and ask to confirm")
    sp.add_argument("--yes", action="store_true", help="Skip confirmation when --preview is used")
    sp.add_argument("--no-write", action="store_true", help="Print the row only; do not write the file")
    sp.set_defaults(func=cmd_add_auto)

    sp = sub.add_parser("sync", help="Align TECH_DEBT.md with meta/plan.yml (current_day)")
    sp.add_argument("--plan", default="meta/plan.yml", help="Path to plan.yml")
    sp.add_argument("--dry-run", action="store_true", help="Print file with changes instead of writing")
    sp.set_defaults(func=cmd_sync)

    args = ap.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
