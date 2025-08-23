#!/usr/bin/env python3
"""
learning_log.py — aggregate 'Learn:' and 'Next:' trailers from today's commits
and write notes/day{N}-learning.md. Detects the day's start by the commit that
added notes/day{N}-kickoff.md (created by day_start.py).

Usage:
  python tools/learning_log.py [--day N]
"""
from __future__ import annotations
import argparse, subprocess, sys, re
from pathlib import Path
from typing import List, Tuple

REPO = Path(__file__).resolve().parents[1]
NOTES = REPO / "notes"
PLAN = REPO / "meta" / "plan.yml"

def sh(cmd: list[str]) -> str:
    return subprocess.check_output(cmd, text=True).strip()

def current_day_from_plan() -> int | None:
    import yaml  # requires PyYAML
    d = yaml.safe_load((PLAN).read_text(encoding="utf-8")) if PLAN.exists() else {}
    v = d.get("current_day")
    if isinstance(v, int): return v
    if isinstance(v, str) and v.strip().isdigit(): return int(v)
    return None

def kickoff_commit_for(day: int) -> str | None:
    # commit that ADDED the kickoff note
    path = f"notes/day{day}-kickoff.md"
    try:
        out = sh(["git", "log", "--diff-filter=A", "--format=%H", "--", path])
        return out.splitlines()[0] if out else None
    except subprocess.CalledProcessError:
        return None

def commits_since(commit: str) -> List[str]:
    # exclusive of kickoff commit, inclusive of HEAD
    rng = f"{commit}..HEAD" if commit else "HEAD"
    try:
        out = sh(["git", "log", rng, "--pretty=%H"])
        return out.splitlines()[::-1]  # chronological
    except subprocess.CalledProcessError:
        return []

def parse_message(msg: str) -> Tuple[List[str], List[str]]:
    learns, nexts = [], []
    for line in msg.splitlines():
        m = re.match(r"(?i)^\s*Learn\s*:\s*(.+)$", line)
        if m: learns.append(m.group(1).strip())
        m = re.match(r"(?i)^\s*Next\s*:\s*(.+)$", line)
        if m: nexts.append(m.group(1).strip())
    return learns, nexts

def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--day", type=int)
    args = ap.parse_args()

    day = args.day or current_day_from_plan()
    if not day:
        print("❌ Could not determine day (use --day or set current_day in meta/plan.yml).", file=sys.stderr)
        return 1

    kc = kickoff_commit_for(day)
    cs = commits_since(kc) if kc else commits_since("")
    learns: list[str] = []
    nexts: list[str] = []

    for h in cs:
        msg = sh(["git", "log", "-1", "--pretty=%B", h])
        l, n = parse_message(msg)
        learns.extend(l)
        nexts .extend(n)

    NOTES.mkdir(parents=True, exist_ok=True)
    out = NOTES / f"day{day}-learning.md"
    lines = ["# Day {} — Learning Log".format(day), ""]
    lines += ["## What I learned"] + (["- " + x for x in learns] or ["- (add a `Learn:` trailer to a commit)"])
    lines += ["", "## Questions / Next",] + (["- " + x for x in nexts] or ["- (add a `Next:` trailer to a commit)"])
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(str(out))
    return 0

if __name__ == "__main__":
    sys.exit(main())
