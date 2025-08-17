# Automation Scripts Reference

## Contents
- [Python tools](#python-tools)
  - [tools/docgen_scripts.py](#sec-tools-docgen-scripts-py)
  - [tools/gen_pr_body.py](#sec-tools-gen-pr-body-py)
  - [tools/tech_debt.py](#sec-tools-tech-debt-py)
  - [tools/validate_plan.py](#sec-tools-validate-plan-py)
  - [tools/validate_structure.py](#sec-tools-validate-structure-py)
- [Shell scripts](#shell-scripts)
  - [scripts/onboard.sh](#sec-scripts-onboard-sh)
  - [scripts/open_pr.sh](#sec-scripts-open-pr-sh)

## Python tools

### `tools/docgen_scripts.py`
<a id="sec-tools-docgen-scripts-py"></a>
_Source: [tools/docgen_scripts.py](tools/docgen_scripts.py)_

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
_Source: [tools/gen_pr_body.py](tools/gen_pr_body.py)_

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

### `tools/tech_debt.py`
<a id="sec-tools-tech-debt-py"></a>
_Source: [tools/tech_debt.py](tools/tech_debt.py)_

_Summary:_

CourtIQ Tech Debt CLI

Automations for TECH_DEBT.md:
- Parse/update the main Markdown table
- Resolve/add items quickly
- Sync with meta/plan.yml (resolve/add for current day)

Usage examples:
  # View table
  python tools/tech_debt.py list

  # Resolve a TD
  python tools/tech_debt.py resolve TD2

  # Add a new TD row
  python tools/tech_debt.py add --id TD19 --desc "Normalize error envelope to arrays" --when "Day 11" --status Pending

  # Set explicit status
  python tools/tech_debt.py set-status TD2 Resolved

  # Sync from plan.yml (applies tech_debt_resolve/add for current_day)
  python tools/tech_debt.py sync --plan meta/plan.yml

  # Preview changes only
  python tools/tech_debt.py sync --dry-run

**`--help` output:**

```text
usage: tech_debt.py [-h] {list,set-status,resolve,add,sync} ...

CourtIQ Tech Debt CLI

positional arguments:
  {list,set-status,resolve,add,sync}
    list                List TD rows
    set-status          Set a TD status (Pending, In-Progress, ✅ Resolved)
    resolve             Mark a TD as ✅ Resolved
    add                 Add a new TD row
    sync                Align TECH_DEBT.md with meta/plan.yml (current_day)

options:
  -h, --help            show this help message and exit
```

### `tools/validate_plan.py`
<a id="sec-tools-validate-plan-py"></a>
_Source: [tools/validate_plan.py](tools/validate_plan.py)_

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
_Source: [tools/validate_structure.py](tools/validate_structure.py)_

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
_Source: [scripts/onboard.sh](scripts/onboard.sh)_

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
_Source: [scripts/open_pr.sh](scripts/open_pr.sh)_

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
_Generated on 2025-08-16T20:16:12_
