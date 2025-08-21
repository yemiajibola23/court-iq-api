#!/usr/bin/env python3
"""
tech_debt.py — manage TECH_DEBT.md rows and (optionally) mirror as ROADMAP subtasks.

Commands:
  list                                Show parsed TECH_DEBT rows
  add --desc ... --when "Day N"       Add a new row (auto TD id) and append a ROADMAP checklist line
    [--status Pending] [--scope storage] [--no-roadmap] [--preview] [--yes] [--no-write]
  sync [--day N] [--apply]            Cross-check plan.yml (current day by default) vs ROADMAP vs TECH_DEBT
    [--scope storage] [--no-roadmap-write] [--no-plan-write]

Row format in TECH_DEBT.md (pipe table):
  | TD5  | Description here | Day 12 | Pending |

ROADMAP checklist line we write:
  - [ ] 💳 techdebt(scope): Description here (TD5)
or (when no scope)
  - [ ] 💳 techdebt: Description here (TD5)
"""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Tuple, Optional, Dict

# Optional dependency: PyYAML for plan.yml
try:
    import yaml  # type: ignore
except Exception as e:
    yaml = None  # We'll error only when sync needs it
    

_NUM_RE = re.compile(r"\d+")

def _num_from_id(s: str) -> int:
    """Extract the first integer from an id like 'TD12' or 'D11-3'. Returns 0 if none."""
    m = _NUM_RE.search(s or "")
    return int(m.group(0)) if m else 0

def _as_int_or_none(value) -> Optional[int]:
    """Best-effort parse of current_day which may be int/str/None."""
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        try:
            return int(value.strip())
        except ValueError:
            return None
    return None


# --------------------------------------------------------------------------- #
# Paths
# --------------------------------------------------------------------------- #

REPO = Path(__file__).resolve().parents[1]
TD_FILE = REPO / "TECH_DEBT.md"
ROADMAP_FILE = REPO / "ROADMAP.md"
PLAN_FILE = REPO / "meta" / "plan.yml"

# --------------------------------------------------------------------------- #
# Parsing helpers
# --------------------------------------------------------------------------- #

ROW_RE = re.compile(
    r"^\|\s*(TD\d+)\s*\|\s*(.*?)\s*\|\s*(Day\s*\d+)\s*\|\s*(.*?)\s*\|\s*$"
)
DAY_HDR_RE = re.compile(r"^##\s+Day\s+(\d+)\s+[–-]\s*")

@dataclass
class TdRow:
    tdid: str         # e.g., TD5
    desc: str
    when: str         # e.g., Day 12
    status: str       # e.g., Pending | ✅ Resolved

def read_td_lines() -> List[str]:
    if not TD_FILE.exists():
        raise FileNotFoundError(f"{TD_FILE} not found")
    return TD_FILE.read_text(encoding="utf-8").splitlines()

def write_td_lines(lines: List[str]) -> None:
    TD_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")

def parse_rows(lines: List[str]) -> List[TdRow]:
    rows: List[TdRow] = []
    for ln in lines:
        m = ROW_RE.match(ln)
        if m:
            rows.append(TdRow(m.group(1), m.group(2), m.group(3), m.group(4)))
    return rows

def next_td_id(rows: List[TdRow]) -> str:
    mx = 0
    for r in rows:
        try:
            mx = max(mx, int(r.tdid[2:]))
        except Exception:
            pass
    return f"TD{mx + 1}"

def format_row(tdid: str, desc: str, when: str, status: str) -> str:
    return f"| {tdid} | {desc} | {when} | {status} |"

def find_insert_index_for_row(lines: List[str]) -> int:
    """
    Returns the index AFTER the last existing row. If no rows are found,
    returns the end of file (we do not create headers—assume file has them).
    """
    last_row_idx = -1
    for i, ln in enumerate(lines):
        if ROW_RE.match(ln):
            last_row_idx = i
    return last_row_idx + 1 if last_row_idx >= 0 else len(lines)

# --------------------------------------------------------------------------- #
# ROADMAP helpers
# --------------------------------------------------------------------------- #

def roadmap_read_lines() -> List[str]:
    if not ROADMAP_FILE.exists():
        raise FileNotFoundError("ROADMAP.md not found at repo root")
    return ROADMAP_FILE.read_text(encoding="utf-8").splitlines()

