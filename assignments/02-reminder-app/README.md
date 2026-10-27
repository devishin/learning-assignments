# Напоминалка (Windows 11)

Приложение на Python + Tkinter с хранением напоминаний в SQLite3 и фоновыми уведомлениями.

## Установка

```powershell
cd D:\learning-assignments\assignments\02-reminder-app
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Запуск

```powershell
python main.py
```

## Структура

- `database.py` — класс `ReminderDatabase`
- `notifications.py` — класс `NotificationManager`
- `gui.py` — интерфейс Tkinter
- `main.py` — точка входа

## Возможности

- добавление, удаление, фильтр по статусу;
- статусы: Ожидает / Готово / Просрочено / Отменено;
- автоматический перевод просроченных одноразовых напоминаний;
- одноразовые и повторяющиеся напоминания (интервал в минутах);
- toast-уведомления Windows и резервное popup-окно Tkinter.

Скриншот сработавшего напоминания:

```powershell
python capture_fired_reminder.py
```

Файл: `screenshots/reminder_fired.png`
