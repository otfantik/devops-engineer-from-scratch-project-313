def test_create_link(client):
    data = {"original_url": "https://example.com/long-url", "short_name": "exmpl"}

    response = client.post("/api/links", json=data)

    assert response.status_code == 201
    response_data = response.get_json()
    assert response_data["original_url"] == data["original_url"]
    assert response_data["short_name"] == data["short_name"]
    assert "id" in response_data
    assert "short_url" in response_data
    assert response_data["short_name"] in response_data["short_url"]
    assert "created_at" in response_data


def test_create_duplicate_link(client):
    data = {"original_url": "https://example.com", "short_name": "test"}

    response1 = client.post("/api/links", json=data)
    assert response1.status_code == 201

    response2 = client.post("/api/links", json=data)
    assert response2.status_code == 409
    assert response2.get_json()["error"] == "Short name already exists"


def test_get_all_links(client):
    links = [
        {"original_url": "https://example.com/1", "short_name": "test1"},
        {"original_url": "https://example.com/2", "short_name": "test2"},
    ]

    for link in links:
        client.post("/api/links", json=link)

    response = client.get("/api/links")
    assert response.status_code == 200

    data = response.get_json()
    assert "links" in data
    assert len(data["links"]) == 2

    # Проверяем, что у каждой ссылки есть short_url
    for link in data["links"]:
        assert "short_url" in link
        assert link["short_name"] in link["short_url"]


def test_get_link_by_id(client):
    data = {"original_url": "https://example.com/long-url", "short_name": "exmpl"}

    create_response = client.post("/api/links", json=data)
    link_id = create_response.get_json()["id"]

    response = client.get(f"/api/links/{link_id}")
    assert response.status_code == 200

    response_data = response.get_json()
    assert response_data["id"] == link_id
    assert response_data["original_url"] == data["original_url"]
    assert response_data["short_name"] == data["short_name"]
    assert "short_url" in response_data


def test_get_nonexistent_link(client):
    response = client.get("/api/links/999")
    assert response.status_code == 404
    assert response.get_json()["error"] == "Link not found"


def test_update_link(client):
    data = {"original_url": "https://example.com/long-url", "short_name": "test"}

    create_response = client.post("/api/links", json=data)
    link_id = create_response.get_json()["id"]

    update_data = {
        "original_url": "https://example.com/updated",
        "short_name": "updated",
    }

    response = client.put(f"/api/links/{link_id}", json=update_data)
    assert response.status_code == 200

    response_data = response.get_json()
    assert response_data["original_url"] == update_data["original_url"]
    assert response_data["short_name"] == update_data["short_name"]
    assert "short_url" in response_data


def test_delete_link(client):
    data = {"original_url": "https://example.com/long-url", "short_name": "exmpl"}

    create_response = client.post("/api/links", json=data)
    link_id = create_response.get_json()["id"]

    response = client.delete(f"/api/links/{link_id}")
    assert response.status_code == 200
    assert response.get_json()["message"] == "Link deleted successfully"

    get_response = client.get(f"/api/links/{link_id}")
    assert get_response.status_code == 404


def test_redirect_by_short_name(client):
    data = {"original_url": "https://example.com/long-url", "short_name": "exmpl"}

    create_response = client.post("/api/links", json=data)
    assert create_response.status_code == 201

    response = client.get(f"/{data['short_name']}")
    assert response.status_code == 302
    assert response.get_json()["redirect_to"] == data["original_url"]


def test_redirect_nonexistent_short_name(client):
    response = client.get("/nonexistent")
    assert response.status_code == 404
    assert response.get_json()["error"] == "Link not found"
