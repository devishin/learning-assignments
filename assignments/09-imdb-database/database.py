"""Модуль для работы с SQLite3 через класс DatabaseManager."""

from __future__ import annotations

import logging
import sqlite3
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Менеджер подключения и CRUD-операций SQLite.

    Использование::

        with DatabaseManager("base.db") as db:
            rows = db.select_records("imdb_movies", limit=5)
    """

    def __init__(self, db_path: str | Path) -> None:
        """Сохранить путь к файлу базы данных.

        :param db_path: путь к файлу .db (создаётся при первом подключении).
        """
        self.db_path = Path(db_path)
        self._conn: sqlite3.Connection | None = None

    def __enter__(self) -> DatabaseManager:
        """Контекстный менеджер: подключение при входе."""
        self.connect()
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        """Контекстный менеджер: отключение при выходе."""
        self.close()

    def connect(self) -> sqlite3.Connection:
        """Открыть соединение с базой (создаёт каталог при необходимости).

        :return: объект соединения sqlite3.
        """
        if self._conn is not None:
            return self._conn
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(self.db_path)
        self._conn.row_factory = sqlite3.Row
        self._conn.execute("PRAGMA foreign_keys = ON")
        logger.info("Подключение к БД: %s", self.db_path)
        return self._conn

    def close(self) -> None:
        """Закрыть соединение, если оно открыто."""
        if self._conn is not None:
            self._conn.close()
            self._conn = None
            logger.info("Соединение закрыто: %s", self.db_path)

    @property
    def connection(self) -> sqlite3.Connection:
        """Текущее соединение; вызывает :meth:`connect`, если ещё не открыто."""
        return self.connect()

    def execute(
        self,
        sql: str,
        params: Sequence[Any] | None = None,
        *,
        commit: bool = False,
    ) -> sqlite3.Cursor:
        """Выполнить произвольный SQL с параметрами ``?``.

        :param sql: текст запроса с плейсхолдерами ``?``.
        :param params: кортеж/список значений (никогда f-строка в SQL).
        :param commit: зафиксировать транзакцию после выполнения.
        """
        cur = self.connection.execute(sql, params or ())
        if commit:
            self.connection.commit()
        return cur

    def executemany(
        self,
        sql: str,
        seq_of_params: Iterable[Sequence[Any]],
        *,
        commit: bool = True,
    ) -> sqlite3.Cursor:
        """Пакетное выполнение (INSERT/UPDATE и т.п.)."""
        cur = self.connection.executemany(sql, seq_of_params)
        if commit:
            self.connection.commit()
        return cur

    def execute_script(self, script: str) -> None:
        """Выполнить многострочный SQL-скрипт."""
        self.connection.executescript(script)
        self.connection.commit()

    def table_exists(self, table_name: str) -> bool:
        """Проверить, существует ли таблица."""
        row = self.execute(
            "SELECT name FROM sqlite_master WHERE type = 'table' AND name = ?",
            (table_name,),
        ).fetchone()
        return row is not None

    def insert_record(self, table_name: str, data: Mapping[str, Any]) -> int:
        """Вставить одну строку; ключи ``data`` — имена колонок.

        :return: id последней вставленной строки (lastrowid).
        """
        columns = list(data.keys())
        placeholders = ", ".join("?" * len(columns))
        cols_sql = ", ".join(columns)
        sql = f"INSERT INTO {table_name} ({cols_sql}) VALUES ({placeholders})"
        values = tuple(data[c] for c in columns)
        cur = self.execute(sql, values, commit=True)
        logger.debug("INSERT в %s: %s", table_name, data)
        return int(cur.lastrowid)

    def insert_many(self, table_name: str, rows: Sequence[Mapping[str, Any]]) -> int:
        """Вставить несколько строк с одинаковым набором колонок."""
        if not rows:
            return 0
        columns = list(rows[0].keys())
        placeholders = ", ".join("?" * len(columns))
        cols_sql = ", ".join(columns)
        sql = f"INSERT INTO {table_name} ({cols_sql}) VALUES ({placeholders})"
        values = [tuple(r[c] for c in columns) for r in rows]
        cur = self.executemany(sql, values, commit=True)
        logger.info("Пакетная вставка в %s: %s строк", table_name, cur.rowcount)
        return cur.rowcount

    def select_records(
        self,
        table_name: str,
        columns: Sequence[str] | None = None,
        where_clause: str | None = None,
        params: Sequence[Any] | None = None,
        order_by: str | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """Выбрать строки; условие только с ``?`` в ``where_clause``.

        Пример: ``where_clause="genre LIKE ?"``, ``params=("%Thriller%",)``.
        """
        cols = ", ".join(columns) if columns else "*"
        sql = f"SELECT {cols} FROM {table_name}"
        if where_clause:
            sql += f" WHERE {where_clause}"
        if order_by:
            sql += f" ORDER BY {order_by}"
        if limit is not None:
            sql += " LIMIT ?"
            params = tuple(params or ()) + (limit,)
        cur = self.execute(sql, params)
        return [dict(row) for row in cur.fetchall()]

    def select_one(
        self,
        table_name: str,
        where_clause: str,
        params: Sequence[Any],
        columns: Sequence[str] | None = None,
    ) -> dict[str, Any] | None:
        """Выбрать одну строку или ``None``."""
        rows = self.select_records(
            table_name,
            columns=columns,
            where_clause=where_clause,
            params=params,
            limit=1,
        )
        return rows[0] if rows else None

    def update_records(
        self,
        table_name: str,
        data: Mapping[str, Any],
        where_clause: str,
        params: Sequence[Any],
    ) -> int:
        """Обновить строки. Обязательно указывать ``where_clause`` с ``?``.

        :return: число изменённых строк.
        """
        sets = ", ".join(f"{k} = ?" for k in data.keys())
        sql = f"UPDATE {table_name} SET {sets} WHERE {where_clause}"
        all_params = tuple(data.values()) + tuple(params)
        cur = self.execute(sql, all_params, commit=True)
        logger.info("UPDATE %s: затронуто %s строк", table_name, cur.rowcount)
        return cur.rowcount

    def delete_records(self, table_name: str, where_clause: str, params: Sequence[Any]) -> int:
        """Удалить строки. Только с ``WHERE`` и параметрами.

        :return: число удалённых строк.
        """
        sql = f"DELETE FROM {table_name} WHERE {where_clause}"
        cur = self.execute(sql, params, commit=True)
        logger.info("DELETE из %s: удалено %s строк", table_name, cur.rowcount)
        return cur.rowcount

    def count_records(
        self,
        table_name: str,
        where_clause: str | None = None,
        params: Sequence[Any] | None = None,
    ) -> int:
        """Подсчитать строки в таблице (опционально с фильтром)."""
        sql = f"SELECT COUNT(*) AS cnt FROM {table_name}"
        if where_clause:
            sql += f" WHERE {where_clause}"
        row = self.execute(sql, params).fetchone()
        return int(row["cnt"]) if row else 0