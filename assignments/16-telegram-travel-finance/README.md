# Финансовый помощник (Telegram)

Учебный бот для планирования бюджета в поездке: курсы через **API**, путешествие и расходы в **SQLite**.

## Сценарий

1. `/newtrip` → страна выезда (Россия → RUB)  
2. Страна назначения (Италия → EUR)  
3. Курс из [open.er-api.com](https://open.er-api.com)  
4. Начальная сумма (например `200000` RUB)  
5. Бот создаёт поездку и показывает эквивалент в EUR  
6. Расходы: `/spend 50` или просто число в чате (в валюте назначения)

Дополнительно: `/balance`, `/history`, `/rate 104` (тестовый курс), `/resetrate`.

## Структура

| Файл | Назначение |
|------|------------|
| `currency_api.py` | HTTP API курсов |
| `countries.py` | Страна → валюта |
| `database.py` | SQLite: trips, expenses |
| `bot.py` | aiogram, `/start`, `/newtrip` |

## Установка

```powershell
cd assignments/16-telegram-travel-finance
copy .env.example .env
# или: copy telegram.env.example .env  — заготовка с полями BOT_TOKEN и FINANCE_DB_PATH
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

В `.env` укажите `BOT_TOKEN` от [@BotFather](https://t.me/BotFather). Секреты в репозиторий не попадают.

## Проверка

```powershell
python console_test.py
python check_telegram.py
python bot.py
```

## Сдача

Репозиторий: [learning-assignments](https://github.com/devishin/learning-assignments) → `assignments/16-telegram-travel-finance`.