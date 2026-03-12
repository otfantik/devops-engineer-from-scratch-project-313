from fastapi.testclient import TestClient
from app.main import app
from app.database import engine
from sqlmodel import SQLModel, Session
from app.models import Link

client = TestClient(app)

def setup_module():
    SQLModel.metadata.create_all(engine)
    # Создаем 15 тестовых записей
    with Session(engine) as session:
        for i in range(15):
            link = Link(
                original_url=f"https://example.com/{i}",
                short_name=f"test{i}"
            )
            session.add(link)
        session.commit()

def teardown_module():
    SQLModel.metadata.drop_all(engine)

def test_get_links_without_range():
    response = client.get("/api/links")
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 10  # По умолчанию первые 10

def test_get_first_10_links():
    headers = {"range": "[0,9]"}
    response = client.get("/api/links", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 10
    assert data[0]["short_name"] == "test0"
    assert data[9]["short_name"] == "test9"

def test_get_next_5_links():
    headers = {"range": "[10,14]"}
    response = client.get("/api/links", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5
    assert data[0]["short_name"] == "test10"
    assert data[4]["short_name"] == "test14"

def test_get_middle_5_links():
    headers = {"range": "[5,9]"}
    response = client.get("/api/links", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 5
    assert data[0]["short_name"] == "test5"
    assert data[4]["short_name"] == "test9"

def test_invalid_range_falls_back_to_default():
    # Невалидный диапазон (start > end)
    headers = {"range": "[10,5]"}
    response = client.get("/api/links", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 10  # Должен вернуть первые 10
    assert data[0]["short_name"] == "test0"

    # Отрицательный start
    headers = {"range": "[-5,5]"}
    response = client.get("/api/links", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 10

def test_range_beyond_total():
    headers = {"range": "[20,25]"}  # За пределами имеющихся данных
    response = client.get("/api/links", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 0  # Пустой список

def test_single_item_range():
    headers = {"range": "[5,5]"}
    response = client.get("/api/links", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["short_name"] == "test5"