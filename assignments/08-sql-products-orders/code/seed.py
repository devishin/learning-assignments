#!/usr/bin/env python3
"""Generate >=100 products and sample orders into products_orders.db."""
from __future__ import annotations

import random
import sqlite3
from datetime import datetime, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SQL_DIR = ROOT / "sql"
DB = ROOT / "products_orders.db"

CATEGORIES = {
    "electronics": (49.0, 2500.0),
    "home": (5.0, 450.0),
    "sports": (12.0, 900.0),
    "books": (3.0, 80.0),
    "grocery": (1.0, 35.0),
    "beauty": (8.0, 120.0),
    "toys": (6.0, 150.0),
    "automotive": (15.0, 600.0),
}

ADJECTIVES = [
    "Pro", "Lite", "Classic", "Eco", "Smart", "Urban", "Compact", "Premium", "Basic", "Max",
]
NOUNS = [
    "Router", "Lamp", "Ball", "Novel", "Tea", "Shampoo", "Puzzle", "Filter", "Cable", "Mug",
    "Sensor", "Mat", "Racket", "Cookbook", "Rice", "Serum", "Drone", "Wiper", "Hub", "Brush",
]


def sku(cat: str, n: int) -> str:
    return f"{cat[:3].upper()}-{n:04d}"


def product_name(i: int, cat: str) -> str:
    adj = ADJECTIVES[i % len(ADJECTIVES)]
    noun = NOUNS[(i // 3) % len(NOUNS)]
    return f"{adj} {noun} {cat.title()} {i}"


def load_schema(conn: sqlite3.Connection) -> None:
    conn.executescript((SQL_DIR / "schema.sql").read_text(encoding="utf-8"))


def generate_products(count: int = 120) -> list[tuple]:
    rows = []
    i = 0
    per_cat = max(count // len(CATEGORIES), 1)
    for cat, (lo, hi) in CATEGORIES.items():
        for j in range(per_cat):
            i += 1
            price = round(random.uniform(lo, hi), 2)
            rows.append((sku(cat, j + 1), product_name(i, cat), cat, price, 1))
    while len(rows) < count:
        i += 1
        cat = random.choice(list(CATEGORIES))
        lo, hi = CATEGORIES[cat]
        rows.append((sku(cat, 900 + i), product_name(i, cat), cat, round(random.uniform(lo, hi), 2), 1))
    return rows[:count]


def generate_orders(conn: sqlite3.Connection, n_orders: int = 40) -> None:
    ids = [r[0] for r in conn.execute("SELECT id FROM products").fetchall()]
    start = datetime(2026, 1, 1)
    for k in range(n_orders):
        pid = random.choice(ids)
        qty = random.randint(1, 5)
        day = start + timedelta(days=random.randint(0, 300))
        is_test = 1 if k < 5 else 0
        note = "TEST_ORDER" if is_test else None
        conn.execute(
            "INSERT INTO orders (product_id, quantity, order_date, customer_note, is_test) VALUES (?, ?, ?, ?, ?)",
            (pid, qty, day.strftime("%Y-%m-%d %H:%M:%S"), note, is_test),
        )


def main() -> None:
    if DB.exists():
        DB.unlink()
    conn = sqlite3.connect(DB)
    try:
        load_schema(conn)
        products = generate_products(120)
        conn.executemany(
            "INSERT INTO products (sku, name, category, price, in_stock) VALUES (?, ?, ?, ?, ?)",
            products,
        )
        # Seed a few ABC-prefixed names for LIKE demo
        conn.executemany(
            "INSERT INTO products (sku, name, category, price, in_stock) VALUES (?, ?, ?, ?, ?)",
            [
                ("ABC-001", "ABC Starter Kit", "electronics", 199.99, 1),
                ("ABC-002", "abc mini charger", "electronics", 29.50, 1),
                ("HOM-999", "Home ABC organizer", "home", 15.00, 1),
            ],
        )
        generate_orders(conn)
        conn.commit()
        pc = conn.execute("SELECT COUNT(*) FROM products").fetchone()[0]
        oc = conn.execute("SELECT COUNT(*) FROM orders").fetchone()[0]
        print(f"Built {DB} — products: {pc}, orders: {oc}")
    finally:
        conn.close()


if __name__ == "__main__":
    main()