FROM python:3.9-slim AS backend

WORKDIR /app

RUN pip install uv

COPY pyproject.toml README.md Makefile ./
COPY app/ ./app/

RUN uv sync --no-dev


FROM node:20-slim AS frontend

WORKDIR /app

COPY package.json ./
RUN npm install
RUN cp -r node_modules/@hexlet/project-devops-deploy-crud-frontend/dist /app/dist


FROM caddy:2-alpine

ENV XDG_CONFIG_HOME=/config
ENV XDG_DATA_HOME=/data

COPY --from=backend /usr/local/bin/uv /usr/local/bin/uv
COPY --from=backend /app /app
COPY --from=backend /usr/local/lib/python3.9 /usr/local/lib/python3.9

COPY --from=frontend /app/dist /usr/share/caddy

COPY Caddyfile /etc/caddy/Caddyfile

RUN apk add --no-cache python3 py3-pip && \
    chmod +x /usr/bin/caddy && \
    mkdir -p /config /data && \
    chown -R 1000:1000 /config /data

USER 1000:1000

WORKDIR /app

EXPOSE 8080

CMD sh -c "cd /app && uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 & /usr/bin/caddy run --config /etc/caddy/Caddyfile --adapter caddyfile"