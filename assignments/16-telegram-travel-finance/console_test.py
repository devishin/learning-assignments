"""Проверка курсов и логики бюджета без Telegram."""

from __future__ import annotations

import tempfile
from pathlib import Path

from countries import resolve_country
from current_api import convert_amount, from_per_to_rate
from database import (
    add_expense,
    create_trip,
    effective_from_per_to,
    effective_to_per_from,
    get_active_trip,
    get_connection,
    init_db,
    list_expenses,
    set_rate_override,
    spent_to,
)


def _balance_text(conn, trip) -> str:
    spent = spent_to(conn, int(trip["id"]))
    left_to = float(trip["initial_to"]) - spent
    rate = effective_to_per_from(trip)
    left_from = left_to / rate
    return (
        f"остаток {left_to:.2f} {trip['to_currency']} / {left_from:.2f} {trip['from_currency']}, "
        f"курс {effective_from_per_to(trip):.2f} {trip['from_currency']} за 1 {trip['to_currency']}"
    )


def main() -> None:
    ru, rub = resolve_country("Россия")
    it, eur = resolve_country("Италия")
    to_per_from, from_per_to = from_per_to_rate(rub, eur)
    budget = 200_000.0
    in_eur = convert_amount(budget, to_per_from)
    print(f"{ru} → {it}: {from_per_to:.2f} {rub} за 1 {eur}")
    print(f"{budget:.0f} {rub} ≈ {in_eur:.2f} {eur}")

    tmp = Path(tempfile.mkdtemp())
    db_file = tmp / "test.db"
    conn = get_connection(str(db_file))
    try:
        init_db(conn)
        uid = 1
        tid = create_trip(conn, uid, ru, it, rub, eur, budget, in_eur, to_per_from)
        trip = get_active_trip(conn, uid)
        add_expense(conn, trip, 150.0)
        add_expense(conn, trip, 50.0)
        trip = get_active_trip(conn, uid)
        print("после расходов:", _balance_text(conn, trip))
        set_rate_override(conn, tid, 104.0)
        trip = get_active_trip(conn, uid)
        print("тестовый курс 104:", _balance_text(conn, trip))
        print("записей в истории:", len(list_expenses(conn, tid)))
    finally:
        conn.close()
        db_file.unlink(missing_ok=True)
        tmp.rmdir()
    print("OK")


if __name__ == "__main__":
    main()