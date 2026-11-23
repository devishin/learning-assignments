# PostgreSQL из Python — чтение `users`

Цель: «живое» подключение к PostgreSQL через **psycopg2** и вывод строк из таблицы.

## Подготовка в pgAdmin

1. Создайте базу **`test`** (схема **`public`** по умолчанию).
2. Откройте **Query Tool** и выполните `schema.sql` (или SQL из задания).
3. **Просмотр/редактирование данных** → таблица `users` → вручную добавьте **не менее 3** строк (`name`, `age`; `id` подставится сам).

## Переменные окружения

```powershell
cd assignments/10-postgresql-users
copy .env.example .env
```

Заполните в `.env` реальный пароль пользователя `postgres` (или своего пользователя БД). Файл **`.env` в git не коммитится** — в репозитории только `.env.example`.

## Виртуальное окружение

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

Ожидаемый вывод — кортежи `(id, name, age)` для всех пользователей, например:

```
(1, 'Анна', 28)
(2, 'Борис', 35)
(3, 'Вика', 22)
```

## Файлы для сдачи

| Файл | Назначение |
|------|------------|
| `main.py` | Подключение, `SELECT`, `try/except/finally`, закрытие соединения |
| `requirements.txt` | `psycopg2-binary`, `python-dotenv` |
| `.env.example` | Шаблон без секретов |
| `README.md` | Команды запуска |

Ссылка на репозиторий:  
https://github.com/devishin/learning-assignments/tree/main/assignments/10-postgresql-users

## Критерии зачёта

- `python main.py` без правок кода после настройки `.env` и данных в БД;
- в консоли видны добавленные пользователи;
- при ошибке подключения — сообщение в stderr, соединение закрывается в `finally` без утечки.