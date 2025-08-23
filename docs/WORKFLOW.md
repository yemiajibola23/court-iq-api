# CourtIQ — Daily Workflow Reference (Snapshot)

> A practical, step‑by‑step guide to run a full day from kickoff → TDD loops → EOD → PR, with the exact Make targets and conventions we use.

---

## Prereqs (once per machine)
- Python 3 + PyYAML (`pip install pyyaml`)
- GitHub CLI (`gh auth login`)
- Pre-commit hooks
  - Install post-commit stage + always_run for commit effects
  - `pre-commit install --hook-type post-commit`
- Optional tools: ripgrep (`rg`), bat

## Conventions & IDs
- **Subtasks**: `D<day>-<n>` (e.g., `D11-2`)
- **Tech Debt**: `TD<n>` (e.g., `TD5`)
- **Commit trailers** we parse:
  - `Resolves-TD: TD1, TD5`
  - `Learn: <insight>`
  - `Next: <next micro-step>`

## TL;DR flow (Day N)
1) **Kickoff** → `make day-start DAY=N TYPE=feat` (add `FLAGS=--dry-run` to preview)
2) **Plan subtasks** (ROADMAP Day N) and add TD items as needed
3) **TDD loops** with smart commits (include `D<N>-#`, trailers as needed)
4) **Docs & checks** → `make docs-refresh` / `make check`
5) **End of Day** → `make eod` (sync TD↔plan↔ROADMAP + write EOD note)
6) **Learning log** (optional) → `make learn-log`
7) **Commit EOD artifacts** → `make eod-commit`
8) **PR body** → `make pr-body`
9) **Open PR** → `make eod-pr`

---

## Detailed sequence (Day N)

### 0) Prep (optional)
- Ensure you’re up to date on the base branch (e.g., `dev`):
  ```bash
  git checkout dev && git pull --ff-only
  ```

### 1) Start the day
- **Command**
  ```bash
  make day-start DAY=N TYPE=feat [DESC="…"] [FLAGS=--dry-run]
  ```
- **Effects**
  - Sets `meta/plan.yml: current_day = N`
  - Ensures `ROADMAP.md` has a `## Day N – <heading>` and an `**Objective:** …` line
  - Creates or checks out branch (from plan `days[].branch` or `TYPE/desc`)
  - Writes `notes/dayN-kickoff.md` with a kickoff block
  - (Dry run prints the plan without changing files)

### 2) Draft subtasks in ROADMAP (Day N)
Use the standard checklist format:
```md
## Day N – <Heading>
- [ ] ✨ feat(scope): … (D<N>-1)
- [ ] 🧹 chore(scope): … (D<N>-2)
- [ ] ✅ test(scope): … (D<N>-3)
- [ ] 🔨 refactor(scope): … (D<N>-4)
- [ ] 📝 docs: … (D<N>-5)
- [ ] 💳 techdebt(scope): <desc> (TD#)  # optional TD links
```

### 3) Add Tech Debt items (mirrors into ROADMAP)
- **Command**
  ```bash
  python tools/tech_debt.py add \
    --desc "<TD description>" \
    --when "Day N" \
    --status Pending \
    --scope <scope>                # optional
  ```
- **Effects**
  - Appends a `| TD# | … | Day N | Pending |` row to `TECH_DEBT.md`
  - Inserts `- [ ] 💳 techdebt(scope): <desc> (TD#)` into **Day N** in `ROADMAP.md`

### 4) Development loop (pairing + TDD)
- **Loop**: Red → Green → Refactor → Commit
- **Commit subject** must include the subtask ID: `D<N>-#:`
- **Optional trailers** (improve learning + navigation):
  ```
  Learn: <insight captured>
  Next: <next thin slice>
  Resolves-TD: TD5[, TD8]
  ```
- **Automation** (post-commit hook):
  - Ticks `ROADMAP.md` line matching `D<N>-#`
  - If `Resolves-TD:` present: marks those `TD#` rows as **✅ Resolved** and ticks any matching `(TD#)` line in ROADMAP

#### Examples
```text
D11-1: ✨ feat(storage): add provider interface

Learn: adapter seams help testing
Next: add fake provider tests (D11-3)
```
```text
D11-4: 🔨 refactor(services): inject storage provider

Resolves-TD: TD1
```

### 5) Docs & checks (run as needed)
- Rebuild scripts index: `make docs-refresh`
- Validate structure & plan, run tests: `make check`

### 6) End of Day sync & note
- **Command**: `make eod [DAY=N] [EOD_SCOPE=scope]`
- **Effects**
  - `tech_debt.py sync --apply` aligns **plan.yml** ↔ **ROADMAP** ↔ **TECH_DEBT** for Day N
  - Writes `notes/dayN-eod.md` summarizing shipped items, carry-overs, and TD status

### 7) Learning log (optional but recommended)
- **Command**: `make learn-log [DAY=N]`
- **Effects**: aggregates `Learn:`/`Next:` from today’s commits into `notes/dayN-learning.md`

