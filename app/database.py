import os
import re
from typing import Generator
from sqlmodel import SQLModel, create_engine, Session
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
BASE_URL = os.getenv("BASE_URL", "http://localhost:8080")

# Для тестов используем SQLite
if os.environ.get("TESTING") == "true":
    DATABASE_URL = "sqlite:///:memory:?cache=shared"
    engine = create_engine(
        DATABASE_URL, connect_args={"check_same_thread": False}, echo=False
    )
else:
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL environment variable is not set")

    # Исправляем URL для PostgreSQL
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

    DATABASE_URL = re.sub(r"^postgresql\+psycopg2://", "postgresql://", DATABASE_URL)
    engine = create_engine(DATABASE_URL, echo=False, pool_pre_ping=True)


def create_db_and_tables():
    """Создает таблицы в базе данных"""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Получает сессию для работы с БД"""
    with Session(engine) as session:
        yield session
