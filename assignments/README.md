# Учебные проекты

- `02-reminder-app` — напоминалка (Tkinter + SQLite + уведомления)
- `03-password-manager` — CLI менеджер паролей (SQLite + Fernet)
- `04-invoice-pdf` — генерация PDF-счетов из CSV/JSON и HTML (WeasyPrint)
- `06-telegram-tasks-bot` — Telegram-бот задач (aiogram + SQLite)

## Быстрый запуск демо

```powershell
cd D:\learning-assignments\assignments
python run_homework_demo.py
```

Скрипт:
- установит зависимости;
- добавит 2 напоминания (одноразовое + повторяющееся);
- добавит 2 пароля (`Gmail`, `Telegram`);
- сохранит скриншоты в `screenshots/`.

## Запуск вручную

```powershell
cd D:\learning-assignments\assignments\02-reminder-app
python main.py
```

```powershell
cd D:\learning-assignments\assignments\03-password-manager
python password_manager.py menu
```

Демо-мастер-пароль (после `seed_demo.py`): **`StudyDemo123!`** — см. `03-password-manager/DEMO.md`

```powershell
cd D:\learning-assignments\assignments\06-telegram-tasks-bot
copy .env.example .env
# вставьте BOT_TOKEN от @BotFather
pip install -r requirements.txt
python bot.py
```
