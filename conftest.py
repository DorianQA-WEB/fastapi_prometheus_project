import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
# Импортируем объекты из приложения: сам app, DI-функцию и модели

from app.main import app, get_db, Base, Item


# -------- Движок для ТЕКУЩЕГО теста (in-memory + StaticPool) --------
@pytest.fixture(scope="function")
def test_engine():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,  # <-- гарантирует одно соединение для всей БД в этом тесте
    )
    Base.metadata.create_all(bind=engine)  # создаём таблицы на ЭТОМ движке
    try:
        yield engine
    finally:
        engine.dispose()

# -------- Сессия к тестовому движку --------
@pytest.fixture(scope="function")
def test_session(test_engine):
    TestingSessionLocal = sessionmaker(autocommit=False,
                                       autoflush=False,
                                       bind=test_engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()

# -------- Клиент с переопределённым get_db --------
@pytest.fixture(scope='module')
def client(db_session):
    """Фикстура для создания TestClient"""
    # Переопределяем зависимость get_db так, чтобы эндпоинты использовали ТЕКУЩУЮ тестовую сессию.
    def override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = override_get_db
    try:
        with TestClient(app) as c:
            yield c
    finally:
    # Чистим переопределения, чтобы тесты не влияли друг на друга.
        app.dependency_overrides.clear()


@pytest.fixture
def test_user():
    """Фикстура для тестового user"""
    return {"username": "test_user"}


@pytest.fixture
def setup_and_teardown(db_session):
    """Фикстура для подготовки и очистки базы данных"""
    original_data = db_session.copy()
    db_session.append({"username": "test_users"})
    yield
    db_session.clear()
    db_session.extend(original_data)


@pytest.fixture(scope="session")
def app_version():
    """Фикстура для версии приложения"""
    return "1.0.0"

