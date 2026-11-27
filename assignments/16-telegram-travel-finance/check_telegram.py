"""getMe — проверка BOT_TOKEN (и TELEGRAM_PROXY)."""

import asyncio

from aiogram import Bot
from aiogram.client.session.aiohttp import AiohttpSession

from config import BOT_TOKEN, TELEGRAM_PROXY, check_token


async def main() -> None:
    check_token()
    if TELEGRAM_PROXY:
        bot = Bot(token=BOT_TOKEN, session=AiohttpSession(proxy=TELEGRAM_PROXY))
    else:
        bot = Bot(token=BOT_TOKEN)
    me = await bot.get_me()
    print(f"OK: @{me.username} ({me.first_name})")
    await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())