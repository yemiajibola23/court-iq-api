#!/usr/bin/env python3
"""
eod.py — End-of-Day helper:
- Reads meta/plan.yml (or --day) to locate today's Day block in ROADMAP.md
- Summarizes checked/unchecked subtasks
- Summarizes TDs in today's block (resolved vs pending from TECH_DEBT.md)
- Writes notes/day{N}-eod.md
"""

from __future__ import annotations
import argparse, re, sys
from pathlib import Path
from typing import Optional, List, Tuple, Dict

# Optional: PyYAML for plan.yml
try:
    import yaml  # type: ignore
except Exception:
    yaml = None

REPO = Path(__file__).resolve().parents[1]
PLAN = REPO / "meta" / "plan.yml"
ROADMAP = REPO / "ROADMAP.md"
TECH_DEBT = REPO / "TECH_DEBT.md"
NOTES = REPO / "notes"

DAY_HDR_RE = re.compile(r"^##\s+Day\s+(\d+)\s+[–-]\s*(.*)$")
UNCHECKED_RE = re.compile(r"^[ \t\xa0]*-\s\[\s\]\s")
CHECKED_RE   = re.compile(r"^[ \t\xa0]*-\s\[x\]\s", re.IGNORECASE)

TD_ROW_RE = re.compile(r"^\|\s*(TD\d+)\s*\|\s*(.*?)\s*\|\s*(Day\s*\d+)\s*\|\s*(.*?)\s*\|\s*$")
NUM_RE = re.compile(r"\d+")
TD_ID_RE = re.compile(r"\bTD\d+\b")

def load_plan() -> dict:
    if not PLAN.exists():
        raise FileNotFoundError(f"Missing {PLAN}")
    if yaml is None:
        raise RuntimeError("PyYAML not installed. `pip install pyyaml`.")
    return yaml.safe_load(PLAN.read_text(encoding="utf-8"))

def plan_current_day(data: dict) -> Optional[int]:
    val = data.get("current_day")
    if isinstance(val, int): return val
    if isinstance(val, str):
        try: return int(val.strip())
        except ValueError: return None
    return None

def roadmap_lines() -> List[str]:
    if not ROADMAP.exists():
        raise FileNotFoundError(f"Missing {ROADMAP}")
    return ROADMAP.read_text(encoding="utf-8").splitlines()

def find_day_block(lines: List[str], day: int) -> Tuple[int, int, str]:
    """Return (start_idx, end_idx, heading_text_after_dash)."""
    start = None; heading_tail = ""
    for i, ln in enumerate(lines):
        m = DAY_HDR_RE.match(ln)
        if m and int(m.group(1)) == day:
            start = i
            heading_tail = m.group(2).strip()
            break
    if start is None:
        raise SystemExit(f"Could not find '## Day {day} – …' in {ROADMAP.name}")
    end = next((j for j in range(start+1, len(lines)) if lines[j].startswith("## ")), len(lines))
    return start, end, heading_tail

def parse_checklist(block_lines: List[str]) -> Tuple[List[str], List[str]]:
    """Return (checked_lines, unchecked_lines) as raw lines (no trimming)."""
    checked, unchecked = [], []
    for ln in block_lines:
        if CHECKED_RE.match(ln):
            checked.append(ln)
        elif UNCHECKED_RE.match(ln):
            unchecked.append(ln)
    return checked, unchecked

def parse_td_table() -> Dict[str, Dict[str,str]]:
    """Map TD id → dict(desc, when, status)."""
    if not TECH_DEBT.exists():
        return {}
    d: Dict[str, Dict[str,str]] = {}
    for ln in TECH_DEBT.read_text(encoding="utf-8").splitlines():
        m = TD_ROW_RE.match(ln)
        if m:
            tdid, desc, when, status = m.groups()
            d[tdid.upper()] = {"desc": desc, "when": when, "status": status}
    return d

def extract_td_ids(lines: List[str]) -> List[str]:
    ids: set[str] = set()
    for ln in lines:
        for td in TD_ID_RE.findall(ln):
            ids.add(td.upper())
    return sorted(ids, key=lambda s: int(NUM_RE.search(s).group(0)) if NUM_RE.search(s) else 0) # type: ignore

def tidy_item_text(ln: str) -> str:
    # Strip the leading checkbox only; keep the rest verbatim
    ln = re.sub(r"^[ \t\xa0]*-\s\[[ xX]\]\s", "", ln)
    return ln.strip()

def write_note(day: int, heading: str, checked: List[str], unchecked: List[str], td_info: Dict[str, Dict[str,str]]) -> Path:
    NOTES.mkdir(parents=True, exist_ok=True)
    out = NOTES / f"day{day}-eod.md"

    shipped = [tidy_item_text(x) for x in checked]
    carry   = [tidy_item_text(x) for x in unchecked]

    # TDs present in today's block
    todays_td_ids = extract_td_ids(checked + unchecked)
    resolved, pending = [], []
    for td in todays_td_ids:
        row = td_info.get(td, {})
        status = (row.get("status") or "").strip()
        if status.startswith("✅"):
            resolved.append(f"{td} — {row.get('desc','')}".strip())
        else:
            pending.append(f"{td} — {row.get('desc','')}".strip())

    # Suggested next micro-task
    next_up = carry[0] if carry else ""

    lines: List[str] = []
    lines.append(f"# Day {day} — End of Day Summary")
    lines.append("")
    lines.append(f"**Focus:** {heading}" if heading else "")
    lines.append("")
    lines.append("## What shipped")
    lines.extend([f"- {x}" for x in shipped] or ["- (none)"])
    lines.append("")
    lines.append("## Carry-overs")
    lines.extend([f"- {x}" for x in carry] or ["- (none)"])
    lines.append("")
    lines.append("## Tech debt status (today’s IDs)")
    lines.append("### Resolved")
    lines.extend([f"- {x}" for x in resolved] or ["- (none)"])
    lines.append("### Still outstanding")
    lines.extend([f"- {x}" for x in pending] or ["- (none)"])
    lines.append("")
    lines.append("## Tomorrow: suggested first micro-task")
    lines.append(f"- {next_up}" if next_up else "- (clear slate 🎉)")
    lines.append("")
    lines.append("> Tip: start with `make day-start DAY={}` then tackle the first carry-over using TDD.".format(day+1))

    out.write_text("\n".join(lines).strip() + "\n", encoding="utf-8")
    print(str(out))  # path for Make or humans
    return out

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--day", type=int, help="Day number (defaults to plan.yml current_day)")
    args = ap.parse_args()

    day = args.day
    if not day:
        plan = load_plan()
        day = plan_current_day(plan)
    if not day:
        print("❌ Could not determine day; use --day or set current_day in meta/plan.yml.", file=sys.stderr)
        return 1

    rlines = roadmap_lines()
    start, end, heading = find_day_block(rlines, day)
    block = rlines[start+1:end]  # lines after the header
    checked, unchecked = parse_checklist(block)
    td_map = parse_td_table()
    note = write_note(day, heading, checked, unchecked, td_map)
    print(f"🧾 EOD note -> {note}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
