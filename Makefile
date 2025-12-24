.PHONY: run install test lint format clean docker-build docker-run

install:
	uv pip install flask sentry_sdk[flask] sqlmodel psycopg2-binary python-dotenv pytest ruff

run:
	python main.py

dev:
	FLASK_ENV=development python main.py

test:
	python -m pytest -v

lint:
	python -m ruff check .

format:
	python -m ruff format .
	python -m ruff check --fix .

docker-build:
	docker build -t devops-app .

docker-run:
	docker run -p 8080:8080 --env-file .env devops-app

clean:
	rm -rf __pycache__ .pytest_cache .ruff_cache
	find . -name "*.pyc" -delete
	find . -type d -name "__pycache__" -exec rm -rf {} +
