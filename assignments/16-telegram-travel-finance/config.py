"""Настройки из .env."""

import os
from pathlib import Path

from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

BOT_TOKEN = os.getenv("BOT_TOKEN", "").strip()
_raw_db = (os.getenv("FINANCE_DB_PATH", "travel_finance.db").strip() or "travel_finance.db")
DB_PATH = str(
    (BASE_DIR / _raw_db).resolve() if not Path(_raw_db).is_absolute() else Path(_raw_db)
)


def _normalize_telegram_proxy(raw: str | None) -> str | None:
    url = (raw or "").strip()
    if not url:
        return None
    if url.startswith("socks5h://"):
        return "socks5://" + url[len("socks5h://") :]
    return url


TELEGRAM_PROXY = _normalize_telegram_proxy(os.getenv("TELEGRAM_PROXY"))


def check_token() -> None:
    if not BOT_TOKEN:
        raise SystemExit("Задайте BOT_TOKEN в .env (токен от @BotFather).")