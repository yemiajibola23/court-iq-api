.PHONY: test validate check
validate:
	python tools/validate_structure.py && python tools/validate_plan.py
test:
	pytest -q
check: validate test
