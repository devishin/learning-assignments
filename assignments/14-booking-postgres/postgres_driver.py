"""Драйвер PostgreSQL: подключение и выполнение SQL."""

from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Any, Iterator

import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor

_ENV_PATH = os.path.join(os.path.dirname(__file__), ".env")
load_dotenv(_ENV_PATH)


def _connection_kwargs() -> dict[str, Any]:
    required = ("DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD")
    missing = [key for key in required if not os.getenv(key)]
    if missing:
        raise RuntimeError(
            f"Не заданы переменные в .env: {', '.join(missing)}"
        )
    return {
        "host": os.environ["DB_HOST"],
        "port": int(os.environ["DB_PORT"]),
        "dbname": os.environ["DB_NAME"],
        "user": os.environ["DB_USER"],
        "password": os.environ["DB_PASSWORD"],
    }


class PostgresDriver:
    def __init__(self) -> None:
        self._conn: psycopg2.extensions.connection | None = None

    def connect(self) -> None:
        if self._conn is None or self._conn.closed:
            self._conn = psycopg2.connect(**_connection_kwargs())

    def close(self) -> None:
        if self._conn is not None and not self._conn.closed:
            self._conn.close()
        self._conn = None

    def execute(
        self,
        sql: str,
        params: tuple | dict | None = None,
        *,
        fetch: bool = False,
    ) -> list[dict[str, Any]] | None:
        self.connect()
        assert self._conn is not None
        with self._conn.cursor(cursor_factory=RealDictCursor) as cur:
            cur.execute(sql, params)
            if fetch:
                rows = cur.fetchall()
                return [dict(row) for row in rows]
            self._conn.commit()
            return None

    def executemany(self, sql: str, seq: list[tuple]) -> None:
        self.connect()
        assert self._conn is not None
        with self._conn.cursor() as cur:
            cur.executemany(sql, seq)
        self._conn.commit()


@contextmanager
def get_driver() -> Iterator[PostgresDriver]:
    driver = PostgresDriver()
    try:
        driver.connect()
        yield driver
    finally:
        driver.close()