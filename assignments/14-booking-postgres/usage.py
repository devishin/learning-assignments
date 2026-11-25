"""Пример подключения через postgres_driver (из урока)."""

from postgres_driver import get_driver

# Параметры — в .env:
# DB_HOST=localhost
# DB_PORT=5432
# DB_NAME=booking
# DB_USER=admin
# DB_PASSWORD=...

with get_driver() as db:
    rows = db.execute("SELECT version();", fetch=True)
    print(rows[0]["version"] if rows else "нет ответа")