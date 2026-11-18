#!/usr/bin/env python3
"""Загрузка imdb_top_250.csv в SQLite (таблица imdb_movies)."""

from __future__ import annotations

import csv
import logging
from pathlib import Path

import database

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "base.db"
CSV_DEFAULT = Path(r"C:\Users\a.devishin\Downloads\imdb_top_250.csv")

CREATE_SQL = """
CREATE TABLE IF NOT EXISTS imdb_movies (
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    year INTEGER,
    genre TEXT,
    duration TEXT,
    origin TEXT,
    director TEXT,
    imdb_rating REAL,
    rating_count INTEGER,
    imdb_link TEXT
);
"""

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def _parse_int(value: str) -> int | None:
    value = (value or "").strip().replace(",", "")
    if not value:
        return None
    try:
        return int(value)
    except ValueError:
        return None


def _parse_float(value: str) -> float | None:
    value = (value or "").strip()
    if not value:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def load_csv(csv_path: Path = CSV_DEFAULT, db_path: Path = DB_PATH) -> int:
    """Создать таблицу и загрузить CSV; возвращает число вставленных строк."""
    if not csv_path.is_file():
        raise FileNotFoundError(f"CSV не найден: {csv_path}")

    rows: list[dict] = []
    with csv_path.open(encoding="utf-8-sig", newline="") as fh:
        reader = csv.DictReader(fh)
        for raw in reader:
            rank = raw.get("") or raw.get("Rank") or raw.get("#")
            if rank is None:
                first_key = next(iter(raw.keys()))
                rank = raw.get(first_key)
            rows.append(
                {
                    "id": _parse_int(str(rank)),
                    "title": (raw.get("Title") or "").strip(),
                    "year": _parse_int(raw.get("Year", "")),
                    "genre": (raw.get("Genre") or "").strip(),
                    "duration": (raw.get("Duration") or "").strip(),
                    "origin": (raw.get("Origin") or "").strip(),
                    "director": (raw.get("Director") or "").strip(),
                    "imdb_rating": _parse_float(raw.get("IMDB rating", "")),
                    "rating_count": _parse_int(raw.get("Rating count", "")),
                    "imdb_link": (raw.get("IMDB link") or "").strip(),
                }
            )

    with database.DatabaseManager(db_path) as db:
        db.execute_script(CREATE_SQL)
        db.execute("DELETE FROM imdb_movies", commit=True)
        db.insert_many("imdb_movies", rows)

    logging.info("Загружено %s фильмов в %s", len(rows), db_path)
    return len(rows)


if __name__ == "__main__":
    load_csv()