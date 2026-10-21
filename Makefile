.PHONY: validate test status check

validate:
	python3 tools/validate.py

test:
	python3 tools/test_lookup.py

status:
	python3 tools/status.py

check: validate test
