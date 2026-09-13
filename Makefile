VENV := .venv
PY := $(VENV)/bin/python
PIP := $(VENV)/bin/pip

.PHONY: setup test lint evals clean

setup:
	python3 -m venv $(VENV)
	$(PIP) install --quiet --upgrade pip
	$(PIP) install --quiet -r requirements.txt

test:
	$(VENV)/bin/pytest -q

lint:
	$(VENV)/bin/ruff check .

# エージェントを制御する設定の回帰テスト。testpaths は tests のままなので
# evals を明示して渡す（spec/agent-evals.md の設計節）。
evals:
	$(VENV)/bin/pytest evals -q

clean:
	rm -rf $(VENV) .pytest_cache .ruff_cache
	find . -name __pycache__ -type d -exec rm -rf {} +
