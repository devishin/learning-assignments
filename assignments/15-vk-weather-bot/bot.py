"""VK-бот погоды (VKBottle, Long Poll)."""

from __future__ import annotations

import logging
import os
import re
from pathlib import Path

from dotenv import load_dotenv

# На части сетей api.vk.ru нестабилен; для запросов vkbottle используем api.vk.com.
import vkbottle_types
from vkbottle.api.api import API as VkApi

vkbottle_types.API_URL = "https://api.vk.com/method/"
VkApi.API_URL = "https://api.vk.com/method/"

from vkbottle import (
    BaseStateGroup,
    Bot,
    Keyboard,
    KeyboardButtonColor,
    Text,
)
from vkbottle.bot import Message

from openweather_api import (
    WeatherApiError,
    air_quality,
    compare_cities,
    coords_from_weather,
    current_weather,
    format_current_now,
    format_extended,
    format_forecast_hourly,
    forecast_5d,
)
from user_storage import get_my_city, remember_from_weather, set_my_city

load_dotenv(Path(__file__).resolve().parent / ".env")
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("vk-weather-bot")

bot = Bot(token=os.environ["VK_BOT_TOKEN"])


class Form(BaseStateGroup):
    WAIT_CITY = 0
    WAIT_MY_CITY = 1
    WAIT_COMPARE = 2


def main_keyboard() -> str:
    kb = Keyboard(one_time=False, inline=False)
    kb.add(Text("🌤 Сейчас", {"cmd": "now"}), color=KeyboardButtonColor.POSITIVE)
    kb.add(Text("🏙 Мой город", {"cmd": "my"}), color=KeyboardButtonColor.PRIMARY)
    kb.row()
    kb.add(Text("📅 Прогноз", {"cmd": "forecast"}), color=KeyboardButtonColor.SECONDARY)
    kb.add(Text("📍 Геолокация", {"cmd": "geo_help"}), color=KeyboardButtonColor.PRIMARY)
    kb.row()
    kb.add(Text("🌫 Расширенный", {"cmd": "extended"}), color=KeyboardButtonColor.SECONDARY)
    kb.add(Text("⚖ Сравнить", {"cmd": "compare"}), color=KeyboardButtonColor.SECONDARY)
    kb.row()
    kb.add(Text("ℹ Помощь", {"cmd": "help"}))
    return kb.get_json()


async def _reply_weather_now(message: Message, *, city: str | None = None,
                              lat: float | None = None, lon: float | None = None) -> None:
    data = current_weather(city=city, lat=lat, lon=lon)
    remember_from_weather(message.peer_id, data, fallback_city=city or "")
    await message.answer(format_current_now(data), keyboard=main_keyboard())


async def _city_or_my(message: Message, explicit: str | None) -> str:
    if explicit and explicit.strip():
        return explicit.strip()
    saved = get_my_city(message.peer_id)
    if saved:
        return saved
    raise WeatherApiError('Сначала введите город (🌤 Сейчас) или задайте «🏙 Мой город».')


@bot.on.message(text=["/start", "начать", "Начать", "старт"])
async def cmd_start(message: Message) -> None:
    saved = get_my_city(message.peer_id)
    hint = f"\nВаш город: {saved}" if saved else ""
    await message.answer(
        "Бот погоды OpenWeather." + hint + "\n\n"
        "🌤 Сейчас — температура, влажность, ветер\n"
        "🏙 Мой город — запомнить последний / задать вручную\n"
        "📅 Прогноз — по часам на 5 дней\n"
        "📍 Геолокация — прикрепите точку на карте\n"
        "🌫 Расширенный — качество воздуха\n"
        "⚖ Сравнить — два города: Город1 | Город2",
        keyboard=main_keyboard(),
    )


@bot.on.message(payload={"cmd": "help"})
@bot.on.message(text=["помощь", "help", "ℹ Помощь"])
async def cmd_help(message: Message) -> None:
    await cmd_start(message)


@bot.on.message(payload={"cmd": "now"})
@bot.on.message(text=["🌤 Сейчас", "сейчас"])
async def btn_now(message: Message) -> None:
    await bot.state_dispenser.set(message.peer_id, Form.WAIT_CITY, city_mode="now")
    await message.answer("Введите город (например Москва):")


@bot.on.message(payload={"cmd": "my"})
@bot.on.message(text=["🏙 Мой город", "мой город"])
async def btn_my_city(message: Message) -> None:
    saved = get_my_city(message.peer_id)
    if saved:
        try:
            await _reply_weather_now(message, city=saved)
            return
        except WeatherApiError as exc:
            await message.answer(str(exc), keyboard=main_keyboard())
    await bot.state_dispenser.set(message.peer_id, Form.WAIT_MY_CITY)
    await message.answer("Введите город, который запомнить как «Мой город»:")


