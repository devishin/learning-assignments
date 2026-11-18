#!/usr/bin/env python3
"""
Mini-demo: unsafe string concatenation vs parameterized queries (sqlite3).

Run: python sql_injection_demo.py
"""
import sqlite3
from pathlib import Path

DB = Path(__file__).resolve().parent.parent / "products_orders.db"


def unsafe_lookup(sku_user_input: str) -> None:
    """РИСК: SQL-инъекция — злоумышленник может подставить '; DROP ...' или UNION."""
    conn = sqlite3.connect(DB)
    try:
        query = f"SELECT id, name, price FROM products WHERE sku = '{sku_user_input}'"
        print("UNSAFE SQL:", query)
        try:
            rows = conn.execute(query).fetchall()
            print("Rows:", len(rows))
        except sqlite3.Error as e:
            print("Error:", e)
    finally:
        conn.close()


def safe_lookup(sku_user_input: str) -> None:
    """Параметры (?) — значение не становится частью SQL, только данные."""
    conn = sqlite3.connect(DB)
    try:
        query = "SELECT id, name, price FROM products WHERE sku = ?"
        print("SAFE SQL:", query, "| params:", (sku_user_input,))
        rows = conn.execute(query, (sku_user_input,)).fetchall()
        print("Rows:", len(rows))
    finally:
        conn.close()


if __name__ == "__main__":
    legit = "ABC-001"
    malicious = "x' OR '1'='1"

    print("=== Legitimate SKU ===")
    unsafe_lookup(legit)
    safe_lookup(legit)

    print("\n=== Malicious input (injection attempt) ===")
    unsafe_lookup(malicious)
    safe_lookup(malicious)