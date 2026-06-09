# ER-диаграмма: Структура базы данных

## 1. Таблица: currencies (Валюты)
| Поле | Тип | Ограничения | Описание |
| :--- | :--- | :--- | :--- |
| id | INTEGER | PRIMARY KEY | Идентификатор |
| code | TEXT | UNIQUE, NOT NULL | Код (USD, EUR) |
| full_name | TEXT | NOT NULL | Полное название |
| sign | TEXT | NOT NULL | Символ |

## 2. Таблица: exchange_rates (Курсы)
| Поле | Тип | Ограничения | Описание |
| :--- | :--- | :--- | :--- |
| id | INTEGER | PRIMARY KEY | Идентификатор |
| base_currency_id | INTEGER | FOREIGN KEY | Базовая валюта |
| target_currency_id | INTEGER | FOREIGN KEY | Целевая валюта |
| rate | DECIMAL | NOT NULL, >0 | Курс |

## Связи
- `currencies` (1) ──< `exchange_rates` (по base_currency_id)
- `currencies` (1) ──< `exchange_rates` (по target_currency_id)
