# YAML Guide (CourtIQ)

This is a **practical** YAML crash course tied to the files in this repo.  
By the end, you’ll be able to read and modify our YAML with confidence.

---

## 1) meta/plan.yml — the single source of truth

**What it controls**
- `current_day` → which day validators enforce
- `days[]` → drives PR body generation, docs alignment, and tech-debt syncing

**Key fields we use**
```yaml
current_day: 10          # validators only check this day
days:
  - day: 10
    branch: feat/validation-clamps
    objective: Validation polish + list clamps
    deliverables:
      - Harden video_path validation (https-only; len ≤ 2048; ext in {.mp4,.mov,.m4v,.webm})
      - List default limit = 10; clamp to [1,100]
      - Optional hasMore boolean in list response
    tech_debt_resolve: [TD2, TD18]   # must be ✅ in TECH_DEBT.md
    tech_debt_add:     [TD9]         # must exist (can be Pending)
```
**Tips**

-   Lists use `-` (dash). Inline lists are allowed: `[TD2, TD18]`.

-   Indentation matters. Use **2 spaces** per level (no tabs).

-   Strings with `:` are fine unquoted in YAML as long as they don't look like keys.

* * * * *

### 2) .pre-commit-config.yaml --- local checks before commit
**What it controls**

-   Which hooks run (and when), mapped to scripts or tools.

**Minimal config we use**
```yaml
repos:
  - repo: local
    hooks:
      - id: validate-structure
        name: validate structure
        entry: python tools/validate_structure.py
        language: system
        pass_filenames: false

      - id: validate-plan
        name: validate plan vs roadmap/tech_debt
        entry: python tools/validate_plan.py
        language: system
        pass_filenames: false
```
**Tips**

-   `repo: local` means "run a command from our repo", not a remote hook.

-   `pass_filenames: false` prevents pre-commit from appending file paths to our command.

-   Optional: add `stages: [commit, push]` if you want hooks to run on push too.

### 3) GitHub Actions workflow --- CI for validators/tests

**What it controls**

-   When CI runs and what jobs it executes on PRs.

**Example:** `.github/workflows/plan-validate.yml`

```yaml
name: Plan & Structure Validation
on:
  pull_request:
    paths:
      - "meta/**"
      - "TECH_DEBT.md"
      - "ROADMAP.md"
      - "tools/**"
      - ".github/workflows/plan-validate.yml"

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.12" }
      - run: pip install -r requirements-dev.txt || true
      - name: Validate structure
        run: python tools/validate_structure.py
      - name: Validate plan alignment
        run: python tools/validate_plan.py

```

**Tips**

-   `on.pull_request.paths` lets us run only when relevant files change (faster CI).

-   Reusable `actions/*` are referenced with `uses:`.

-   Each `run:` line runs a shell command in the runner VM.

* * * * *

4) YAML gotchas (quick cheats)
------------------------------

-   **Indentation**: 2 spaces per level; tabs will break parsers.

-   **Booleans**: `true/false` (lowercase) are real booleans; `"true"` (quoted) is a string.

-   **Strings**: Quote only when needed (special characters, leading `[` or `{`, trailing spaces).

-   **Anchors & aliases**: Advanced YAML feature to reuse blocks. We avoid them here for clarity.

* * * * *

Practice (do it once)
---------------------

1.  Open `meta/plan.yml`. Change `current_day` to a day you're working on.

2.  Add a dummy TD to `tech_debt_add` (`TD99`) and run:

    `python tools/tech_debt.py sync`

    Confirm `TECH_DEBT.md` now contains `TD99` as Pending.

3.  Open `.pre-commit-config.yaml` and run:

    `pre-commit validate-config && pre-commit list-hooks`

4.  Skim a workflow in `.github/workflows/` and identify each step's purpose.
---
