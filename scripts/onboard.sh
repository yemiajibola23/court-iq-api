#!/usr/bin/env bash
# What: One-shot setup for a fresh clone (venv, dev deps, pre-commit)
# Why:  Make onboarding and context switching painless & consistent
# Usage: scripts/onboard.sh

set -euo pipefail

# Resolve repo root regardless of where script is invoked
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_ROOT"

VENV=".venv"
PYTHON="${PYTHON:-python3}"

echo "⏳ Creating virtualenv at ${VENV} (if missing)…"
if [ ! -d "$VENV" ]; then
  $PYTHON -m venv "$VENV"
fi

# shellcheck source=/dev/null
source "$VENV/bin/activate"

echo "⬆️  Upgrading pip…"
pip install --upgrade pip

echo "📦 Installing dev deps…"
if [ -f requirements.txt ]; then pip install -r requirements.txt || true; fi
if [ -f requirements-dev.txt ]; then pip install -r requirements-dev.txt || true; fi

echo "🧩 Installing pre-commit hooks…"
pip install pre-commit || true
pre-commit install || true

echo "🔍 (Optional) Running hooks on all files once…"
pre-commit run --all-files || true

echo "🧪 Running quick checks (skip failures)…"
python -c "import sys; print('python', sys.version)" || true
command -v pytest >/dev/null 2>&1 && pytest -q || echo "pytest not available or tests failing (ok for now)"

echo "✅ Onboarding complete. You’re ready to code."
echo "   Pro tips:"
echo "   - 'source ${VENV}/bin/activate' to enter the venv"
echo "   - 'make help' to see project commands"
echo "   - 'pre-commit run --all-files' to lint/validate entire repo"
