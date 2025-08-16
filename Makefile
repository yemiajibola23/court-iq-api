# ---- Self-documenting Makefile ----------------------------------------------
.DEFAULT_GOAL := help
SHELL := /bin/bash

# Config (override via: make VAR=value)
PY := python
VENV ?= .venv
ACTIVATE := source $(VENV)/bin/activate

help: ## Show available commands 
	@awk 'BEGIN {FS = ":.*##"; printf "\nTargets:\n"} /^[a-zA-Z0-9_.-]+:.*?##/ { printf "  \033[36m%-22s\033[0m %s\n", $$1, $$2 }' $(MAKEFILE_LIST)

# ---- Setup ------------------------------------------------------------------

venv: ## Create local Python virtualenv (.venv) and upgrade pip
	@$(PY) -m venv $(VENV) && $(ACTIVATE) && pip install --upgrade pip

deps: ## Install runtime & dev dependencies
	@$(ACTIVATE) && pip install -r requirements.txt || true
	@$(ACTIVATE) && pip install -r requirements-dev.txt || true

hooks: ## Install pre-commit hooks locally
	@$(ACTIVATE) && pre-commit install
	@echo "Run once now with: pre-commit run --all-files"

# ---- Quality gates -----------------------------------------------------------

test: ## Run pytest quietly
	@$(ACTIVATE) && pytest -q

validate: ## Run structure + plan validators
	@$(ACTIVATE) && python tools/validate_structure.py
	@$(ACTIVATE) && python tools/validate_plan.py

check: validate test ## Validate + tests (the gate you should run before PR)

# ---- Docs & automation -------------------------------------------------------

docs: ## Rebuild scripts reference to docs/SCRIPTS.md
	@$(ACTIVATE) && python tools/docgen_scripts.py --out docs/SCRIPTS.md || echo "Skipping: docgen not present yet."

td: ## View TECH_DEBT.md list items
	python tools/tech_debt.py list

td-sync: ## Align TECH_DEBT.md with meta/plan.yml for current_day
	@$(ACTIVATE) && python tools/tech_debt.py sync || echo "Skipping: tech_debt.py not present yet."

pr: ## Open a PR prefilled from plan.yml (requires gh)
	@scripts/open_pr.sh "Day $$DAY: $$TITLE"

.PHONY: help venv deps hooks test validate check docs td-sync pr
