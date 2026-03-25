FROM python:3.12-slim AS backend

WORKDIR /app

RUN apt-get update && \
    apt-get install -y nginx && \
    rm -rf /var/lib/apt/lists/*

RUN pip install uv

COPY pyproject.toml README.md Makefile ./
COPY app/ ./app/

RUN uv sync --no-dev


FROM node:20-slim AS frontend

WORKDIR /app

COPY package.json ./
RUN npm install
RUN cp -r node_modules/@hexlet/project-devops-deploy-crud-frontend/dist /app/dist


FROM backend AS final

COPY --from=backend /app /app
COPY --from=frontend /app/dist /var/www/html

COPY nginx.conf /etc/nginx/sites-available/default

RUN rm /etc/nginx/sites-enabled/default && \
    ln -s /etc/nginx/sites-available/default /etc/nginx/sites-enabled/default

EXPOSE 80

CMD sh -c "uv run uvicorn app.main:app --host 127.0.0.1 --port 8000 --log-level info & nginx -g 'daemon off;'"