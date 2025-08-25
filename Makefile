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

pr-check: validate test ## Validate + tests (the gate you should run before PR)
# ---- Docs & automation -------------------------------------------------------

docs: ## Rebuild scripts reference to docs/SCRIPTS.md
	@$(ACTIVATE) && python tools/docgen_scripts.py --out docs/SCRIPTS.md || echo "Skipping: docgen not present yet."

# ---- Tech Debt helpers (single-source) --------------------------------------

td: ## View TECH_DEBT.md list items
	python tools/tech_debt.py list

td-sync: ## Align TECH_DEBT.md with meta/plan.yml for current_day
	@$(ACTIVATE) && python tools/tech_debt.py sync || echo "Skipping: tech_debt.py not present yet."

# ---- Tech Debt helpers (always auto-id) --------------------------------------

TD_STATUS ?= Pending
TD_WHEN ?= Day $(DAY)
SCOPE ?=

td-add: ## Add TD (preview+confirm) for a specific day AND update plan.yml. Usage: make td-add DAY=12 DESC="..." [STATUS=Pending]
	@if [ -z "$(DAY)" ]; then echo "❌ Missing DAY (e.g., DAY=12)"; exit 1; fi
	@if [ -z "$(DESC)" ]; then echo "❌ Missing DESC (e.g., DESC=\"Opaque cursor token after DB migration\")"; exit 1; fi
	@out_file=$$(mktemp 2>/dev/null || echo /tmp/td_add_$$.log); \
	( $(ACTIVATE) && python tools/tech_debt.py add \
		--desc "$(DESC)" \
		--when "Day $(DAY)" \
		--status "$(TD_STATUS)" \
		--scope "$(SCOPE)" \
		--preview ) | tee "$$out_file"; \
	td=$$( awk -F= '/^NEW_TD_ID=/{print $$2}' "$$out_file" ); rm -f "$$out_file"; \
	if [ -z "$$td" ]; then echo "❌ Could not detect NEW_TD_ID from output"; exit 1; fi; \
	echo "🆕 Detected $$td — updating meta/plan.yml for Day $(DAY)…"; \
	$(ACTIVATE) && python tools/plan_td_update.py --day $(DAY) --add $$td; \
	echo "✅ Added $$td to plan.yml Day $(DAY) (tech_debt_add)"

td-add-yes: ## Add TD (no prompt) for a specific day AND update plan.yml. Usage: make td-add-yes DAY=12 DESC="..." [STATUS=Pending]
	@if [ -z "$(DAY)" ]; then echo "❌ Missing DAY (e.g., DAY=12)"; exit 1; fi
	@if [ -z "$(DESC)" ]; then echo "❌ Missing DESC (e.g., DESC=\"Live badges via GHA\")"; exit 1; fi
	@out=$$( $(ACTIVATE) && python tools/tech_debt.py add \
		--desc "$(DESC)" \
		--when "$(TD_WHEN)" \
		--status "$(TD_STATUS)" \
		--scope "$(SCOPE)" \
		--yes ); \
	echo "$$out"; \
	td=$$( echo "$$out" | awk -F= '/^NEW_TD_ID=/{print $$2}' ); \
	if [ -z "$$td" ]; then echo "❌ Could not detect NEW_TD_ID from output"; exit 1; fi; \
	echo "🆕 Detected $$td — updating meta/plan.yml for Day $(DAY)…"; \
	$(ACTIVATE) && python tools/plan_td_update.py --day $(DAY) --add $$td; \
	echo "✅ Added $$td to plan.yml Day $(DAY) (tech_debt_add)"

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
	@bat --style=plain --paging=never docs/VISION.md || cat docs/VISION.md
	$(PAUSE)
	@echo
	@echo "🗺️ ROADMAP.md ---------------------------------------------------"
	@bat --style=plain --paging=never ROADMAP.md || cat ROADMAP.md
	$(PAUSE)
	@echo
	@echo "💡 TECH_DEBT.md -------------------------------------------------"
	@bat --style=plain --paging=never TECH_DEBT.md || cat TECH_DEBT.md
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

# Put these near the top of your Makefile
REPO_URL ?= https://github.com/yemiajibola23/court-iq-api           # e.g. https://github.com/yourname/yourrepo
DEFAULT_BRANCH ?= dev

DOCGEN_FLAGS :=
ifneq ($(strip $(REPO_URL)),)
DOCGEN_FLAGS += --repo-url $(REPO_URL) --default-branch $(DEFAULT_BRANCH)
endif

