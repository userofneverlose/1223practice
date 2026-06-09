"""Интеграционные тесты REST API.
Проверяем, что эндпоинты работают корректно и взаимодействуют с БД.
"""

from decimal import Decimal

from fastapi import status


class TestCurrenciesAPI:
    """Тесты эндпоинтов для валют"""

    def test_get_currencies_empty(self, client):
        """GET /currencies — пустой список (нет валют)"""
        response = client.get("/currencies")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_create_currency_success(self, client):
        """POST /currencies — создание валюты"""
        response = client.post(
            "/currencies", json={"code": "USD", "full_name": "US Dollar", "sign": "$"}
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["code"] == "USD"
        assert data["full_name"] == "US Dollar"
        assert data["sign"] == "$"
        assert "id" in data

    def test_create_currency_duplicate(self, client):
        """POST /currencies — дубликат кода → 409 Conflict"""
        client.post(
            "/currencies", json={"code": "USD", "full_name": "US Dollar", "sign": "$"}
        )
        response = client.post(
            "/currencies", json={"code": "USD", "full_name": "US Dollar 2", "sign": "$"}
        )

        assert response.status_code == status.HTTP_409_CONFLICT

    def test_create_currency_invalid_code(self, client):
        """POST /currencies — неверный код (не 3 буквы) → 422 Unprocessable Entity"""
        response = client.post(
            "/currencies", json={"code": "US", "full_name": "US Dollar", "sign": "$"}
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_get_currency_by_code_success(self, client):
        """GET /currency/{code} — успешный поиск"""
        client.post(
            "/currencies", json={"code": "USD", "full_name": "US Dollar", "sign": "$"}
        )

        response = client.get("/currency/USD")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["code"] == "USD"

    def test_get_currency_by_code_not_found(self, client):
        """GET /currency/{code} — валюта не найдена → 404"""
        response = client.get("/currency/XXX")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "не найдена" in response.json()["detail"]

    def test_get_currencies_with_data(self, client):
        """GET /currencies — список после добавления валют"""
        client.post(
            "/currencies", json={"code": "USD", "full_name": "US Dollar", "sign": "$"}
        )
        client.post(
            "/currencies", json={"code": "EUR", "full_name": "Euro", "sign": "€"}
        )

        response = client.get("/currencies")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 2
        codes = [c["code"] for c in data]
        assert "USD" in codes
        assert "EUR" in codes


class TestExchangeRatesAPI:
    """Тесты эндпоинтов для курсов обмена"""

    def setup_method(self):
        """Перед каждым тестом создаём валюты"""
        self.currencies = ["USD", "EUR", "RUB"]

    def test_create_exchange_rate_success(self, client):
        """POST /exchangeRates — создание курса"""
        # Сначала создаём валюты
        client.post(
            "/currencies", json={"code": "USD", "full_name": "US Dollar", "sign": "$"}
        )
        client.post(
            "/currencies", json={"code": "EUR", "full_name": "Euro", "sign": "€"}
        )

        response = client.post(
            "/exchangeRates",
            json={
                "base_currency_code": "USD",
                "target_currency_code": "EUR",
                "rate": 0.92,
            },
        )

        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert float(data["rate"]) == 0.92
        assert data["base_currency"]["code"] == "USD"
        assert data["target_currency"]["code"] == "EUR"

    def test_create_exchange_rate_duplicate_pair(self, client):
        """POST /exchangeRates — дубликат пары → 409"""
        client.post(
            "/currencies", json={"code": "USD", "full_name": "US Dollar", "sign": "$"}
        )
        client.post(
            "/currencies", json={"code": "EUR", "full_name": "Euro", "sign": "€"}
        )
        client.post(
            "/exchangeRates",
            json={
                "base_currency_code": "USD",
                "target_currency_code": "EUR",
                "rate": 0.92,
            },
        )

        response = client.post(
            "/exchangeRates",
            json={
                "base_currency_code": "USD",
                "target_currency_code": "EUR",
                "rate": 0.95,
            },
        )

        assert response.status_code == status.HTTP_409_CONFLICT

    def test_get_exchange_rate_by_pair_success(self, client):
        """GET /exchangeRate/{pair} — успешный поиск"""
        client.post(
            "/currencies", json={"code": "USD", "full_name": "US Dollar", "sign": "$"}
        )
        client.post(
            "/currencies", json={"code": "EUR", "full_name": "Euro", "sign": "€"}
        )
        client.post(
            "/exchangeRates",
            json={
                "base_currency_code": "USD",
                "target_currency_code": "EUR",
                "rate": 0.92,
            },
        )

        response = client.get("/exchangeRate/USDEUR")

        assert response.status_code == status.HTTP_200_OK
        assert float(response.json()["rate"]) == 0.92

    def test_get_exchange_rate_by_pair_not_found(self, client):
        """GET /exchangeRate/{pair} — курс не найден → 404"""
        client.post(
            "/currencies", json={"code": "USD", "full_name": "US Dollar", "sign": "$"}
        )
        client.post(
            "/currencies", json={"code": "EUR", "full_name": "Euro", "sign": "€"}
        )

        response = client.get("/exchangeRate/USDEUR")

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_update_exchange_rate_success(self, client):
        """PATCH /exchangeRate/{pair} — обновление курса"""
        client.post(
            "/currencies", json={"code": "USD", "full_name": "US Dollar", "sign": "$"}
        )
        client.post(
            "/currencies", json={"code": "EUR", "full_name": "Euro", "sign": "€"}
        )
        client.post(
            "/exchangeRates",
            json={
                "base_currency_code": "USD",
                "target_currency_code": "EUR",
                "rate": 0.92,
            },
        )

        response = client.patch("/exchangeRate/USDEUR", json={"rate": 0.95})

        assert response.status_code == status.HTTP_200_OK
        assert float(response.json()["rate"]) == 0.95


class TestExchangeAPI:
    """Тесты главного эндпоинта конвертации"""

    def setup_currencies_and_rates(self, client):
        """Подготовка тестовых данных"""
        client.post(
            "/currencies", json={"code": "USD", "full_name": "US Dollar", "sign": "$"}
        )
        client.post(
            "/currencies", json={"code": "EUR", "full_name": "Euro", "sign": "€"}
        )
        client.post(
            "/currencies",
            json={"code": "RUB", "full_name": "Russian Ruble", "sign": "₽"},
        )
        client.post(
            "/exchangeRates",
            json={
                "base_currency_code": "USD",
                "target_currency_code": "EUR",
                "rate": 0.92,
            },
        )
        client.post(
            "/exchangeRates",
            json={
                "base_currency_code": "USD",
                "target_currency_code": "RUB",
                "rate": 92.50,
            },
        )

    def test_convert_direct_rate(self, client):
        """GET /exchange — прямой курс (USD→EUR)"""
        self.setup_currencies_and_rates(client)

        response = client.get("/exchange?from=USD&to=EUR&amount=100.00")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["converted_amount"] == "92.00"
        assert data["base_currency"]["code"] == "USD"
        assert data["target_currency"]["code"] == "EUR"
        assert data["amount"] == "100.00"

    def test_convert_reverse_rate(self, client):
        """GET /exchange — обратный курс (EUR→USD через USD→EUR)"""
        self.setup_currencies_and_rates(client)

        response = client.get("/exchange?from=EUR&to=USD&amount=100")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # 100 EUR * (1/0.92) = 108.6956 → 108.70
        assert data["converted_amount"] == "108.70"

    def test_convert_cross_rate(self, client):
        """GET /exchange — кросс-курс (EUR→RUB через USD)"""
        self.setup_currencies_and_rates(client)

        response = client.get("/exchange?from=EUR&to=RUB&amount=100")

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        # 100 * (92.50 / 0.92) = 10054.3478 → 10054.35
        assert data["converted_amount"] == "10054.35"

    def test_convert_same_currency(self, client):
        """GET /exchange — одинаковая валюта (USD→USD)"""
        self.setup_currencies_and_rates(client)

        response = client.get("/exchange?from=USD&to=USD&amount=100")

        assert response.status_code == status.HTTP_200_OK
        assert response.json()["converted_amount"] == "100.00"

    def test_convert_negative_amount(self, client):
        """GET /exchange — отрицательная сумма → ошибка валидации"""
        self.setup_currencies_and_rates(client)

        response = client.get("/exchange?from=USD&to=EUR&amount=-100")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_convert_currency_not_found(self, client):
        """GET /exchange — несуществующая валюта → 404"""
        self.setup_currencies_and_rates(client)

        response = client.get("/exchange?from=XXX&to=EUR&amount=100")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "не найдена" in response.json()["detail"]

    def test_convert_no_rate_available(self, client):
        """GET /exchange — нет курса для пары → 404"""
        # Создаём только валюты, без курсов
        client.post(
            "/currencies", json={"code": "USD", "full_name": "US Dollar", "sign": "$"}
        )
        client.post(
            "/currencies",
            json={"code": "GBP", "full_name": "British Pound", "sign": "£"},
        )

        response = client.get("/exchange?from=USD&to=GBP&amount=100")
        print(f"\n🔍 Status: {response.status_code}")
        print(f"🔍 Response: {response.json()}")
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "не найден" in response.json()["detail"]
