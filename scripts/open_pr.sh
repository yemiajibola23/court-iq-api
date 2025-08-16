#!/usr/bin/env bash
# Open a PR with a body auto-generated from meta/plan.yml.
# Requires: gh, Python (PyYAML), and tools/gen_pr_body.py
set -euo pipefail

TITLE="${1:-"CourtIQ: Day PR"}"
TMP="$(mktemp)"
python tools/gen_pr_body.py --write "$TMP"
gh pr create --fill --title "$TITLE" --body-file "$TMP"
echo "Opened PR: $TITLE"
