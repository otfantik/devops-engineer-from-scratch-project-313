.PHONY: run test lint format setup

run:
	uv run uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload

setup:
	uv sync --dev

test:
	uv run pytest tests/ -v --tb=short

lint:
	uv run ruff check .
	uv run ruff format --check .

format:
	uv run ruff format .

dev:
	npx concurrently \
		"uv run uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload" \
		"npx start-hexlet-devops-deploy-crud-frontend"