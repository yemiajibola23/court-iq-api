#!/usr/bin/env bash
# What: Open a PR using a body auto-generated from meta/plan.yml
# Why:  No manual copy/paste of objectives or tech debt
# Usage: scripts/open_pr.sh "Day 10: Validation polish"
# Requires: gh, Python (PyYAML), and tools/gen_pr_body.py
set -euo pipefail

TITLE="${1:-"CourtIQ: Day PR"}"
TMP="$(mktemp)"
python tools/gen_pr_body.py --write "$TMP"
gh pr create --fill --title "$TITLE" --body-file "$TMP"
echo "Opened PR: $TITLE"
