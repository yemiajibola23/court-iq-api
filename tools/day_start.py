#!/usr/bin/env python3
"""
Day Start v2 — streamlines the daily kickoff:
- Sets meta/plan.yml current_day
- Ensures ROADMAP.md has Day N section + Objective line (from plan.yml)
- Creates or checks out the branch (from plan.yml days[].branch if present; else {type}/{desc})
- Emits a kickoff block and writes notes/day{N}-kickoff.md
"""

import argparse
import os
import re
import subprocess
import sys
from pathlib import Path

try:
    import yaml  # PyYAML
except ImportError:
    print("Missing dependency: PyYAML. Install with `pip install pyyaml`.", file=sys.stderr)
    sys.exit(2)

REPO_ROOT = Path(__file__).resolve().parents[1]
PLAN_PATH = REPO_ROOT / "meta" / "plan.yml"
ROADMAP_PATH = REPO_ROOT / "ROADMAP.md"
NOTES_DIR = REPO_ROOT / "notes"

DAY_HEADER_RE = re.compile(r"^## Day\s+(\d+)\s+[\u2013-]\s*(.*)$", re.IGNORECASE)  # matches '## Day 9 – ...'
OBJ_LINE_RE = re.compile(r"^\*\*Objective:\*\s*(.+)$", re.IGNORECASE)

def run(cmd, check=True, capture=False):
    if capture:
        return subprocess.run(cmd, check=check, stdout=subprocess.PIPE, text=True).stdout.strip()
    subprocess.run(cmd, check=check)

def kebab_case(s: str) -> str:
    s = re.sub(r"[^\w\s-]", "", s).strip().lower()
    s = re.sub(r"\s+", "-", s)
    s = re.sub(r"-{2,}", "-", s)
    return s[:50]

def load_plan():
    if not PLAN_PATH.exists():
        sys.exit(f"missing {PLAN_PATH}")
    with PLAN_PATH.open() as f:
        return yaml.safe_load(f)

def save_plan(plan):
    PLAN_PATH.parent.mkdir(parents=True, exist_ok=True)
    with PLAN_PATH.open("w") as f:
        yaml.safe_dump(plan, f, sort_keys=False)

def ensure_roadmap_day(day: int, objective: str):
    if not ROADMAP_PATH.exists():
        sys.exit(f"missing {ROADMAP_PATH}")

    with ROADMAP_PATH.open() as f:
        lines = f.read().splitlines()

    # Find the '## Day N –' header if present
    start_idx = None
    for i, line in enumerate(lines):
        m = DAY_HEADER_RE.match(line)
        if m and int(m.group(1)) == day:
            start_idx = i
            break

    day_header = f"## Day {day} – {objective[:60]}"
    obj_line = f"**Objective:** {objective}"

    if start_idx is None:
        # Append a new section at the end with minimal checklist
        snippet = [
            "",
            day_header,
            "",
            obj_line,
            "",
            "- [ ]",
            "",
        ]
        lines.extend(snippet)
    else:
        # Ensure header line is updated (keep rest of section)
        lines[start_idx] = day_header
        # Ensure an **Objective:** line exists/updated somewhere until next H2
        end_idx = next((j for j in range(start_idx + 1, len(lines)) if lines[j].startswith("## ")), len(lines))
        # Search for objective line within this block
        found = False
        for j in range(start_idx + 1, end_idx):
            if OBJ_LINE_RE.match(lines[j] if j < len(lines) else ""):
                lines[j] = obj_line
                found = True
                break
        if not found:
            lines.insert(start_idx + 1, "")
            lines.insert(start_idx + 2, obj_line)

    with ROADMAP_PATH.open("w") as f:
        f.write("\n".join(lines))

def ensure_branch(branch: str):
    # If branch exists, checkout; else create
    existing = run(["git", "branch", "--list", branch], capture=True)
    if existing:
        run(["git", "checkout", branch])
    else:
        run(["git", "checkout", "-b", branch])

def kickoff_block(day: int, branch: str, objective: str) -> str:
    return (
        f"CourtIQ – Day {day} Hybrid Dev Flow\n"
        f"Branch: `{branch}`\n\n"
        f"Objective: {objective}\n\n"
        f"Notes: Follow branch/commit conventions. Work step-by-step through today’s subtasks."
    )

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--day", type=int, required=True)
    p.add_argument("--type", default="feat", choices=["feat","test","docs","refactor","chore","fix","perf"])
    p.add_argument("--desc", default="")
    p.add_argument("--dry-run", action="store_true")
    args = p.parse_args()

    plan = load_plan()
    if "days" not in plan or not isinstance(plan["days"], list):
        sys.exit("meta/plan.yml: missing 'days' list")

    day_entry = next((d for d in plan["days"] if int(d.get("day", -1)) == args.day), None)
    if not day_entry:
        sys.exit(f"meta/plan.yml: no entry for day {args.day}")
    objective = day_entry.get("objective")
    if not objective:
        sys.exit(f"meta/plan.yml: day {args.day} has no 'objective'")

    desc = args.desc.strip() or kebab_case(objective)
    branch = day_entry.get("branch") or f"{args.type}/{desc}"

    # Print plan of action
    print(f"→ Day: {args.day}")
    print(f"→ Objective: {objective}")
    print(f"→ Branch: {branch}")
    print(f"→ Notes file: notes/day{args.day}-kickoff.md")
    if args.dry_run:
        print("DRY RUN: no files will be changed.")
        return

    # Create or checkout branch
    ensure_branch(branch)

    # Update current_day in plan.yml
    plan["current_day"] = args.day
    save_plan(plan)

    # Ensure ROADMAP section + objective line
    ensure_roadmap_day(args.day, objective)
    
    # Ensure notes dir and write kickoff
    NOTES_DIR.mkdir(parents=True, exist_ok=True)
    notes_file = NOTES_DIR / f"day{args.day}-kickoff.md"
    block = kickoff_block(args.day, branch, objective)
    notes_file.write_text(block)

    # Stage files
    to_add = [str(PLAN_PATH), str(ROADMAP_PATH), str(notes_file)]
    run(["git", "add"] + to_add)

    # Final message
    print("\n----- Kickoff -----\n")
    print(block)
    print("\n-------------------\n")
    print("✔ Updated plan.yml current_day, synced ROADMAP.md, prepared notes, and switched to branch.")

if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as e:
        sys.exit(e.returncode)
