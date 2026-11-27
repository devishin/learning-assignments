# VK + OpenWeather (домашнее задание)

Отдельный модуль **`openweather_api.py`** и бот **`bot.py`** (vkbottle, Long Poll).

## Функции бота

| Кнопка | Поведение |
|--------|-----------|
| 🌤 **Сейчас** | Город → **t°, влажность %, ветер м/с** |
| 🏙 **Мой город** | Запоминает последний город; можно задать вручную |
| 📅 **Прогноз** | До 5 дней, **по часам** (из API forecast) |
| 📍 **Геолокация** | Метка на карте → погода сейчас |
| 🌫 **Расширенный** | Погода + **качество воздуха** (AQI, PM2.5…) |
| ⚖ **Сравнить** | `сравни: Москва \| Казань` — t, влажность, ветер, **Δ** |

«Мой город» хранится в `user_cities.json` (можно позже заменить на БД).

## Установка

```powershell
cd assignments/15-vk-weather-bot
copy .env.example .env
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

`.env`:

- `OPENWEATHER_API_KEY` — с [openweathermap.org](https://openweathermap.org/api)
- `VK_BOT_TOKEN` — ключ сообщества с **Сообщения** + Long Poll

## Тест API (консоль)

```powershell
python console_test.py
python vk_smoke_test.py
python vk_live_test.py
```

Минимум два города: **Moscow**, **Kazan** (или Москва / Казань).

`vk_live_test` — клавиатура, OpenWeather и VK messages API.

## Запуск бота

```powershell
python bot.py
```

В ЛС сообществу: **начать** → кнопки.

## Сдача

- Репозиторий `learning-assignments`, папка `15-vk-weather-bot`
- `.env` в `.gitignore`, в репо только `.env.example`
- Настройка сообщества: [VK_BOTS.md](VK_BOTS.md)

Документация vkbottle: https://vkbottle.readthedocs.io/ru/v4.x/