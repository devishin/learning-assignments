"""Проверка токена и прокси (getMe). Запуск: python check_telegram.py"""

import asyncio

from bot import create_bot
from config import TELEGRAM_PROXY, check_token


async def main() -> None:
    check_token()
    bot = create_bot()
    try:
        me = await bot.get_me()
        print("proxy:", TELEGRAM_PROXY or "(не задан)")
        print("ok:", f"@{me.username}" if me.username else me.id)
    finally:
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
