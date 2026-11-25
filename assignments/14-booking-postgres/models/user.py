"""Модель пользователя (только описание полей, без репозитория)."""


class User:
    __tablename__ = "users"

    fields: dict[str, str] = {
        "id": "SERIAL PRIMARY KEY",
        "email": "TEXT NOT NULL UNIQUE",
        "first_name": "TEXT NOT NULL",
        "last_name": "TEXT NOT NULL",
        "password": "TEXT NOT NULL",
    }