#!/usr/bin/env python3
"""
Generate a PR body tailored to CourtIQ's meta/plan.yml schema.

Usage:
  python tools/gen_pr_body.py [--plan META_PATH] [--day N] [--no-git] [--write FILE]

- Reads meta/plan.yml (or --plan path)
- Selects the current day (plan.current_day) or --day override
- Emits a PR body matching .github/pull_request_template.md
- Tries to infer Branch from plan.days[].branch or `git rev-parse --abbrev-ref HEAD`
"""
import argparse
import os
import sys
from typing import Any, Dict, List, Optional
import re

try:
    import yaml  # PyYAML
except Exception as e:
    print("ERROR: PyYAML is required. `pip install pyyaml`", file=sys.stderr)
    sys.exit(2)


TEMPLATE = """### Day & Branch
- **Day:** {day_field}
- **Branch:** {branch_field}

### Scope
- **Objective (from meta/plan.yml):** {objective_field}
- **Deliverables checked:**
{deliverables_block}

### Tech Debt
- **Resolves TD:** {td_resolve_field}
- **Adds TD:** {td_add_field}

### Validation (run locally before opening PR)
- [ ] `python tools/validate_structure.py` passed
- [ ] `python tools/validate_plan.py` passed
- [ ] `pytest -q` passed
- [ ] Docs updated where needed (README / ROADMAP / TECH_DEBT)

### Notes / Screenshots (optional)
<!-- Add any context, screenshots, or follow-ups here -->
""".rstrip()


def load_plan(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def guess_branch(use_git: bool) -> str:
    if not use_git:
        return ""
    try:
        import subprocess
        b = subprocess.check_output(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()
        return b
    except Exception:
        return ""


def find_day(plan: Dict[str, Any], day_override: Optional[int]) -> Dict[str, Any]:
    days = plan.get("days", []) or []
    target = day_override if day_override is not None else plan.get("current_day")
    if target is None:
        return {}
    # tolerate string or int in YAML
    def norm(x):
        try:
            return int(x)
        except Exception:
            return x
    target_norm = norm(target)
    for d in days:
        if norm(d.get("day")) == target_norm:
            return d
    # fallback: first matching by index (rare)
    return {}


def fmt_checklist(items: List[str]) -> str:
    if not items:
        return "  - [ ] …"
    lines = []
    for it in items:
        it = str(it).strip()
        if not it:
            continue
        # If caller already included checkbox syntax, keep it, else add unchecked box
        if it.lstrip().startswith("- ["):
            lines.append(f"  {it}")
        else:
            lines.append(f"  - [ ] {it}")
    return "\n".join(lines) if lines else "  - [ ] …"

def extract_day_section(markdown: str, day: int) -> str:
    """
    Return the markdown slice for '## Day {day} …' up to (but not including) the next '## ' heading.
    If not found, return empty string.
    """
    # Start of section
    start_pat = re.compile(rf"^##\s*Day\s+{re.escape(str(day))}\b.*$", re.IGNORECASE | re.MULTILINE)
    m = start_pat.search(markdown)
    if not m:
        return ""
    start_idx = m.start()
    # Next section
    next_pat = re.compile(r"^##\s+.*$", re.MULTILINE)
    m_next = next_pat.search(markdown, m.end())
    end_idx = m_next.start() if m_next else len(markdown)
    return markdown[start_idx:end_idx]


def roadmap_has_objective(roadmap_text: str, day: int, objective: str) -> bool:
    """
    Check that the Day N section contains an 'Objective' line including the objective string (case-insensitive substring).
    Accepts variations like:
      **Objective:** …
      Objective: …
    """
    section = extract_day_section(roadmap_text, day)
    if not section:
        return False
    # Find a line starting with (optional bold) Objective:
    obj_line_pat = re.compile(r"^\s*(\*\*)?\s*Objective\s*:\s*(.*)$", re.IGNORECASE | re.MULTILINE)
    m = obj_line_pat.search(section)
    if not m:
        return False
    line_val = m.group(2).strip()
    return objective.strip().lower() in line_val.lower()

def main(argv=None):
    p = argparse.ArgumentParser()
    p.add_argument("--plan", default="meta/plan.yml", help="Path to meta/plan.yml")
    p.add_argument("--day", type=int, help="Override day number")
    p.add_argument("--no-git", action="store_true", help="Skip git branch detection")
    p.add_argument("--write", help="Write output to file instead of stdout")
    args = p.parse_args(argv)

    # Load plan
    try:
        plan = load_plan(args.plan)
    except FileNotFoundError:
        # Graceful fallback emitting placeholders
        plan = {}

    day_obj = find_day(plan, args.day)
    current_day = day_obj.get("day") or plan.get("current_day") or "<fill>"
    branch = day_obj.get("branch") or guess_branch(not args.no_git) or "<fill>"
    objective = day_obj.get("objective") or "<fill>"
    deliverables = day_obj.get("deliverables", []) or []
    td_resolve = day_obj.get("tech_debt_resolve", []) or []
    td_add = day_obj.get("tech_debt_add", []) or []

    body = TEMPLATE.format(
        day_field=current_day,
        branch_field=branch,
        objective_field=objective,
        deliverables_block=fmt_checklist(deliverables),
        td_resolve_field=", ".join(map(str, td_resolve)) if td_resolve else "<none>",
        td_add_field=", ".join(map(str, td_add)) if td_add else "<none>",
    ).rstrip()

    if args.write:
        os.makedirs(os.path.dirname(args.write) or ".", exist_ok=True)
        with open(args.write, "w", encoding="utf-8") as f:
            f.write(body + "\n")
    else:
        print(body)


if __name__ == "__main__":
    sys.exit(main())
