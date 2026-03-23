from sqlmodel import SQLModel, create_engine

from app.config import settings

if not settings.DATABASE_URL or settings.DATABASE_URL.startswith("sqlite"):
    engine = create_engine(
        "sqlite:///./test.db", echo=True, connect_args={"check_same_thread": False}
    )
else:
    engine = create_engine(settings.DATABASE_URL, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
