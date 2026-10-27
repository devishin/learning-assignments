# Telegram-бот: список задач

Учебный проект: **Python**, **aiogram 3**, **SQLite3**.

## Часть 1. Бот

### 1. Токен

1. В Telegram откройте [@BotFather](https://t.me/BotFather).
2. Команда `/newbot` → имя и username бота.
3. Скопируйте токен в файл `.env` (см. `.env.example`):

```env
BOT_TOKEN=ваш_токен
TASKS_DB_PATH=tasks.db
# если Telegram не открывается напрямую (VLESS/Clash и т.п.):
TELEGRAM_PROXY=socks5h://127.0.0.1:10808
```

### 2. Установка и запуск

```powershell
cd D:\learning-assignments\assignments\06-telegram-tasks-bot
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python check_telegram.py   # getMe через TELEGRAM_PROXY (если задан)
python bot.py
```

### 3. Важно: какой бот в Telegram

Команды `/add`, `/list`, `/list_csv` есть только у **учебного** бота из этой папки (в консоли при запуске будет `@username`, например `@zerocode_test_bot`).

У **сервисного diagnostic-бота** из `tcompany-service-diagnostic-bot` есть `/start`, `/help`, но **нет** `/add` — на такие команды он молчит.

### 4. Команды

| Команда | Действие |
|---------|----------|
| `/start` | Приветствие и подсказки |
| `/add текст` | Добавить задачу |
| `/list` | Список задач (порядок по id) |
| `/list_csv` | Файл `tasks.csv` в чат |

### 5. База данных

Таблица `tasks`: `id`, `text`, `user` (Telegram user id), `created_at`.  
Для части 2 добавляются колонки `status`, `category` (см. `database.py`).

## Часть 2. Эксперименты

Выполните сами и сделайте скриншоты для сдачи:

1. **Сохранение после перезапуска**  
   Добавьте 3–4 задачи через `/add`, остановите бота (`Ctrl+C`), снова `python bot.py`.  
   Проверьте `/list` — задачи на месте (файл `tasks.db`).

2. **Порядок в /list**  
   Задачи должны идти в том же порядке, в каком вы их добавляли.

3. **CSV в Excel / LibreOffice**  
   `/list_csv` → скачайте файл → откройте. Разделитель `;`, кодировка UTF-8 с BOM.

4. **Колонки «Статус» и «Категория»**  
   В проекте они уже есть в CSV (`status`, `category`). Можно обновить строки вручную в SQLite:

```sql
UPDATE tasks SET status = 'в работе', category = 'учёба' WHERE id = 1;
```

Снова `/list_csv` и проверьте новые колонки в таблице.

## Скриншоты для сдачи

Папка `screenshots/`:

- добавление задачи (`/add`);
- список (`/list`);
- выгрузка CSV (`/list_csv` + файл в Excel по желанию).

## Структура проекта

```
06-telegram-tasks-bot/
├── .env              # токен (не коммитить)
├── .env.example
├── bot.py            # обработчики команд
├── config.py         # чтение .env
├── database.py       # SQLite
├── requirements.txt
└── README.md
```
