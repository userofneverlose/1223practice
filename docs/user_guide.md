# Руководство пользователя Currency Exchange API
## Для кого это руководство
- Разработчики, интегрирующие API в свои приложения
- Администраторы, управляющие курсами валют
- Тестировщики, проверяющие работу системы
## Быстрый старт
### 1. Проверка работы сервера
```bash
curl http://api.example.com/
2. Получение всех валют
3. Конвертация 100 USD в EUR
Полная документация API
Валюты (Currencies)
GET /currencies — список всех валют
Ответ (200 OK):
# Руководство пользователя Currency Exchange API
## Для кого это руководство
- Разработчики, интегрирующие API в свои приложения
- Администраторы, управляющие курсами валют
- Тестировщики, проверяющие работу системы
## Быстрый старт
### 1. Проверка работы сервера
```bash
curl http://api.example.com/
curl http://api.example.com/currencies
curl "http://api.example.com/exchange?from=USD&to=EUR&amount=100"
[
 {
 "id": 1,
 "code": "USD",
 "full_name": "US Dollar",
GET /currency/{code} — получить одну валюту
Пример: GET /currency/USD
POST /currencies — создать валюту
Тело запроса:
Курсы обмена (Exchange Rates)
GET /exchangeRates — список всех курсов
Ответ содержит вложенные объекты валют:
GET /exchangeRate/{pair} — курс по паре
 "sign": "$"
 }
]
{
 "code": "GBP",
 "full_name": "British Pound",
 "sign": "£"
}
[
 {
 "id": 1,
 "rate": 0.92,
 "base_currency": {"code": "USD", "full_name": "US Dollar", "sign":
"$"},
 "target_currency": {"code": "EUR", "full_name": "Euro", "sign":
"€"}
 }
]
Пример: GET /exchangeRate/USDEUR
POST /exchangeRates — создать курс
Тело запроса:
PATCH /exchangeRate/{pair} — обновить курс
Пример: PATCH /exchangeRate/USDEUR с телом {"rate": 0.95}
Конвертация (Exchange)
GET /exchange — главный эндпоинт
Параметры:
Пример: GET /exchange?from=USD&to=EUR&amount=100
Ответ:
{
 "base_currency_code": "USD",
 "target_currency_code": "EUR",
 "rate": 0.92
}
from — код исходной валюты (обязательный)
to — код целевой валюты (обязательный)
amount — сумма для конвертации (обязательный, >0)
{
 "base_currency": {"code": "USD", "full_name": "US Dollar", "sign":
"$"},
 "target_currency": {"code": "EUR", "full_name": "Euro", "sign": "€"},
 "rate": 0.92,
 "amount": 100,
 "converted_amount": 92.00
}
Административные эндпоинты (требуют аутентификации)
PATCH /currency/{code}/deactivate — скрыть валюту
GET /admin/stats — статистика системы
Коды ответов
Код Значение
200 OK — запрос выполнен успешно
201 Created — объект создан
400 Bad Request — неверные параметры запроса
404 Not Found — объект не найден
409 Conflict — дубликат (валюта или курс уже существует)
422 Unprocessable Entity — ошибка валидации
500 Internal Server Error — ошибка на сервере
Примеры в разных языках
Python (requests)
curl -X PATCH http://api.example.com/currency/USD/deactivate \
 -u admin:your_password
curl http://api.example.com/admin/stats -u admin:your_password
import requests
response = requests.get(
 "http://api.example.com/exchange",
 params={"from": "USD", "to": "EUR", "amount": 100}
JavaScript (fetch)
cURL
Часто задаваемые вопросы (FAQ)
Вопрос: Почему курс USD→EUR = 0.92, а не 1.086?
Ответ: Курсы всегда указываются как количество целевой валюты за 1 единицу базовой.
Вопрос: Как добавить кросс-курс?
Ответ: Не нужно. Система сама вычисляет кросс-курсы через USD.
Вопрос: Почему конвертация EUR→USD даёт 108.70, а не 100/0.92?
Ответ: Обратный курс вычисляется как 1/0.92 = 1.086956, затем 100 * 1.086956 =
108.6956 → округление до 108.70.
)
print(response.json()["converted_amount"])
fetch('http://api.example.com/exchange?from=USD&to=EUR&amount=100')
 .then(res => res.json())
 .then(data => console.log(data.converted_amount));
