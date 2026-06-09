# Руководство по развёртыванию Currency Exchange API
## Требования к серверу
- ОС: Ubuntu 20.04+ / Debian 11+ (или Windows Server 2019+)
- Python 3.9+
- 1 GB RAM (минимум), 2 GB RAM (рекомендуется)
- 10 GB свободного дискового пространства
## Вариант 1: Локальный запуск (разработка)
1. **Клонирование репозитория**
 ```bash
 git clone https://github.com/yourusername/currency-exchange.git
 cd currency-exchange
2. Создание виртуального окружения
python -m venv venv
source venv/bin/activate # Linux/Mac
# venv\Scripts\activate # Windows
3. Установка зависимостей
pip install -r requirements.txt
4. Запуск приложения
uvicorn app.main:app --reload

Вариант 2: Production-запуск (Ubuntu)
Шаг 1: Установка Python 3.11
sudo apt update
sudo apt install python3.11 python3.11-venv python3-pip -y
Шаг 2: Клонирование и настройка
git clone https://github.com/yourusername/currency-exchange.git
cd currency-exchange
python3.11 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
Шаг 3: Настройка .env файла
cat > .env << EOF
DEBUG=False
HOST=127.0.0.1
PORT=8000
DATABASE_URL=sqlite:///./currencies.db
EOF
Шаг 4: Настройка systemd-сервиса
sudo cp systemd/currency-exchange.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable currency-exchange
sudo systemctl start currency-exchange
Шаг 5: Настройка Nginx (reverse proxy + статика)
sudo apt install nginx -y
sudo cp docs/nginx_currency_exchange.conf /etc/nginx/sitesavailable/currency-exchange
sudo ln -s /etc/nginx/sites-available/currency-exchange /etc/nginx/sitesenabled/
sudo nginx -t
sudo systemctl restart nginx
Шаг 6: Настройка HTTPS (Let's Encrypt)
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d api.yourdomain.com
