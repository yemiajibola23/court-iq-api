### Day & Branch
- **Day:** 11
- **Branch:** feat/sqlite-migration-and-validation

### Scope
- **Objective (from meta/plan.yml):** SQLite migration + video_path validator hardening + 422 envelope
- **Deliverables checked:**
  - [ ] SQLite-backed repo
  - [ ] HTTPS-only, length, extension checks
  - [ ] 422 per-field array envelope

### Tech Debt
- **Resolves TD:** TD1, TD4, TD9, TD12
- **Adds TD:** <none>

### Validation (run locally before opening PR)
- [ ] `python tools/validate_structure.py` passed
- [ ] `python tools/validate_plan.py` passed
- [ ] `pytest -q` passed
- [ ] Docs updated where needed (README / ROADMAP / TECH_DEBT)

### Notes / Screenshots (optional)
<!-- Add any context, screenshots, or follow-ups here -->
