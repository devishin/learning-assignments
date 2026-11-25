"""Задел под CLI; основной UI — app.py."""

from __future__ import annotations

import sys

import backend


def cli_list_bookings() -> None:
    backend.init_database()
    rows = backend.get_all_bookings()
    if not rows:
        print("Бронирований пока нет.")
        return
    for row in rows:
        print(
            f"#{row['id']} {row['booked_at']} | {row['email']} | "
            f"стол {row['table_number']} | {row.get('note') or ''}"
        )


if __name__ == "__main__":
    try:
        if len(sys.argv) > 1 and sys.argv[1] == "seed":
            backend.init_database()
            backend.seed_demo_data()
            print("Таблицы созданы, демо-данные добавлены.")
        elif len(sys.argv) > 1 and sys.argv[1] == "bookings":
            cli_list_bookings()
        else:
            print(
                "Использование:\n"
                "  python main.py seed      — таблицы + демо-данные\n"
                "  python main.py bookings — список бронирований в консоли\n"
                "  python app.py           — графический интерфейс"
            )
    except Exception as exc:
        print(f"Ошибка: {exc}", file=sys.stderr)
        sys.exit(1)