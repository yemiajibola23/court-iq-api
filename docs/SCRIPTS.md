# Automation Scripts Reference

## Contents
- [Python tools](#python-tools)
  - [tools/day_start.py](#sec-tools-day-start-py)
  - [tools/docgen_scripts.py](#sec-tools-docgen-scripts-py)
  - [tools/gen_pr_body.py](#sec-tools-gen-pr-body-py)
  - [tools/plan_td_update.py](#sec-tools-plan-td-update-py)
  - [tools/tech_debt.py](#sec-tools-tech-debt-py)
  - [tools/validate_plan.py](#sec-tools-validate-plan-py)
  - [tools/validate_structure.py](#sec-tools-validate-structure-py)
- [Shell scripts](#shell-scripts)
  - [scripts/onboard.sh](#sec-scripts-onboard-sh)
  - [scripts/open_pr.sh](#sec-scripts-open-pr-sh)

## Python tools

### `tools/day_start.py`
<a id="sec-tools-day-start-py"></a>
_Source: [tools/day_start.py](https://github.com/yemiajibola23/court-iq-api/blob/dev/tools/day_start.py)_

_Summary:_

Day Start v2 — streamlines the daily kickoff:
- Sets meta/plan.yml current_day
- Ensures ROADMAP.md has Day N section + Objective line (from plan.yml)
- Creates or checks out the branch (from plan.yml days[].branch if present; else {type}/{desc})
- Emits a kickoff block and writes notes/day{N}-kickoff.md

**`--help` output:**

```text
usage: day_start.py [-h] --day DAY
                    [--type {feat,test,docs,refactor,chore,fix,perf}]
                    [--desc DESC] [--dry-run]

options:
  -h, --help            show this help message and exit
  --day DAY
  --type {feat,test,docs,refactor,chore,fix,perf}
  --desc DESC
  --dry-run
```

### `tools/docgen_scripts.py`
<a id="sec-tools-docgen-scripts-py"></a>
_Source: [tools/docgen_scripts.py](https://github.com/yemiajibola23/court-iq-api/blob/dev/tools/docgen_scripts.py)_

_Summary:_

Script Docs Generator (polished)

Features:
- Contents section with explicit, stable anchors (works in VSCode & GitHub)
- "Source:" link on its own line (no nested backticks in headers)
- Deterministic ordering by filename
- Clamp long --help output (default 60 lines) to keep docs readable
- Optional GitHub linkification via --repo-url / --default-branch

Usage:
  python tools/docgen_scripts.py \
      --out docs/SCRIPTS.md \
      --py-glob "tools/*.py" \
      --sh-glob "scripts/*.sh" \
      --clamp 60 \
      [--repo-url https://github.com/OWNER/REPO] \
      [--default-branch main]

**`--help` output:**

```text
usage: docgen_scripts.py [-h] [--out OUT] [--py-glob PY_GLOB]
                         [--sh-glob SH_GLOB] [--clamp CLAMP]
                         [--repo-url REPO_URL]
                         [--default-branch DEFAULT_BRANCH] [--check]

options:
  -h, --help            show this help message and exit
  --out OUT
  --py-glob PY_GLOB
  --sh-glob SH_GLOB
  --clamp CLAMP
  --repo-url REPO_URL   e.g. https://github.com/OWNER/REPO
  --default-branch DEFAULT_BRANCH
  --check               Check if output would change; do not write; exit 1 if
                        different
```

### `tools/gen_pr_body.py`
<a id="sec-tools-gen-pr-body-py"></a>
_Source: [tools/gen_pr_body.py](https://github.com/yemiajibola23/court-iq-api/blob/dev/tools/gen_pr_body.py)_

_Summary:_

Generate a PR body tailored to CourtIQ's meta/plan.yml schema.

Usage:
  python tools/gen_pr_body.py [--plan META_PATH] [--day N] [--no-git] [--write FILE]

- Reads meta/plan.yml (or --plan path)
- Selects the current day (plan.current_day) or --day override
- Emits a PR body matching .github/pull_request_template.md
- Tries to infer Branch from plan.days[].branch or `git rev-parse --abbrev-ref HEAD`

**`--help` output:**

```text
usage: gen_pr_body.py [-h] [--plan PLAN] [--day DAY] [--no-git]
                      [--write WRITE]

options:
  -h, --help     show this help message and exit
  --plan PLAN    Path to meta/plan.yml
  --day DAY      Override day number
  --no-git       Skip git branch detection
  --write WRITE  Write output to file instead of stdout
```

### `tools/plan_td_update.py`
<a id="sec-tools-plan-td-update-py"></a>
_Source: [tools/plan_td_update.py](https://github.com/yemiajibola23/court-iq-api/blob/dev/tools/plan_td_update.py)_

_Summary:_

Update meta/plan.yml TD lists for a given day (defaults to current_day).

Usage:
  # Add TDs to Day 15 (tech_debt_add)
  python tools/plan_td_update.py --day 15 --add TD42 TD43

  # Mark TDs resolved on Day 12
  python tools/plan_td_update.py --day 12 --resolve TD7

  # No --day provided -> uses current_day in plan.yml

**`--help` output:**

```text
usage: plan_td_update.py [-h] [--plan PLAN] [--day DAY] [--add [ADD ...]]
                         [--resolve [RESOLVE ...]]

options:
  -h, --help            show this help message and exit
  --plan PLAN
  --day DAY             Day number to update (default: current_day)
  --add [ADD ...]       TD ids to add under tech_debt_add
  --resolve [RESOLVE ...]
                        TD ids to add under tech_debt_resolve
```

### `tools/tech_debt.py`
<a id="sec-tools-tech-debt-py"></a>
_Source: [tools/tech_debt.py](https://github.com/yemiajibola23/court-iq-api/blob/dev/tools/tech_debt.py)_

_Summary:_

CourtIQ Tech Debt CLI

Subcommands:
  list                List TD rows (raw table lines)
  set-status          Set a TD status (Pending | In-Progress 🔧 | ✅ Resolved)
  resolve             Convenience alias for set-status <id> "✅ Resolved"
  add                 Add a new TD row (auto-increment id)
  sync                Align TECH_DEBT.md with meta/plan.yml (current_day)

Highlights:
- `add` always auto-increments the id from the last table row (TDn -> TDn+1)
- `add` supports --preview (with optional --yes confirm), and --no-write
- Status normalization (accepts common variants for in-progress/resolved)
- `sync`:
    * For plan.days[current_day].tech_debt_resolve[] → mark as ✅ Resolved
    * For plan.days[current_day].tech_debt_add[]     → ensure present (Pending)
- Emits NEW_TD_ID=TD## after a successful `add`

**`--help` output:**

```text
usage: tech_debt.py [-h] {list,set-status,resolve,add,sync} ...

CourtIQ Tech Debt CLI

positional arguments:
  {list,set-status,resolve,add,sync}
    list                List TD rows
    set-status          Set a TD status (Pending, In-Progress, ✅ Resolved)
    resolve             Mark a TD as ✅ Resolved
    add                 Add a new TECH_DEBT row (auto-increment id)
    sync                Align TECH_DEBT.md with meta/plan.yml (current_day)

options:
  -h, --help            show this help message and exit
```

### `tools/validate_plan.py`
<a id="sec-tools-validate-plan-py"></a>
_Source: [tools/validate_plan.py](https://github.com/yemiajibola23/court-iq-api/blob/dev/tools/validate_plan.py)_

_Summary:_

def load_plan(path: Path) -> Dict[str, Any]:
    if not path.exists():
        fail([f"Missing plan file: {path}"])
    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except Exception as e:
        fail([f"Failed to parse {path}: {e}"])

def parse_tech_debt_table(md_text: str) -> Dict[str, Dict[str, str]]:

**`--help` output:**

```text
usage: validate_plan.py [-h]

Validate that today's plan (meta/plan.yml) matches TECH_DEBT.md and
ROADMAP.md. Checks: 1) Every TD in today's `tech_debt_resolve` exists in
TECH_DEBT.md and is marked Resolved. 2) Every TD in today's `tech_debt_add`
exists in TECH_DEBT.md (status can be Pending). 3) ROADMAP.md contains a Day
<current_day> section AND includes today's objective text.

options:
  -h, --help  show this help message and exit
```

### `tools/validate_structure.py`
<a id="sec-tools-validate-structure-py"></a>
_Source: [tools/validate_structure.py](https://github.com/yemiajibola23/court-iq-api/blob/dev/tools/validate_structure.py)_

_Summary:_

Return (missing, satisfied) for required paths. Globs are satisfied if at least one match exists.

**`--help` output:**

```text
usage: validate_structure.py [-h]

Validate required repo structure and paths. Globs are satisfied if at least
one match exists.

options:
  -h, --help  show this help message and exit
```

## Shell scripts

### `scripts/onboard.sh`
<a id="sec-scripts-onboard-sh"></a>
_Source: [scripts/onboard.sh](https://github.com/yemiajibola23/court-iq-api/blob/dev/scripts/onboard.sh)_

_Summary:_

What: One-shot setup for a fresh clone (venv, dev deps, pre-commit)
Why:  Make onboarding and context switching painless & consistent
Usage: scripts/onboard.sh

**`--help` output:**

```text
Usage: scripts/onboard.sh

What: One-shot setup for a fresh clone (venv, dev deps, pre-commit)
Why:  Make onboarding and context switching painless & consistent

Steps:
  - Create/activate .venv
  - Upgrade pip
  - Install (dev) requirements
  - Install pre-commit and hooks
  - (Optional) pre-commit run --all-files
  - Quick smoke checks
```

### `scripts/open_pr.sh`
<a id="sec-scripts-open-pr-sh"></a>
_Source: [scripts/open_pr.sh](https://github.com/yemiajibola23/court-iq-api/blob/dev/scripts/open_pr.sh)_

_Summary:_

What: Open a PR using a body auto-generated from meta/plan.yml
Why:  No manual copy/paste of objectives or tech debt
Usage: scripts/open_pr.sh "Day 10: Validation polish"
Requires: gh, Python (PyYAML), and tools/gen_pr_body.py

**`--help` output:**

```text
Usage: scripts/open_pr.sh "Day <N>: <Short title>"

Requires:
  - gh (GitHub CLI), authenticated
  - python + tools/gen_pr_body.py

Behavior:
  - Generates PR body from meta/plan.yml
  - Creates PR with provided title

Examples:
  scripts/open_pr.sh "Day 10: Validation polish"
```
---
_Generated on 2025-08-20T13:49:22_
