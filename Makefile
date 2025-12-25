.PHONY: run install test lint format clean setup db-init dev docker-build docker-run help

install:
	uv pip install -e ".[dev]"

run:
	uv run python3 main.py

test:
	TESTING=true uv run python3 -m pytest -v

lint:
	uv run ruff check .

format:
	uv run ruff format .
	uv run ruff check --fix .

clean:
	rm -rf __pycache__ .pytest_cache .ruff_cache
	find . -name "*.pyc" -delete
	rm -f database.db

setup:
	@echo "Creating .env file..."
	@if [ ! -f .env ]; then \
		echo "BASE_URL=http://localhost:8080" > .env; \
		echo "DATABASE_URL=sqlite:///database.db" >> .env; \
		echo ".env file created"; \
	else \
		echo ".env file already exists"; \
	fi

db-init:
	uv run python3 -c "from app.main import create_db_and_tables; create_db_and_tables(); print('Database initialized')"

dev:
	uv run python3 main.py

docker-build:
	docker build -t url-shortener .

docker-run:
	docker run -p 8080:8080 --env-file .env url-shortener
