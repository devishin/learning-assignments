# Финансовый помощник (Telegram)

Telegram-бот для бюджета в поездке: **exchangerate.host**, SQLite.

## Структура

| Файл | Назначение |
|------|------------|
| `current_api.py` | `get_current_rate()` — `/live`; `convert_currency()` — `/convert` |
| `requirements.txt` | `requests`, `python-dotenv`, `aiogram` |
| `bot.py` | `/start`, `/newtrip`, расходы и остаток |
| `database.py` | путешествия и история расходов |
| `countries.py` | страна → валюта |

Курсы и конвертация: `https://api.exchangerate.host` (`access_key`, `CURRENCY_API_KEY` в `.env`).

## Установка

```powershell
cd assignments/16-telegram-travel-finance
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

Заполните в `.env`: `BOT_TOKEN`, `CURRENCY_API_KEY`.

```powershell
python current_api.py
python console_test.py
python bot.py
```

## Команды бота

`/newtrip` — новое путешествие; `/balance`, `/history`, `/spend`, `/rate`, `/resetrate`.

## Сдача

[learning-assignments / 16-telegram-travel-finance](https://github.com/devishin/learning-assignments/tree/main/assignments/16-telegram-travel-finance)