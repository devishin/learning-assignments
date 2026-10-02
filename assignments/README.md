# Учебные проекты (параллельно)

- `02-reminder-app` — напоминалка (Tkinter + SQLite + уведомления)
- `03-password-manager` — CLI менеджер паролей (SQLite + Fernet)
- `04-invoice-pdf` — генерация PDF-счетов из CSV/JSON и HTML (WeasyPrint)

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
