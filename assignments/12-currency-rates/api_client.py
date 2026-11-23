"""HTTP-запросы к open.er-api.com."""

from __future__ import annotations

import requests

API_URL = "https://open.er-api.com/v6/latest/{base}"


class CurrencyApiError(Exception):
    """Ошибка ответа API курсов валют."""


def get_currency_rates(base: str) -> dict:
    """GET https://open.er-api.com/v6/latest/{base}, вернуть JSON как dict."""
    code = base.strip().upper()
    if not code:
        raise CurrencyApiError("Базовая валюта не указана.")
    url = f"{API_URL.format(base=code)}"
    try:
        response = requests.get(url, timeout=30)
    except requests.RequestException as exc:
        raise CurrencyApiError(f"Сеть недоступна или запрос не выполнен: {exc}") from exc
    if response.status_code != 200:
        raise CurrencyApiError(
            f"Сервер вернул статус {response.status_code}. Повторите позже."
        )
    try:
        data = response.json()
    except ValueError as exc:
        raise CurrencyApiError("Ответ не похож на JSON.") from exc
    if data.get("result") != "success":
        err = data.get("error-type", "unknown")
        raise CurrencyApiError(
            f"Курс для «{code}» не получен (тип ошибки API: {err}). "
            "Проверьте код валюты (ISO 4217, например USD)."
        )
    return data