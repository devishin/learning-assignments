"""Background notifications for due reminders."""

from __future__ import annotations

import threading
import time
import tkinter as tk
from tkinter import ttk

from database import Reminder, ReminderDatabase

try:
    from win10toast import ToastNotifier

    TOAST_AVAILABLE = True
except ImportError:
    TOAST_AVAILABLE = False


class NotificationManager:
    def __init__(self, database: ReminderDatabase, root: tk.Tk | None = None) -> None:
        self.database = database
        self.root = root
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._shown_ids: set[int] = set()
        self._toast = ToastNotifier() if TOAST_AVAILABLE else None

    def start_monitoring(self) -> None:
        if self._thread and self._thread.is_alive():
            return
        self._stop_event.clear()
        self._thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self._thread.start()

    def stop_monitoring(self) -> None:
        self._stop_event.set()

    def _monitor_loop(self) -> None:
        while not self._stop_event.is_set():
            self.database.mark_overdue()
            due_items = self.database.get_due_reminders()
            for reminder in due_items:
                if reminder.id in self._shown_ids:
                    continue
                self._shown_ids.add(reminder.id)
                self._handle_due_reminder(reminder)
            time.sleep(1)

    def _handle_due_reminder(self, reminder: Reminder) -> None:
        shown = self._show_notification(reminder.title, reminder.description)
        if not shown:
            if self.root is not None:
                self.root.after(0, lambda: self._show_popup(reminder.title, reminder.description))
            else:
                self._show_popup(reminder.title, reminder.description)

        if reminder.repeat_interval_minutes:
            self.database.reschedule_repeating(reminder.id, reminder.repeat_interval_minutes)
            self._shown_ids.discard(reminder.id)

    def _show_notification(self, title: str, message: str) -> bool:
        if not self._toast:
            return False
        try:
            self._toast.show_toast(
                title=title,
                msg=message,
                duration=10,
                threaded=True,
            )
            return True
        except Exception:
            return False

    def _show_popup(self, title: str, message: str) -> None:
        popup = tk.Toplevel(self.root)
        popup.title("Напоминание")
        popup.attributes("-topmost", True)
        popup.geometry("420x220")
        popup.focus_force()

        frame = ttk.Frame(popup, padding=16)
        frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(frame, text=title, font=("Segoe UI", 12, "bold"), wraplength=380).pack(anchor=tk.W)
        ttk.Label(frame, text=message, wraplength=380).pack(anchor=tk.W, pady=(8, 0))
        ttk.Button(frame, text="Закрыть", command=popup.destroy).pack(anchor=tk.E, pady=(16, 0))

        popup.after(30_000, popup.destroy)

    def show_manual_notification(self, title: str, message: str) -> None:
        if not self._show_notification(title, message):
            self._show_popup(title, message)

    def test_notification(self) -> None:
        self.show_manual_notification("Тест", "Проверка системы уведомлений")
