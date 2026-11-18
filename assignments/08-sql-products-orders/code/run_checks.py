#!/usr/bin/env python3
"""Apply queries.sql blocks that are safe on a fresh seeded DB (read-only checks)."""
import re
import sqlite3
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "products_orders.db"
QUERIES = ROOT / "sql" / "queries.sql"
OUT = ROOT / "screenshots"


def export(name: str, sql: str) -> None:
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    cur = con.execute(sql)
    cols = [d[0] for d in cur.description]
    rows = cur.fetchall()
    con.close()
    lines = [" | ".join(cols), "-+-".join("-" * len(c) for c in cols)]
    for r in rows[:30]:
        lines.append(" | ".join(str(r[c]) for c in cols))
    if len(rows) > 30:
        lines.append(f"... ({len(rows)} rows total)")
    (OUT / name).write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"{name}: {len(rows)} rows")


def main() -> None:
    OUT.mkdir(exist_ok=True)
    if not DB.exists():
        raise SystemExit("Run code/seed.py first")
    export("03_join_orders.txt", """
        SELECT o.id, p.sku, p.name, ROUND(o.quantity * p.price, 2) AS line_total
        FROM orders o JOIN products p ON p.id = o.product_id LIMIT 10
    """)
    export("04_aggregate_category.txt", """
        SELECT category, COUNT(*), ROUND(AVG(price), 2)
        FROM products GROUP BY category HAVING COUNT(*) > 5
    """)
    export("05_like_abc.txt", "SELECT sku, name FROM products WHERE UPPER(name) LIKE 'ABC%'")
    schema = sqlite3.connect(DB).execute(
        "SELECT sql FROM sqlite_master WHERE type='table' AND name IN ('products','orders')"
    ).fetchall()
    (OUT / "01_tables_structure.txt").write_text(
        "\n\n".join(r[0] for r in schema if r[0]) + "\n",
        encoding="utf-8",
    )
    export("02_top_price_electronics.txt", """
        SELECT sku, name, price FROM products
        WHERE category = 'electronics' AND in_stock = 1
        ORDER BY price DESC LIMIT 10
    """)
    (OUT / "README.md").write_text(
        "# Скриншоты DBeaver\n\n"
        "Добавьте 3–5 скринов:\n\n"
        "1. Структура `products` и `orders` (Diagram или Columns)\n"
        "2. Результат JOIN (заказы + товар)\n"
        "3. Агрегат по категориям (GROUP BY / HAVING)\n"
        "4. LIKE `ABC%`\n"
        "5. (опционально) SQL injection demo в консоли Python\n\n"
        "Файлы `*.txt` — текстовые выгрузки для самопроверки.\n",
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()