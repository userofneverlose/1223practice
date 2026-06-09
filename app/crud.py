"""
CRUD-операции для работы с БД.
Здесь только взаимодействие с базой данных, без бизнес-логики.
Бизнес-логика (конвертация) — в отдельном файле calculator.py.

Обновлено (Раздел 12): Добавлена поддержка поля is_active.
"""

from decimal import Decimal
from typing import List, Optional, Tuple

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import Currency, ExchangeRate
from app.schemas import CurrencyCreate, ExchangeRateCreate

# ========== Валюты (Currencies) ==========


def get_all_currencies(db: Session, include_inactive: bool = False) -> List[Currency]:
    """
    Получить список всех валют.

    Args:
        db: Сессия БД
        include_inactive: Если True, возвращает все валюты (включая неактивные).
                          Если False (по умолчанию), возвращает только активные.

    Returns:
        List[Currency]: Список валют.
    """
    query = db.query(Currency)

    # Фильтруем неактивные, если не запрошено обратное
    if not include_inactive:
        query = query.filter(Currency.is_active == 1)

    return query.order_by(Currency.code).all()


def get_currency_by_code(
    db: Session, code: str, include_inactive: bool = False
) -> Optional[Currency]:
    """
    Найти валюту по её коду (например, USD, EUR).

    Args:
        db: Сессия БД
        code: Код валюты (3 буквы, регистронезависимо)
        include_inactive: Если True, возвращает и неактивные валюты.

    Returns:
        Optional[Currency]: Найденная валюта или None.
    """
    query = db.query(Currency).filter(Currency.code == code.upper())

    # Фильтруем неактивные, если не запрошено обратное
    if not include_inactive:
        query = query.filter(Currency.is_active == 1)

    return query.first()


def create_currency(db: Session, currency_data: CurrencyCreate) -> Currency:
    """
    Создать новую валюту.

    Args:
        db: Сессия БД
        currency_data: Данные из POST-запроса (код, имя, символ)

    Returns:
        Currency: Созданная валюта (с присвоенным id)

    Raises:
        IntegrityError: Если валюта с таким кодом уже существует
    """
    # Преобразуем Pydantic-схему в SQLAlchemy-модель
    db_currency = Currency(
        code=currency_data.code.upper(),
        full_name=currency_data.full_name,
        sign=currency_data.sign,
        is_active=1,  # По умолчанию валюта активна
    )

    db.add(db_currency)
    try:
        db.commit()  # Пытаемся сохранить
        db.refresh(db_currency)  # Загружаем сгенерированный id из БД
    except IntegrityError:
        db.rollback()  # Откатываем изменения при ошибке
        raise  # Пробрасываем исключение выше (для обработки в API)

    return db_currency


def deactivate_currency(db: Session, code: str) -> bool:
    """
    Деактивировать валюту (скрыть от API).
    Физически запись не удаляется, просто ставится флаг is_active=0.

    Args:
        db: Сессия БД
        code: Код валюты

    Returns:
        bool: True если валюта найдена и деактивирована, иначе False.
    """
    # Ищем валюту, игнорируя её текущий статус
    currency = get_currency_by_code(db, code, include_inactive=True)

    if not currency:
        return False

    currency.is_active = 0
    db.commit()
    return True


def activate_currency(db: Session, code: str) -> bool:
    """
    Активировать валюту (вернуть в список доступных).

    Args:
        db: Сессия БД
        code: Код валюты

    Returns:
        bool: True если валюта найдена и активирована, иначе False.
    """
    # Ищем валюту, игнорируя её текущий статус
    currency = get_currency_by_code(db, code, include_inactive=True)

    if not currency:
        return False

    currency.is_active = 1
    db.commit()
    return True


# ========== Курсы обмена (Exchange Rates) ==========


