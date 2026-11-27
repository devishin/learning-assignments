"""SQLite: путешествия и расходы."""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path


def get_connection(db_path: str) -> sqlite3.Connection:
    path = Path(db_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS trips (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            from_country TEXT NOT NULL,
            to_country TEXT NOT NULL,
            from_currency TEXT NOT NULL,
            to_currency TEXT NOT NULL,
            initial_from REAL NOT NULL,
            initial_to REAL NOT NULL,
            api_to_per_from REAL NOT NULL,
            rate_from_per_to_override REAL,
            is_active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            trip_id INTEGER NOT NULL,
            amount_to REAL NOT NULL,
            amount_from REAL NOT NULL,
            created_at TEXT NOT NULL,
            FOREIGN KEY (trip_id) REFERENCES trips(id)
        );
        """
    )
    conn.commit()


def _now() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")


def deactivate_user_trips(conn: sqlite3.Connection, user_id: int) -> None:
    conn.execute(
        "UPDATE trips SET is_active = 0 WHERE user_id = ? AND is_active = 1",
        (user_id,),
    )
    conn.commit()


def create_trip(
    conn: sqlite3.Connection,
    user_id: int,
    from_country: str,
    to_country: str,
    from_currency: str,
    to_currency: str,
    initial_from: float,
    initial_to: float,
    api_to_per_from: float,
) -> int:
    deactivate_user_trips(conn, user_id)
    cur = conn.execute(
        """
        INSERT INTO trips (
            user_id, from_country, to_country, from_currency, to_currency,
            initial_from, initial_to, api_to_per_from, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            user_id,
            from_country,
            to_country,
            from_currency,
            to_currency,
            initial_from,
            initial_to,
            api_to_per_from,
            _now(),
        ),
    )
    conn.commit()
    return int(cur.lastrowid)


def get_active_trip(conn: sqlite3.Connection, user_id: int) -> sqlite3.Row | None:
    cur = conn.execute(
        """
        SELECT * FROM trips
        WHERE user_id = ? AND is_active = 1
        ORDER BY id DESC LIMIT 1
        """,
        (user_id,),
    )
    return cur.fetchone()


def effective_to_per_from(trip: sqlite3.Row) -> float:
    if trip["rate_from_per_to_override"] is not None:
        override = float(trip["rate_from_per_to_override"])
        if override <= 0:
            return float(trip["api_to_per_from"])
        return 1.0 / override
    return float(trip["api_to_per_from"])


def effective_from_per_to(trip: sqlite3.Row) -> float:
    return 1.0 / effective_to_per_from(trip)


def spent_to(conn: sqlite3.Connection, trip_id: int) -> float:
    row = conn.execute(
        "SELECT COALESCE(SUM(amount_to), 0) AS s FROM expenses WHERE trip_id = ?",
        (trip_id,),
    ).fetchone()
    return float(row["s"])


def add_expense(conn: sqlite3.Connection, trip: sqlite3.Row, amount_to: float) -> int:
    if amount_to <= 0:
        raise ValueError("Сумма расхода должна быть положительной")
    rate = effective_to_per_from(trip)
    amount_from = amount_to / rate
    cur = conn.execute(
        """
        INSERT INTO expenses (trip_id, amount_to, amount_from, created_at)
        VALUES (?, ?, ?, ?)
        """,
        (int(trip["id"]), amount_to, amount_from, _now()),
    )
    conn.commit()
    return int(cur.lastrowid)


def list_expenses(conn: sqlite3.Connection, trip_id: int) -> list[sqlite3.Row]:
    cur = conn.execute(
        """
        SELECT id, amount_to, amount_from, created_at
        FROM expenses WHERE trip_id = ?
        ORDER BY id ASC
        """,
        (trip_id,),
    )
    return list(cur.fetchall())


def set_rate_override(conn: sqlite3.Connection, trip_id: int, from_per_to: float) -> None:
    if from_per_to <= 0:
        raise ValueError("Курс должен быть > 0")
    conn.execute(
        "UPDATE trips SET rate_from_per_to_override = ? WHERE id = ?",
        (from_per_to, trip_id),
    )
    conn.commit()


def clear_rate_override(conn: sqlite3.Connection, trip_id: int) -> None:
    conn.execute(
        "UPDATE trips SET rate_from_per_to_override = NULL WHERE id = ?",
        (trip_id,),
    )
    conn.commit()