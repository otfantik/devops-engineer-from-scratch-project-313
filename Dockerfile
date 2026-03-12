FROM python:3.9-slim AS backend

WORKDIR /app

COPY pyproject.toml README.md Makefile ./
COPY app/ ./app/

RUN pip install --no-cache-dir fastapi uvicorn sqlmodel psycopg2-binary python-dotenv pydantic-settings


FROM node:20-slim AS frontend

WORKDIR /app

COPY package.json ./
RUN npm install
RUN cp -r node_modules/@hexlet/project-devops-deploy-crud-frontend/dist /app/dist


FROM caddy:2-alpine

COPY --from=backend /app /app
COPY --from=frontend /app/dist /usr/share/caddy
COPY Caddyfile /etc/caddy/Caddyfile

RUN apk add --no-cache python3 py3-pip && \
    pip3 install --break-system-packages fastapi uvicorn sqlmodel psycopg2-binary python-dotenv pydantic-settings && \
    chmod +x /usr/bin/caddy && \
    mkdir -p /config /data && \
    chown -R 1000:1000 /config /data && \
    setcap -r /usr/bin/caddy

USER 1000:1000

WORKDIR /app

EXPOSE 8080

CMD sh -c "\
  python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --log-level info & \
  /usr/bin/caddy run --config /etc/caddy/Caddyfile --adapter caddyfile \
"