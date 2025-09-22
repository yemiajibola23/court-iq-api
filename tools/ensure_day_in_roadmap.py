#!/usr/bin/env python3
from __future__ import annotations
import re
from pathlib import Path
from typing import Tuple, Optional
import sys
import yaml

ROOT = Path(__file__).resolve().parents[1]
PLAN = ROOT / "meta" / "plan.yml"
ROADMAP = ROOT / "ROADMAP.md"

DAY_HDR_RE = re.compile(r"^##\s*Day\s+(\d+)\b.*$", re.IGNORECASE)
NEXT_H2_RE = re.compile(r"^##\s+", re.IGNORECASE)

def _find_day_block(lines: list[str], day: int) -> Optional[Tuple[int, int]]:
    start = None
    for i, ln in enumerate(lines):
        m = DAY_HDR_RE.match(ln)
        if m and int(m.group(1)) == day:
            start = i
            break
    if start is None:
        return None
    end = next((j for j in range(start + 1, len(lines)) if NEXT_H2_RE.match(lines[j])), len(lines))
    return (start, end)

def main() -> int:
    if not PLAN.exists():
        print(f"❌ Missing {PLAN}", file=sys.stderr)
        return 1
    if not ROADMAP.exists():
        print(f"❌ Missing {ROADMAP}", file=sys.stderr)
        return 1

    plan = yaml.safe_load(PLAN.read_text(encoding="utf-8"))
    current_day = int(plan.get("current_day", 0))
    if not current_day:
        print("❌ plan.yml current_day is not set.", file=sys.stderr)
        return 1

    days = {int(d["day"]): d for d in plan.get("days", []) if "day" in d}
    if current_day not in days:
        print(f"❌ Day {current_day} not found in plan.yml days.", file=sys.stderr)
        return 1

    objective = (days[current_day].get("objective") or "").strip()
    if not objective:
        print("⚠️  No objective for today; will still ensure the Day section exists.")
    rlines = ROADMAP.read_text(encoding="utf-8").splitlines()

    block = _find_day_block(rlines, current_day)
    if block is None:
        # Append a minimal Day section with objective
        if rlines and rlines[-1].strip() != "":
            rlines.append("")
        rlines.append(f"## Day {current_day} — {objective}" if objective else f"## Day {current_day}")
        rlines.append("")  # spacer
        ROADMAP.write_text("\n".join(rlines) + "\n", encoding="utf-8")
        print(f"🧾 Created Day {current_day} section in ROADMAP.md")
        return 0

    start, end = block
    # Ensure the objective text is present somewhere in the file to satisfy validate_plan
    full_text = "\n".join(rlines)
    if objective and (objective.lower() not in full_text.lower()):
        # Put a simple objective line right after the header
        insert_at = start + 1
        rlines.insert(insert_at, f"**Objective:** {objective}")
        rlines.insert(insert_at + 1, "")  # spacer
        ROADMAP.write_text("\n".join(rlines) + "\n", encoding="utf-8")
        print(f"🧾 Added objective to Day {current_day} in ROADMAP.md")

    return 0

if __name__ == "__main__":
    sys.exit(main())
