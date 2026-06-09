# Отчёт о модификации системы
## Запрос заказчика
> Добавить возможность временно отключать валюты (поле is_active)
## Изменения
### 1. База данных
- Добавлено поле `is_active` в таблицу `currencies` (INTEGER, DEFAULT 1)
- Создан скрипт миграции: `scripts/migrate_add_is_active.py`
### 2. Модель данных
```python
is_active = Column(Integer, default=1, nullable=False)
