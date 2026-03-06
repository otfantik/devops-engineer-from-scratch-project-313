FROM python:3.10-slim

# Устанавливаем Node.js и Nginx
RUN apt-get update && apt-get install -y \
    curl \
    gcc \
    libpq-dev \
    nginx \
    && curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv

WORKDIR /app

# Копируем Python зависимости
COPY pyproject.toml .
RUN uv pip install --system .

# Копируем фронтенд зависимости
COPY package.json package-lock.json* ./
RUN npm install

# Копируем конфигурацию Nginx
COPY nginx.conf /etc/nginx/sites-available/default

# Копируем остальной код
COPY . .

# Копируем и делаем исполняемым скрипт запуска
COPY start.sh /start.sh
RUN chmod +x /start.sh

# Открываем порт 80
EXPOSE 80

# Запускаем скрипт
CMD ["/start.sh"]