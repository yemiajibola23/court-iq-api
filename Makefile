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

onboard: ## One-shot setup: venv, dev deps, pre-commit, quick checks
	@scripts/onboard.sh

# ---- System Tour -------------------------------------------------------------

TOUR_DIR := docs/system-tours
TOUR_DATE := $(shell date +%F)
TOUR_FILE := $(TOUR_DIR)/$(TOUR_DATE).md

tour-note: ## Create today's System Tour note (docs/system-tours/YYYY-MM-DD.md)
	@mkdir -p $(TOUR_DIR)
	@if [ -f "$(TOUR_FILE)" ]; then \
		echo "🔁 Tour for $(TOUR_DATE) already exists at $(TOUR_FILE)"; \
	else \
		printf "# System Tour — %s — <Topic>\n\n## ELI5\n\n## Expert Notes\n- \n- \n- \n\n## Diagram (optional)\n\`\`\`mermaid\nflowchart LR\n  A[Trigger] --> B[Tool/Hook]\n  B --> C[Outcome]\n\`\`\`\n" "$(TOUR_DATE)" > "$(TOUR_FILE)"; \
		echo "✅ Created $(TOUR_FILE)"; \
	fi
	@echo "💡 Set a topic and fill in ELI5 + Expert Notes."

tour-list: ## List existing System Tour notes
	@ls -1 $(TOUR_DIR) 2>/dev/null || echo "(none yet — run 'make tour-note')"

tour-open: ## Open the latest System Tour note in your $EDITOR (or print path)
	@latest=$$(ls -1 $(TOUR_DIR) 2>/dev/null | tail -n 1); \
	if [ -z "$$latest" ]; then \
		echo "(none yet — run 'make tour-note')"; \
	else \
		path="$(TOUR_DIR)/$$latest"; \
		echo "📄 $$path"; \
		if [ -n "$$EDITOR" ]; then "$$EDITOR" "$$path"; fi; \
	fi

# Pause helper (skip with NO_TOUR_PAUSE=1)
PAUSE = @if [ -z "$$NO_TOUR_PAUSE" ]; then read -r -p "⏸  Press Enter to continue… " _; fi

tour: tour-note ## Walk through key project docs (vision, roadmap, tech debt, workflow, contributing)
	@echo "🚀 Welcome to the CourtIQ project tour!"
	@echo
	@echo "📖 VISION.md ---------------------------------------------------"
	@bat --style=plain --paging=never docs/VISION.md || cat VISION.md
	$(PAUSE)
	@echo
	@echo "🗺️ ROADMAP.md ---------------------------------------------------"
	@bat --style=plain --paging=never ROADMAP.md || cat ROADMAP.md
	$(PAUSE)
	@echo
	@echo "💡 TECH_DEBT.md -------------------------------------------------"
	@bat --style=plain --paging=never docs/TECH_DEBT.md || cat TECH_DEBT.md
	$(PAUSE)
	@echo
	@echo "🔧 WORKFLOW.md --------------------------------------------------"
	@bat --style=plain --paging=never ../../docs/WORKFLOW.md || cat WORKFLOW.md
	$(PAUSE)
	@echo
	@echo "🤝 CONTRIBUTING.md ---------------------------------------------"
	@bat --style=plain --paging=never CONTRIBUTING.md || cat CONTRIBUTING.md
	$(PAUSE)
	@echo
	@echo "📋 GUIDELINES.md ------------------------------------------------"
	@bat --style=plain --paging=never ../../docs/GUIDELINES.md || cat GUIDELINES.md
	@echo
	@echo "🎉 End of tour! You now know the core docs that drive this project."

handbook: ## Open the DevOps Handbook in your $EDITOR (or print path)
	@path="docs/DEVOPS_HANDBOOK.md"; \
	echo "📘 $$path"; \
	if [ -n "$$EDITOR" ]; then "$$EDITOR" "$$path"; else echo "(set $$EDITOR to auto-open)"; fi

docs-refresh: ## Regenerate docs/SCRIPTS.md and show the first screen
	@$(ACTIVATE) && python tools/docgen_scripts.py --out docs/SCRIPTS.md
	@echo "✅ docs/SCRIPTS.md regenerated"
	@head -n 40 docs/SCRIPTS.md | sed -e 's/^/│ /'


.PHONY: help venv deps hooks test validate check docs td td-sync pr onboard \
        tour tour-note tour-list tour-open handbook docs-refresh
