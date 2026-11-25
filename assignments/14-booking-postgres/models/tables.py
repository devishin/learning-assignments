"""Модель столика в ресторане."""


class Table:
    __tablename__ = "tables"

    fields: dict[str, str] = {
        "id": "SERIAL PRIMARY KEY",
        "table_number": "INTEGER NOT NULL UNIQUE",
        "seats": "INTEGER NOT NULL CHECK (seats > 0)",
        "status": "TEXT NOT NULL DEFAULT 'free'",
    }