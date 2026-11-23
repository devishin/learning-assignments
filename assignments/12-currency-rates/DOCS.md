# open.er-api.com — поля ответа `GET /v6/latest/{base}`

Документация: [open.er-api.com](https://open.er-api.com) (ExchangeRate-API, без ключа для open endpoint).

## 5 ключевых полей (как в задании)

| Поле | Пример / смысл |
|------|----------------|
| `base_code` | `"USD"` — базовая валюта запроса |
| `time_last_update_utc` | `"Mon, 23 Nov 2025 00:00:01 +0000"` — время последнего обновления |
| `time_next_update_utc` | когда ожидается следующее обновление (free tier — раз в сутки) |
| `rates.RUB` | сколько RUB за **1** единицу `base_code` (в v6 объект называется **`rates`**, не `conversion_rates`) |
| `rates.USD` | курс USD относительно базы (для базы USD обычно `1`) |

Дополнительно полезны: `result` (`success` / `error`), `time_last_update_unix`, `rates` (полная таблица ~160 валют).

## Пример запроса

```
GET https://open.er-api.com/v6/latest/USD
```

При неверном коде: HTTP 200, `result: "error"`, `error-type: "unsupported-code"`.