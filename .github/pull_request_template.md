# CourtIQ — Day PR

<!-- Keep this section short; reviewers skim it first. -->
**Day:** <!-- e.g., 11 -->
**Branch:** <!-- e.g., feat/sqlite-migration-and-validation -->
**Objective (paste from meta/plan.yml current_day.objective):**
<!-- exact text from plan.yml so ROADMAP/plan stay in lockstep -->

---

## Scope & Outcomes
- What changed (1–3 bullets):
  - …
  - …
- Why it changed (user/system impact in one line):
  - …

## Subtasks Done (by ID)
<!-- Use D##-# tokens so commit auto-checkoff can work too. -->
- [ ] D11-1 — …
- [ ] D11-2 — …
- [ ] D11-3 — …
- [ ] D11-4 — …
- [ ] D11-5 — …

## Tech Debt
- **Resolves TD:** <!-- e.g., TD4, TD9, TD12 -->
- **Adds TD:** <!-- e.g., TD18 (short description) -->
<!-- For the final squash commit message, include a trailer like:
Resolves-TD: TD4, TD9, TD12
This enables auto-marking in TECH_DEBT.md. -->

---

## API / DB Notes
- [ ] API surface changed (documented in README/ROADMAP)
- [ ] 422 error envelope conforms to per-field arrays (e.g., `{ "video_path": ["…"] }`)
- [ ] DB schema/migration details:
  - Table(s): …
  - Migration safety: forward-only / reversible
  - Backfill/seed (if any): …

---

## Validation Checklist (run locally before opening)
- [ ] Structure: `python tools/validate_structure.py` ✅
- [ ] Plan: `python tools/validate_plan.py` ✅
- [ ] Tests: `pytest -q` ✅
- [ ] Lint/type (if applicable): `ruff` / `mypy` ✅
- [ ] Docs updated (README / ROADMAP / TECH_DEBT) ✅

### Drift/Synchronization (must stay in sync)
- [ ] Plan ↔ ROADMAP ↔ TECH_DEBT check (dry run):  
      `python tools/tech_debt.py sync --dry-run`
- [ ] If mismatches, applied auto-fix (optional):  
      `python tools/tech_debt.py sync --apply`
- [ ] Confirm ROADMAP day section includes all `techdebt(…)` lines for today’s TDs

---

## Test Evidence
- New/updated tests (names or paths):
  - …
- Notable scenarios covered (edge cases, failure modes):
  - …
- Local run summary (paste or paraphrase):
  - `45 passed, 13 skipped` (example)

---

## Reviewer Notes
- How to run locally (env vars, seeds, feature flags):
  - …
- Known out-of-scope items / follow-ups:
  - …

---

## What I Learned (brief bullets)
<!-- Helps future-you and reviewers; aim for 2–4 bullets. -->
- …
- …
- …

## Screenshots / Logs (optional)
<!-- curl examples, HTTP traces, UI shots, SQL explain plans, etc. -->
