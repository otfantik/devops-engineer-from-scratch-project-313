import sys
import os

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from app.main import app


def test_ping_route():
    """Test that /ping returns 'pong'"""
    with app.test_client() as client:
        response = client.get("/ping")
        assert response.status_code == 200
        assert response.data.decode("utf-8") == "pong"


def test_ping_content_type():
    """Test that /ping returns correct content type"""
    with app.test_client() as client:
        response = client.get("/ping")
        assert "text/html" in response.content_type


def test_non_existent_route():
    """Test that non-existent route returns 404"""
    with app.test_client() as client:
        response = client.get("/non-existent")
        assert response.status_code == 404
