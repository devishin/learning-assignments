"""Capture GUI screenshot for homework report."""

from __future__ import annotations

from pathlib import Path

import tkinter as tk

from database import ReminderDatabase
from gui import ReminderApp
from notifications import NotificationManager

OUTPUT = Path(__file__).resolve().parent / "screenshots" / "reminder_gui.png"


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    db = ReminderDatabase(Path(__file__).resolve().parent / "reminders.db")
    notifications = NotificationManager(db)
    app = ReminderApp(db, notifications)

    def capture() -> None:
        app.root.update_idletasks()
        x = app.root.winfo_rootx()
        y = app.root.winfo_rooty()
        width = app.root.winfo_width()
        height = app.root.winfo_height()
        try:
            from PIL import ImageGrab

            image = ImageGrab.grab(bbox=(x, y, x + width, y + height))
            image.save(OUTPUT)
            print(f"Screenshot saved: {OUTPUT}")
        except ImportError:
            print("Install pillow for screenshot: pip install pillow")
        app.notifications.stop_monitoring()
        app.root.destroy()

    app.root.after(1200, capture)
    app.run()
    db.close()


if __name__ == "__main__":
    main()
