import pytest
import os

os.environ["TESTING"] = "true"
os.environ["BASE_URL"] = "http://testserver"

from app.main import app
from sqlmodel import SQLModel


@pytest.fixture(autouse=True)
def create_tables():
    from app.main import engine

    SQLModel.metadata.create_all(engine)
    yield
    SQLModel.metadata.drop_all(engine)


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client