# Update docs-refresh:
docs-refresh: ## Regenerate docs/SCRIPTS.md and preview the top
	@$(ACTIVATE) && python tools/docgen_scripts.py --out docs/SCRIPTS.md $(DOCGEN_FLAGS)
	@echo "✅ docs/SCRIPTS.md regenerated"
	@head -n 40 docs/SCRIPTS.md | sed -e 's/^/│ /'


# Daily prompts
TYPE ?= feat
DESC ?=
FLAGS ?=

day-start: ## Run to start each day
	@if [ -z "$(DAY)" ]; then \
		echo "Usage: make day-start DAY=11 [TYPE=feat] [DESC=\"...\"] [FLAGS=--dry-run]"; \
		exit 1; \
	fi
	@echo "→ python tools/day_start.py --day $(DAY) --type $(TYPE) --desc '$(DESC)' $(FLAGS)"
	@python tools/day_start.py --day $(DAY) \
		$(if $(TYPE), --type $(TYPE),) \
		$(if $(DESC), --desc "$(DESC)",) \
		$(FLAGS)

	@echo "→ Ensuring ROADMAP Day $(DAY) section & objective"
	@python tools/ensure_day_in_roadmap.py || true

	@echo "→ Syncing plan ↔ ROADMAP tech-debt (Day $(DAY))"
	@python tools/tech_debt.py sync --day $(DAY) --apply || true

	@echo "→ Validating plan alignment"
	@python tools/validate_plan.py || true

	@echo "✅ Kickoff checks complete."

# Optional knobs
EOD_SCOPE ?=           # e.g., storage — forwarded to tech_debt.py sync
PR_BASE   ?= dev       # default branch
PR_DRAFT  ?= 1         # set empty to open a non-draft PR
PR_LABELS ?= day-$(DAY),auto-eod
PR_REVIEWERS ?=        # comma-separated GitHub handles
PR_BODY_DIR ?= notes/pr

eod: ## End of day: sync TD↔plan↔ROADMAP and generate notes/day{N}-eod.md
	@echo "🔁 Syncing tech debt with plan.yml and ROADMAP…"
	@python tools/tech_debt.py sync $(if $(DAY),--day $(DAY),) --apply $(if $(EOD_SCOPE),--scope $(EOD_SCOPE),)
	@echo "📝 Writing EOD summary note…"
	@python tools/eod.py $(if $(DAY),--day $(DAY),)
	@echo "✅ EOD complete."

eod-commit: ## Commit EOD artifacts iff there are changes
	@git add ROADMAP.md TECH_DEBT.md meta/plan.yml notes/ || true
	@if git diff --cached --quiet; then \
		echo "🟢 Nothing to commit for EOD."; \
	else \
		git commit -m "📝 docs(day$(DAY)): 🧾 EOD summary + TD/ROADMAP sync"; \
	fi

pr-body: ## Build PR body from meta/plan.yml into notes/pr/day{N}-pr.md
	@mkdir -p $(PR_BODY_DIR)
	@python tools/gen_pr_body.py $(if $(DAY),--day $(DAY),) --write $(PR_BODY_DIR)/day$(DAY)-pr.md
	@note="notes/day$(DAY)-eod.md"; \
	if [ -f "$$note" ]; then \
	  printf "\n---\n\n## End of Day Notes\n\n" >> $(PR_BODY_DIR)/day$(DAY)-pr.md; \
	  cat "$$note" >> $(PR_BODY_DIR)/day$(DAY)-pr.md; \
	fi
	@echo "📝 PR body -> $(PR_BODY_DIR)/day$(DAY)-pr.md"

eod-pr: eod eod-commit ## Run EOD, then push and open a PR (requires gh)
	@./scripts/open_pr.sh $(if $(DAY),--day $(DAY),) --base "$(PR_BASE)" \
		$(if $(PR_DRAFT),--draft,) \
		$(if $(PR_LABELS),--labels "$(PR_LABELS)",) \
		$(if $(PR_REVIEWERS),--reviewers "$(PR_REVIEWERS)",)

learn-log: ## Aggregate Learn:/Next: trailers into notes/day{N}-learning.md
	@python tools/learning_log.py $(if $(DAY),--day $(DAY),)

eod-all: eod learn-log eod-commit pr-body eod-pr ## Full EOD with learning log + PR

.PHONY: help venv deps hooks test validate pr-check docs td td-sync td-add td-add-yes onboard \
        tour tour-note tour-list tour-open handbook docs-refresh day-start eod eod-commit pr-body eod-pr \
		learn-log eod-all
