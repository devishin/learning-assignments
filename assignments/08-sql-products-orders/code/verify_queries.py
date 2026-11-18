#!/usr/bin/env python3
"""One-shot: seed fresh DB and run queries.sql (stops on first error)."""
import sqlite3
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB = ROOT / "products_orders.db"


def main() -> int:
    subprocess.check_call([sys.executable, str(ROOT / "code" / "seed.py")])
    sql = (ROOT / "sql" / "queries.sql").read_text(encoding="utf-8")
    # split on semicolon-terminated statements
    parts = []
    buf = []
    for line in sql.splitlines():
        if line.strip().startswith("--") and not buf:
            continue
        buf.append(line)
        if ";" in line:
            block = "\n".join(buf).strip()
            if block and not block.startswith("--"):
                parts.append(block)
            buf = []
    con = sqlite3.connect(DB)
    for i, stmt in enumerate(parts, 1):
        try:
            cur = con.execute(stmt)
            if stmt.lstrip().upper().startswith("SELECT"):
                rows = cur.fetchall()
                print(f"OK [{i}] SELECT -> {len(rows)} rows")
            else:
                con.commit()
                print(f"OK [{i}] {stmt.split()[0].upper()} -> {con.total_changes} changes")
        except sqlite3.Error as e:
            print(f"FAIL [{i}]: {e}\n{stmt[:120]}...")
            return 1
    con.close()
    print("All query blocks passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())