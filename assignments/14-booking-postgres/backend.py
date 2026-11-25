"""Таблицы и CRUD для users, tables, bookings."""

from __future__ import annotations

from datetime import datetime
from typing import Any, Type

from models.booking import Booking
from models.tables import Table
from models.user import User
from postgres_driver import get_driver

MODELS_ORDER: list[type] = [User, Table, Booking]


def create_table_if_not_exists(model: Type[Any]) -> None:
    """CREATE TABLE IF NOT EXISTS по полям model.fields (строками SQL-типов)."""
    table = model.__tablename__
    parts = [f"{name} {definition}" for name, definition in model.fields.items()]
    sql = f"CREATE TABLE IF NOT EXISTS {table} ({', '.join(parts)});"
    with get_driver() as db:
        db.execute(sql)


def init_database() -> None:
    for model in MODELS_ORDER:
        create_table_if_not_exists(model)


# --- Users ---


def create_user(
    email: str,
    first_name: str,
    last_name: str,
    password: str,
) -> dict[str, Any]:
    sql = """
        INSERT INTO users (email, first_name, last_name, password)
        VALUES (%s, %s, %s, %s)
        RETURNING id, email, first_name, last_name;
    """
    with get_driver() as db:
        rows = db.execute(
            sql, (email, first_name, last_name, password), fetch=True
        )
    return rows[0] if rows else {}


def get_users() -> list[dict[str, Any]]:
    with get_driver() as db:
        return db.execute(
            "SELECT id, email, first_name, last_name FROM users ORDER BY id;",
            fetch=True,
        ) or []


def update_user(
    user_id: int,
    email: str,
    first_name: str,
    last_name: str,
    password: str,
) -> None:
    sql = """
        UPDATE users
        SET email=%s, first_name=%s, last_name=%s, password=%s
        WHERE id=%s;
    """
    with get_driver() as db:
        db.execute(sql, (email, first_name, last_name, password, user_id))


def delete_user(user_id: int) -> None:
    with get_driver() as db:
        db.execute("DELETE FROM users WHERE id=%s;", (user_id,))


# --- Tables ---


def create_table_record(
    table_number: int,
    seats: int,
    status: str = "free",
) -> dict[str, Any]:
    sql = """
        INSERT INTO tables (table_number, seats, status)
        VALUES (%s, %s, %s)
        RETURNING id, table_number, seats, status;
    """
    with get_driver() as db:
        rows = db.execute(
            sql, (table_number, seats, status), fetch=True
        )
    return rows[0] if rows else {}


def get_tables() -> list[dict[str, Any]]:
    with get_driver() as db:
        return db.execute(
            "SELECT id, table_number, seats, status FROM tables ORDER BY table_number;",
            fetch=True,
        ) or []


def update_table_record(
    table_id: int,
    table_number: int,
    seats: int,
    status: str,
) -> None:
    sql = """
        UPDATE tables
        SET table_number=%s, seats=%s, status=%s
        WHERE id=%s;
    """
    with get_driver() as db:
        db.execute(sql, (table_number, seats, status, table_id))


def delete_table_record(table_id: int) -> None:
    with get_driver() as db:
        db.execute("DELETE FROM tables WHERE id=%s;", (table_id,))


# --- Bookings ---


def create_booking(
    user_id: int,
    table_id: int,
    booked_at: datetime,
    note: str = "",
) -> dict[str, Any]:
    sql = """
        INSERT INTO bookings (user_id, table_id, booked_at, note)
        VALUES (%s, %s, %s, %s)
        RETURNING id, user_id, table_id, booked_at, note;
    """
    with get_driver() as db:
        rows = db.execute(
            sql, (user_id, table_id, booked_at, note or None), fetch=True
        )
    return rows[0] if rows else {}


def get_all_bookings() -> list[dict[str, Any]]:
    sql = """
        SELECT
            b.id,
            b.booked_at,
            b.note,
            u.id AS user_id,
            u.email,
            u.first_name,
            u.last_name,
            t.id AS table_id,
            t.table_number,
            t.seats,
            t.status AS table_status
        FROM bookings b
        JOIN users u ON u.id = b.user_id
        JOIN tables t ON t.id = b.table_id
        ORDER BY b.booked_at DESC;
    """
    with get_driver() as db:
        return db.execute(sql, fetch=True) or []


def update_booking(
    booking_id: int,
    user_id: int,
    table_id: int,
    booked_at: datetime,
    note: str = "",
) -> None:
    sql = """
        UPDATE bookings
        SET user_id=%s, table_id=%s, booked_at=%s, note=%s
        WHERE id=%s;
    """
    with get_driver() as db:
        db.execute(sql, (user_id, table_id, booked_at, note or None, booking_id))


def delete_booking(booking_id: int) -> None:
    with get_driver() as db:
        db.execute("DELETE FROM bookings WHERE id=%s;", (booking_id,))


def seed_demo_data() -> None:
    """≥3 пользователей, ≥3 стола, ≥2 брони (идемпотентно по email/номеру стола)."""
    users = [
        ("anna@example.com", "Анна", "Иванова", "demo1"),
        ("boris@example.com", "Борис", "Петров", "demo2"),
        ("vika@example.com", "Вика", "Сидорова", "demo3"),
    ]
    for row in users:
        with get_driver() as db:
            exists = db.execute(
                "SELECT id FROM users WHERE email=%s;",
                (row[0],),
                fetch=True,
            )
        if not exists:
            create_user(*row)

    tables = [(1, 2, "free"), (5, 4, "free"), (10, 6, "reserved")]
    for num, seats, status in tables:
        with get_driver() as db:
            exists = db.execute(
                "SELECT id FROM tables WHERE table_number=%s;",
                (num,),
                fetch=True,
            )
        if not exists:
            create_table_record(num, seats, status)

    with get_driver() as db:
        u_rows = db.execute("SELECT id FROM users ORDER BY id LIMIT 3;", fetch=True) or []
        t_rows = db.execute("SELECT id FROM tables ORDER BY id LIMIT 2;", fetch=True) or []
        b_count = db.execute("SELECT COUNT(*) AS c FROM bookings;", fetch=True) or []

    if u_rows and t_rows and b_count and b_count[0]["c"] < 2:
        create_booking(
            int(u_rows[0]["id"]),
            int(t_rows[0]["id"]),
            datetime(2026, 3, 1, 19, 0),
            "У окна",
        )
        create_booking(
            int(u_rows[1]["id"]),
            int(t_rows[1]["id"]),
            datetime(2026, 3, 2, 20, 30),
            "День рождения",
        )