def roadmap_write_lines(lines: List[str]) -> None:
    ROADMAP_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")

def roadmap_find_day_block(lines: List[str], day: int) -> Optional[Tuple[int, int]]:
    """
    Returns (start, end) indices of the Day block, or None if not present.
    start points at the '## Day N – ...' header; end is the first next H2 or EOF.
    """
    start = None
    for i, ln in enumerate(lines):
        m = DAY_HDR_RE.match(ln)
        if m and int(m.group(1)) == day:
            start = i
            break
    if start is None:
        return None
    end = next((j for j in range(start + 1, len(lines)) if lines[j].startswith("## ")), len(lines))
    return (start, end)

def parse_day_num(when: str) -> Optional[int]:
    m = re.search(r"(\d+)", when or "")
    return int(m.group(1)) if m else None

def roadmap_insert_td_subtask(day: int, tdid: str, desc: str, scope: Optional[str] = None, emoji: str = "💳") -> bool:
    """
    Insert a TD checklist line at the end of the Day block if not already present.

    Line format:
      - [ ] 💳 techdebt(scope): <desc> (TD#)
      - [ ] 💳 techdebt: <desc> (TD#)                # when scope missing
    """
    lines = roadmap_read_lines()
    block = roadmap_find_day_block(lines, day)
    if block is None:
        # Do not silently create a new Day section
        return False
    start, end = block

    # If the ID already appears in the Day block, skip
    id_pat = re.compile(rf"(?<!\w)\(?{re.escape(tdid)}\)?(?!\w)")
    for j in range(start, end):
        if id_pat.search(lines[j]):
            return False

    scope_part = f"techdebt({scope})" if scope else "techdebt"
    new_line = f"- [ ] {emoji} {scope_part}: {desc} ({tdid})"

    # Insert just before the Day block end, keeping a blank spacer if needed
    insert_at = end
    k = end - 1
    while k > start and lines[k].strip() == "":
        k -= 1
    insert_at = k + 1
    # Ensure a blank line before the new checklist item for readability
    if insert_at == start + 1 or (insert_at - 1 < len(lines) and lines[insert_at - 1].strip() != ""):
        lines.insert(insert_at, "")
        insert_at += 1
    lines.insert(insert_at, new_line)

    roadmap_write_lines(lines)
    return True

def roadmap_collect_td_ids_for_day(day: int) -> List[str]:
    """Return all TD ids (e.g., ['TD1','TD5']) present in the Day block checklist."""
    lines = roadmap_read_lines()
    block = roadmap_find_day_block(lines, day)
    if block is None:
        return []
    start, end = block
    ids: set[str] = set()
    for j in range(start, end):
        for td in re.findall(r"\bTD\d+\b", lines[j]):
            ids.add(td)
    return sorted(ids)

# --------------------------------------------------------------------------- #
# plan.yml helpers
# --------------------------------------------------------------------------- #

def plan_load() -> dict:
    if not PLAN_FILE.exists():
        raise FileNotFoundError(f"{PLAN_FILE} not found")
    if yaml is None:
        raise RuntimeError("PyYAML not installed. Install with `pip install pyyaml`.")
    return yaml.safe_load(PLAN_FILE.read_text(encoding="utf-8"))

def plan_save(data: dict) -> None:
    assert yaml is not None
    PLAN_FILE.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8")

def plan_current_day(data: dict) -> Optional[int]:
    return _as_int_or_none(data.get("current_day"))

def plan_find_day_entry(data: dict, day: int) -> Optional[dict]:
    for d in (data.get("days") or []):
        try:
            if int(d.get("day")) == day:
                return d
        except Exception:
            pass
    return None

def plan_get_tdr_list(day_entry: dict) -> List[str]:
    lst = (day_entry or {}).get("tech_debt_resolve") or []
    # normalize to uppercase TD# strings
    norm = []
    for x in lst:
        x = str(x).strip().upper()
        if not x.startswith("TD"):
            # allow numeric-only list (e.g., [1,5]) though not recommended
            try:
                x = f"TD{int(x)}"
            except Exception:
                pass
        norm.append(x)
    return sorted(set(norm))

