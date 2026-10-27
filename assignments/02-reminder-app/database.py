"""SQLite storage for reminders."""

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable

STATUS_PENDING = "Ожидает"
STATUS_DONE = "Готово"
STATUS_OVERDUE = "Просрочено"
STATUS_CANCELLED = "Отменено"

ALL_STATUSES = (STATUS_PENDING, STATUS_DONE, STATUS_OVERDUE, STATUS_CANCELLED)


@dataclass(frozen=True)
class Reminder:
    id: int
    title: str
    description: str
    due_at: datetime
    status: str
    created_at: datetime
    repeat_interval_minutes: int | None


class ReminderDatabase:
    def __init__(self, db_path: str | Path = "reminders.db") -> None:
        self.db_path = Path(db_path)
        self.connection = sqlite3.connect(self.db_path, check_same_thread=False)
        self.connection.row_factory = sqlite3.Row
        self.init_database()

    def init_database(self) -> None:
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                due_at TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'Ожидает',
                created_at TEXT NOT NULL,
                repeat_interval_minutes INTEGER
            )
            """
        )
        self.connection.commit()

    def add_reminder(
        self,
        title: str,
        description: str,
        due_at: datetime,
        status: str = STATUS_PENDING,
        repeat_interval_minutes: int | None = None,
    ) -> int:
        cursor = self.connection.execute(
            """
            INSERT INTO reminders (title, description, due_at, status, created_at, repeat_interval_minutes)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                title.strip(),
                description.strip(),
                due_at.isoformat(timespec="seconds"),
                status,
                datetime.now().isoformat(timespec="seconds"),
                repeat_interval_minutes,
            ),
        )
        self.connection.commit()
        return int(cursor.lastrowid)

    def _row_to_reminder(self, row: sqlite3.Row) -> Reminder:
        repeat_value = row["repeat_interval_minutes"]
        return Reminder(
            id=row["id"],
            title=row["title"],
            description=row["description"],
            due_at=datetime.fromisoformat(row["due_at"]),
            status=row["status"],
            created_at=datetime.fromisoformat(row["created_at"]),
            repeat_interval_minutes=int(repeat_value) if repeat_value is not None else None,
        )

    def get_all_reminders(self, status_filter: str | None = None) -> list[Reminder]:
        if status_filter and status_filter != "Все":
            rows = self.connection.execute(
                "SELECT * FROM reminders WHERE status = ? ORDER BY due_at",
                (status_filter,),
            ).fetchall()
        else:
            rows = self.connection.execute("SELECT * FROM reminders ORDER BY due_at").fetchall()
        return [self._row_to_reminder(row) for row in rows]

    def get_due_reminders(self, now: datetime | None = None) -> list[Reminder]:
        current = now or datetime.now()
        rows = self.connection.execute(
            """
            SELECT * FROM reminders
            WHERE status = ? AND due_at <= ?
            ORDER BY due_at
            """,
            (STATUS_PENDING, current.isoformat(timespec="seconds")),
        ).fetchall()
        return [self._row_to_reminder(row) for row in rows]

    def sort_by_due_time(self, reminders: Iterable[Reminder]) -> list[Reminder]:
        return sorted(reminders, key=lambda item: item.due_at)

    def update_status(self, reminder_id: int, status: str) -> None:
        self.connection.execute(
            "UPDATE reminders SET status = ? WHERE id = ?",
            (status, reminder_id),
        )
        self.connection.commit()

    def reschedule_repeating(self, reminder_id: int, interval_minutes: int, base_time: datetime | None = None) -> None:
        next_due = (base_time or datetime.now()) + timedelta(minutes=interval_minutes)
        self.connection.execute(
            """
            UPDATE reminders
            SET due_at = ?, status = ?
            WHERE id = ?
            """,
            (next_due.isoformat(timespec="seconds"), STATUS_PENDING, reminder_id),
        )
        self.connection.commit()

    def delete_reminder(self, reminder_id: int) -> None:
        self.connection.execute("DELETE FROM reminders WHERE id = ?", (reminder_id,))
        self.connection.commit()

    def mark_overdue(self, now: datetime | None = None) -> int:
        current = now or datetime.now()
        threshold = current - timedelta(minutes=1)
        cursor = self.connection.execute(
            """
            UPDATE reminders
            SET status = ?
            WHERE status = ? AND due_at < ? AND repeat_interval_minutes IS NULL
            """,
            (STATUS_OVERDUE, STATUS_PENDING, threshold.isoformat(timespec="seconds")),
        )
        self.connection.commit()
        return cursor.rowcount

    def get_reminder_by_id(self, reminder_id: int) -> Reminder | None:
        row = self.connection.execute(
            "SELECT * FROM reminders WHERE id = ?",
            (reminder_id,),
        ).fetchone()
        if row is None:
            return None
        return self._row_to_reminder(row)

    def get_reminders_count(self) -> int:
        row = self.connection.execute("SELECT COUNT(*) AS cnt FROM reminders").fetchone()
        return int(row["cnt"])

    def close(self) -> None:
        self.connection.close()
