"""Entry point for the reminder application."""

from __future__ import annotations

from database import ReminderDatabase
from gui import ReminderApp
from notifications import NotificationManager


def main() -> None:
    database = ReminderDatabase("reminders.db")
    notifications = NotificationManager(database)
    app = ReminderApp(database, notifications)
    app.run()
    database.close()


if __name__ == "__main__":
    main()
