"""Работа с SQLite: таблица tasks и выборки для бота."""

import sqlite3
from datetime import datetime, timezone
from pathlib import Path


def get_connection(db_path: str) -> sqlite3.Connection:
    """Открываем соединение с базой (один файл на диске)."""
    path = Path(db_path)
    conn = sqlite3.connect(path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(conn: sqlite3.Connection) -> None:
    """Создаём таблицу tasks, если её ещё нет."""
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            text TEXT NOT NULL,
            user INTEGER NOT NULL,
            created_at TEXT NOT NULL
        )
        """
    )
    # Часть 2: эксперимент с дополнительными колонками для CSV
    _add_column_if_missing(conn, "tasks", "status", "TEXT NOT NULL DEFAULT 'новая'")
    _add_column_if_missing(conn, "tasks", "category", "TEXT NOT NULL DEFAULT ''")
    conn.commit()


def _add_column_if_missing(
    conn: sqlite3.Connection, table: str, column: str, definition: str
) -> None:
    """Добавляем колонку в существующую таблицу (для доработки после части 1)."""
    rows = conn.execute(f"PRAGMA table_info({table})").fetchall()
    names = {row[1] for row in rows}
    if column not in names:
        conn.execute(f"ALTER TABLE {table} ADD COLUMN {column} {definition}")


def add_task(conn: sqlite3.Connection, user_id: int, text: str) -> int:
    """Сохраняем новую задачу и возвращаем её id."""
    created = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    cursor = conn.execute(
        "INSERT INTO tasks (text, user, created_at) VALUES (?, ?, ?)",
        (text.strip(), user_id, created),
    )
    conn.commit()
    return int(cursor.lastrowid)


def list_tasks(conn: sqlite3.Connection, user_id: int) -> list[sqlite3.Row]:
    """Все задачи пользователя в порядке добавления (по id)."""
    cursor = conn.execute(
        """
        SELECT id, text, user, created_at, status, category
        FROM tasks
        WHERE user = ?
        ORDER BY id ASC
        """,
        (user_id,),
    )
    return list(cursor.fetchall())
