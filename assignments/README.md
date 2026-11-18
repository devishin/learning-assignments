# Учебные проекты

- `02-reminder-app` — напоминалка (Tkinter + SQLite + уведомления)
- `03-password-manager` — CLI менеджер паролей (SQLite + Fernet)
- `04-invoice-pdf` — генерация PDF-счетов из CSV/JSON и HTML (WeasyPrint)
- `06-telegram-tasks-bot` — Telegram-бот задач (aiogram + SQLite)
- `07-sports-club` — SQLite: спортивный клуб (схема, seed, checks, ER)
- `08-sql-products-orders` — SQLite: products/orders, DML, JOIN, seed, SQL injection demo
- `09-imdb-database` — Python `DatabaseManager`, IMDB CSV, поиск по жанру, CLI

## Клонирование

```powershell
git clone https://github.com/devishin/learning-assignments.git
cd learning-assignments
```

Дальше в примерах пути **относительно корня репозитория** (после `cd learning-assignments`).

## Быстрый запуск демо

```powershell
cd assignments
python run_homework_demo.py
```

Скрипт:
- установит зависимости;
- добавит 2 напоминания (одноразовое + повторяющееся);
- добавит 2 пароля (`Gmail`, `Telegram`);
- сохранит скриншоты в `screenshots/`.

## Запуск вручную

```powershell
cd assignments/02-reminder-app
python main.py
```

```powershell
cd assignments/03-password-manager
python password_manager.py menu
```

Демо-мастер-пароль (после `seed_demo.py`): **`StudyDemo123!`** — см. `03-password-manager/DEMO.md`

```powershell
cd assignments/06-telegram-tasks-bot
copy .env.example .env
# вставьте BOT_TOKEN от @BotFather
pip install -r requirements.txt
python bot.py
```
