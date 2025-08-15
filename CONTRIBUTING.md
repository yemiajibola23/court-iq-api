# Contributing Guidelines

Welcome! This document explains how to work on this project so we keep a consistent, high-quality workflow across all contributors.

---

## 1. Branch Naming Convention

Branches follow this pattern:
`<type>/<short-description>`

**Types**:
- `feat` — New feature
- `fix` — Bug fix
- `chore` — Tooling/infra changes (no behavior change)
- `docs` — Documentation changes only
- `refactor` — Code changes that don’t alter behavior
- `test` — Adding or updating tests
- `perf` — Performance improvements

**Examples**:
```
feat/add-play-upload
fix/video-processing-bug
docs/update-readme
```
> **Tip:** Keep branch names short and descriptive.

---

## 2. Commit Message Convention (Conventional Commits)

We follow the **Conventional Commits** format:
`<type>(optional scope): short summary`

Body (optional): why + context

### Common Types
- **feat** — new user-visible functionality
- **fix** — bug fix
- **chore** — tooling/infra
- **docs** — documentation only
- **refactor** — internal restructure
- **test** — add/adjust tests
- **perf** — performance improvement

**Examples**:
```
feat(api): add POST /v1/plays
fix(upload): handle empty title with 422
chore(ci): add backend pytest workflow
```

**Rules**:
- Max ~72 characters in the summary.
- Use present tense (“add”, “fix”, not “added”, “fixes”).
- Each commit should represent a coherent change.

---
## 3. Pull Request (PR) Rules

- **One PR = One purpose**
- Keep PRs small and reviewable (~10 min read max)
- Always open a PR (even if working solo)
- Match PR title to branch name purpose
- Include:
  - Summary (2–4 bullets on *what* and *why*)
  - Changes list (notable code areas touched)
  - Verification steps (commands, simulator steps, curl requests)
  - Screenshots or logs if applicable
- All tests must pass locally before marking ready
- Use **Squash Merge** with a Conventional Commit title

For more detail, see [`docs/WORKFLOW.md`](docs/WORKFLOW.md).

---

## 4. Testing Requirements

- **Backend**: Run `pytest` locally before committing.
- **iOS**: Run all Xcode tests before committing.
- Write new tests for any new functionality.
- Update existing tests if functionality changes.

---

## 5. Repo-Specific Setup

### Backend (court-iq-api)
- **Environment**: Python 3.12, `pip install -r requirements.txt`
- **Run tests**: `pytest -q`
- **Local server**: `uvicorn app.main:app --reload`

### iOS (court-iq-ios)
- **Environment**: Xcode (latest stable)
- **SwiftLint**: install via `brew install swiftlint`
- **Run tests**: Command-U in Xcode

---

## 6. Communication

- **Questions**: Open a GitHub Discussion or tag in PR.
- **Decisions**: Document major architectural decisions in `/docs/` or as ADRs.

---


## Planning & Sync — CourtIQ Hybrid Dev Flow

This section explains how we keep **roadmap**, **tech debt**, **PRs**, and **daily work** in sync using a small set of files, local hooks, and CI checks. It’s meant to make alignment boring and automatic.

---

### Quick Start (TL;DR)

1. **Single Source of Truth (SSOT)**: `meta/plan.yml`  
   - Update `current_day` to the active day (e.g., `8`).
   - Each day has `objective`, `deliverables`, `tech_debt_resolve`, `tech_debt_add`.

2. **Validators** (local & CI):  
   - `python tools/validate_structure.py` → checks repo layout matches `meta/project_structure.yml`  
   - `python tools/validate_plan.py` → checks **today** in `meta/plan.yml` matches **TECH_DEBT.md** & **ROADMAP.md** (Day heading + objective line).

3. **Pre-commit** (runs validators before every commit):  
   - Installed with `pre-commit install`.  
   - Config at `.pre-commit-config.yaml`.

4. **CI** (blocks drift on PRs):  
   - `.github/workflows/plan-validate.yml` runs both validators.  
   - `.github/workflows/tests.yml` runs `pytest`.

5. **Daily habit**:  
   - Keep ROADMAP’s **Day N** section and **Objective** line in sync with `meta/plan.yml`.  
   - Resolve/add tech debt items in **TECH_DEBT.md** per the plan.  
   - Run `make check` locally (if Makefile is present).

---

### Files & What They Do

#### 1) `meta/plan.yml` — Single Source of Truth
- **Fields**
  - `current_day`: the only day enforced by the validator.
  - `days[].day`: numeric day (8, 9, 10…)
  - `days[].branch`: the branch name for that day.
  - `days[].objective`: exact phrase the validator expects to find in ROADMAP for the current day.
  - `days[].deliverables`: short bullet list of what ships that day.
  - `days[].tech_debt_resolve`: list of TD ids (e.g., `TD8`) expected to be marked **Resolved** today.
  - `days[].tech_debt_add`: list of TD ids that must exist in TECH_DEBT.md by end of day (status can be Pending).

