# Automation Scripts Reference

## Python tools

### `tools/gen_pr_body.py`

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

_Summary:_

Validate that today's plan (meta/plan.yml) matches TECH_DEBT.md and ROADMAP.md.

Checks:
1) Every TD in today's `tech_debt_resolve` exists in TECH_DEBT.md and is marked Resolved.
2) Every TD in today's `tech_debt_add` exists in TECH_DEBT.md (status can be Pending).
3) ROADMAP.md contains a Day <current_day> section AND includes today's objective text.

**`--help` output:**

```text
✅ Plan validation passed for Day 9
```

### `tools/validate_structure.py`

_Summary:_

Return (missing, satisfied) for required paths. Globs are satisfied if at least one match exists.

**`--help` output:**

```text
✅ Structure validation passed.
```

## Shell scripts

### `scripts/open_pr.sh`

_Summary:_

What: Open a PR using a body auto-generated from meta/plan.yml
Why:  No manual copy/paste of objectives or tech debt
Usage: scripts/open_pr.sh "Day 10: Validation polish"
Requires: gh, Python (PyYAML), and tools/gen_pr_body.py

**`--help` output:**

```text
Warning: 3 uncommitted changes
aborted: you must first push the current branch to a remote, or use the --head flag
```
