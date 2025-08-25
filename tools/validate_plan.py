#!/usr/bin/env python3
from __future__ import annotations
import argparse
import re
import sys
from pathlib import Path
from typing import NoReturn, Dict, List, Tuple, Any, Optional

import yaml  # required by your repo

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "meta" / "plan.yml"
TECH_DEBT = ROOT / "TECH_DEBT.md"
ROADMAP = ROOT / "ROADMAP.md"

DESC = """Validate that today's plan (meta/plan.yml) matches TECH_DEBT.md and ROADMAP.md.

Checks:
1) Every TD in today's `tech_debt_resolve` exists in TECH_DEBT.md and is marked Resolved.
2) Every TD in today's `tech_debt_add` exists in TECH_DEBT.md (status can be Pending).
3) ROADMAP.md contains a Day <current_day> section AND includes today's objective text.

Skip conditions (non-fatal):
- --allow-prefix <prefix>   (repeatable): if commit subject starts with any prefix
- --allow-trailer key:value (repeatable): if commit trailers include key with a truthy value
"""

# --------------------------- parsing helpers ---------------------------

def load_plan(path: Path) -> Dict[str, Any]:
    if not path.exists():
        fail([f"Missing plan file: {path}"])
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as e:
        fail([f"Failed to parse {path}: {e}"])

def parse_tech_debt_table(md_text: str) -> Dict[str, Dict[str, str]]:
    """
    Parse the main TECH_DEBT table into:
    { "TD8": {"when": "Day 8", "status": "✅ Resolved", "row": "<raw>"} }
    """
    lines = md_text.splitlines()
    # find the header row (contains "| ID |")
    start = None
    for i, line in enumerate(lines):
        if re.search(r"\|\s*ID\s*\|", line):
            start = i
            break
    if start is None:
        return {}

    # collect rows until table ends
    rows = []
    for line in lines[start + 1:]:
        if not line.strip().startswith("|"):
            break
        # skip delimiter-like rows such as |----|
        if re.match(r"^\|\s*-", line):
            continue
        rows.append(line)

    data: Dict[str, Dict[str, str]] = {}
    for row in rows:
        cols = [c.strip() for c in row.strip().strip("|").split("|")]
        if len(cols) < 4:
            continue
        td_id, desc, when, status = cols[0], cols[1], cols[2], cols[3]
        if not re.match(r"^TD\d+$", td_id):
            continue
        data[td_id] = {"when": when, "status": status, "row": row}
    return data

def roadmap_has_day_and_objective(md_text: str, day: int, objective: str) -> Tuple[bool, List[str]]:
    errs: List[str] = []
    # Heading like "## Day 8" or "# Day 8 — ..." (case-insensitive)
    has_day = bool(re.search(rf"^#+\s*Day\s*{day}\b", md_text, flags=re.IGNORECASE | re.MULTILINE))
    if not has_day:
        errs.append(f"ROADMAP missing a 'Day {day}' heading.")
    if objective.strip().lower() not in md_text.lower():
        errs.append("ROADMAP missing today's objective text.")
    return (len(errs) == 0, errs)

def fail(errors: List[str]) -> NoReturn:
    print("❌ Plan validation failed:")
    for e in errors:
        print(f"- {e}")
    raise SystemExit(1)

# --------------------------- skip logic ---------------------------

_TRUTHY = {"1", "true", "yes", "y", "on"}

def _read_commit_message_from(path: Optional[Path]) -> str:
    if path and path.exists():
        try:
            return path.read_text(encoding="utf-8", errors="replace")
        except Exception:
            pass
    # Fallback commonly available in commit-msg hooks
    cem = ROOT / ".git" / "COMMIT_EDITMSG"
    if cem.exists():
        try:
            return cem.read_text(encoding="utf-8", errors="replace")
        except Exception:
            pass
    return ""

def _parse_subject(msg: str) -> str:
    return (msg.splitlines()[0] if msg else "").strip()

def _parse_trailers(msg: str) -> Dict[str, str]:
    """
    Very loose trailer parser:
    accepts lines like 'key: value' or 'key=value' anywhere in the message.
    Keys are lowercased; last one wins.
    """
    trailers: Dict[str, str] = {}
    for ln in msg.splitlines():
        if ":" in ln:
            k, v = ln.split(":", 1)
        elif "=" in ln:
            k, v = ln.split("=", 1)
        else:
            continue
        k = k.strip().lower()
        v = v.strip()
        if k:
            trailers[k] = v
    return trailers

