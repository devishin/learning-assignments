"""OpenWeather API: текущая погода, прогноз, геокодинг, качество воздуха."""

from __future__ import annotations

import os
from collections import defaultdict
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv

_ENV_PATH = Path(__file__).resolve().parent / ".env"
load_dotenv(_ENV_PATH)

GEO_URL = "https://api.openweathermap.org/geo/1.0/direct"
CURRENT_URL = "https://api.openweathermap.org/data/2.5/weather"
FORECAST_URL = "https://api.openweathermap.org/data/2.5/forecast"
AIR_URL = "https://api.openweathermap.org/data/2.5/air_pollution"

AQI_LABELS = {
    1: "хорошее",
    2: "удовлетворительное",
    3: "среднее",
    4: "плохое",
    5: "очень плохое",
}


class WeatherApiError(Exception):
    """Ошибка API без лишних деталей для пользователя."""


def _api_key() -> str:
    key = (os.getenv("OPENWEATHER_API_KEY") or os.getenv("API_KEY") or "").strip()
    if not key:
        raise WeatherApiError("Не задан OPENWEATHER_API_KEY (или API_KEY) в .env")
    return key


def _get(url: str, params: dict[str, Any]) -> Any:
    params = {**params, "appid": _api_key()}
    try:
        response = requests.get(url, params=params, timeout=30)
    except requests.RequestException as exc:
        raise WeatherApiError(f"Сеть недоступна: {exc}") from exc
    if response.status_code == 401:
        raise WeatherApiError("Неверный ключ OpenWeather (401).")
    if response.status_code != 200:
        raise WeatherApiError(f"HTTP {response.status_code}")
    try:
        return response.json()
    except ValueError as exc:
        raise WeatherApiError("Ответ не JSON") from exc


def geocode(city: str, *, limit: int = 1) -> dict[str, Any]:
    name = city.strip()
    if not name:
        raise WeatherApiError("Пустое название города")
    data = _get(GEO_URL, {"q": name, "limit": limit, "lang": "ru"})
    if not isinstance(data, list) or not data:
        raise WeatherApiError(f"Город «{name}» не найден")
    return data[0]


def current_weather(
    *,
    city: str | None = None,
    lat: float | None = None,
    lon: float | None = None,
) -> dict:
    if city:
        geo = geocode(city)
        lat, lon = float(geo["lat"]), float(geo["lon"])
    if lat is None or lon is None:
        raise WeatherApiError("Нужен город или координаты")
    data = _get(
        CURRENT_URL,
        {"lat": lat, "lon": lon, "units": "metric", "lang": "ru"},
    )
    if not isinstance(data, dict) or "main" not in data:
        raise WeatherApiError("Пустой ответ погоды")
    return data


def forecast_5d(
    *,
    city: str | None = None,
    lat: float | None = None,
    lon: float | None = None,
) -> dict:
    if city:
        geo = geocode(city)
        lat, lon = float(geo["lat"]), float(geo["lon"])
    if lat is None or lon is None:
        raise WeatherApiError("Нужен город или координаты")
    data = _get(
        FORECAST_URL,
        {"lat": lat, "lon": lon, "units": "metric", "lang": "ru"},
    )
    if not isinstance(data, dict) or "list" not in data:
        raise WeatherApiError("Пустой прогноз")
    return data


def air_quality(*, lat: float, lon: float) -> dict:
    data = _get(AIR_URL, {"lat": lat, "lon": lon})
    if not isinstance(data, dict) or "list" not in data:
        raise WeatherApiError("Нет данных о воздухе")
    return data


def _wind_ms(data: dict) -> float:
    return float(data.get("wind", {}).get("speed", 0))


def format_current_now(data: dict) -> str:
    """Погода сейчас: температура, влажность, ветер."""
    name = data.get("name") or "—"
    main = data["main"]
    temp = main["temp"]
    humidity = main.get("humidity", "—")
    wind = _wind_ms(data)
    desc = data["weather"][0]["description"]
    return (
        f"🌤 Погода сейчас — {name}\n"
        f"Температура: {temp}°C\n"
        f"Влажность: {humidity}%\n"
        f"Ветер: {wind} м/с\n"
        f"{desc}"
    )


def format_forecast_hourly(data: dict, *, max_days: int = 5) -> str:
    """Прогноз: по часам, сгруппировано по дням (до 5 суток)."""
    city = data.get("city", {}).get("name", "—")
    by_day: dict[str, list[str]] = defaultdict(list)
    for item in data.get("list", []):
        day = item["dt_txt"][:10]
        if day not in by_day and len(by_day) >= max_days:
            continue
        if len(by_day) >= max_days and day not in by_day:
            continue
        hour = item["dt_txt"][11:16]
        temp = item["main"]["temp"]
        desc = item["weather"][0]["description"]
        by_day[day].append(f"    {hour} — {temp}°C, {desc}")
    lines = [f"📅 Прогноз (по часам, до {max_days} дн.) — {city}:"]
    for day in sorted(by_day.keys())[:max_days]:
        lines.append(f"  {day}:")
        lines.extend(by_day[day][:8])
    return "\n".join(lines)


def format_extended(data: dict, air: dict) -> str:
    """Расширенный режим: текущая погода + качество воздуха."""
    base = format_current_now(data)
    block = air["list"][0]
    aqi = block["main"]["aqi"]
    label = AQI_LABELS.get(aqi, str(aqi))
    comp = block.get("components") or {}
    parts = []
    for key in ("pm2_5", "pm10", "no2", "o3"):
        if key in comp:
            parts.append(f"{key}={comp[key]}")
    extra = ", ".join(parts) if parts else "—"
    return (
        f"{base}\n\n"
        f"🌫 Расширенный режим (воздух)\n"
        f"AQI: {aqi} ({label})\n"
        f"Загрязнители (μg/m³): {extra}"
    )


def compare_cities(city_a: str, city_b: str) -> str:
    wa = current_weather(city=city_a)
    wb = current_weather(city=city_b)
    na = wa.get("name") or city_a
    nb = wb.get("name") or city_b
    ta, tb = float(wa["main"]["temp"]), float(wb["main"]["temp"])
    ha, hb = int(wa["main"].get("humidity", 0)), int(wb["main"].get("humidity", 0))
    wa_wind, wb_wind = _wind_ms(wa), _wind_ms(wb)
    lines = [
        "⚖ Сравнение городов",
        f"\n{na}:",
        f"  t={ta}°C, влажность {ha}%, ветер {wa_wind} м/с",
        f"\n{nb}:",
        f"  t={tb}°C, влажность {hb}%, ветер {wb_wind} м/с",
        "\nРазница:",
        f"  Δt = {ta - tb:+.1f}°C",
        f"  Δвлажность = {ha - hb:+d}%",
        f"  Δветер = {wa_wind - wb_wind:+.1f} м/с",
    ]
    return "\n".join(lines)


def coords_from_weather(data: dict) -> tuple[float, float]:
    c = data.get("coord") or {}
    return float(c["lat"]), float(c["lon"])