from sqlmodel import SQLModel, create_engine

from app.config import settings


def get_engine():
    if settings.DATABASE_URL and settings.DATABASE_URL.startswith("postgresql"):
        return create_engine(settings.DATABASE_URL, echo=True)
    else:
        return create_engine(
            "sqlite:///./test.db", echo=True, connect_args={"check_same_thread": False}
        )


engine = get_engine()


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
