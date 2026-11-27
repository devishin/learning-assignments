"""Telegram-бот «Финансовый помощник» (aiogram + SQLite)."""

from __future__ import annotations

import asyncio
import logging
import re

from aiogram import Bot, Dispatcher, F
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.filters import Command, CommandObject, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand, ErrorEvent, Message

from config import BOT_TOKEN, DB_PATH, TELEGRAM_PROXY, check_token
from countries import CountryError, resolve_country
from currency_api import CurrencyApiError, convert_amount, from_per_to_rate
from database import (
    add_expense,
    clear_rate_override,
    create_trip,
    effective_from_per_to,
    effective_to_per_from,
    get_active_trip,
    get_connection,
    init_db,
    list_expenses,
    set_rate_override,
    spent_to,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
db = get_connection(DB_PATH)


class NewTrip(StatesGroup):
    from_country = State()
    to_country = State()
    budget = State()


def _fmt_money(value: float) -> str:
    return f"{value:,.2f}".replace(",", " ")


def format_balance(trip) -> str:
    spent = spent_to(db, int(trip["id"]))
    left_to = float(trip["initial_to"]) - spent
    rate = effective_to_per_from(trip)
    left_from = left_to / rate
    from_per_to = effective_from_per_to(trip)
    override = trip["rate_from_per_to_override"]
    rate_line = (
        f"Курс: {_fmt_money(from_per_to)} {trip['from_currency']} за 1 {trip['to_currency']}"
    )
    if override is not None:
        rate_line += " (тестовый)"
    else:
        rate_line += " (API)"
    return (
        f"✈ {trip['from_country']} → {trip['to_country']}\n"
        f"{rate_line}\n\n"
        f"Остаток: {_fmt_money(left_to)} {trip['to_currency']}\n"
        f"         ≈ {_fmt_money(left_from)} {trip['from_currency']}\n"
        f"Потрачено: {_fmt_money(spent)} {trip['to_currency']}"
    )


def format_history(trip) -> str:
    rows = list_expenses(db, int(trip["id"]))
    if not rows:
        return "Расходов пока нет. Отправьте сумму в валюте назначения или /spend 50"
    lines = [f"📒 История ({trip['to_country']}, {trip['to_currency']}):"]
    for row in rows:
        lines.append(
            f"• {row['created_at']}: −{_fmt_money(row['amount_to'])} {trip['to_currency']} "
            f"(≈ {_fmt_money(row['amount_from'])} {trip['from_currency']})"
        )
    return "\n".join(lines)


async def cmd_start(message: Message, bot: Bot) -> None:
    me = await bot.get_me()
    name = message.from_user.first_name if message.from_user else "друг"
    username = f"@{me.username}" if me.username else "бот"
    await message.answer(
        f"Привет, {name}!\n\n"
        f"{username} — финансовый помощник для поездок.\n\n"
        "Планируйте бюджет: страна выезда → страна назначения → сумма → расходы.\n\n"
        "Команды:\n"
        "/newtrip — новое путешествие\n"
        "/balance — остаток в двух валютах\n"
        "/history — история расходов\n"
        "/spend 120 — записать расход (в валюте назначения)\n"
        "/rate 104 — тестовый курс (RUB за 1 EUR и т.п.)\n"
        "/resetrate — снова курс из API"
    )


async def cmd_newtrip(message: Message, state: FSMContext) -> None:
    await state.set_state(NewTrip.from_country)
    await message.answer("Страна выезда (например Россия):")


async def newtrip_from(message: Message, state: FSMContext) -> None:
    try:
        country, ccy = resolve_country(message.text or "")
    except CountryError as exc:
        await message.answer(str(exc))
        return
    await state.update_data(from_country=country, from_currency=ccy)
    await state.set_state(NewTrip.to_country)
    await message.answer(
        f"Выезд: {country}, валюта {ccy}.\nСтрана назначения (например Италия):"
    )


async def newtrip_to(message: Message, state: FSMContext) -> None:
    try:
        country, ccy = resolve_country(message.text or "")
    except CountryError as exc:
        await message.answer(str(exc))
        return
    data = await state.get_data()
    if ccy == data["from_currency"] and country != data["from_country"]:
        await message.answer("Валюты совпали — выберите другую страну назначения.")
        return
    await state.update_data(to_country=country, to_currency=ccy)
    await state.set_state(NewTrip.budget)
    await message.answer(
        f"Назначение: {country}, валюта {ccy}.\n"
        f"Начальная сумма в {data['from_currency']} (например 200000):"
    )


async def newtrip_budget(message: Message, state: FSMContext) -> None:
    if not message.from_user:
        return
    text = (message.text or "").replace(" ", "").replace(",", ".")
    try:
        amount = float(text)
    except ValueError:
        await message.answer("Введите число, например 200000")
        return
    if amount <= 0:
        await message.answer("Сумма должна быть больше 0.")
        return
    data = await state.get_data()
    try:
        to_per_from, from_per_to = from_per_to_rate(data["from_currency"], data["to_currency"])
        amount_to = convert_amount(amount, to_per_from)
    except CurrencyApiError as exc:
        await message.answer(f"Не удалось получить курс: {exc}")
        return
    trip_id = create_trip(
        db,
        message.from_user.id,
        data["from_country"],
        data["to_country"],
        data["from_currency"],
        data["to_currency"],
        amount,
        amount_to,
        to_per_from,
    )
    await state.clear()
    trip = get_active_trip(db, message.from_user.id)
    await message.answer(
        f"Путешествие #{trip_id} создано.\n"
        f"Курс: {_fmt_money(from_per_to)} {data['from_currency']} за 1 {data['to_currency']}\n"
        f"Бюджет: {_fmt_money(amount)} {data['from_currency']} "
        f"≈ {_fmt_money(amount_to)} {data['to_currency']}\n\n"
        f"{format_balance(trip)}"
    )


async def cmd_balance(message: Message) -> None:
    if not message.from_user:
        return
    trip = get_active_trip(db, message.from_user.id)
    if not trip:
        await message.answer("Нет активного путешествия. Создайте: /newtrip")
        return
    await message.answer(format_balance(trip))


async def cmd_history(message: Message) -> None:
    if not message.from_user:
        return
    trip = get_active_trip(db, message.from_user.id)
    if not trip:
        await message.answer("Нет активного путешествия. /newtrip")
        return
    await message.answer(format_history(trip))


async def cmd_spend(message: Message, command: CommandObject) -> None:
    if not message.from_user:
        return
    trip = get_active_trip(db, message.from_user.id)
    if not trip:
        await message.answer("Сначала /newtrip")
        return
    arg = (command.args or "").replace(" ", "").replace(",", ".")
    try:
        amount = float(arg)
    except ValueError:
        await message.answer("Пример: /spend 45.90")
        return
    try:
        add_expense(db, trip, amount)
    except ValueError as exc:
        await message.answer(str(exc))
        return
    trip = get_active_trip(db, message.from_user.id)
    await message.answer(
        f"Расход −{_fmt_money(amount)} {trip['to_currency']} учтён.\n\n{format_balance(trip)}"
    )


async def cmd_rate(message: Message, command: CommandObject) -> None:
    if not message.from_user:
        return
    trip = get_active_trip(db, message.from_user.id)
    if not trip:
        await message.answer("Сначала /newtrip")
        return
    arg = (command.args or "").replace(" ", "").replace(",", ".")
    try:
        from_per_to = float(arg)
    except ValueError:
        await message.answer(
            f"Укажите, сколько {trip['from_currency']} за 1 {trip['to_currency']}.\n"
            "Пример: /rate 104"
        )
        return
    set_rate_override(db, int(trip["id"]), from_per_to)
    trip = get_active_trip(db, message.from_user.id)
    await message.answer(
        f"Тестовый курс: {_fmt_money(from_per_to)} {trip['from_currency']} "
        f"за 1 {trip['to_currency']}.\n\n{format_balance(trip)}"
    )


async def cmd_resetrate(message: Message) -> None:
    if not message.from_user:
        return
    trip = get_active_trip(db, message.from_user.id)
    if not trip:
        await message.answer("Сначала /newtrip")
        return
    clear_rate_override(db, int(trip["id"]))
    trip = get_active_trip(db, message.from_user.id)
    await message.answer(f"Курс снова из API.\n\n{format_balance(trip)}")


async def plain_expense(message: Message) -> None:
    """Число в чате = расход в валюте назначения (если есть поездка)."""
    if not message.from_user or not message.text:
        return
    if message.text.startswith("/"):
        return
    if not re.fullmatch(r"[\d\s.,]+", message.text.strip()):
        return
    trip = get_active_trip(db, message.from_user.id)
    if not trip:
        return
    text = message.text.replace(" ", "").replace(",", ".")
    try:
        amount = float(text)
    except ValueError:
        return
    if amount <= 0:
        return
    try:
        add_expense(db, trip, amount)
    except ValueError:
        return
    trip = get_active_trip(db, message.from_user.id)
    await message.answer(
        f"Расход −{_fmt_money(amount)} {trip['to_currency']}.\n\n{format_balance(trip)}"
    )


def create_bot() -> Bot:
    if TELEGRAM_PROXY:
        return Bot(token=BOT_TOKEN, session=AiohttpSession(proxy=TELEGRAM_PROXY))
    return Bot(token=BOT_TOKEN)


async def on_error(event: ErrorEvent) -> None:
    logging.exception("handler error: %s", event.exception)
    if event.update.message:
        await event.update.message.answer("Ошибка обработки. Проверьте консоль бота.")


async def main() -> None:
    check_token()
    init_db(db)
    bot = create_bot()
    storage = MemoryStorage()
    dp = Dispatcher(storage=storage)
    dp.errors.register(on_error)

    def cmd(name: str) -> Command:
        return Command(name, ignore_mention=True)

    dp.message.register(cmd_start, cmd("start"))
    dp.message.register(cmd_newtrip, cmd("newtrip"))
    dp.message.register(cmd_balance, cmd("balance"))
    dp.message.register(cmd_history, cmd("history"))
    dp.message.register(cmd_spend, cmd("spend"))
    dp.message.register(cmd_rate, cmd("rate"))
    dp.message.register(cmd_resetrate, cmd("resetrate"))

    dp.message.register(newtrip_from, StateFilter(NewTrip.from_country))
    dp.message.register(newtrip_to, StateFilter(NewTrip.to_country))
    dp.message.register(newtrip_budget, StateFilter(NewTrip.budget))
    dp.message.register(plain_expense, F.text, StateFilter(None))

    await bot.set_my_commands(
        [
            BotCommand(command="start", description="Справка"),
            BotCommand(command="newtrip", description="Новое путешествие"),
            BotCommand(command="balance", description="Остаток"),
            BotCommand(command="history", description="История расходов"),
            BotCommand(command="spend", description="Расход"),
        ]
    )
    me = await bot.get_me()
    username = f"@{me.username}" if me.username else str(me.id)
    print(f"Бот {username}, БД: {DB_PATH}")
    await dp.start_polling(bot, drop_pending_updates=True)


if __name__ == "__main__":
    asyncio.run(main())