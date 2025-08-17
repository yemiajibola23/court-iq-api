# Pre-commit Hooks (CourtIQ)

Pre-commit runs checks **before** a commit lands. It prevents “oops” commits and keeps the repo aligned with our plan.

## What it does here
- Runs validators for repo **structure** and **plan alignment**
- Can run linters/formatters (add as needed)
- Fails fast locally with clear messages

## One-time setup
```bash
pip install pre-commit
pre-commit install
# Optional: run on the whole repo once
pre-commit run --all-files
```

## Daily use
---------

-   Just commit like normal: `git commit -m "feat(...): ..."`

-   If a hook fails, fix what it says, then re-commit.

## Typical hooks we run
--------------------

-   **validate-structure** → checks folder/files match our manifest

-   **validate-plan** → ensures `meta/plan.yml (current_day)` matches:

    -   `ROADMAP.md` → has **Day N** and an **Objective** line containing the objective string

    -   `TECH_DEBT.md` → has the items listed in `tech_debt_resolve` (marked ✅ Resolved) and `tech_debt_add`(present)

> Tip: You can run validators directly:\
> `python tools/validate_structure.py`\
> `python tools/validate_plan.py`

## Common fixes (fast path)
------------------------

-   **Plan mismatch** → Update `ROADMAP.md` "Day N" objective text to match `meta/plan.yml`.

-   **Tech debt drift** → Use our CLI:\
    `python tools/tech_debt.py sync`\
    Or resolve/add specific TDs with `resolve` / `add`.

-   **Missing tools** → `pip install -r requirements-dev.txt` (includes `pre-commit`, `pytest`, `PyYAML`).

## Advanced
--------

-   See installed hooks & config:\
    `pre-commit validate-config && pre-commit list-hooks`

-   Run a single hook on all files:\
    `pre-commit run <hook-id> --all-files`

-   Upgrade hooks:\
    `pre-commit autoupdate` (then commit the version bumps)

## FAQ
---

**Q: Can I skip hooks?**\
A: Only in emergencies: `git commit --no-verify`. CI will still run checks.

**Q: When do hooks run?**\
A: On the **commit** stage by default. You can also configure a **push** stage if desired.

**Q: Where's the config?**\
A: `.pre-commit-config.yaml` in the repo root