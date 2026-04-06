import pytest
from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_index_page(client):
    """Тест: главная страница открывается"""
    response = client.get('/')
    assert response.status_code == 200

def test_login_page(client):
    """Тест: страница логина открывается"""
    response = client.get('/login')
    assert response.status_code == 200

def test_logout(client):
    """Тест: выход из системы"""
    response = client.get('/logout')
    assert response.status_code == 302