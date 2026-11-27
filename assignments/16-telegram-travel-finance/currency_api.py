"""Конвертация валют через open.er-api.com (отдельный модуль API)."""

from __future__ import annotations

import requests

API_URL = "https://open.er-api.com/v6/latest/{base}"


class CurrencyApiError(Exception):
    """Ошибка при запросе курсов."""


def get_rates(base_currency: str) -> dict:
    code = base_currency.strip().upper()
    if not code:
        raise CurrencyApiError("Не указана базовая валюта.")
    url = API_URL.format(base=code)
    try:
        response = requests.get(url, timeout=30)
    except requests.RequestException as exc:
        raise CurrencyApiError(f"Сеть недоступна: {exc}") from exc
    if response.status_code != 200:
        raise CurrencyApiError(f"HTTP {response.status_code}")
    try:
        data = response.json()
    except ValueError as exc:
        raise CurrencyApiError("Ответ не JSON") from exc
    if data.get("result") != "success":
        raise CurrencyApiError(data.get("error-type", "unknown"))
    return data


def quote_to_per_from(base: str, quote: str) -> float:
    """Сколько quote-валюты за 1 единицу base (как в API rates[quote])."""
    data = get_rates(base)
    rates = data.get("rates") or {}
    quote_u = quote.strip().upper()
    if quote_u not in rates:
        raise CurrencyApiError(f"Нет курса {quote_u} для базы {base.upper()}")
    return float(rates[quote_u])


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