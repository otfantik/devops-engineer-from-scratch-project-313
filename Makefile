.PHONY: run test lint db-shell

run:
	uv run uvicorn app.main:app --host 0.0.0.0 --port 8080 --reload

test:
	uv run pytest tests/ -v --tb=short

lint:
	uv run ruff check .
	uv run ruff format --check .

db-shell:
	uv run python -c "from app.database import engine; from sqlmodel import SQLModel; SQLModel.metadata.create_all(engine); print('Tables created')"