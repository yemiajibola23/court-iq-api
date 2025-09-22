# Automation Scripts Reference

## Contents
- [Python tools](#python-tools)
  - [tools/commit_effects.py](#sec-tools-commit-effects-py)
  - [tools/day_start.py](#sec-tools-day-start-py)
  - [tools/docgen_scripts.py](#sec-tools-docgen-scripts-py)
  - [tools/ensure_day_in_roadmap.py](#sec-tools-ensure-day-in-roadmap-py)
  - [tools/eod.py](#sec-tools-eod-py)
  - [tools/gen_pr_body.py](#sec-tools-gen-pr-body-py)
  - [tools/learning_log.py](#sec-tools-learning-log-py)
  - [tools/plan_td_update.py](#sec-tools-plan-td-update-py)
  - [tools/tech_debt.py](#sec-tools-tech-debt-py)
  - [tools/validate_plan.py](#sec-tools-validate-plan-py)
  - [tools/validate_structure.py](#sec-tools-validate-structure-py)
- [Shell scripts](#shell-scripts)
  - [scripts/onboard.sh](#sec-scripts-onboard-sh)
  - [scripts/open_pr.sh](#sec-scripts-open-pr-sh)

## Python tools

### `tools/commit_effects.py`
<a id="sec-tools-commit-effects-py"></a>
_Source: [tools/commit_effects.py](https://github.com/yemiajibola23/court-iq-api/blob/dev/tools/commit_effects.py)_

_Summary:_

commit_effects.py — auto-checkoff ROADMAP subtasks (D##-#) and mark TECH_DEBT rows
as resolved based on commit messages.

Usage with pre-commit:

  stages: [commit-msg]   # recommended
  pass_filenames: true   # pre-commit passes the temp commit message file

Message conventions:
  - Include subtasks anywhere:        D11-2
  - Include trailer for tech debt:    Resolves-TD: TD4, TD9, TD12

**`--help` output:**

```text
[commit-effects] ids_to_tick=[]
```

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

### `tools/ensure_day_in_roadmap.py`
<a id="sec-tools-ensure-day-in-roadmap-py"></a>
_Source: [tools/ensure_day_in_roadmap.py](https://github.com/yemiajibola23/court-iq-api/blob/dev/tools/ensure_day_in_roadmap.py)_

**`--help` output:**

```text
(no help output)
```

### `tools/eod.py`
<a id="sec-tools-eod-py"></a>
_Source: [tools/eod.py](https://github.com/yemiajibola23/court-iq-api/blob/dev/tools/eod.py)_

_Summary:_

eod.py — End-of-Day helper:
- Reads meta/plan.yml (or --day) to locate today's Day block in ROADMAP.md
- Summarizes checked/unchecked subtasks
- Summarizes TDs in today's block (resolved vs pending from TECH_DEBT.md)
- Writes notes/day{N}-eod.md

**`--help` output:**

```text
usage: eod.py [-h] [--day DAY]

options:
  -h, --help  show this help message and exit
  --day DAY   Day number (defaults to plan.yml current_day)
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

### `tools/learning_log.py`
<a id="sec-tools-learning-log-py"></a>
_Source: [tools/learning_log.py](https://github.com/yemiajibola23/court-iq-api/blob/dev/tools/learning_log.py)_

_Summary:_

learning_log.py — aggregate 'Learn:' and 'Next:' trailers from today's commits
and write notes/day{N}-learning.md. Detects the day's start by the commit that
added notes/day{N}-kickoff.md (created by day_start.py).

Usage:
  python tools/learning_log.py [--day N]

**`--help` output:**

```text
usage: learning_log.py [-h] [--day DAY]

options:
  -h, --help  show this help message and exit
  --day DAY
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

tech_debt.py — manage TECH_DEBT.md rows and (optionally) mirror as ROADMAP subtasks.

Commands:
  list                                Show parsed TECH_DEBT rows
  add --desc ... --when "Day N"       Add a new row (auto TD id) and append a ROADMAP checklist line
    [--status Pending] [--scope storage] [--no-roadmap] [--preview] [--yes] [--no-write]
  sync [--day N] [--apply]            Cross-check plan.yml (current day by default) vs ROADMAP vs TECH_DEBT
    [--scope storage] [--no-roadmap-write] [--no-plan-write]

Row format in TECH_DEBT.md (pipe table):
  | TD5  | Description here | Day 12 | Pending |

ROADMAP checklist line we write:
  - [ ] 💳 techdebt(scope): Description here (TD5)
or (when no scope)
  - [ ] 💳 techdebt: Description here (TD5)

**`--help` output:**

```text
usage: tech_debt.py [-h] {list,add,sync} ...

Manage TECH_DEBT.md (and optional ROADMAP checklist lines).

positional arguments:
  {list,add,sync}
    list           List rows from TECH_DEBT.md
    add            Add a new TECH_DEBT row (auto-increment id) and append a
                   ROADMAP checklist line
    sync           Cross-check plan.yml (tech_debt_resolve) vs today's ROADMAP
                   vs TECH_DEBT; optionally apply fixes

options:
  -h, --help       show this help message and exit
```

### `tools/validate_plan.py`
<a id="sec-tools-validate-plan-py"></a>
_Source: [tools/validate_plan.py](https://github.com/yemiajibola23/court-iq-api/blob/dev/tools/validate_plan.py)_

_Summary:_

# --------------------------- parsing helpers ---------------------------

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
usage: validate_plan.py [-h] [--allow-prefix ALLOW_PREFIX]
                        [--allow-trailer ALLOW_TRAILER]
                        [--commit-msg-file COMMIT_MSG_FILE]

Validate that today's plan (meta/plan.yml) matches TECH_DEBT.md and
ROADMAP.md. Checks: 1) Every TD in today's `tech_debt_resolve` exists in
TECH_DEBT.md and is marked Resolved. 2) Every TD in today's `tech_debt_add`
exists in TECH_DEBT.md (status can be Pending). 3) ROADMAP.md contains a Day
<current_day> section AND includes today's objective text. Skip conditions
(non-fatal): - --allow-prefix <prefix> (repeatable): if commit subject starts
with any prefix - --allow-trailer key:value (repeatable): if commit trailers
include key with a truthy value

options:
  -h, --help            show this help message and exit
  --allow-prefix ALLOW_PREFIX
                        If the commit SUBJECT starts with any of these
                        prefixes, skip validation. Repeatable.
  --allow-trailer ALLOW_TRAILER
                        If commit trailers contain key:true for any of these
                        keys, skip validation. Format key:value or key=value;
                        value treated as truthy when in {true,1,yes,on}.
                        Repeatable.
  --commit-msg-file COMMIT_MSG_FILE
                        Optional path to the commit message file (commit-msg
                        hook). If omitted, we try .git/COMMIT_EDITMSG. Any
                        extra positional arg that is a file is also used.
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

Open a PR with a body generated from meta/plan.yml (and optionally EOD note)
Works with Make targets:
make pr-body DAY=11  -> writes notes/pr/day11-pr.md
make eod-pr DAY=11   -> calls this script with --body-file ...

Usage:
scripts/open_pr.sh [--day N] [--base dev] [--draft] \
[--labels "a,b"] [--reviewers "u1,u2"] \
[--title "Day N: ..."] [--body-file path] [--no-push]

Requires: gh (authenticated), Python (PyYAML), tools/gen_pr_body.py

**`--help` output:**

```text
Usage:
  scripts/open_pr.sh [--day N] [--base dev] [--draft]
                     [--labels "label1,label2"] [--reviewers "alice,bob"]
                     [--title "Day N: Title"] [--body-file path] [--no-push]

Notes:
  - --labels is optional and may be provided with or without a value.
    * With a value (e.g., --labels "l1,l2"): applies those labels.
    * Without a value (e.g., --labels): applies no labels.
  - --reviewers requires a value if provided.

Behavior:
  - Determines day from --day or meta/plan.yml (current_day)
  - Title defaults to "Day N: <ROADMAP heading>" when possible
  - Body comes from:
      1) --body-file, or
      2) notes/pr/dayN-pr.md (if present), or
      3) generated via tools/gen_pr_body.py --day N
  - Pushes current branch and opens a PR to --base
```
---
_Generated on 2025-09-22T00:24:47_
