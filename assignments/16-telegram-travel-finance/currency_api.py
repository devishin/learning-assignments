"""Конвертация валют через api.exchangerate.host (отдельный модуль API)."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import requests
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent / ".env")

API_BASE = "https://api.exchangerate.host"


class CurrencyApiError(Exception):
    """Ошибка при запросе курсов."""


def _access_key() -> str:
    key = (os.getenv("EXCHANGERATE_ACCESS_KEY") or os.getenv("ACCESS_KEY") or "").strip()
    if not key:
        raise CurrencyApiError(
            "Не задан EXCHANGERATE_ACCESS_KEY в .env (бесплатный ключ: exchangerate.host)"
        )
    return key


def _get(path: str, **params: Any) -> dict:
    params = {**params, "access_key": _access_key()}
    url = f"{API_BASE}/{path.lstrip('/')}"
    try:
        response = requests.get(url, params=params, timeout=30)
    except requests.RequestException as exc:
        raise CurrencyApiError(f"Сеть недоступна: {exc}") from exc
    if response.status_code != 200:
        raise CurrencyApiError(f"HTTP {response.status_code}")
    try:
        data = response.json()
    except ValueError as exc:
        raise CurrencyApiError("Ответ не JSON") from exc
    if not data.get("success"):
        err = data.get("error") or {}
        if isinstance(err, dict):
            msg = err.get("info") or err.get("type") or "ошибка API"
        else:
            msg = str(err)
        raise CurrencyApiError(f"exchangerate.host: {msg}")
    return data


def convert(from_ccy: str, to_ccy: str, amount: float) -> dict:
    """GET /convert?from=&to=&amount= — ответ APILayer / exchangerate.host."""
    base = from_ccy.strip().upper()
    quote = to_ccy.strip().upper()
    if not base or not quote:
        raise CurrencyApiError("Укажите валюты")
    if amount <= 0:
        raise CurrencyApiError("Сумма должна быть > 0")
    return _get(
        "convert",
        from=base,
        to=quote,
        amount=amount,
    )


def get_rates(base_currency: str) -> dict:
    """
    Курс из /live (для совместимости с тестами).
    source = base, currencies = все основные — для конвертации используйте convert().
    """
    code = base_currency.strip().upper()
    return _get("live", source=code)


def quote_to_per_from(base: str, quote: str) -> float:
    """Сколько quote-валюты за 1 единицу base (через /convert amount=1)."""
    data = convert(base, quote, 1.0)
    info = data.get("info") or {}
    rate = info.get("rate")
    if rate is not None:
        return float(rate)
    result = float(data.get("result", 0))
    if result <= 0:
        raise CurrencyApiError("Некорректный курс в ответе API")
    return result


def from_per_to_rate(base: str, quote: str) -> tuple[float, float]:
    """
    (to_per_from, from_per_to) — для подписи «104 ₽ за €1» и пересчёта сумм.
    """
    to_per_from = quote_to_per_from(base, quote)
    if to_per_from <= 0:
        raise CurrencyApiError("Некорректный курс")
    from_per_to = 1.0 / to_per_from
    return to_per_from, from_per_to


def convert_amount(amount_from: float, to_per_from: float) -> float:
    return amount_from * to_per_from