# Финансовый помощник (Telegram)

Учебный бот: бюджет поездки, курсы **[exchangerate.host](https://exchangerate.host)**, SQLite.

## Файлы по уроку

| Файл | Назначение |
|------|------------|
| **`current_api.py`** | `get_current_rate()` → `/live`, `convert_currency()` → `/convert`, ключ из `.env` |
| `requirements.txt` | `requests`, `python-dotenv`, `aiogram` |
| `bot.py` | Telegram, `/start`, `/newtrip` |
| `database.py` | путешествия и расходы |

## API (current_api.py)

- **Курсы:** `GET https://api.exchangerate.host/live` — `source`, `currencies`, `access_key`
- **Конвертация:** `GET https://api.exchangerate.host/convert` — `from`, `to`, `amount`, `access_key`
- Ключ в `.env`: **`CURRENCY_API_KEY`** (не в коде)

Проверка модуля:

```powershell
python current_api.py
```

## Сценарий бота

1. `/newtrip` → страна выезда → назначения → сумма в валюте выезда  
2. Курс и бюджет в двух валютах, расходы в чате или `/spend`  
3. `/balance`, `/history`, `/rate`, `/resetrate`

## Установка

```powershell
cd assignments/16-telegram-travel-finance
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
copy .env.example .env
```

В `.env`: `BOT_TOKEN` (BotFather), `CURRENCY_API_KEY` (exchangerate.host).

```powershell
python console_test.py
python check_telegram.py
python bot.py
```

## Сдача

[learning-assignments / 16-telegram-travel-finance](https://github.com/devishin/learning-assignments/tree/main/assignments/16-telegram-travel-finance)