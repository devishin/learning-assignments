"""Seed demo reminders for homework."""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

from database import ReminderDatabase, STATUS_PENDING

DB_PATH = Path(__file__).resolve().parent / "reminders.db"


def main() -> None:
    db = ReminderDatabase(DB_PATH)
    db.connection.execute("DELETE FROM reminders")
    db.connection.commit()

    db.add_reminder(
        title="Сдать домашнее задание",
        description="Одноразовое напоминание",
        due_at=datetime.now() + timedelta(minutes=10),
        status=STATUS_PENDING,
        repeat_interval_minutes=None,
    )
    db.add_reminder(
        title="Пить воду",
        description="Повторяющееся напоминание",
        due_at=datetime.now() + timedelta(minutes=2),
        status=STATUS_PENDING,
        repeat_interval_minutes=30,
    )
    print("Добавлено 2 напоминания: одноразовое и повторяющееся.")
    db.close()


if __name__ == "__main__":
    main()