curl "http://api.example.com/exchange?from=USD&to=EUR&amount=100"
### 13.2. Создаём `docs/admin_guide.md` — руководство администратора
```markdown
# Руководство администратора Currency Exchange API
## Установка системы
### Минимальные требования
Установка как systemd-сервис (Linux)
Настройка
Переменные окружения (файл .env)
Переменная Описание По умолчанию
DEBUG Режим отладки False
HOST Адрес для привязки 0.0.0.0
- ОС: Ubuntu 20.04+ / Debian 11+ / Windows Server 2019+
- Python 3.9+
- 1 GB RAM
- 5 GB свободного места
### Быстрая установка
```bash
# Клонирование
git clone https://github.com/yourusername/currency-exchange.git
cd currency-exchange
# Настройка виртуального окружения
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
# Настройка .env
cp .env.example .env
# Отредактируйте .env (пароль администратора)
# Запуск
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
sudo cp systemd/currency-exchange.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable currency-exchange
sudo systemctl start currency-exchange
sudo systemctl status currency-exchange
Переменная Описание По умолчанию
PORT Порт сервера 8000
DATABASE_URL URL базы данных sqlite:///./currencies.db
ADMIN_USERNAME Имя администратора admin
ADMIN_PASSWORD Пароль администратора Обязательно сменить!
API_KEY Ключ для мобильных приложений Обязательно сменить!
Настройка Nginx (reverse proxy)
Настройка HTTPS (Let's Encrypt)
Управление базой данных
Резервное копирование
server {
 listen 80;
 server_name api.yourdomain.com;

 location / {
 proxy_pass http://127.0.0.1:8000;
 proxy_set_header Host $host;
 proxy_set_header X-Real-IP $remote_addr;
 }
}
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d api.yourdomain.com
# Ручной бэкап
./scripts/backup.sh
# Восстановление из бэкапа
./scripts/restore.sh backups/currencies_backup_20240101_120000.db.gz
Автоматический бэкап (cron)
# Добавьте в crontab -e
0 2 * * * /path/to/currency-exchange/scripts/backup.sh
Миграции
# Добавление нового поля
python scripts/migrate_add_is_active.py
Мониторинг
Проверка состояния
# Статус сервиса
systemctl status currency-exchange
# Просмотр логов
journalctl -u currency-exchange -f
# Статистика через API
curl -u admin:password http://localhost:8000/admin/stats
Метрики производительности
# Нагрузочное тестирование
python scripts/performance_test.py
Настройка оповещений (Prometheus + Alertmanager)
Устранение неполадок
Ошибка: «Address already in use»
Причина: Порт 8000 уже занят.
Решение:
Ошибка: «database is locked»
Причина: SQLite не поддерживает высокую конкурентность.
Решение для production:
# Популярные эндпоинты
ab -n 1000 -c 10 http://localhost:8000/currencies
# Пример правила для Prometheus
groups:
 - name: currency-alerts
 rules:
 - alert: HighResponseTime
 expr: histogram_quantile(0.95, http_request_duration_seconds) > 1
 annotations:
 summary: "Высокое время отклика API"
# Найти процесс
sudo lsof -i :8000
# Убить процесс
sudo kill -9 PID
# Или сменить порт в .env
PORT=8001
1. Перейти на PostgreSQL
2. Уменьшить количество воркеров: --workers 2
Медленные запросы
Диагностика:
# Включить логирование SQL
export DEBUG=True
uvicorn app.main:app --reload
# Посмотреть долгие запросы
grep "SELECT" logs/app.log | awk '{print $NF}' | sort -n
Оптимизация:
1. Добавить индексы в БД
2. Увеличить количество воркеров
3. Использовать кэширование (Redis)
Обновление системы
# 1. Остановить сервис
sudo systemctl stop currency-exchange
# 2. Создать бэкап
./scripts/backup.sh
# 3. Обновить код
git pull origin main
# 4. Обновить зависимости
source venv/bin/activate
pip install -r requirements.txt --upgrade
# 5. Запустить миграции
python scripts/migrate_add_is_active.py
# 6. Запустить тесты
pytest tests/ -v
# 7. Запустить сервис
sudo systemctl start currency-exchange
Контактная информация
Техническая поддержка: support@yourdomain.com
Репозиторий: https://github.com/yourusername/currency-exchange
Документация API: https://api.yourdomain.com/docs
