# Project Workflow

This document describes how we work on this project, step-by-step.

---

## Step 1: Repository & Branch Protection

- Main branches: `main` (production-ready), `dev` (integration branch).
- All features and fixes are developed in separate branches.
- No direct commits to `main`.
- PRs must pass tests before merge.
- Squash merge into `main` to keep history linear.

---

## Step 2: Commit Style

- Use **Conventional Commits** to keep history clean and searchable.
- Format: `{emoji} {type}: {short description}`
- See [Contributing](../CONTRIBUTING.md) for full details.

---

## Step 3: Pull Request Rules

- PRs should focus on one clear purpose.
- Keep them small and easy to review.
- Always include:
  - Summary
  - Changes
  - Verification steps
  - Screenshots/logs (if applicable)
- Draft PRs can be used while coding; convert to "Ready for Review" once done.

---