def get_all_exchange_rates(db: Session) -> List[ExchangeRate]:
    """
    Получить список всех курсов с подгруженными связанными валютами.

    Note:
        joinedload() — это "жадная загрузка" (eager loading).
        Вместо N+1 запросов мы делаем один запрос с JOIN.
    """
    from sqlalchemy.orm import joinedload

    return (
        db.query(ExchangeRate)
        .options(
            joinedload(ExchangeRate.base_currency),
            joinedload(ExchangeRate.target_currency),
        )
        .all()
    )


def get_exchange_rate_by_pair(
    db: Session, base_code: str, target_code: str
) -> Optional[ExchangeRate]:
    """
    Найти курс по паре валют (например, USD → EUR).

    Args:
        db: Сессия БД
        base_code: Код базовой валюты (например, "USD")
        target_code: Код целевой валюты (например, "EUR")

    Returns:
        Optional[ExchangeRate]: Найденный курс или None.
    """
    # Сначала получаем объекты валют (чтобы знать их id)
    # Важно: для поиска курса нам нужны даже неактивные валюты?
    # Обычно да, так как исторические курсы могут относиться к старым валютам.
    base_currency = get_currency_by_code(db, base_code, include_inactive=True)
    target_currency = get_currency_by_code(db, target_code, include_inactive=True)

    # Если хоть одна валюта не найдена вообще — возвращаем None
    if not base_currency or not target_currency:
        return None

    # Ищем курс по числовым id (быстрее, чем по кодам)
    return (
        db.query(ExchangeRate)
        .filter(
            ExchangeRate.base_currency_id == base_currency.id,
            ExchangeRate.target_currency_id == target_currency.id,
        )
        .first()
    )


def create_exchange_rate(db: Session, rate_data: ExchangeRateCreate) -> ExchangeRate:
    """
    Создать новый курс обмена.

    Args:
        db: Сессия БД
        rate_data: Данные из POST-запроса (коды валют и курс)

    Returns:
        ExchangeRate: Созданный курс

    Raises:
        ValueError: Если одна из валют не найдена
        IntegrityError: Если курс для такой пары уже существует
    """
    # Находим валюты по кодам
    base_currency = get_currency_by_code(
        db, rate_data.base_currency_code, include_inactive=True
    )
    target_currency = get_currency_by_code(
        db, rate_data.target_currency_code, include_inactive=True
    )

    if not base_currency:
        raise ValueError(f"Валюта {rate_data.base_currency_code} не найдена")
    if not target_currency:
        raise ValueError(f"Валюта {rate_data.target_currency_code} не найдена")

    # Создаём курс
    db_rate = ExchangeRate(
        base_currency_id=base_currency.id,
        target_currency_id=target_currency.id,
        rate=rate_data.rate,
    )

    db.add(db_rate)
    try:
        db.commit()
        db.refresh(db_rate)
        # Подгружаем связанные валюты для ответа
        db.refresh(db_rate, attribute_names=["base_currency", "target_currency"])
    except IntegrityError:
        db.rollback()
        raise

    return db_rate


def update_exchange_rate(
    db: Session, pair: str, new_rate: Decimal  # например "USDEUR"
) -> Optional[ExchangeRate]:
    """
    Обновить существующий курс.

    Args:
        db: Сессия БД
        pair: Строка из 6 символов (код1 + код2), например "USDEUR"
        new_rate: Новое значение курса

    Returns:
        Optional[ExchangeRate]: Обновлённый курс или None, если не найден
    """
    # Разбираем pair на два кода: первые 3 и последние 3 символа
    if len(pair) != 6:
        raise ValueError("Pair должен быть строкой из 6 символов (например, USDEUR)")

    base_code = pair[:3]  # "USD"
    target_code = pair[3:]  # "EUR"

    # Находим курс
    rate = get_exchange_rate_by_pair(db, base_code, target_code)

    if not rate:
        return None

    # Обновляем курс
    rate.rate = new_rate
    db.commit()
    db.refresh(rate)

    return rate
