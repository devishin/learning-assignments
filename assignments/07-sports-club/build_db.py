#!/usr/bin/env python3
"""Rebuild sports.db from schema.sql + seed.sql and run checks.sql."""
from pathlib import Path
import sqlite3
import sys

ROOT = Path(__file__).resolve().parent
DB = ROOT / "sports.db"


def run_sql_file(conn: sqlite3.Connection, path: Path) -> None:
    sql = path.read_text(encoding="utf-8")
    conn.executescript(sql)


def main() -> int:
    if DB.exists():
        DB.unlink()
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    try:
        run_sql_file(conn, ROOT / "schema.sql")
        run_sql_file(conn, ROOT / "seed.sql")
        conn.commit()
        total = sum(
            conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
            for t in (
                "members",
                "trainers",
                "membership_types",
                "memberships",
                "classes",
                "class_enrollments",
                "visits",
                "payments",
            )
        )
        print(f"Built {DB} ({total} data rows)")
        import re

        checks = (ROOT / "checks.sql").read_text(encoding="utf-8")
        headers = re.findall(r"(?m)^-- \d+\. (.+)$", checks)
        bodies = re.split(r"(?m)^-- \d+\. .+$", checks)
        ok = 0
        for i, body in enumerate(bodies[1:], start=1):
            title = headers[i - 1] if i - 1 < len(headers) else f"query {i}"
            q = body.strip().rstrip(";").strip()
            if not q:
                continue
            rows = conn.execute(q).fetchall()
            print(f"  [{i}] {title}: {len(rows)} row(s)")
            ok += 1
        print(f"Checks executed: {ok}")
    finally:
        conn.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())