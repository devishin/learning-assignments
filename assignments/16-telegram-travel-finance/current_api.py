"""Модуль работы с api.exchangerate.host (курсы и конвертация)."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

LIVE_URL = "https://api.exchangerate.host/live"
CONVERT_URL = "https://api.exchangerate.host/convert"


class CurrencyApiError(Exception):
    """Ошибка запроса к exchangerate.host."""


def _api_key() -> str:
    key = (os.getenv("CURRENCY_API_KEY") or "").strip()
    if not key:
        raise CurrencyApiError("Задайте CURRENCY_API_KEY в файле .env")
    return key


def _check_response(data: dict) -> dict:
    if not data.get("success"):
        err = data.get("error") or {}
        if isinstance(err, dict):
            msg = err.get("info") or err.get("type") or "ошибка API"
        else:
            msg = str(err)
        raise CurrencyApiError(f"exchangerate.host: {msg}")
    return data


def get_current_rate(
    default: str = "USD",
    currencies: list[str] | None = None,
) -> dict[str, Any]:
    """GET /live — актуальные курсы (source + currencies)."""
    if currencies is None:
        currencies = ["EUR", "GBP", "JPY"]
    params = {
        "access_key": _api_key(),
        "source": default.strip().upper(),
        "currencies": ",".join(c.strip().upper() for c in currencies),
    }
    try:
        response = requests.get(LIVE_URL, params=params, timeout=30)
    except requests.RequestException as exc:
        raise CurrencyApiError(f"Сеть недоступна: {exc}") from exc
    try:
        data = response.json()
    except ValueError as exc:
        raise CurrencyApiError("Ответ не JSON") from exc
    return _check_response(data)


def convert_currency(
    amount: float,
    from_currency: str,
    to_currency: str,
) -> dict[str, Any]:
    """GET /convert — сумма из одной валюты в другую."""
    params = {
        "access_key": _api_key(),
        "from": from_currency.strip().upper(),
        "to": to_currency.strip().upper(),
        "amount": amount,
    }
    try:
        response = requests.get(CONVERT_URL, params=params, timeout=30)
    except requests.RequestException as exc:
        raise CurrencyApiError(f"Сеть недоступна: {exc}") from exc
    try:
        data = response.json()
    except ValueError as exc:
        raise CurrencyApiError("Ответ не JSON") from exc
    return _check_response(data)


def _quote_from_live(base: str, quote: str) -> float | None:
    data = get_current_rate(default=base, currencies=[quote])
    quotes = data.get("quotes") or {}
    pair = f"{base.upper()}{quote.upper()}"
    if pair in quotes:
        return float(quotes[pair])
    return None


def quote_to_per_from(base: str, quote: str) -> float:
    """Сколько quote за 1 base (для бота и SQLite)."""
    rate = _quote_from_live(base, quote)
    if rate is not None and rate > 0:
        return rate
    data = convert_currency(1, base, quote)
    info = data.get("info") or {}
    if info.get("rate") is not None:
        return float(info["rate"])
    result = float(data.get("result", 0))
    if result <= 0:
        raise CurrencyApiError(f"Нет курса {base} → {quote}")
    return result


def from_per_to_rate(base: str, quote: str) -> tuple[float, float]:
    to_per_from = quote_to_per_from(base, quote)
    return to_per_from, 1.0 / to_per_from


def convert_amount(amount_from: float, to_per_from: float) -> float:
    return amount_from * to_per_from


if __name__ == "__main__":
    sample = get_current_rate(
        default="RUB",
        currencies=["USD", "EUR", "GBP", "JPY", "CNY"],
    )
    print(sample.get("quotes"))
    print(convert_currency(100, "USD", "EUR"))