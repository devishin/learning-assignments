"""getMe — проверка BOT_TOKEN."""

import asyncio

from aiogram import Bot

from config import BOT_TOKEN, check_token


async def main() -> None:
    check_token()
    bot = Bot(token=BOT_TOKEN)
    me = await bot.get_me()
    print(f"OK: @{me.username} ({me.first_name})")
    await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())