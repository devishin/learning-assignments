"""Подключение к PostgreSQL и вывод таблицы users."""

from __future__ import annotations

import os
import sys

import psycopg2
from dotenv import load_dotenv


def _connection_params() -> dict[str, str | int]:
    load_dotenv()
    required = ("DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD")
    missing = [key for key in required if not os.getenv(key)]
    if missing:
        raise RuntimeError(
            f"Не заданы переменные в .env: {', '.join(missing)}. "
            "Скопируйте .env.example в .env и заполните значения."
        )
    return {
        "host": os.environ["DB_HOST"],
        "port": int(os.environ["DB_PORT"]),
        "dbname": os.environ["DB_NAME"],
        "user": os.environ["DB_USER"],
        "password": os.environ["DB_PASSWORD"],
    }


def main() -> None:
    conn = None
    try:
        conn = psycopg2.connect(**_connection_params())
        with conn.cursor() as cur:
            cur.execute("SELECT id, name, age FROM users ORDER BY id;")
            rows = cur.fetchall()
        if not rows:
            print("Таблица users пуста — добавьте минимум 3 записи в pgAdmin.")
        for row in rows:
            print(row)
    except psycopg2.Error as exc:
        print(f"Ошибка PostgreSQL: {exc}", file=sys.stderr)
        sys.exit(1)
    except RuntimeError as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)
    finally:
        if conn is not None:
            conn.close()


if __name__ == "__main__":
    main()