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



*Following these guidelines helps us keep the project organized, consistent, and easy to maintain.*