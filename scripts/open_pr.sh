#!/usr/bin/env bash
# Open a PR with a body generated from meta/plan.yml (and optionally EOD note)
# Works with Make targets:
#   make pr-body DAY=11  -> writes notes/pr/day11-pr.md
#   make eod-pr DAY=11   -> calls this script with --body-file ...
#
# Usage:
#   scripts/open_pr.sh [--day N] [--base dev] [--draft] \
#                      [--labels "a,b"] [--reviewers "u1,u2"] \
#                      [--title "Day N: ..."] [--body-file path] [--no-push]
#
# Requires: gh (authenticated), Python (PyYAML), tools/gen_pr_body.py

set -euo pipefail

usage() {
  cat <<'EOF'
Usage:
  scripts/open_pr.sh [--day N] [--base dev] [--draft]
                     [--labels "label1,label2"] [--reviewers "alice,bob"]
                     [--title "Day N: Title"] [--body-file path] [--no-push]

Notes:
  - --labels is optional and may be provided with or without a value.
    * With a value (e.g., --labels "l1,l2"): applies those labels.
    * Without a value (e.g., --labels): applies no labels.
  - --reviewers requires a value if provided.

Behavior:
  - Determines day from --day or meta/plan.yml (current_day)
  - Title defaults to "Day N: <ROADMAP heading>" when possible
  - Body comes from:
      1) --body-file, or
      2) notes/pr/dayN-pr.md (if present), or
      3) generated via tools/gen_pr_body.py --day N
  - Pushes current branch and opens a PR to --base

Examples:
  scripts/open_pr.sh --day 11 --base dev --labels "day-11,auto-eod" --draft
  scripts/open_pr.sh --body-file notes/pr/day11-pr.md
EOF
}

# Help flag
if [[ "${1:-}" == "-h" || "${1:-}" == "--help" ]]; then usage; exit 0; fi

# --- Defaults ---------------------------------------------------------------
BASE="dev"
DRAFT=0
LABELS=""
REVIEWERS=""
TITLE=""
BODY_FILE=""
DAY=""
NO_PUSH=0

# --- Parse args -------------------------------------------------------------
while [[ $# -gt 0 ]]; do
  case "$1" in
    --base) BASE="$2"; shift 2;;
    --draft) DRAFT=1; shift;;
    --labels)
      # Optional value: if next token exists and doesn't start with '-', consume it.
      if [[ $# -ge 2 && "${2:0:1}" != "-" ]]; then
        LABELS="$2"
        shift 2
      else
        LABELS=""
        shift 1
      fi
      ;;
    --reviewers) REVIEWERS="$2"; shift 2;;
    --day) DAY="$2"; shift 2;;
    --title) TITLE="$2"; shift 2;;
    --body-file) BODY_FILE="$2"; shift 2;;
    --no-push) NO_PUSH=1; shift;;
    -h|--help) usage; exit 0;;
    *) echo "Unknown arg: $1" >&2; usage; exit 2;;
  esac
done

# --- Preconditions ----------------------------------------------------------
command -v gh >/dev/null || { echo "❌ gh CLI not found"; exit 1; }

# --- Determine day ----------------------------------------------------------
if [[ -z "$DAY" ]]; then
  if [[ -f meta/plan.yml ]]; then
    DAY="$(python - <<'PY'
import yaml,sys
try:
  d=yaml.safe_load(open("meta/plan.yml","r",encoding="utf-8")) or {}
  v=d.get("current_day")
  if isinstance(v,int): print(v)
  elif isinstance(v,str) and v.strip().isdigit(): print(int(v))
  else: print("",end="")
except Exception: print("",end="")
PY
)"
  fi
fi

if [[ -z "$DAY" ]]; then
  echo "❌ Could not determine day (use --day or set current_day in meta/plan.yml)." >&2
  exit 1
fi

# --- Figure out branch and ensure it's pushed -------------------------------
BRANCH="$(git rev-parse --abbrev-ref HEAD)"
if [[ "$NO_PUSH" -eq 0 ]]; then
  if ! git rev-parse --symbolic-full-name --verify -q "@{u}" >/dev/null; then
    git push -u origin "$BRANCH"
  else
    git push
  fi
fi

# --- Title: derive from ROADMAP heading if not provided ---------------------
if [[ -z "$TITLE" ]]; then
  if [[ -f ROADMAP.md ]]; then
    # Match "## Day N – <heading>" (unicode en dash or hyphen)
    HEADING="$(awk -v d="$DAY" '
      $0 ~ "^## Day " d " [\342\200\223-] " {
        sub(/^## Day [0-9]+ [\342\200\223-] /,"",$0); print; exit
      }' ROADMAP.md 2>/dev/null || true)"
  else
    HEADING=""
  fi
  if [[ -n "$HEADING" ]]; then
    TITLE="Day ${DAY}: ${HEADING}"
  else
    TITLE="Day ${DAY}: Update"
  fi
fi

# --- Body: prefer provided file, else notes/pr/dayN-pr.md, else generate ----
TMP=""
cleanup() { [[ -n "$TMP" && -f "$TMP" ]] && rm -f "$TMP"; }
trap cleanup EXIT

if [[ -z "$BODY_FILE" ]]; then
  CAND="notes/pr/day${DAY}-pr.md"
  if [[ -f "$CAND" ]]; then
    BODY_FILE="$CAND"
  else
    # generate with gen_pr_body.py
    if [[ ! -f tools/gen_pr_body.py ]]; then
      echo "❌ tools/gen_pr_body.py not found and no --body-file provided." >&2
      exit 1
    fi
    TMP="$(mktemp)"
    python tools/gen_pr_body.py --day "$DAY" --write "$TMP"
    BODY_FILE="$TMP"
  fi
fi

# --- Build gh args and open PR ---------------------------------------------
args=(pr create --base "$BASE" --head "$BRANCH" --title "$TITLE" --body-file "$BODY_FILE")
[[ $DRAFT -eq 1 ]] && args+=(--draft)

# Labels (comma-separated -> multiple flags)
if [[ -n "$LABELS" ]]; then
  IFS=',' read -r -a _labels <<< "$LABELS"
  for l in "${_labels[@]}"; do
    l_trim="$(echo "$l" | xargs)"
    [[ -n "$l_trim" ]] && args+=(--label "$l_trim")
  done
fi

# Reviewers (comma-separated -> multiple flags)
if [[ -n "$REVIEWERS" ]]; then
  IFS=',' read -r -a _revs <<< "$REVIEWERS"
  for r in "${_revs[@]}"; do
    r_trim="$(echo "$r" | xargs)"
    [[ -n "$r_trim" ]] && args+=(--reviewer "$r_trim")
  done
fi

echo "🔗 Opening PR to base='$BASE' from head='$BRANCH' with title: $TITLE"
gh "${args[@]}"
