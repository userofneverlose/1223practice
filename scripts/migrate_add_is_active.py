#!/usr/bin/env python
"""
Скрипт миграции: добавляет поле is_active в таблицу currencies.
Используется для обновления схемы БД без потери данных.

Запуск:
    python scripts/migrate_add_is_active.py
"""
import os
import sqlite3
import sys

# Добавляем корень проекта в PATH, чтобы работали импорты, если они понадобятся
# Но здесь мы используем чистый SQL, поэтому импорты не нужны
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Путь к базе данных (относительно корня проекта)
DB_PATH = "currencies.db"


def migrate():
    """
    Добавляет колонку is_active в таблицу currencies.
    Возвращает True при успехе, False при ошибке.
    """
    print("🚀 Запуск миграции: добавление поля is_active...")

    # Проверка существования файла БД
    if not os.path.exists(DB_PATH):
        print(f"❌ База данных не найдена по пути: {DB_PATH}")
        print("💡 Сначала запустите приложение хотя бы один раз, чтобы создать БД.")
        return False

    conn = None
    try:
        # Подключаемся к БД
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # 1. Проверяем, существует ли уже колонка is_active
        cursor.execute("PRAGMA table_info(currencies)")
        columns = [col[1] for col in cursor.fetchall()]  # col[1] — это имя колонки

        if "is_active" in columns:
            print("✅ Поле 'is_active' уже существует. Миграция не требуется.")
            return True

        # 2. Выполняем изменение схемы
        # SQLite позволяет добавлять колонки с DEFAULT значением
        # Все существующие записи получат значение 1 (активна)
        sql = "ALTER TABLE currencies ADD COLUMN is_active INTEGER NOT NULL DEFAULT 1"

        print(f"⚙️  Выполнение SQL: {sql}")
        cursor.execute(sql)

        # 3. Сохраняем изменения
        conn.commit()
        print("✅ Поле 'is_active' успешно добавлено!")
        print("💡 Все существующие валюты теперь активны (is_active=1).")

        # 4. Дополнительная проверка (опционально)
        cursor.execute("SELECT code, is_active FROM currencies LIMIT 5")
        rows = cursor.fetchall()
        if rows:
            print("\n📊 Пример данных после миграции:")
            for row in rows:
                print(f"   - {row[0]}: is_active={row[1]}")

        return True

    except Exception as e:
        print(f"❌ Ошибка миграции: {e}")
        if conn:
            conn.rollback()  # Откатываем изменения при ошибке
        return False

    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    success = migrate()

    if success:
        print("\n🎉 Миграция завершена успешно!")
        sys.exit(0)
    else:
        print("\n💥 Миграция не удалась!")
        sys.exit(1)
