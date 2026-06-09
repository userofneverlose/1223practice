"""
Общие фикстуры для всех тестов.
Pytest автоматически подхватывает этот файл.
"""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app import crud
from app.database import Base, get_db
from app.main import app
from app.schemas import CurrencyCreate, ExchangeRateCreate


# ========== Фикстура для тестовой БД ==========
@pytest.fixture(scope="function")
def db_session():
    """
    Создаёт тестовую базу данных в памяти (SQLite :memory:).
    Использует StaticPool, чтобы база не стиралась между потоками FastAPI.
    """
    # Создаём движок с пулом StaticPool
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    # Создаём все таблицы
    Base.metadata.create_all(bind=engine)

    # Создаём сессию
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    db = TestingSessionLocal()

    try:
        yield db  # Передаём сессию в тест
    finally:
        db.close()


# ========== Фикстура для тестового клиента FastAPI ==========
@pytest.fixture(scope="function")
def client(db_session):
    """
    Создаёт тестовый клиент FastAPI, который использует нашу тестовую БД.
    """

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    # Подменяем зависимость в приложении
    app.dependency_overrides[get_db] = override_get_db

    # Создаём тестовый клиент
    with TestClient(app) as test_client:
        yield test_client

    # Очищаем подмену после тестов
    app.dependency_overrides.clear()


# ========== Вспомогательные фикстуры для заполнения тестовыми данными ==========
@pytest.fixture
def sample_currencies(db_session):
    """
    Создаёт тестовые валюты: USD, EUR, RUB.
    """
    currencies_data = [
        CurrencyCreate(code="USD", full_name="US Dollar", sign="$"),
        CurrencyCreate(code="EUR", full_name="Euro", sign="€"),
        CurrencyCreate(code="RUB", full_name="Russian Ruble", sign="₽"),
    ]

    currencies = {}
    for currency_data in currencies_data:
        currency = crud.create_currency(db_session, currency_data)
        currencies[currency.code] = currency

    return currencies


@pytest.fixture
def sample_exchange_rates(db_session, sample_currencies):
    """
    Создаёт тестовые курсы на основе sample_currencies.
    """
    rates_data = [
        ExchangeRateCreate(
            base_currency_code="USD", target_currency_code="EUR", rate=0.92
        ),
        ExchangeRateCreate(
            base_currency_code="USD", target_currency_code="RUB", rate=92.50
        ),
    ]

    rates = []
    for rate_data in rates_data:
        rate = crud.create_exchange_rate(db_session, rate_data)
        rates.append(rate)

    return rates
