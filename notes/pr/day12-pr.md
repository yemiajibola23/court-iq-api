### Day & Branch
- **Day:** 12
- **Branch:** feat/dev-override-path-policy-and-cursor

### Scope
- **Objective (from meta/plan.yml):** Local path override policy + traversal protection + cursor plan
- **Deliverables checked:**
  - [ ] ALLOW_LOCAL_VIDEO_PATHS + MEDIA_ROOT policy
  - [ ] Traversal blocking
  - [ ] Cursor design note (composite/opaque)

### Tech Debt
- **Resolves TD:** TD5, TD10, TD11, TD14
- **Adds TD:** TD14

### Validation (run locally before opening PR)
- [ ] `python tools/validate_structure.py` passed
- [ ] `python tools/validate_plan.py` passed
- [ ] `pytest -q` passed
- [ ] Docs updated where needed (README / ROADMAP / TECH_DEBT)

### Notes / Screenshots (optional)
<!-- Add any context, screenshots, or follow-ups here -->
