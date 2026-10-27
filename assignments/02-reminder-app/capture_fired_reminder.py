"""Capture screenshot of a fired reminder popup."""

from __future__ import annotations

import ctypes
import time
from ctypes import wintypes
from datetime import datetime, timedelta
from pathlib import Path

import mss
import tkinter as tk

from database import ReminderDatabase, STATUS_PENDING
from gui import ReminderApp
from notifications import NotificationManager

BASE = Path(__file__).resolve().parent
OUTPUT = BASE / "screenshots" / "reminder_fired.png"
DB_PATH = BASE / "reminders.db"

user32 = ctypes.windll.user32
SW_RESTORE = 9


def _find_window(title_part: str) -> int | None:
    matches: list[int] = []

    @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    def callback(hwnd: int, _lparam: int) -> bool:
        if not user32.IsWindowVisible(hwnd):
            return True
        length = user32.GetWindowTextLengthW(hwnd)
        if length == 0:
            return True
        buffer = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buffer, length + 1)
        if title_part in buffer.value:
            matches.append(hwnd)
        return True

    user32.EnumWindows(callback, 0)
    return matches[-1] if matches else None


def _capture_window(hwnd: int, output_path: Path) -> None:
    user32.ShowWindow(hwnd, SW_RESTORE)
    user32.SetForegroundWindow(hwnd)
    time.sleep(0.3)

    rect = wintypes.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    monitor = {
        "left": rect.left,
        "top": rect.top,
        "width": max(1, rect.right - rect.left),
        "height": max(1, rect.bottom - rect.top),
    }
    with mss.MSS() as grabber:
        shot = grabber.grab(monitor)
        mss.tools.to_png(shot.rgb, shot.size, output=str(output_path))


def _prepare_due_reminder(db: ReminderDatabase) -> None:
    db.connection.execute("DELETE FROM reminders")
    db.connection.commit()
    db.add_reminder(
        title="Проверка напоминания",
        description="Это сработавшее одноразовое напоминание.",
        due_at=datetime.now() + timedelta(seconds=3),
        status=STATUS_PENDING,
        repeat_interval_minutes=None,
    )


def main() -> None:
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    db = ReminderDatabase(DB_PATH)
    _prepare_due_reminder(db)

    notifications = NotificationManager(db)
    # Для демонстрации показываем popup, а не toast (toast сложнее снять на скрин).
    notifications._show_notification = lambda _title, _message: False  # type: ignore[method-assign]

    app = ReminderApp(db, notifications)
    app.root.after(100, lambda: app.root.iconify())  # свернуть главное окно, как в реальной работе

    captured = {"done": False}

    def wait_and_capture() -> None:
        deadline = time.time() + 20
        hwnd = None
        while time.time() < deadline:
            hwnd = _find_window("Напоминание")
            if hwnd:
                break
            app.root.update()
            time.sleep(0.2)

        if hwnd is None:
            print("Popup не появился за 20 секунд.")
            app.notifications.stop_monitoring()
            app.root.destroy()
            return

        time.sleep(0.4)
        _capture_window(hwnd, OUTPUT)
        print(f"Saved: {OUTPUT}")
        captured["done"] = True
        app.notifications.stop_monitoring()
        app.root.destroy()

    app.root.after(500, wait_and_capture)
    app.run()
    db.close()

    if not captured["done"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