def _should_skip(args: argparse.Namespace, unknown: List[str]) -> bool:
    # Determine commit message file, if any
    cm_path: Optional[Path] = None
    if getattr(args, "commit_msg_file", None):
        cm_path = Path(args.commit_msg_file)
    elif unknown:
        # Accept the first unknown arg if it looks like a file path
        p = Path(unknown[0])
        if p.exists():
            cm_path = p

    msg = _read_commit_message_from(cm_path)
    if not msg:
        return False  # nothing to evaluate; continue with validation

    subject = _parse_subject(msg)
    trailers = _parse_trailers(msg)

    # Prefix check
    for pref in (args.allow_prefix or []):
        if subject.startswith(pref):
            print(f"ℹ️  Skipping plan validation (subject starts with allowed prefix: {pref!r})")
            return True

    # Trailer check
    for item in (args.allow_trailer or []):
        # support "key:value" or "key=value"
        if ":" in item:
            k, v = item.split(":", 1)
        elif "=" in item:
            k, v = item.split("=", 1)
        else:
            k, v = item, "true"
        k = k.strip().lower()
        v = v.strip().lower()
        actual = trailers.get(k, "").strip().lower()
        if actual in _TRUTHY or (not actual and v in _TRUTHY and k in trailers):
            print(f"ℹ️  Skipping plan validation (allowed trailer matched: {k}:{trailers.get(k,'')})")
            return True

    return False

# --------------------------- main validation ---------------------------

def run_validation() -> None:
    errors: List[str] = []

    # Basic existence
    missing = [str(p) for p in [PLAN, TECH_DEBT, ROADMAP] if not p.exists()]
    if missing:
        fail([f"Missing files: {', '.join(missing)}"])

    # Load plan
    plan = load_plan(PLAN)
    current_day = int(plan.get("current_day", 0))
    days = {d["day"]: d for d in plan.get("days", []) if "day" in d}
    if current_day not in days:
        fail([f"current_day {current_day} not found in meta/plan.yml days."])

    today = days[current_day]
    resolve_ids = [str(x).strip().upper() for x in today.get("tech_debt_resolve", [])]
    add_ids     = [str(x).strip().upper() for x in today.get("tech_debt_add", [])]
    objective   = (today.get("objective", "") or "").strip()

    # Parse TECH_DEBT table
    td_map = parse_tech_debt_table(TECH_DEBT.read_text(encoding="utf-8"))
    if not td_map:
        errors.append("Could not parse TECH_DEBT.md table (is the main table present?).")

    # 1) Resolved items must exist + be resolved
    for td in resolve_ids:
        row = td_map.get(td)
        if not row:
            errors.append(f"TECH_DEBT missing row for {td} (should be resolved today).")
            continue
        status = row["status"]
        if not (("Resolved" in status) or ("✅" in status)):
            errors.append(f"{td} is not marked Resolved in TECH_DEBT (status='{status}').")

    # 2) Added items must exist in TECH_DEBT
    for td in add_ids:
        if td not in td_map:
            errors.append(f"TECH_DEBT missing row for new item {td} (added today).")

    # 3) ROADMAP day + objective presence
    ok, road_errs = roadmap_has_day_and_objective(
        ROADMAP.read_text(encoding="utf-8"), current_day, objective
    )
    if not ok:
        errors.extend(road_errs)

    if errors:
        fail(errors)

    print(f"✅ Plan validation passed for Day {current_day}")

def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=DESC, add_help=True)
    p.add_argument(
        "--allow-prefix",
        action="append",
        default=[],
        help="If the commit SUBJECT starts with any of these prefixes, skip validation. Repeatable.",
    )
    p.add_argument(
        "--allow-trailer",
        action="append",
        default=[],
        help="If commit trailers contain key:true for any of these keys, skip validation. "
             "Format key:value or key=value; value treated as truthy when in {true,1,yes,on}. Repeatable.",
    )
    p.add_argument(
        "--commit-msg-file",
        help="Optional path to the commit message file (commit-msg hook). "
             "If omitted, we try .git/COMMIT_EDITMSG. Any extra positional arg that is a file is also used.",
    )
    return p

def main() -> int:
    parser = build_parser()
    args, unknown = parser.parse_known_args()
    try:
        if _should_skip(args, unknown):
            return 0
        run_validation()
        return 0
    except SystemExit as se:
        # Let explicit fail() exit propagate as 1
        raise se
    except Exception as e:
        # Unexpected problems shouldn't block developers
        print(f"⚠️  validate_plan.py encountered a non-fatal error: {e}", file=sys.stderr)
        return 0

if __name__ == "__main__":
    sys.exit(main())
