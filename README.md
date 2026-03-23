# DevOps Engineer Project

[![Actions Status](https://github.com/otfantik/devops-engineer-from-scratch-project-313/actions/workflows/hexlet-check.yml/badge.svg)](https://github.com/otfantik/devops-engineer-from-scratch-project-313/actions)

## Технологии

- Python 3.9, FastAPI, SQLModel, PostgreSQL
- Nginx, Docker
- UV, Ruff, pytest
- GitHub Actions, Render

## Деплой

Приложение развернуто на Render:  
[https://devops-engineer-from-scratch-project-313-6wfs.onrender.com](https://devops-engineer-from-scratch-project-313-6wfs.onrender.com)

## API Endpoints

| Метод | Путь | Описание |
|-------|------|----------|
| GET | `/ping` | Проверка работоспособности |
| GET | `/api/links` | Список ссылок |
| POST | `/api/links` | Создание ссылки |
| GET | `/api/links/{id}` | Получение ссылки |
| PUT | `/api/links/{id}` | Обновление ссылки |
| DELETE | `/api/links/{id}` | Удаление ссылки |
| GET | `/r/{short_name}` | Редирект на оригинальный URL |

## Локальный запуск

```bash
uv sync --dev

# Отредактируйте .env
make run