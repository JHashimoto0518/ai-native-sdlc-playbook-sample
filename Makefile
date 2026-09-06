VENV := .venv
PY := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

.PHONY: setup test lint clean

setup:
	python3 -m venv $(VENV)
	$(PIP) install --quiet --upgrade pip
	$(PIP) install --quiet -r requirements.txt

test:
	$(VENV)/bin/pytest -q

lint:
	$(VENV)/bin/ruff check .

clean:
	rm -rf $(VENV) .pytest_cache .ruff_cache
	find . -name __pycache__ -type d -exec rm -rf {} +
