"""GUI бронирования (tkinter)."""

from __future__ import annotations

import tkinter as tk
from datetime import datetime
from tkinter import messagebox, ttk

import backend


class BookingApp(tk.Tk):
    def __init__(self) -> None:
        super().__init__()
        self.title("Бронирование столиков")
        self.geometry("900x520")
        self.notebook = ttk.Notebook(self)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=8, pady=8)

        self._build_users_tab()
        self._build_tables_tab()
        self._build_bookings_tab()

        try:
            backend.init_database()
        except Exception as exc:
            messagebox.showerror("База данных", str(exc))

    def _build_users_tab(self) -> None:
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Пользователи")

        fields = {}
        for i, label in enumerate(
            ("Email", "Имя", "Фамилия", "Пароль (учебный)")
        ):
            ttk.Label(frame, text=label).grid(row=i, column=0, sticky=tk.W, pady=2)
            entry = ttk.Entry(frame, width=40)
            entry.grid(row=i, column=1, pady=2)
            fields[label] = entry

        tree = ttk.Treeview(
            frame,
            columns=("id", "email", "first", "last"),
            show="headings",
            height=12,
        )
        for col, title in zip(
            ("id", "email", "first", "last"),
            ("ID", "Email", "Имя", "Фамилия"),
            strict=False,
        ):
            tree.heading(col, text=title)
            tree.column(col, width=120 if col == "id" else 180)
        tree.grid(row=5, column=0, columnspan=3, sticky="nsew", pady=8)
        frame.rowconfigure(5, weight=1)
        frame.columnconfigure(1, weight=1)

        def refresh() -> None:
            tree.delete(*tree.get_children())
            for row in backend.get_users():
                tree.insert(
                    "",
                    tk.END,
                    values=(
                        row["id"],
                        row["email"],
                        row["first_name"],
                        row["last_name"],
                    ),
                )

        def on_create() -> None:
            try:
                backend.create_user(
                    fields["Email"].get().strip(),
                    fields["Имя"].get().strip(),
                    fields["Фамилия"].get().strip(),
                    fields["Пароль (учебный)"].get(),
                )
                refresh()
            except Exception as exc:
                messagebox.showerror("Ошибка", str(exc))

        def on_delete() -> None:
            sel = tree.selection()
            if not sel:
                return
            uid = tree.item(sel[0], "values")[0]
            try:
                backend.delete_user(int(uid))
                refresh()
            except Exception as exc:
                messagebox.showerror("Ошибка", str(exc))

        def on_update() -> None:
            sel = tree.selection()
            if not sel:
                messagebox.showinfo("Обновление", "Выберите строку в таблице.")
                return
            uid = int(tree.item(sel[0], "values")[0])
            try:
                backend.update_user(
                    uid,
                    fields["Email"].get().strip(),
                    fields["Имя"].get().strip(),
                    fields["Фамилия"].get().strip(),
                    fields["Пароль (учебный)"].get(),
                )
                refresh()
            except Exception as exc:
                messagebox.showerror("Ошибка", str(exc))

        btn_row = ttk.Frame(frame)
        btn_row.grid(row=4, column=0, columnspan=3, sticky=tk.W)
        ttk.Button(btn_row, text="Создать", command=on_create).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_row, text="Обновить выбранного", command=on_update).pack(
            side=tk.LEFT, padx=4
        )
        ttk.Button(btn_row, text="Удалить", command=on_delete).pack(side=tk.LEFT, padx=4)
        ttk.Button(btn_row, text="Обновить список", command=refresh).pack(
            side=tk.LEFT, padx=4
        )
        refresh()

    def _build_tables_tab(self) -> None:
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Столы")

        ttk.Label(frame, text="Номер").grid(row=0, column=0, sticky=tk.W)
        num_e = ttk.Entry(frame)
        num_e.grid(row=0, column=1)
        ttk.Label(frame, text="Мест").grid(row=1, column=0, sticky=tk.W)
        seats_e = ttk.Entry(frame)
        seats_e.grid(row=1, column=1)
        ttk.Label(frame, text="Статус").grid(row=2, column=0, sticky=tk.W)
        status_e = ttk.Entry(frame)
        status_e.insert(0, "free")
        status_e.grid(row=2, column=1)

        tree = ttk.Treeview(
            frame,
            columns=("id", "num", "seats", "status"),
            show="headings",
            height=14,
        )
        for col, title in zip(
            ("id", "num", "seats", "status"),
            ("ID", "Номер", "Мест", "Статус"),
            strict=False,
        ):
            tree.heading(col, text=title)
        tree.grid(row=4, column=0, columnspan=3, sticky="nsew", pady=8)
        frame.rowconfigure(4, weight=1)

        def refresh() -> None:
            tree.delete(*tree.get_children())
            for row in backend.get_tables():
                tree.insert(
                    "",
                    tk.END,
                    values=(
                        row["id"],
                        row["table_number"],
                        row["seats"],
                        row["status"],
                    ),
                )

        def on_create() -> None:
            try:
                backend.create_table_record(
                    int(num_e.get()),
                    int(seats_e.get()),
                    status_e.get().strip() or "free",
                )
                refresh()
            except Exception as exc:
                messagebox.showerror("Ошибка", str(exc))

        def on_delete() -> None:
            sel = tree.selection()
            if not sel:
                return
            tid = int(tree.item(sel[0], "values")[0])
            try:
                backend.delete_table_record(tid)
                refresh()
            except Exception as exc:
                messagebox.showerror("Ошибка", str(exc))

        def on_update() -> None:
            sel = tree.selection()
            if not sel:
                return
            tid = int(tree.item(sel[0], "values")[0])
            try:
                backend.update_table_record(
                    tid,
                    int(num_e.get()),
                    int(seats_e.get()),
                    status_e.get().strip(),
                )
                refresh()
            except Exception as exc:
                messagebox.showerror("Ошибка", str(exc))

        row = ttk.Frame(frame)
        row.grid(row=3, column=0, columnspan=3, sticky=tk.W)
        ttk.Button(row, text="Создать", command=on_create).pack(side=tk.LEFT, padx=4)
        ttk.Button(row, text="Изменить", command=on_update).pack(side=tk.LEFT, padx=4)
        ttk.Button(row, text="Удалить", command=on_delete).pack(side=tk.LEFT, padx=4)
        ttk.Button(row, text="Обновить список", command=refresh).pack(side=tk.LEFT, padx=4)
        refresh()

    def _build_bookings_tab(self) -> None:
        frame = ttk.Frame(self.notebook)
        self.notebook.add(frame, text="Бронирования")

        ttk.Label(frame, text="user_id").grid(row=0, column=0, sticky=tk.W)
        uid_e = ttk.Entry(frame)
        uid_e.grid(row=0, column=1)
        ttk.Label(frame, text="table_id").grid(row=1, column=0, sticky=tk.W)
        tid_e = ttk.Entry(frame)
        tid_e.grid(row=1, column=1)
        ttk.Label(frame, text="Дата и время (ГГГГ-ММ-ДД ЧЧ:ММ)").grid(
            row=2, column=0, sticky=tk.W
        )
        when_e = ttk.Entry(frame, width=30)
        when_e.insert(0, "2026-04-01 18:00")
        when_e.grid(row=2, column=1)
        ttk.Label(frame, text="Заметка").grid(row=3, column=0, sticky=tk.W)
        note_e = ttk.Entry(frame, width=40)
        note_e.grid(row=3, column=1)

        cols = (
            "id",
            "when",
            "email",
            "table",
            "note",
        )
        tree = ttk.Treeview(frame, columns=cols, show="headings", height=14)
        headers = {
            "id": "ID",
            "when": "Когда",
            "email": "Пользователь",
            "table": "Стол",
            "note": "Заметка",
        }
        for c in cols:
            tree.heading(c, text=headers[c])
            tree.column(c, width=160)
        tree.grid(row=5, column=0, columnspan=3, sticky="nsew", pady=8)
        frame.rowconfigure(5, weight=1)

        def refresh() -> None:
            tree.delete(*tree.get_children())
            for row in backend.get_all_bookings():
                tree.insert(
                    "",
                    tk.END,
                    values=(
                        row["id"],
                        row["booked_at"],
                        row["email"],
                        row["table_number"],
                        row.get("note") or "",
                    ),
                )

        def on_create() -> None:
            try:
                when = datetime.strptime(when_e.get().strip(), "%Y-%m-%d %H:%M")
                backend.create_booking(
                    int(uid_e.get()),
                    int(tid_e.get()),
                    when,
                    note_e.get().strip(),
                )
                refresh()
            except Exception as exc:
                messagebox.showerror("Ошибка", str(exc))

        def on_delete() -> None:
            sel = tree.selection()
            if not sel:
                return
            bid = int(tree.item(sel[0], "values")[0])
            try:
                backend.delete_booking(bid)
                refresh()
            except Exception as exc:
                messagebox.showerror("Ошибка", str(exc))

        def on_update() -> None:
            sel = tree.selection()
            if not sel:
                return
            bid = int(tree.item(sel[0], "values")[0])
            try:
                when = datetime.strptime(when_e.get().strip(), "%Y-%m-%d %H:%M")
                backend.update_booking(
                    bid,
                    int(uid_e.get()),
                    int(tid_e.get()),
                    when,
                    note_e.get().strip(),
                )
                refresh()
            except Exception as exc:
                messagebox.showerror("Ошибка", str(exc))

        row = ttk.Frame(frame)
        row.grid(row=4, column=0, columnspan=3, sticky=tk.W)
        ttk.Button(row, text="Создать", command=on_create).pack(side=tk.LEFT, padx=4)
        ttk.Button(row, text="Изменить", command=on_update).pack(side=tk.LEFT, padx=4)
        ttk.Button(row, text="Удалить", command=on_delete).pack(side=tk.LEFT, padx=4)
        ttk.Button(row, text="Обновить список", command=refresh).pack(side=tk.LEFT, padx=4)
        refresh()


def main() -> None:
    BookingApp().mainloop()


if __name__ == "__main__":
    main()