- **Effects**
  - Changing `current_day` flips which Day the validator enforces.
  - If the validator fails: either update ROADMAP/TECH_DEBT to match, or adjust the plan (and re-commit).

#### 2) `meta/project_structure.yml` — Structure Manifest
- Lists **required directories/files** and optional files.
- `tools/validate_structure.py` uses it to ensure the repo layout stays consistent as we add new parts (routers, tests, notes, workflows, etc.).

#### 3) `tools/validate_plan.py` — Plan ↔ Docs Alignment
- **Checks:**
  1) Every TD in `tech_debt_resolve` for `current_day` exists in TECH_DEBT.md and is marked **Resolved**.
  2) Every TD in `tech_debt_add` exists in TECH_DEBT.md (status may be Pending).
  3) ROADMAP.md contains a **“Day N”** heading and includes the day’s **Objective** string (substring match, case-insensitive).
- **Usage:**  
  `python tools/validate_plan.py`  
  ✅ prints success; ❌ prints specific lines to fix.

**Tip:** We intentionally only validate the **current day** so future sections can evolve without failing today’s work.

#### 4) `tools/validate_structure.py` — Layout Guard
- Checks every required folder/file exists, supports `*` globs, and warns (non-fatal) about missing optional files.
- **Usage:**  
  `python tools/validate_structure.py`

#### 5) Pre-commit Hooks
- Config: `.pre-commit-config.yaml`
- Hooks:  
  - `validate-structure` → runs the structure validator  
  - `validate-plan` → runs the plan validator
- **Setup:**  
  ```bash
  pip install pre-commit
  pre-commit install
  pre-commit run --all-files
  ```
If you see “deprecated stage names” warnings, run `pre-commit migrate-config` (we keep config current).

#### 6) CI Workflows

- **Plan & Structure Validation:** `.github/workflows/plan-validate.yml`  
  Runs both validators on PRs touching `meta/**`, `TECH_DEBT.md`, `ROADMAP.md`, `tools/**`, or the workflow itself.

- **Tests:** `.github/workflows/tests.yml`  
  Installs deps, runs `pytest -q`. Triggers on PRs touching Python files, tests, or requirements.

#### 7) Makefile (optional, but handy)

If present:

```make
.PHONY: test validate check

validate:
	python tools/validate_structure.py && python tools/validate_plan.py

test:
	pytest -q

check: validate test
```

---

### PR Expectations

Use the PR template (`.github/pull_request_template.md`) to map work to the plan:

- **Day & Branch:** e.g., `8` / `feat/api-validation-and-list-polish`
- **Objective:** paste from `meta/plan.yml`
- **Deliverables checked:** (boxes ticked)
- **Tech Debt:** which TDs you resolved/added
- **Validation:** confirm you ran `python tools/validate_plan.py` locally and updated docs

CI will enforce the same checks on your PR.

---

### Daily Flow Checklist

1. Set `current_day` in `meta/plan.yml`.
2. Implement work per the day’s deliverables.
3. Update **TECH_DEBT.md** (resolve/add items per plan).
4. Ensure **ROADMAP.md** has a “Day N” heading and includes the day’s **Objective** phrase.
5. Run locally:
   ```bash
   python tools/validate_structure.py
   python tools/validate_plan.py
   pytest -q
   # or simply:
   make check
   ```
6. Commit & open a PR. CI will run validators + tests.

---

### Troubleshooting

- **PyYAML missing**
```text
ModuleNotFoundError: No module named 'yaml'
```
→ Install dev deps: `pip install -r requirements-dev.txt` (or `pip install PyYAML pytest`)

- **Plan validator: ROADMAP missing today’s objective**
Add the exact line under the correct day heading:
```md
**Objective:** GET /v1/plays with pagination & title filter
```
(Adjust phrase to match `meta/plan.yml` for that day.)

- **Plan validator: TECH_DEBT rows mismatched**
Ensure the TDs listed in `tech_debt_resolve` are present in **TECH_DEBT.md** and marked **Resolved**; ensure TDs in `tech_debt_add` exist.

- **Structure validator failed**
Create missing dirs/files as reported, or update `meta/project_structure.yml` if the repo structure legitimately changed.

- **Pre-commit warnings (deprecated stages)**
Run `pre-commit migrate-config`, commit the updated `.pre-commit-config.yaml`.

---

### FAQ

- **Q:** Won’t ROADMAP objective checks break future days?  
  **A:** No — we only check the **current day** from `meta/plan.yml`.

- **Q:** How do we carry a TD to a later day?  
  **A:** Update `meta/plan.yml` to move that TD to a future day’s `tech_debt_resolve`. If it was already marked resolved in **TECH_DEBT.md**, either unresolve it (if truly not done) or adjust the plan to reflect reality.

- **Q:** Can we relax the “exact objective string” rule?  
  **A:** Yes. We can add a `--strict` flag or make the objective check a warning. For now, we keep it strict for clarity.

- **Q:** Where do daily recaps go?  
  **A:** `notes/dayNN-summary.md` (optional but encouraged). The structure validator treats these as optional.
