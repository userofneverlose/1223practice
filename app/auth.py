"""
Модуль аутентификации и авторизации.
Реализует базовую защиту административных эндпоинтов.
"""

import os
import secrets
from typing import Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import (HTTPAuthorizationCredentials, HTTPBasic,
                              HTTPBasicCredentials, HTTPBearer)

# Инициализация схем безопасности
security_basic = HTTPBasic()
security_bearer = HTTPBearer()

# Получение настроек из переменных окружения
# В реальном проекте пароли должны быть только в .env файле!
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")
API_KEY = os.getenv("API_KEY", "secret-api-key-for-mobile-app")


def verify_admin(credentials: HTTPBasicCredentials = Depends(security_basic)) -> str:
    """
    Проверка администратора через Basic Auth.
    Используется для защищённых эндпоинтов (/admin/...).

    Возвращает имя пользователя, если проверка успешна.
    Выбрасывает HTTPException 401, если credentials неверны.
    """
    # secrets.compare_digest защищает от атак по времени сравнения
    correct_username = secrets.compare_digest(credentials.username, ADMIN_USERNAME)
    correct_password = secrets.compare_digest(credentials.password, ADMIN_PASSWORD)

    if not (correct_username and correct_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверные имя пользователя или пароль",
            headers={"WWW-Authenticate": "Basic"},
        )

    return credentials.username


def verify_api_key(
    auth: HTTPAuthorizationCredentials = Depends(security_bearer),
) -> str:
    """
    Проверка API-ключа для мобильных приложений (Bearer Token).
    Используется для эндпоинтов /mobile/...

    Возвращает ключ, если он верен.
    Выбрасывает HTTPException 401, если ключ неверен.
    """
    if auth.credentials != API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный API-ключ",
        )

    return auth.credentials
