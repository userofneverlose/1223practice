#!/bin/bash
# Скрипт запуска приложения в production-режиме
# Использование: ./scripts/start.sh

echo "🚀 Запуск Currency Exchange API..."

# Переходим в корень проекта
cd "$(dirname "$0")/.."

# Активируем виртуальное окружение
source venv/bin/activate

# Устанавливаем переменные окружения для production
export DEBUG=False
export HOST=0.0.0.0 # Доступно с любого IP
export PORT=8000

# Запускаем через uvicorn с несколькими воркерами
# --workers 4 — 4 параллельных процесса (используем все ядра CPU)
# --log-level info — информативные логи
uvicorn app.main:app --host $HOST --port $PORT --workers 4 --log-level info

# Сохраняем PID для возможной остановки
echo $! > app.pid
echo "✅ Сервер запущен, PID: $(cat app.pid)"
