FROM python:3.10-slim

RUN pip install --no-cache-dir uv

WORKDIR /app

COPY pyproject.toml .

RUN uv pip install --system .

COPY . .

RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8080

CMD ["python", "main.py"]
