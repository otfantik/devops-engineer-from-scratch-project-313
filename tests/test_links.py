from fastapi.testclient import TestClient
from app.main import app
from app.database import engine
from sqlmodel import SQLModel

client = TestClient(app)


def setup_module():
    SQLModel.metadata.create_all(engine)


def teardown_module():
    SQLModel.metadata.drop_all(engine)


def test_create_link():
    response = client.post(
        "/api/links",
        json={"original_url": "https://example.com", "short_name": "exmpl"},
    )
    assert response.status_code == 201
    data = response.json()
    assert data["original_url"] == "https://example.com"
    assert data["short_name"] == "exmpl"
    assert "short_url" in data


def test_create_duplicate_short_name():
    client.post(
        "/api/links", json={"original_url": "https://example.com", "short_name": "test"}
    )
    response = client.post(
        "/api/links", json={"original_url": "https://another.com", "short_name": "test"}
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Short name already exists"


def test_get_links():
    response = client.get("/api/links")
    assert response.status_code == 200
    assert isinstance(response.json(), list)


def test_get_link_by_id():
    create_resp = client.post(
        "/api/links",
        json={"original_url": "https://example.com", "short_name": "gettest"},
    )
    link_id = create_resp.json()["id"]

    response = client.get(f"/api/links/{link_id}")
    assert response.status_code == 200
    assert response.json()["short_name"] == "gettest"


def test_get_nonexistent_link():
    response = client.get("/api/links/99999")
    assert response.status_code == 404


def test_update_link():
    create_resp = client.post(
        "/api/links",
        json={"original_url": "https://example.com", "short_name": "update"},
    )
    link_id = create_resp.json()["id"]

    response = client.put(
        f"/api/links/{link_id}",
        json={"original_url": "https://updated.com", "short_name": "updated"},
    )
    assert response.status_code == 200
    assert response.json()["original_url"] == "https://updated.com"
    assert response.json()["short_name"] == "updated"


def test_delete_link():
    create_resp = client.post(
        "/api/links",
        json={"original_url": "https://example.com", "short_name": "delete"},
    )
    link_id = create_resp.json()["id"]

    response = client.delete(f"/api/links/{link_id}")
    assert response.status_code == 204

    get_response = client.get(f"/api/links/{link_id}")
    assert get_response.status_code == 404
