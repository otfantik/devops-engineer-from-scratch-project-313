FROM python:3.9-slim

WORKDIR /app

RUN pip install uv

COPY pyproject.toml .
COPY Makefile .
COPY app/ ./app/

RUN uv sync --no-dev

EXPOSE 8080

CMD uv run uvicorn app.main:app --host 0.0.0.0 --port $PORT