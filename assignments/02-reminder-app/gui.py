"""Tkinter GUI for the reminder application."""

from __future__ import annotations

import tkinter as tk
from datetime import datetime, timedelta
from tkinter import messagebox, ttk

from database import (
    ALL_STATUSES,
    STATUS_CANCELLED,
    STATUS_DONE,
    STATUS_PENDING,
    ReminderDatabase,
)
from notifications import NotificationManager


class ReminderApp:
    def __init__(self, database: ReminderDatabase, notifications: NotificationManager) -> None:
        self.database = database
        self.notifications = notifications
        self.root = tk.Tk()
        self.root.title("Напоминалка")
        self.root.geometry("900x560")
        self.notifications.root = self.root
        self.status_filter = tk.StringVar(value="Все")
        self.setup_ui()
        self.refresh_reminders()
        self.notifications.start_monitoring()
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

    def setup_ui(self) -> None:
        main = ttk.Frame(self.root, padding=12)
        main.pack(fill=tk.BOTH, expand=True)

        form = ttk.LabelFrame(main, text="Новое напоминание", padding=10)
        form.pack(fill=tk.X)

        ttk.Label(form, text="Заголовок").grid(row=0, column=0, sticky=tk.W)
        self.title_entry = ttk.Entry(form, width=40)
        self.title_entry.grid(row=0, column=1, padx=8, sticky=tk.W)

        ttk.Label(form, text="Описание").grid(row=1, column=0, sticky=tk.W, pady=(8, 0))
        self.description_entry = ttk.Entry(form, width=60)
        self.description_entry.grid(row=1, column=1, padx=8, pady=(8, 0), sticky=tk.W)

        ttk.Label(form, text="Дата и время (ГГГГ-ММ-ДД ЧЧ:ММ)").grid(row=2, column=0, sticky=tk.W, pady=(8, 0))
        self.due_entry = ttk.Entry(form, width=24)
        self.due_entry.grid(row=2, column=1, padx=8, pady=(8, 0), sticky=tk.W)
        self.due_entry.insert(0, (datetime.now() + timedelta(minutes=5)).strftime("%Y-%m-%d %H:%M"))

        ttk.Label(form, text="Повтор (мин., пусто = одноразово)").grid(row=3, column=0, sticky=tk.W, pady=(8, 0))
        self.repeat_entry = ttk.Entry(form, width=10)
        self.repeat_entry.grid(row=3, column=1, padx=8, pady=(8, 0), sticky=tk.W)

        quick = ttk.Frame(form)
        quick.grid(row=4, column=1, sticky=tk.W, pady=(8, 0))
        ttk.Button(quick, text="+1 мин", command=lambda: self.set_quick_time(1)).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(quick, text="+5 мин", command=lambda: self.set_quick_time(5)).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(quick, text="+15 мин", command=lambda: self.set_quick_time(15)).pack(side=tk.LEFT)

        actions = ttk.Frame(form)
        actions.grid(row=5, column=1, sticky=tk.W, pady=(10, 0))
        ttk.Button(actions, text="Добавить", command=self.add_reminder).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(actions, text="Обновить список", command=self.refresh_reminders).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(actions, text="Тест уведомления", command=self.test_notification).pack(side=tk.LEFT)

        filter_frame = ttk.Frame(main)
        filter_frame.pack(fill=tk.X, pady=(12, 6))
        ttk.Label(filter_frame, text="Фильтр по статусу:").pack(side=tk.LEFT)
        ttk.Combobox(
            filter_frame,
            textvariable=self.status_filter,
            values=["Все", *ALL_STATUSES],
            state="readonly",
            width=16,
        ).pack(side=tk.LEFT, padx=8)
        ttk.Button(filter_frame, text="Применить", command=self.refresh_reminders).pack(side=tk.LEFT)

        list_frame = ttk.LabelFrame(main, text="Напоминания", padding=8)
        list_frame.pack(fill=tk.BOTH, expand=True)

        columns = ("id", "title", "due_at", "status", "repeat")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=12)
        self.tree.heading("id", text="ID")
        self.tree.heading("title", text="Заголовок")
        self.tree.heading("due_at", text="Время")
        self.tree.heading("status", text="Статус")
        self.tree.heading("repeat", text="Повтор")
        self.tree.column("id", width=50, anchor=tk.CENTER)
        self.tree.column("title", width=220)
        self.tree.column("due_at", width=160)
        self.tree.column("status", width=120, anchor=tk.CENTER)
        self.tree.column("repeat", width=100, anchor=tk.CENTER)
        self.tree.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
        self.tree.bind("<Double-1>", self.on_double_click)

        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.tree.configure(yscrollcommand=scrollbar.set)

        bottom = ttk.Frame(main)
        bottom.pack(fill=tk.X, pady=(8, 0))
        ttk.Button(bottom, text="Готово", command=self.mark_as_done).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(bottom, text="Отменено", command=self.mark_as_cancelled).pack(side=tk.LEFT, padx=(0, 6))
        ttk.Button(bottom, text="Удалить", command=self.delete_reminder).pack(side=tk.LEFT)

        self.status_bar = ttk.Label(main, text="")
        self.status_bar.pack(fill=tk.X, pady=(8, 0))
        self.update_status_bar()

    def update_status_bar(self) -> None:
        self.status_bar.config(text=f"Всего напоминаний: {self.database.get_reminders_count()}")

    def test_notification(self) -> None:
        self.notifications.test_notification()

    def set_quick_time(self, minutes: int) -> None:
        self.due_entry.delete(0, tk.END)
        self.due_entry.insert(0, (datetime.now() + timedelta(minutes=minutes)).strftime("%Y-%m-%d %H:%M"))

    def add_reminder(self) -> None:
        title = self.title_entry.get().strip()
        if not title:
            messagebox.showwarning("Проверка", "Введите заголовок.")
            return
        try:
            due_at = datetime.strptime(self.due_entry.get().strip(), "%Y-%m-%d %H:%M")
        except ValueError:
            messagebox.showerror("Ошибка", "Неверный формат даты. Используйте ГГГГ-ММ-ДД ЧЧ:ММ")
            return

        repeat_raw = self.repeat_entry.get().strip()
        repeat_minutes = int(repeat_raw) if repeat_raw else None
        if repeat_minutes is not None and repeat_minutes <= 0:
            messagebox.showerror("Ошибка", "Интервал повтора должен быть больше 0.")
            return

        self.database.add_reminder(
            title=title,
            description=self.description_entry.get().strip(),
            due_at=due_at,
            status=STATUS_PENDING,
            repeat_interval_minutes=repeat_minutes,
        )
        self.title_entry.delete(0, tk.END)
        self.description_entry.delete(0, tk.END)
        self.refresh_reminders()

    def refresh_reminders(self) -> None:
        self.database.mark_overdue()
        for item in self.tree.get_children():
            self.tree.delete(item)

        reminders = self.database.sort_by_due_time(
            self.database.get_all_reminders(self.status_filter.get())
        )
        for reminder in reminders:
            repeat_text = f"{reminder.repeat_interval_minutes} мин" if reminder.repeat_interval_minutes else "—"
            self.tree.insert(
                "",
                tk.END,
                values=(
                    reminder.id,
                    reminder.title,
                    reminder.due_at.strftime("%Y-%m-%d %H:%M"),
                    reminder.status,
                    repeat_text,
                ),
            )
        self.update_status_bar()

    def _selected_id(self) -> int | None:
        selection = self.tree.selection()
        if not selection:
            messagebox.showinfo("Выбор", "Выберите напоминание в списке.")
            return None
        values = self.tree.item(selection[0], "values")
        return int(values[0])

    def mark_as_done(self) -> None:
        reminder_id = self._selected_id()
        if reminder_id is None:
            return
        self.database.update_status(reminder_id, STATUS_DONE)
        self.refresh_reminders()

    def mark_as_cancelled(self) -> None:
        reminder_id = self._selected_id()
        if reminder_id is None:
            return
        self.database.update_status(reminder_id, STATUS_CANCELLED)
        self.refresh_reminders()

    def delete_reminder(self) -> None:
        reminder_id = self._selected_id()
        if reminder_id is None:
            return
        if messagebox.askyesno("Удаление", "Удалить выбранное напоминание?"):
            self.database.delete_reminder(reminder_id)
            self.refresh_reminders()

    def on_double_click(self, _event: tk.Event) -> None:
        reminder_id = self._selected_id()
        if reminder_id is None:
            return
        reminder = self.database.get_reminder_by_id(reminder_id)
        if reminder is None:
            return
        repeat_text = (
            f"{reminder.repeat_interval_minutes} мин"
            if reminder.repeat_interval_minutes
            else "одноразовое"
        )
        messagebox.showinfo(
            reminder.title,
            f"Описание: {reminder.description or '—'}\n"
            f"Время: {reminder.due_at.strftime('%Y-%m-%d %H:%M')}\n"
            f"Статус: {reminder.status}\n"
            f"Повтор: {repeat_text}",
        )

    def on_closing(self) -> None:
        if messagebox.askyesno("Выход", "Вы уверены, что хотите выйти?"):
            self.notifications.stop_monitoring()
            self.root.destroy()

    def run(self) -> None:
        self.root.mainloop()
