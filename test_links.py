import pytest
from app.main import app
from app.database import create_db_and_tables
from sqlmodel import SQLModel, create_engine, Session
from sqlmodel.pool import StaticPool


@pytest.fixture
def client():
    """Create test client with in-memory SQLite database"""
    # Используем SQLite для тестов
    test_engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(test_engine)
    
    # Мокаем get_session для использования тестовой БД
    def get_test_session():
        with Session(test_engine) as session:
            yield session
    
    # Подменяем зависимость
    app.before_request_funcs = {}
    
    # Создаем тестового клиента
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client


def test_create_link(client):
    """Test creating a new link"""
    data = {
        "original_url": "https://example.com/long-url",
        "short_name": "exmpl"
    }
    
    response = client.post("/api/links", json=data)
    assert response.status_code == 201
    
    result = response.get_json()
    assert result["original_url"] == data["original_url"]
    assert result["short_name"] == data["short_name"]
    assert "short_url" in result
    assert "id" in result


def test_create_duplicate_link(client):
    """Test creating duplicate link should fail"""
    data = {
        "original_url": "https://example.com/long-url",
        "short_name": "exmpl"
    }
    
    # Первое создание
    client.post("/api/links", json=data)
    
    # Второе создание с тем же short_name
    response = client.post("/api/links", json=data)
    assert response.status_code == 409
    
    result = response.get_json()
    assert "error" in result
    assert "already exists" in result["error"]


def test_get_all_links(client):
    """Test getting all links"""
    # Создаем несколько ссылок
    links = [
        {"original_url": "https://example.com/1", "short_name": "test1"},
        {"original_url": "https://example.com/2", "short_name": "test2"},
    ]
    
    for link in links:
        client.post("/api/links", json=link)
    
    response = client.get("/api/links")
    assert response.status_code == 200
    
    result = response.get_json()
    assert isinstance(result, list)
    assert len(result) == 2


def test_get_link_by_id(client):
    """Test getting link by ID"""
    # Создаем ссылку
    data = {
        "original_url": "https://example.com/long-url",
        "short_name": "exmpl"
    }
    
    create_response = client.post("/api/links", json=data)
    link_id = create_response.get_json()["id"]
    
    # Получаем по ID
    response = client.get(f"/api/links/{link_id}")
    assert response.status_code == 200
    
    result = response.get_json()
    assert result["id"] == link_id
    assert result["original_url"] == data["original_url"]


def test_get_nonexistent_link(client):
    """Test getting non-existent link returns 404"""
    response = client.get("/api/links/999")
    assert response.status_code == 404


def test_update_link(client):
    """Test updating a link"""
    # Создаем ссылку
    data = {
        "original_url": "https://example.com/long-url",
        "short_name": "exmpl"
    }
    
    create_response = client.post("/api/links", json=data)
    link_id = create_response.get_json()["id"]
    
    # Обновляем
    update_data = {
        "original_url": "https://example.com/updated-url",
        "short_name": "updated"
    }
    
    response = client.put(f"/api/links/{link_id}", json=update_data)
    assert response.status_code == 200
    
    result = response.get_json()
    assert result["original_url"] == update_data["original_url"]
    assert result["short_name"] == update_data["short_name"]


def test_delete_link(client):
    """Test deleting a link"""
    # Создаем ссылку
    data = {
        "original_url": "https://example.com/long-url",
        "short_name": "exmpl"
    }
    
    create_response = client.post("/api/links", json=data)
    link_id = create_response.get_json()["id"]
    
    # Удаляем
    response = client.delete(f"/api/links/{link_id}")
    assert response.status_code == 204
    
    # Проверяем что удалилась
    get_response = client.get(f"/api/links/{link_id}")
    assert get_response.status_code == 404


def test_redirect_endpoint(client):
    """Test redirect endpoint returns original URL"""
    data = {
        "original_url": "https://example.com/long-url",
        "short_name": "exmpl"
    }
    
    client.post("/api/links", json=data)
    
    response = client.get("/r/exmpl")
    assert response.status_code == 200
    
    result = response.get_json()
    assert result["url"] == data["original_url"]
