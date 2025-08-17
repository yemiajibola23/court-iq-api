# tools/plan_td_update.py  (replace with this updated version)
#!/usr/bin/env python3
"""
Update meta/plan.yml TD lists for a given day (defaults to current_day).

Usage:
  # Add TDs to Day 15 (tech_debt_add)
  python tools/plan_td_update.py --day 15 --add TD42 TD43

  # Mark TDs resolved on Day 12
  python tools/plan_td_update.py --day 12 --resolve TD7

  # No --day provided -> uses current_day in plan.yml
"""
from __future__ import annotations
import argparse, sys
from pathlib import Path
from typing import List
import yaml

PLAN = Path("meta/plan.yml")

def load_plan():
    if not PLAN.exists():
        print("ERROR: meta/plan.yml not found", file=sys.stderr)
        sys.exit(2)
    return yaml.safe_load(PLAN.read_text(encoding="utf-8"))

def save_plan(data):
    PLAN.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")

def find_day_block(data, day_num: int):
    days = data.get("days", [])
    for d in days:
        if int(d.get("day", -1)) == int(day_num):
            return d
    # create if missing (objective/deliverables left empty to be filled later)
    new = {"day": int(day_num), "objective": "", "deliverables": []}
    days.append(new)
    # keep days sorted by day number
    data["days"] = sorted(days, key=lambda x: int(x.get("day", 0)))
    return new

def add_ids(lst: List[str], new_ids: List[str]) -> List[str]:
    seen = set()
    out: List[str] = []
    for x in (lst or []) + new_ids:
        if not x: continue
        if x not in seen:
            seen.add(x)
            out.append(x)
    return out

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plan", default="meta/plan.yml")
    ap.add_argument("--day", type=int, help="Day number to update (default: current_day)")
    ap.add_argument("--add", nargs="*", default=[], help="TD ids to add under tech_debt_add")
    ap.add_argument("--resolve", nargs="*", default=[], help="TD ids to add under tech_debt_resolve")
    args = ap.parse_args()

    global PLAN
    PLAN = Path(args.plan)

    data = load_plan()
    target_day = int(args.day or data.get("current_day"))
    day = find_day_block(data, target_day)

    if args.add:
        day["tech_debt_add"] = add_ids(day.get("tech_debt_add", []), args.add)
    if args.resolve:
        day["tech_debt_resolve"] = add_ids(day.get("tech_debt_resolve", []), args.resolve)

    save_plan(data)
    print(f"Updated {args.plan} for Day {target_day}: add={args.add} resolve={args.resolve}")

if __name__ == "__main__":
    main()
