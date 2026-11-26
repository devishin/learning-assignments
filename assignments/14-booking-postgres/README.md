# Мини-система бронирования (PostgreSQL)

Драйвер `postgres_driver.py`, модели в `models/`, CRUD в `backend.py`, GUI в `app.py`.

## База PostgreSQL (Docker)

```powershell
cd assignments/14-booking-postgres
copy .env.example .env
docker compose up -d
```

По умолчанию: **Postgres** на `localhost:5433`, БД `booking`, пользователь `admin`.  
Пароль в `.env` (см. `.env.example`; для Docker совпадает с `docker-compose.yml`).

Опционально: **pgAdmin** в браузере — http://127.0.0.1:5051 (`admin@local.dev` / `pgadmin`).

Локальный **pgAdmin 4** (установщик): подключение `localhost:5433`, см. `scripts/pgpass` / `pgpass.conf`.

## Проект Python

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### Таблицы и демо-данные (базовый зачёт)

```powershell
python main.py seed
python main.py bookings
```

### GUI (средний уровень)

```powershell
python app.py
```

Вкладки: пользователи, столы, бронирования — полный CRUD, как в `backend.py`.

## Файлы

| Файл | Назначение |
|------|------------|
| `postgres_driver.py` | Подключение, `execute`, контекст `get_driver()` |
| `usage.py` | Пример `SELECT version()` |
| `backend.py` | `create_table_if_not_exists`, CRUD, `get_all_bookings` |
| `models/user.py`, `tables.py`, `booking.py` | Поля таблиц **строками SQL** |
| `app.py` | Tkinter |
| `main.py` | `seed`, список бронирований в CLI |
| `.env.example` | Шаблон без секретов |

## Скриншоты

См. `screenshots/README.md` — три **реальных** снимка в pgAdmin и приложении.

## Безопасность (учебный кейс)

Пароль пользователя в БД хранится **в открытом виде** только для упрощения; в проде нужен хэш.

## Сдача

Репозиторий `learning-assignments`, папка `assignments/14-booking-postgres`.