.PHONY: test validate check td td-sync
validate:
	python tools/validate_structure.py && python tools/validate_plan.py
test:
	pytest -q
check: validate test

td:
\tpython tools/tech_debt.py list

td-sync:
\tpython tools/tech_debt.py sync
