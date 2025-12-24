.PHONY: run install test

install:
	uv pip install flask sentry_sdk[flask] pytest ruff

run:
	uv run python main.py

test:
	uv run python -m pytest -v