def plan_set_tdr_list(day_entry: dict, ids: List[str]) -> None:
    # Normalize to uppercase TD ids, then sort numerically by the embedded number.
    norm = [str(i).strip().upper() for i in ids if str(i).strip()]
    day_entry["tech_debt_resolve"] = sorted(set(norm), key=_num_from_id)


# --------------------------------------------------------------------------- #
# Commands
# --------------------------------------------------------------------------- #

def cmd_list(_: argparse.Namespace) -> None:
    lines = read_td_lines()
    rows = parse_rows(lines)
    if not rows:
        print("(no TECH_DEBT rows found)")
        return
    # Pretty print minimal table (don’t rewrite the file)
    print("| ID   | Description | When   | Status    |")
    print("|------|-------------|--------|-----------|")
    for r in rows:
        print(format_row(r.tdid, r.desc, r.when, r.status))

def cmd_add(args: argparse.Namespace) -> None:
    # Read existing rows
    lines = read_td_lines()
    rows = parse_rows(lines)
    tdid = next_td_id(rows)

    # Construct the new row
    desc = args.desc.strip()
    when = args.when.strip()
    status = args.status.strip()

    new_row = format_row(tdid, desc, when, status)

    # Preview mode
    if args.preview and not args.yes and not args.no_write:
        print("About to add TECH_DEBT row:\n")
        print(new_row)
        ans = input("\nProceed? [y/N] ").strip().lower()
        if ans not in ("y", "yes"):
            print("Canceled.")
            return

    # Print-only mode (for pipelines capturing NEW_TD_ID)
    if args.no_write:
        print(new_row)
        print(f"NEW_TD_ID={tdid}")
        return

    # Insert into TECH_DEBT.md after last existing row
    idx = find_insert_index_for_row(lines)
    lines.insert(idx, new_row)
    write_td_lines(lines)

    # Attempt to mirror as a ROADMAP checklist line (unless disabled)
    day_num = parse_day_num(when)
    if day_num is not None and not args.no_roadmap:
        try:
            added = roadmap_insert_td_subtask(
                day=day_num,
                tdid=tdid,
                desc=desc,
                scope=args.scope,
            )
            if added:
                print(f"🧾 Added to ROADMAP Day {day_num}: {tdid}")
        except FileNotFoundError:
            # ROADMAP not present; silently ignore
            pass

    # Final output (keep for Makefile capture)
    print(f"✅ Added {tdid} to TECH_DEBT.md")
    print(new_row)
    print(f"NEW_TD_ID={tdid}")

def cmd_sync(args: argparse.Namespace) -> None:
    """
    Cross-check plan.yml (tech_debt_resolve) vs ROADMAP (today's Day) vs TECH_DEBT table.

    Default day = plan.yml.current_day (override with --day).
    Prints a report; with --apply, updates ROADMAP and/or plan.yml.
    """
    # Load TECH_DEBT
    td_lines = read_td_lines()
    td_rows = parse_rows(td_lines)
    td_by_id: Dict[str, TdRow] = {r.tdid.upper(): r for r in td_rows}

    # Load plan.yml
    plan = plan_load()
    day = args.day or plan_current_day(plan)
    if not day:
        print("❌ Could not determine day (use --day or set current_day in plan.yml).", file=sys.stderr)
        sys.exit(1)

    day_entry = plan_find_day_entry(plan, day)
    if not day_entry:
        print(f"❌ No entry for Day {day} in plan.yml.", file=sys.stderr)
        sys.exit(1)

    plan_tdr = set(plan_get_tdr_list(day_entry))

    # Collect ROADMAP TD ids for this day
    roadmap_ids = set(roadmap_collect_td_ids_for_day(day))

    # Compare sets
    missing_in_roadmap = sorted(plan_tdr - roadmap_ids)  # present in plan, not listed in today's ROADMAP
    missing_in_plan = sorted(roadmap_ids - plan_tdr)     # present in ROADMAP, not present in plan
    resolved_now = sorted(i for i in plan_tdr if td_by_id.get(i, TdRow(i, "", "", "")).status.strip().startswith("✅"))

    print(f"Day {day} tech-debt sync report")
    print("----------------------------------------------------------------")
    print(f"Plan wants to resolve: {', '.join(sorted(plan_tdr)) or '(none)'}")
    print(f"ROADMAP lists:         {', '.join(sorted(roadmap_ids)) or '(none)'}")
    print(f"Resolved in table:     {', '.join(resolved_now) or '(none)'}")
    print()
    if missing_in_roadmap:
        print(f"• Missing in ROADMAP (will add if --apply): {', '.join(missing_in_roadmap)}")
    if missing_in_plan:
        print(f"• Missing in plan.yml (will add if --apply): {', '.join(missing_in_plan)}")
    if not missing_in_plan and not missing_in_roadmap:
        print("• ROADMAP and plan.yml are aligned for TD ids.")

    # Apply changes if requested
    if args.apply:
        wrote_roadmap = False
        wrote_plan = False

        if missing_in_roadmap and not args.no_roadmap_write:
            for tdid in missing_in_roadmap:
                row = td_by_id.get(tdid)
                desc = row.desc if row else tdid
                try:
                    added = roadmap_insert_td_subtask(
                        day=day,
                        tdid=tdid,
                        desc=desc,
                        scope=args.scope,
                    )
                    wrote_roadmap = wrote_roadmap or added
                except FileNotFoundError:
                    print("⚠️  ROADMAP.md not found; skipping ROADMAP writes.", file=sys.stderr)
                    break

        if missing_in_plan and not args.no_plan_write:
            new_ids = sorted(set(plan_tdr) | set(missing_in_plan), key=_num_from_id)
            plan_set_tdr_list(day_entry, new_ids)
            plan_save(plan)
            wrote_plan = True

        if wrote_roadmap:
            print(f"🧾 Added to ROADMAP Day {day}: {', '.join(missing_in_roadmap)}")
        if wrote_plan:
            print(f"🗂  Updated plan.yml Day {day} tech_debt_resolve: {', '.join(plan_get_tdr_list(day_entry))}")

        if not wrote_plan and not wrote_roadmap:
            print("Nothing to apply.")

# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Manage TECH_DEBT.md (and optional ROADMAP checklist lines).")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp_list = sub.add_parser("list", help="List rows from TECH_DEBT.md")
    sp_list.set_defaults(func=cmd_list)

    sp_add = sub.add_parser(
        "add",
        help="Add a new TECH_DEBT row (auto-increment id) and append a ROADMAP checklist line",
    )
    sp_add.add_argument("--desc", required=True, help="Description of the tech debt")
    sp_add.add_argument("--when", required=True, help='When to address, e.g., "Day 11"')
    sp_add.add_argument("--status", default="Pending", help='Status: Pending | In-Progress | ✅ Resolved')
    sp_add.add_argument("--scope", default=None, help='Optional scope for ROADMAP line, e.g., "storage"')
    sp_add.add_argument("--no-roadmap", action="store_true", help="Skip writing the ROADMAP checklist line")
    sp_add.add_argument("--preview", action="store_true", help="Show the row and ask to confirm")
    sp_add.add_argument("--yes", action="store_true", help="Auto-confirm when --preview is used")
    sp_add.add_argument("--no-write", action="store_true", help="Print the row and NEW_TD_ID only (no file changes)")
    sp_add.set_defaults(func=cmd_add)

    sp_sync = sub.add_parser(
        "sync",
        help="Cross-check plan.yml (tech_debt_resolve) vs today's ROADMAP vs TECH_DEBT; optionally apply fixes",
    )
    sp_sync.add_argument("--day", type=int, help="Day number to sync (defaults to plan.yml current_day)")
    sp_sync.add_argument("--apply", action="store_true", help="Apply changes (write ROADMAP and/or plan.yml)")
    sp_sync.add_argument("--scope", default=None, help='Scope to include on new ROADMAP TD lines, e.g., "storage"')
    sp_sync.add_argument("--no-roadmap-write", action="store_true", help="Do not modify ROADMAP.md")
    sp_sync.add_argument("--no-plan-write", action="store_true", help="Do not modify plan.yml")
    sp_sync.set_defaults(func=cmd_sync)

    return p

def main() -> int:
    try:
        parser = build_parser()
        args = parser.parse_args()
        args.func(args)
        return 0
    except FileNotFoundError as e:
        print(f"❌ {e}", file=sys.stderr)
        return 1
    except RuntimeError as e:
        print(f"❌ {e}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\n(Interrupted)")
        return 130

if __name__ == "__main__":
    sys.exit(main())
