#!/usr/bin/env python3
"""
Validate that today's plan (meta/plan.yml) matches TECH_DEBT.md and ROADMAP.md.

Checks:
1) Every TD in today's `tech_debt_resolve` exists in TECH_DEBT.md and is marked Resolved.
2) Every TD in today's `tech_debt_add` exists in TECH_DEBT.md (status can be Pending).
3) ROADMAP.md contains a Day <current_day> section AND includes today's objective text.
"""
from __future__ import annotations
import re, sys
from pathlib import Path
from typing import NoReturn, Dict, List, Tuple, Any
import yaml

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "meta" / "plan.yml"
TECH_DEBT = ROOT / "docs" / "TECH_DEBT.md"
ROADMAP = ROOT /"ROADMAP.md"

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
    for line in lines[start+1:]:
        if not line.strip().startswith("|"):
            break
        # skip delimiter row like |----|
        if re.match(r"^\|\s*-", line):
            continue
        rows.append(line)

    data = {}
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
    errs = []
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

def main():
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
    resolve_ids = [str(x) for x in today.get("tech_debt_resolve", [])]
    add_ids     = [str(x) for x in today.get("tech_debt_add", [])]
    objective   = today.get("objective", "").strip()

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

if __name__ == "__main__":
    main()
