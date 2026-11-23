# Курсы валют (open.er-api.com)

Чтение [open.er-api.com](https://open.er-api.com), кэш `currency_rate.json`, мини-CLI и конвертер.

## Структура

| Модуль | Назначение |
|--------|------------|
| `currency.py` | Точка входа `python currency.py`, реэкспорт API |
| `api_client.py` | `get_currency_rates(base)` → GET + проверка `status_code` и `result` |
| `storage.py` | `save_to_file`, `read_from_file`, TTL 24 часа |
| `cli.py` | Ввод базы, RUB/EUR/GBP, конвертация, валидация кодов |
| `DOCS.md` | 5 полей ответа `latest` |

## Запуск

```powershell
cd assignments/12-currency-rates
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python currency.py
```

Повторный запуск в течение 24 ч с той же базой читает **`currency_rate.json`** (в `.gitignore`).

## Конвертация

При запросе суммы конвертер использует кросс-курс через `base_code` ответа (одинаково для кэша и свежего API).

Примеры для проверки при базе **USD**: USD→RUB, EUR→GBP (коды из `rates`).

## Ошибки

Невалидная валюта и сбой сети — сообщения в stderr, без стектрейса (`CurrencyApiError`).

## Сдача

Папка в репозитории `learning-assignments`: `assignments/12-currency-rates`.