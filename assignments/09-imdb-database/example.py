#!/usr/bin/env python3
"""Пример использования database.DatabaseManager (учебная БД, не IMDB)."""

from __future__ import annotations

from pathlib import Path

import database

DB_PATH = Path(__file__).resolve().parent / "data" / "demo.db"


def main() -> None:
    with database.DatabaseManager(DB_PATH) as db:
        db.execute_script(
            """
            DROP TABLE IF EXISTS users;
            CREATE TABLE users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT UNIQUE
            );
            """
        )

        # Вставка (параметры, не f-строка в SQL)
        db.insert_record("users", {"name": "Иван", "email": "ivan@example.com"})
        db.insert_record("users", {"name": "Мария", "email": "maria@example.com"})

        # Чтение
        all_users = db.select_records("users", order_by="id")
        print("После вставки:", all_users)

        # Обновление с WHERE
        db.update_records(
            "users",
            {"name": "Иван Петров"},
            "email = ?",
            ("ivan@example.com",),
        )

        # Чтение одной записи
        one = db.select_one("users", "email = ?", ("ivan@example.com",))
        print("После обновления:", one)

        # Удаление с WHERE
        db.delete_records("users", "email = ?", ("maria@example.com",))
        print("Осталось записей:", db.count_records("users"))


if __name__ == "__main__":
    main()