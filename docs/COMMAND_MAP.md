# Command Map (CourtIQ)

| Goal                         | Command                       | Notes                                   |
|-----------------------------|-------------------------------|-----------------------------------------|
| See available tasks         | `make help`                   | Self-documenting targets                |
| First-time setup            | `make onboard`                | Venv, dev deps, pre-commit, smoke checks|
| Validate + tests            | `make check`                  | Runs validators then pytest             |
| Pre-commit, all files       | `pre-commit run --all-files`  | Good baseline after fresh clone         |
| Regenerate script docs      | `make docs` / `make docs-refresh` | Updates `docs/SCRIPTS.md`           |
| Tech debt sync              | `make td-sync`                | From `meta/plan.yml` current_day        |
| Open PR (prefilled)         | `make pr`                     | Uses `scripts/open_pr.sh`               |
| Start weekly System Tour    | `make tour-note`              | Creates dated note                      |
| Guided doc walkthrough      | `make tour`                   | With pause prompts                      |
| Open the Handbook           | `make handbook`               | Uses `$EDITOR` if set                   |
