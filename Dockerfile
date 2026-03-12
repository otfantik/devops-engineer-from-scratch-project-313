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


FROM nginx:alpine

COPY --from=backend /app /app
COPY --from=backend /usr/local/bin/uv /usr/local/bin/uv
COPY --from=backend /usr/local/lib/python3.9 /usr/local/lib/python3.9
COPY --from=backend /usr/local/bin/python3 /usr/local/bin/python3

COPY --from=frontend /app/dist /usr/share/nginx/html

COPY nginx.conf /etc/nginx/nginx.conf

RUN apk add --no-cache python3 py3-pip && \
    pip3 install --break-system-packages uv

WORKDIR /app

EXPOSE 80

CMD sh -c "uv run uvicorn app.main:app --host 127.0.0.1 --port 8000 --log-level info & nginx -g 'daemon off;'"