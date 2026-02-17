import pytest
from fastapi.testclient import TestClient
from app.main import app, fake_user_db

@pytest.fixture(scope='module')
def client():
    """Фикстура для создания TestClient"""
    return TestClient(app)


@pytest.fixture
def test_user():
    """Фикстура для тестового user"""
    return {"username": "test_user"}


@pytest.fixture
def setup_and_teardown():
    """Фикстура для подготовки и очистки базы данных"""
    original_data = fake_user_db.copy()
    fake_user_db.append({"username": "test_users"})
    yield
    fake_user_db.clear()
    fake_user_db.extend(original_data)


@pytest.fixture(scope="session")
def app_version():
    """Фикстура для версии приложения"""
    return "1.0.0"

