"""Погода OpenWeather: геокодинг, current weather, CLI, кэш, ретраи."""

from __future__ import annotations

import json
import os
import sys
import time
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv

GEO_URL = "http://api.openweathermap.org/geo/1.0/direct"
WEATHER_URL = "https://api.openweathermap.org/data/2.5/weather"
CACHE_PATH = "weather_cache.json"
CACHE_TTL_SECONDS = 3 * 60 * 60
RETRY_DELAYS = (1, 2, 4)

load_dotenv()
API_KEY = os.getenv("API_KEY")


class WeatherError(Exception):
    """Ошибка без вывода стектрейса пользователю."""


def _require_api_key() -> str:
    key = (API_KEY or "").strip()
    if not key:
        raise WeatherError(
            "API_KEY не задан. Укажите ключ OpenWeather в файле .env "
            "(скопируйте из .env.example)."
        )
    return key


def _http_status_message(status: int) -> str:
    if status == 401:
        return "Неверный API-ключ (401). Проверьте API_KEY в .env."
    if status == 404:
        return "Данные не найдены (404)."
    if status == 429:
        return "Слишком много запросов (429)."
    return f"Ошибка API: HTTP {status}."


def _request_json(
    url: str,
    params: dict[str, Any],
    *,
    retry_on: frozenset[int] = frozenset({429}),
) -> Any:
    last_error: Exception | None = None
    for attempt, delay in enumerate((*RETRY_DELAYS, None)):
        try:
            response = requests.get(url, params=params, timeout=30)
        except requests.RequestException as exc:
            last_error = exc
            if delay is not None:
                time.sleep(delay)
                continue
            raise WeatherError(
                f"Сеть недоступна или запрос не выполнен: {exc}"
            ) from exc
        if response.status_code in retry_on and delay is not None:
            time.sleep(delay)
            continue
        if response.status_code != 200:
            raise WeatherError(_http_status_message(response.status_code))
        try:
            return response.json()
        except ValueError as exc:
            raise WeatherError("Ответ сервера не похож на JSON.") from exc
    if last_error:
        raise WeatherError(f"Сеть недоступна: {last_error}")
    raise WeatherError("Не удалось выполнить запрос после повторов.")


def get_coordinates(city: str) -> tuple[float, float]:
    """Геокодинг OpenWeather: limit=1, lang=ru."""
    key = _require_api_key()
    name = city.strip()
    if not name:
        raise WeatherError("Название города пустое.")
    data = _request_json(
        GEO_URL,
        {"q": name, "limit": 1, "appid": key, "lang": "ru"},
    )
    if not isinstance(data, list) or not data:
        raise WeatherError(
            f"Город «{name}» не найден. Проверьте написание (латиница/кириллица)."
        )
    item = data[0]
    try:
        lat = float(item["lat"])
        lon = float(item["lon"])
    except (KeyError, TypeError, ValueError) as exc:
        raise WeatherError("Геокодинг вернул неполный ответ.") from exc
    return lat, lon


def get_weather_by_coordinates(lat: float, lon: float) -> dict:
    """Текущая погода: units=metric, lang=ru."""
    key = _require_api_key()
    data = _request_json(
        WEATHER_URL,
        {
            "lat": lat,
            "lon": lon,
            "appid": key,
            "units": "metric",
            "lang": "ru",
        },
    )
    if not isinstance(data, dict) or "main" not in data:
        raise WeatherError("Ответ погоды неполный или пустой.")
    return data


def format_weather_line(city_label: str, weather: dict) -> str:
    try:
        temp = weather["main"]["temp"]
        desc = weather["weather"][0]["description"]
    except (KeyError, IndexError, TypeError) as exc:
        raise WeatherError("В ответе нет температуры или описания.") from exc
    return f"Погода в {city_label}: {temp}°C, {desc}"


def save_cache(
    *,
    city: str | None,
    lat: float,
    lon: float,
    weather: dict,
    path: str = CACHE_PATH,
) -> None:
    payload = {
        "city": city,
        "lat": lat,
        "lon": lon,
        "fetched_at": int(time.time()),
        "weather": weather,
    }
    with Path(path).open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=2)


def load_cache(path: str = CACHE_PATH) -> dict | None:
    file_path = Path(path)
    if not file_path.is_file():
        return None
    try:
        with file_path.open(encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, json.JSONDecodeError):
        return None
    return data if isinstance(data, dict) else None


def cache_is_fresh(data: dict) -> bool:
    fetched = data.get("fetched_at")
    if not isinstance(fetched, (int, float)):
        return False
    return (time.time() - float(fetched)) < CACHE_TTL_SECONDS


def offer_cache_fallback() -> None:
    cached = load_cache()
    if not cached or not cache_is_fresh(cached):
        if cached:
            print("Кэш устарел (> 3 ч).", file=sys.stderr)
        return
    answer = input(
        "Сетевой сбой. Показать данные из кэша (< 3 ч)? [y/N]: "
    ).strip().lower()
    if answer not in ("y", "yes", "д", "да"):
        return
    label = cached.get("city") or (
        f"{cached.get('lat')}, {cached.get('lon')}"
    )
    weather = cached.get("weather") or {}
    try:
        print(format_weather_line(str(label), weather))
        print("(данные из weather_cache.json)")
    except WeatherError as exc:
        print(exc, file=sys.stderr)


def run_by_city() -> None:
    city = input("Введите город: ").strip()
    if not city:
        print("Город не введён.", file=sys.stderr)
        return
    try:
        lat, lon = get_coordinates(city)
        weather = get_weather_by_coordinates(lat, lon)
        label = weather.get("name") or city
        print(format_weather_line(label, weather))
        save_cache(city=city, lat=lat, lon=lon, weather=weather)
    except WeatherError as exc:
        print(exc, file=sys.stderr)
        offer_cache_fallback()


def run_by_coordinates() -> None:
    try:
        lat = float(input("Широта (lat): ").strip().replace(",", "."))
        lon = float(input("Долгота (lon): ").strip().replace(",", "."))
    except ValueError:
        print("Координаты должны быть числами.", file=sys.stderr)
        return
    try:
        weather = get_weather_by_coordinates(lat, lon)
        label = weather.get("name") or f"{lat}, {lon}"
        print(format_weather_line(label, weather))
        save_cache(city=None, lat=lat, lon=lon, weather=weather)
    except WeatherError as exc:
        print(exc, file=sys.stderr)
        offer_cache_fallback()


def print_menu() -> None:
    print()
    print("=== OpenWeather ===")
    print("1 — погода по городу")
    print("2 — погода по координатам")
    print("0 — выход")


def main() -> None:
    while True:
        print_menu()
        choice = input("Выберите режим: ").strip()
        if choice == "1":
            run_by_city()
        elif choice == "2":
            run_by_coordinates()
        elif choice == "0":
            print("Выход.")
            break
        else:
            print("Неизвестный пункт. Введите 0, 1 или 2.")


if __name__ == "__main__":
    main()