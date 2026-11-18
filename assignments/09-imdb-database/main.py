#!/usr/bin/env python3
"""CLI для базы IMDB Top 250 (модуль database)."""

from __future__ import annotations

import logging
from pathlib import Path
from pprint import pprint

import database

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "data" / "base.db"
TABLE = "imdb_movies"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


def search_movies_by_genre(genre: str) -> list[dict]:
    """Поиск фильмов по жанру (LIKE, безопасные параметры)."""
    with database.DatabaseManager(DB_PATH) as db:
        return db.select_records(
            TABLE,
            where_clause="genre LIKE ?",
            params=(f"%{genre}%",),
            order_by="imdb_rating DESC",
        )


def insert_movie(movie: dict) -> int:
    """Добавить фильм (словарь колонок)."""
    with database.DatabaseManager(DB_PATH) as db:
        if "id" not in movie:
            row = db.execute(
                "SELECT COALESCE(MAX(id), 0) + 1 AS next_id FROM imdb_movies",
            ).fetchone()
            movie = {**movie, "id": row["next_id"]}
        return db.insert_record(TABLE, movie)


def delete_movies_older_than(year: int) -> int:
    """Удалить фильмы с годом выпуска строго меньше ``year``."""
    with database.DatabaseManager(DB_PATH) as db:
        return db.delete_records(TABLE, "year < ?", (year,))


def count_movies() -> int:
    """Общее число фильмов в базе."""
    with database.DatabaseManager(DB_PATH) as db:
        return db.count_records(TABLE)


def top_movies_by_rating(limit: int = 5) -> list[dict]:
    """Топ фильмов по рейтингу IMDB."""
    with database.DatabaseManager(DB_PATH) as db:
        return db.select_records(
            TABLE,
            columns=("title", "year", "imdb_rating", "genre"),
            order_by="imdb_rating DESC",
            limit=limit,
        )


def prompt_new_movie() -> dict:
    """Ввод нового фильма через ``input()``."""
    print("Новый фильм (пустой id — авто):")
    raw_id = input("id (номер в списке, Enter — пропустить): ").strip()
    title = input("Название: ").strip()
    year = input("Год: ").strip()
    genre = input("Жанр: ").strip()
    director = input("Режиссёр: ").strip()
    rating = input("Рейтинг IMDB: ").strip()

    data = {
        "title": title,
        "year": int(year) if year.isdigit() else None,
        "genre": genre,
        "director": director,
        "imdb_rating": float(rating.replace(",", ".")) if rating else None,
        "duration": "",
        "origin": "",
        "rating_count": None,
        "imdb_link": "",
    }
    if raw_id.isdigit():
        data["id"] = int(raw_id)
    return data


def print_menu() -> None:
    print(
        """
Выберите действие:
1. Поиск фильмов по жанру
2. Удалить фильмы старше года
3. Добавить новый фильм
4. Показать количество фильмов в базе
5. Топ-5 фильмов по рейтингу
0. Выход
""".strip()
    )


def main() -> None:
    if not DB_PATH.is_file():
        logger.error(
            "База %s не найдена. Сначала выполните: python load_imdb_csv.py",
            DB_PATH,
        )
        return

    while True:
        print_menu()
        choice = input("> ").strip()

        if choice == "0":
            print("Выход.")
            break
        if choice == "1":
            genre = input("Жанр (например Thriller, Horror): ").strip()
            results = search_movies_by_genre(genre)
            logger.info("Найдено фильмов: %s", len(results))
            pprint(results)
        elif choice == "2":
            year_s = input("Удалить фильмы старше какого года? (например 2010): ").strip()
            if year_s.isdigit():
                n = delete_movies_older_than(int(year_s))
                logger.info("Удалено записей: %s", n)
            else:
                print("Некорректный год.")
        elif choice == "3":
            movie = prompt_new_movie()
            if not movie.get("title"):
                print("Название обязательно.")
                continue
            new_id = insert_movie(movie)
            logger.info("Фильм добавлен, lastrowid=%s", new_id)
        elif choice == "4":
            print("Фильмов в базе:", count_movies())
        elif choice == "5":
            pprint(top_movies_by_rating(5))
        else:
            print("Неизвестный пункт меню.")


if __name__ == "__main__":
    main()