### 8) Commit EOD artifacts
- **Command**: `make eod-commit [DAY=N]`
- **Effects**: stages updated docs/notes and commits if there are changes

### 9) PR body and PR
- **Build body**: `make pr-body [DAY=N]`
  - Writes `notes/pr/dayN-pr.md` via `tools/gen_pr_body.py`
  - (Optional) appends the learning log / EOD note if configured in Makefile
- **Open PR**: `make eod-pr [DAY=N] PR_DRAFT=`
  - Pushes branch (sets upstream if needed)
  - Derives title from `ROADMAP` (fallback: `Day N: Update`)
  - Uses `notes/pr/dayN-pr.md` as PR body (or auto-generates if missing)

---

## Target cheat‑sheet (what to run when)
| Phase | Target / Command | Purpose |
|---|---|---|
| Kickoff | `make day-start DAY=N TYPE=feat [DESC]` | Set `current_day`, ensure Day header, create/checkout branch, write kickoff note |
| Plan TD | `python tools/tech_debt.py add --desc "…" --when "Day N" [--scope X]` | Add a TD row and mirror a ROADMAP TD line |
| Work loop | *(commits with `D<N>-#`)* | Tick ROADMAP subtasks automatically |
| Mid‑checks | `make docs-refresh` / `make check` | Update docs index; validate + tests |
| Sync TD | `python tools/tech_debt.py sync --apply [--day N]` | Align plan ↔ ROADMAP ↔ TECH_DEBT for today |
| EOD note | `make eod [DAY=N]` | Sync + write `notes/dayN-eod.md` |
| Learning | `make learn-log [DAY=N]` | Aggregate learning trailers into `notes/dayN-learning.md` |
| Commit | `make eod-commit [DAY=N]` | Commit EOD artifacts if changed |
| PR body | `make pr-body [DAY=N]` | Generate `notes/pr/dayN-pr.md` from plan |
| Open PR | `make eod-pr [DAY=N]` | Push branch and open PR (labels/reviewers via vars) |

---

## System Tours (context & knowledge accrual)

**Why:** keep architecture and guiding docs fresh in your head and capture insights in a lightweight, repeatable way.

**When to run**
- **Quick daily warm‑up (5–10 min):** right after kickoff. Set the tour topic to match today’s objective.
- **Weekly deep dive (20–30 min):** pick a subsystem or doc that needs love.

**Targets**
- `make tour-note` → creates today’s note at `docs/system-tours/YYYY-MM-DD.md` with sections:
  - **ELI5** (plain‑language explanation)
  - **Expert Notes** (bullets, links)
  - **Diagram (optional)** mermaid block prefilled
- `make tour-list` → lists existing tour notes
- `make tour-open` → opens the latest note (uses `$EDITOR` if set)
- `make tour` → guided walk through core docs (VISION, ROADMAP, TECH_DEBT, WORKFLOW, CONTRIBUTING, GUIDELINES); pause between sections unless `NO_TOUR_PAUSE=1`

**Daily flow integration**
1) Run `make tour-note` and set the **Topic** to align with Day N’s objective.
2) If you find gaps, add TODOs or TDs (use `tools/tech_debt.py add --when "Day N" --scope docs`).
3) During pairing, keep the note open; drop brief bullets in **Expert Notes** as you discover patterns.
4) At EOD, link the tour note from your learning log or PR body (optional).

**Examples**
```bash
# morning
make day-start DAY=11 TYPE=feat
make tour-note                       # creates docs/system-tours/2025-08-22.md
NO_TOUR_PAUSE=1 make tour            # quick skim without pauses

# if the tour reveals doc gaps
python tools/tech_debt.py add --desc "Document storage provider matrix" --when "Day 11" --status Pending --scope docs
```

---

## Troubleshooting
- **Subtask didn’t tick**
  - Ensure post-commit hook is installed with `always_run: true` and `pass_filenames: false` for the `commit-effects` hook
  - Line is unchecked (`- [ ]`) and contains `D<N>-#` or `(D<N>-#)`
  - Run manually: `python tools/commit_effects.py`
- **TD not mirrored into ROADMAP**
  - Use `tech_debt.py add --when "Day N"` (not another day)
  - Run `python tools/tech_debt.py sync --apply --day N`
- **PR body empty**
  - `make pr-body DAY=N` to generate, then `make eod-pr`
- **Drop test commits**
  - Keep changes, drop commit: `git reset --soft HEAD~1` → `git commit --amend --no-edit`
  - Delete entirely: `git reset --hard HEAD~1` (danger: discards)

---

## Notes
- The snapshot assumes the Make targets and scripts discussed are present (`day-start`, `docs-refresh`, `check`, `eod`, `learn-log`, `eod-commit`, `pr-body`, `eod-pr`).
- Customize emojis/scopes as you like—IDs (`D<N>-#`, `TD#`) are the automation hooks.

