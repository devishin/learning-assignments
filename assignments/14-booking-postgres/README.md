# Мини-система бронирования (PostgreSQL)

Драйвер `postgres_driver.py`, модели в `models/`, CRUD в `backend.py`, GUI в `app.py`.

## PostgreSQL и пользователь admin

1. Создайте БД **`booking`** в pgAdmin (или psql).
2. Создайте пользователя **`admin`** с паролем и правами на эту БД (или используйте `postgres` — тогда поменяйте `DB_USER` в `.env`).

Пример в psql под суперпользователем:

```sql
CREATE USER admin WITH PASSWORD 'your_password';
CREATE DATABASE booking OWNER admin;
```

## Проект

```powershell
cd assignments/14-booking-postgres
copy .env.example .env
# DB_HOST, DB_PORT, DB_NAME=booking, DB_USER=admin, DB_PASSWORD=...

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