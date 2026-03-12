FROM python:3.9-slim AS backend

WORKDIR /app

RUN pip install uv

COPY pyproject.toml README.md Makefile ./
COPY app/ ./app/

RUN uv sync --no-dev


FROM node:20-slim AS frontend

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm install
RUN npx @hexlet/project-devops-deploy-crud-frontend build


FROM caddy:2-alpine

# Копируем бэкенд
COPY --from=backend /app /app
COPY --from=backend /usr/local/bin/python3 /usr/local/bin/
COPY --from=backend /usr/local/lib/python3.9 /usr/local/lib/python3.9

# Копируем фронтенд
COPY --from=frontend /app/node_modules/@hexlet/project-devops-deploy-crud-frontend/dist /usr/share/caddy

# Копируем Caddyfile
COPY Caddyfile /etc/caddy/Caddyfile

# Устанавливаем Python и uv в финальный образ
RUN apk add --no-cache python3 py3-pip && \
    pip3 install uv

WORKDIR /app

# Запускаем бэкенд в фоне и Caddy на переднем плане
CMD sh -c "uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 & caddy run --config /etc/caddy/Caddyfile --adapter caddyfile"