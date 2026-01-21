# tests/test_pagination.py
import pytest
from app.main import app, parse_range_header


def test_parse_range_header():
    """Тест парсинга заголовка диапазона"""
    # Корректные диапазоны
    assert parse_range_header("[0,10]") == (0, 10)
    assert parse_range_header("[5,15]") == (5, 15)
    assert parse_range_header("[0,0]") == (0, 0)
    
    # Некорректные диапазоны
    assert parse_range_header("[10,5]") == (0, 9)  # start > end
    assert parse_range_header("[-5,10]") == (0, 9)  # отрицательный start
    assert parse_range_header("invalid") == (0, 9)  # некорректный формат
    
    # Пустая строка
    assert parse_range_header("") == (0, 9)


def test_pagination_api(client):
    """Тест API с пагинацией"""
    # Создаем 15 тестовых ссылок
    for i in range(15):
        response = client.post(
            "/api/links",
            json={
                "original_url": f"https://example{i}.com",
                "short_name": f"test{i}"
            }
        )
        assert response.status_code == 201
    
    # Тест 1: Получить первые 10 записей
    response = client.get("/api/links?range=[0,9]")
    assert response.status_code == 200
    assert 'Content-Range' in response.headers
    assert response.headers['Content-Range'] == 'links 0-9/15'
    assert len(response.json['links']) == 10
    
    # Тест 2: Получить записи 5-14
    response = client.get("/api/links?range=[5,14]")
    assert response.status_code == 200
    assert response.headers['Content-Range'] == 'links 5-14/15'
    assert len(response.json['links']) == 10
    
    # Тест 3: Получить записи 10-19 (всего 15 записей)
    response = client.get("/api/links?range=[10,19]")
    assert response.status_code == 200
    assert response.headers['Content-Range'] == 'links 10-14/15'
    assert len(response.json['links']) == 5  # Только 5 записей доступно
    
    # Тест 4: Без параметра range (должен вернуть первые 10)
    response = client.get("/api/links")
    assert response.status_code == 200
    assert response.headers['Content-Range'] == 'links 0-9/15'
    assert len(response.json['links']) == 10


def test_pagination_edge_cases(client):
    """Тест граничных случаев пагинации"""
    # Создаем 5 ссылок
    for i in range(5):
        response = client.post(
            "/api/links",
            json={
                "original_url": f"https://test{i}.com",
                "short_name": f"link{i}"
            }
        )
        assert response.status_code == 201
    
    # Запрос больше, чем есть записей
    response = client.get("/api/links?range=[0,99]")
    assert response.status_code == 200
    assert response.headers['Content-Range'] == 'links 0-4/5'
    assert len(response.json['links']) == 5
    
    # Запрос за пределами диапазона
    response = client.get("/api/links?range=[10,20]")
    assert response.status_code == 200
    assert response.headers['Content-Range'] == 'links 9-9/5'  # start-1 при пустом результате
    assert len(response.json['links']) == 0
