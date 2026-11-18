# IMDB Top 250 — модуль SQLite (`database.py`)

Учебный проект: класс `DatabaseManager`, загрузка CSV, поиск по жанру, CLI.

## Файлы

| Файл | Назначение |
|------|------------|
| `database.py` | Подключение, CRUD, только `?`-параметры |
| `load_imdb_csv.py` | Импорт `imdb_top_250.csv` → `data/base.db` |
| `example.py` | Демо CRUD на таблице `users` |
| `main.py` | Меню управления фильмами |

## Запуск

```powershell
cd assignments/09-imdb-database
python load_imdb_csv.py
python example.py
python main.py
```

CSV по умолчанию: `C:\Users\a.devishin\Downloads\imdb_top_250.csv`  
(путь можно передать в `load_csv(Path(...))`).

База: `data/base.db`, таблица `imdb_movies`.

## Безопасность SQL

Не использовать f-строки в SQL. Пример из `search_movies_by_genre`:

```python
db.select_records(
    "imdb_movies",
    where_clause="genre LIKE ?",
    params=(f"%{genre}%",),
)
```

Значение жанра — только в `params`, не в тексте запроса.