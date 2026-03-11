.PHONY: run test lint

run:
	uv run uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload

test:
	uv run pytest tests/ -v

lint:
	uv run ruff check .
	uv run ruff format --check .