#!/usr/bin/env python3
import re
import sys
import subprocess
from pathlib import Path

# --- Project files
REPO = Path(__file__).resolve().parents[1]
ROADMAP = REPO / "ROADMAP.md"
TECH_DEBT = REPO / "TECH_DEBT.md"
_UNCHECKED_BOX = re.compile(r"^(\s*)-\s\[\s\]\s")  # allows leading spaces

# --- Regexes
RE_SUBTASK = re.compile(r"\bD(\d+)-(\d+)\b")              # D11-2
RE_RESOLVE_TRAILER = re.compile(r"(?mi)^\s*Resolves-TD:\s*(.+)$")  # list like: TD1, TD13
RE_TD_ID = re.compile(r"\bTD(\d+)\b")

def sh(args, capture=False, check=True):
    if capture:
        return subprocess.run(args, check=check, text=True, stdout=subprocess.PIPE).stdout
    subprocess.run(args, check=check)

def last_commit_message():
    return sh(["git", "log", "-1", "--pretty=%B"], capture=True)

def parse_tokens(msg):
    subtasks = set(f"D{d}-{n}" for d, n in RE_SUBTASK.findall(msg))
    td_resolves = set()
    for m in RE_RESOLVE_TRAILER.findall(msg):
        td_resolves |= set("TD" + n for n in RE_TD_ID.findall(m))
    return sorted(subtasks), sorted(td_resolves)

NBSP = "\xa0"  # non-breaking space, often sneaks in from editors

def tick_ids_in_roadmap(ids: list[str]) -> bool:
    """Tick any unchecked checklist line that contains one of the ids (D##-# or TD#) anywhere."""
    if not ids or not ROADMAP.exists():
        return False
    lines = ROADMAP.read_text(encoding="utf-8").splitlines()

    changed = False
    for i, ln in enumerate(lines):
        # allow indentation with spaces/tabs/NBSPs
        lstrip = ln.lstrip(" \t" + NBSP)
        if not lstrip.startswith("- [ ] "):
            continue

        # substring is more robust than regex here; also check "(ID)"
        for tok in ids:
            if tok in ln or f"({tok})" in ln:
                # flip only the *leading* checkbox, preserve original indentation
                lines[i] = _UNCHECKED_BOX.sub(r"\1- [x] ", ln, count=1)
                changed = True
                break

    if changed:
        ROADMAP.write_text("\n".join(lines), encoding="utf-8")
    return changed


def resolve_td_in_table(td_ids: list[str]) -> bool:
    if not td_ids or not TECH_DEBT.exists():
        return False
    lines = TECH_DEBT.read_text().splitlines()
    changed = False

    # Table row shape: | TD5  | Description | When | Status |
    for idx, ln in enumerate(lines):
        m = re.match(r"^\|\s*(TD\d+)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|$", ln)
        if not m:
            continue
        td_id, desc, when, status = m.groups()
        if td_id in td_ids and "✅" not in status:
            status_new = "✅ Resolved"
            lines[idx] = f"| {td_id} | {desc} | {when} | {status_new} |"
            changed = True

    if changed:
        TECH_DEBT.write_text("\n".join(lines))
    return changed

def amend_if_changes():
    # Stage and amend only if there is a staged diff
    # (avoids infinite loops; second invocation finds nothing → exits)
    sh(["git", "add", str(ROADMAP), str(TECH_DEBT)], check=False)
    # If nothing staged, diff --cached is empty → return
    diff = sh(["git", "diff", "--cached", "--name-only"], capture=True, check=False).strip() # type: ignore
    if not diff:
        return False
    # Amend the previous commit without changing message
    sh(["git", "commit", "--amend", "--no-edit"])
    return True

def main():
    msg = last_commit_message()
    subtasks, td_resolves = parse_tokens(msg)
    
    # Tick both D-ids and any TD-ids we resolved
    ids_to_tick = sorted(set(subtasks) | set(td_resolves))
    changed_roadmap = tick_ids_in_roadmap(ids_to_tick)
    changed_td = resolve_td_in_table(td_resolves)
    
    print(f"[commit-effects] ids_to_tick={ids_to_tick}", file=sys.stderr)

    if changed_roadmap or changed_td:
        amended = amend_if_changes()
        # Print minimal feedback; keeps hooks quiet unless useful
        if amended:
            print(f"[commit-effects] Synced: "
                  f"{'subtasks '+','.join(subtasks) if subtasks else ''}"
                  f"{' and ' if subtasks and td_resolves else ''}"
                  f"{'TD '+','.join(td_resolves) if td_resolves else ''}")
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        # Never block your commit; just print and exit 0
        print(f"[commit-effects] non-fatal error: {e}", file=sys.stderr)
        sys.exit(0)
