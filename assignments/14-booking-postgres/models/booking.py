"""Модель бронирования (связь user + table)."""


class Booking:
    __tablename__ = "bookings"

    fields: dict[str, str] = {
        "id": "SERIAL PRIMARY KEY",
        "user_id": "INTEGER NOT NULL REFERENCES users(id) ON DELETE CASCADE",
        "table_id": "INTEGER NOT NULL REFERENCES tables(id) ON DELETE CASCADE",
        "booked_at": "TIMESTAMP NOT NULL",
        "note": "TEXT",
    }