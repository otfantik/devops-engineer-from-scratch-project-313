import pytest
from app.main import app


@pytest.fixture
def client():
    with app.test_client() as client:
        yield client


def test_ping_route(client):
    response = client.get("/ping")
    assert response.status_code == 200
    data = response.get_json()
    assert data["message"] == "pong"


def test_non_existent_route(client):
    response = client.get("/non-existent")
    assert response.status_code == 404
    data = response.get_json()
    assert data is not None
    assert "error" in data
