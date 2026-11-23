# OpenWeather — `weather_app.py`

Геокодинг, текущая погода, кэш `weather_cache.json`, ретраи при 429.

## Настройка

1. Получите ключ: [OpenWeather](https://openweathermap.org/api).
2. Скопируйте шаблон и вставьте ключ:

```powershell
cd assignments/13-weather-app
copy .env.example .env
# в .env: API_KEY=ваш_ключ
```

Файл **`.env` в git не попадает** (см. `.gitignore`).

## Зависимости

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
python weather_app.py
```

## Режимы

| Пункт | Действие |
|-------|----------|
| 1 | Город → геокодинг (`limit=1`, `lang=ru`) → погода (`metric`, `ru`) |
| 2 | Координаты lat/lon |
| 0 | Выход |

Пример строки: `Погода в Москва: 12.4°C, пасмурно`.

## Кэш и ретраи

- Последний успешный ответ → `weather_cache.json` (city, lat, lon, `fetched_at`).
- При сетевой ошибке — предложение показать кэш, если ему **< 3 часов**.
- HTTP **429** и сбои сети — до **3** повторов с паузами **1 с, 2 с, 4 с**.

## Сдача

Папка: `assignments/13-weather-app` в репозитории `learning-assignments`.