@bot.on.message(payload={"cmd": "forecast"})
@bot.on.message(text=["📅 Прогноз", "прогноз"])
async def btn_forecast(message: Message) -> None:
    await bot.state_dispenser.set(message.peer_id, Form.WAIT_CITY, city_mode="forecast")
    await message.answer(
        "Введите город (или пусто — оставьте «Мой город», если уже задан):",
        keyboard=main_keyboard(),
    )


@bot.on.message(payload={"cmd": "extended"})
@bot.on.message(text=["🌫 Расширенный", "расширенный"])
async def btn_extended(message: Message) -> None:
    await bot.state_dispenser.set(message.peer_id, Form.WAIT_CITY, city_mode="extended")
    await message.answer(
        "Введите город для расширенного режима (воздух + погода):",
        keyboard=main_keyboard(),
    )


@bot.on.message(payload={"cmd": "geo_help"})
@bot.on.message(text=["📍 Геолокация", "геолокация"])
async def btn_geo_help(message: Message) -> None:
    await message.answer(
        "Отправьте точку на карте (скрепка → Местоположение). "
        "Бот определит место и покажет погоду.",
        keyboard=main_keyboard(),
    )


@bot.on.message(payload={"cmd": "compare"})
@bot.on.message(text=["⚖ Сравнить", "сравнить"])
async def btn_compare(message: Message) -> None:
    await message.answer(
        "Формат: сравни: Москва | Санкт-Петербург",
        keyboard=main_keyboard(),
    )


@bot.on.message(text=re.compile(r"(?i)^погода\s+(.+)$"))
async def text_weather(message: Message, city: str | None = None) -> None:
    try:
        await _reply_weather_now(message, city=(city or "").strip())
    except WeatherApiError as exc:
        await message.answer(str(exc), keyboard=main_keyboard())


@bot.on.message(text=re.compile(r"(?i)^сравни:\s*(.+)$"))
async def text_compare(message: Message, rest: str | None = None) -> None:
    part = (rest or "").strip()
    cities = [c.strip() for c in re.split(r"\||/", part) if c.strip()]
    if len(cities) != 2:
        await message.answer("Нужно два города: сравни: Город1 | Город2", keyboard=main_keyboard())
        return
    try:
        await message.answer(compare_cities(cities[0], cities[1]), keyboard=main_keyboard())
    except WeatherApiError as exc:
        await message.answer(str(exc), keyboard=main_keyboard())


@bot.on.message()
async def handle_geo_and_states(message: Message) -> None:
    if message.geo:
        lat = message.geo.coordinates.latitude
        lon = message.geo.coordinates.longitude
        try:
            await _reply_weather_now(message, lat=lat, lon=lon)
        except WeatherApiError as exc:
            await message.answer(str(exc), keyboard=main_keyboard())
        return

    state = await bot.state_dispenser.get(message.peer_id)
    if state is None:
        return
    text = (message.text or "").strip()
    mode = state.payload.get("city_mode", "now")

    done = False
    try:
        if state.state == Form.WAIT_MY_CITY:
            if not text:
                return
            set_my_city(message.peer_id, text)
            await _reply_weather_now(message, city=text)
            done = True
            return

        if state.state == Form.WAIT_CITY:
            city = text or get_my_city(message.peer_id) or ""
            if mode == "forecast":
                if not city:
                    raise WeatherApiError("Укажите город или задайте «Мой город».")
                data = forecast_5d(city=city)
                await message.answer(format_forecast_hourly(data), keyboard=main_keyboard())
                done = True
            elif mode == "extended":
                if not city:
                    raise WeatherApiError("Укажите город.")
                data = current_weather(city=city)
                lat, lon = coords_from_weather(data)
                air = air_quality(lat=lat, lon=lon)
                remember_from_weather(message.peer_id, data, fallback_city=city)
                await message.answer(format_extended(data, air), keyboard=main_keyboard())
                done = True
            else:
                if not text:
                    await message.answer("Введите название города.", keyboard=main_keyboard())
                    return
                await _reply_weather_now(message, city=text)
                done = True
    except WeatherApiError as exc:
        await message.answer(str(exc), keyboard=main_keyboard())
        done = True
    if done:
        await bot.state_dispenser.delete(message.peer_id)


def main() -> None:
    if not os.getenv("VK_BOT_TOKEN"):
        raise SystemExit("Задайте VK_BOT_TOKEN в .env")
    logger.info("Старт polling (bot.run)")
    bot.run()


if __name__ == "__main__":
    main()