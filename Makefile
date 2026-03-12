.PHONY: run test lint format dev

run:
	uv run uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload

dev:
	npx concurrently \
		"uv run uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload" \
		"npx start-hexlet-devops-deploy-crud-frontend"

test:
	uv run pytest tests/ -v --tb=short

lint:
	uv run ruff check .
	uv run ruff format --check .

format:
	uv run ruff format .