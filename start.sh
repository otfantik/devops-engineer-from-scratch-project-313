#!/bin/bash

# Копируем собранный фронтенд в публичную директорию
mkdir -p /app/public
cp -r ./node_modules/@hexlet/project-devops-deploy-crud-frontend/dist/. /app/public/

# Запускаем бэкенд в фоне
export PORT=5000
python main.py &

# Запускаем Nginx на переднем плане
nginx -g "daemon off;"
