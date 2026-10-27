"""Загрузка настроек бота из файла .env."""

import os
from pathlib import Path

from dotenv import load_dotenv

# .env лежит рядом с этим файлом
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
_raw_db = (os.getenv("TASKS_DB_PATH", "tasks.db").strip() or "tasks.db")
DB_PATH = str((BASE_DIR / _raw_db).resolve() if not Path(_raw_db).is_absolute() else Path(_raw_db))
def _normalize_telegram_proxy(raw: str | None) -> str | None:
    """aiogram/aiohttp-socks понимают socks5, не socks5h — схему приводим."""
    url = (raw or "").strip()
    if not url:
        return None
    if url.startswith("socks5h://"):
        return "socks5://" + url[len("socks5h://") :]
    return url


# SOCKS/HTTP-прокси до api.telegram.org (например socks5h://127.0.0.1:10808)
TELEGRAM_PROXY = _normalize_telegram_proxy(os.getenv("TELEGRAM_PROXY"))


def check_token() -> None:
    """Проверяем, что токен задан перед запуском бота."""
    if not BOT_TOKEN:
        raise SystemExit(
            "Не задан BOT_TOKEN. Создайте бота у @BotFather и запишите токен в .env"
        )
