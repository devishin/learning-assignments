"""Проверка API в консоли (≥2 города)."""

from openweather_api import (
    compare_cities,
    format_current_now,
    format_forecast_hourly,
    current_weather,
    forecast_5d,
)

if __name__ == "__main__":
    for city in ("Moscow", "Kazan"):
        data = current_weather(city=city)
        print(format_current_now(data))
        print()
    print(compare_cities("Москва", "Казань")[:500])
    print()
    print(format_forecast_hourly(forecast_5d(city="Moscow"))[:600])