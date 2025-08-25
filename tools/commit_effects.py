#!/usr/bin/env python3
"""
commit_effects.py — auto-checkoff ROADMAP subtasks (D##-#) and mark TECH_DEBT rows
as resolved based on commit messages.

Usage with pre-commit:

  stages: [commit-msg]   # recommended
  pass_filenames: true   # pre-commit passes the temp commit message file

Message conventions:
  - Include subtasks anywhere:        D11-2
  - Include trailer for tech debt:    Resolves-TD: TD4, TD9, TD12
"""

import os
import re
import sys
import subprocess
from pathlib import Path

# --- Project files
REPO = Path(__file__).resolve().parents[1]
ROADMAP = REPO / "ROADMAP.md"
TECH_DEBT = REPO / "TECH_DEBT.md"

_UNCHECKED_BOX = re.compile(r"^(\s*)-\s\[\s\]\s")  # allows leading spaces

# --- Regexes (case-insensitive where appropriate)
RE_SUBTASK = re.compile(r"\bD(\d+)-(\d+)\b", re.I)                 # D11-2
RE_RESOLVE_TRAILER = re.compile(r"(?mi)^\s*Resolves-TD:\s*(.+)$")  # list like: TD1, TD13
RE_TD_ID = re.compile(r"\bTD(\d+)\b", re.I)

NBSP = "\xa0"  # non-breaking space, often sneaks in from editors


# ---------------------------- helpers ---------------------------- #

def sh(args, capture=False, check=True):
    if capture:
        return subprocess.run(args, check=check, text=True, stdout=subprocess.PIPE).stdout
    subprocess.run(args, check=check)
    return ""


def _read_file_text(path: str) -> str:
    try:
        return Path(path).read_text(encoding="utf-8")
    except Exception:
        return ""


def resolve_commit_message(argv: list[str]) -> str:
    """
    If invoked as a commit-msg hook under pre-commit, argv[1] is the path to the
    temp commit message file. Fallback to last commit message so this script can
    also be used as a post-commit hook.
    """
    if len(argv) >= 2 and argv[1]:
        text = _read_file_text(argv[1])
        if text.strip():
            return text
    # Fallback (post-commit usage)
    try:
        return sh(["git", "log", "-1", "--pretty=%B"], capture=True)
    except Exception:
        return ""


def parse_tokens(msg: str):
    # Normalize to uppercase IDs; be case-insensitive on capture
    subtasks = {f"D{d}-{n}".upper() for d, n in RE_SUBTASK.findall(msg or "")}
    td_resolves = set()
    for m in RE_RESOLVE_TRAILER.findall(msg or ""):
        td_resolves |= {"TD" + n for n in RE_TD_ID.findall(m)}
    return sorted(subtasks), sorted({t.upper() for t in td_resolves})


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

        for tok in ids:
            # Match tok as a standalone token or in parentheses, case-insensitive
            # Avoid substring collisions (e.g., D1-2 vs D11-2)
            pat = re.compile(rf"(?<!\w)(?:{re.escape(tok)}|\({re.escape(tok)}\))(?!\w)", re.I)
            if pat.search(ln):
                # flip only the *leading* checkbox, preserve original indentation
                lines[i] = _UNCHECKED_BOX.sub(r"\1- [x] ", ln, count=1)
                changed = True
                break

    if changed:
        ROADMAP.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return changed


def resolve_td_in_table(td_ids: list[str]) -> bool:
    if not td_ids or not TECH_DEBT.exists():
        return False
    lines = TECH_DEBT.read_text(encoding="utf-8").splitlines()
    changed = False

    # Table row shape: | TD5  | Description | When | Status |
    target = {t.upper() for t in td_ids}

    for idx, ln in enumerate(lines):
        m = re.match(r"^\|\s*(TD\d+)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|\s*(.*?)\s*\|$", ln, re.I)
        if not m:
            continue
        td_id, desc, when, status = m.groups()
        td_id = td_id.upper()
        if td_id in target and "✅" not in status:
            status_new = "✅ Resolved"
            lines[idx] = f"| {td_id} | {desc} | {when} | {status_new} |"
            changed = True

    if changed:
        TECH_DEBT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return changed


def amend_if_changes():
    # Stage and amend only if there is a staged diff
    # (avoids infinite loops; second invocation finds nothing → exits)
    sh(["git", "add", str(ROADMAP), str(TECH_DEBT)], check=False)
    diff = sh(["git", "diff", "--cached", "--name-only"], capture=True, check=False).strip()
    if not diff:
        return False
    # Guard so we don't recurse on our own amend
    env = dict(os.environ)
    env["COMMIT_EFFECTS_AMEND"] = "1"
    subprocess.run(["git", "commit", "--amend", "--no-edit"], check=True, env=env)
    return True


# ---------------------------- entrypoint ---------------------------- #

def main() -> int:
    # If this amend was triggered by ourselves, skip to avoid loops
    if os.environ.get("COMMIT_EFFECTS_AMEND") == "1":
        return 0

    msg = resolve_commit_message(sys.argv)
    subtasks, td_resolves = parse_tokens(msg)

    # Tick both D-ids and any TD-ids we resolved
    ids_to_tick = sorted(set(subtasks) | set(td_resolves))
    changed_roadmap = tick_ids_in_roadmap(ids_to_tick)
    changed_td = resolve_td_in_table(td_resolves)

    print(f"[commit-effects] ids_to_tick={ids_to_tick}", file=sys.stderr)

    if changed_roadmap or changed_td:
        amended = amend_if_changes()
        if amended:
            # Minimal feedback; keeps hooks quiet unless useful
            left = f"subtasks {', '.join(subtasks)}" if subtasks else ""
            right = f"TD {', '.join(td_resolves)}" if td_resolves else ""
            mid = " and " if left and right else ""
            print(f"[commit-effects] Synced: {left}{mid}{right}", file=sys.stderr)

    return 0


if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        # Never block your commit; just print and exit 0
        print(f"[commit-effects] non-fatal error: {e}", file=sys.stderr)
        sys.exit(0)
