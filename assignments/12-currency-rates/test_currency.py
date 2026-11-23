"""Локальная проверка без интерактива (не обязательна для сдачи)."""

from __future__ import annotations

import os
from pathlib import Path

from api_client import CurrencyApiError, get_currency_rates
from cli import convert_amount, fetch_rates
from storage import read_from_file


def _run() -> None:
    path = Path("currency_rate_test.json")
    if path.is_file():
        path.unlink()
    os.environ["TEST_CACHE"] = str(path)
    data = get_currency_rates("USD")
    assert data["result"] == "success"
    assert "RUB" in data["rates"]
    from storage import save_to_file

    save_to_file(data, str(path))
    loaded = read_from_file(str(path))
    assert loaded["base_code"] == "USD"
    fresh, src = fetch_rates("USD", str(path))
    assert "кэш" in src or "свежий" in src
    rub1 = convert_amount(100, "USD", "RUB", fresh)
    rub2 = convert_amount(100, "USD", "RUB", loaded)
    assert round(rub1, 4) == round(rub2, 4)
    gbp = convert_amount(50, "EUR", "GBP", fresh)
    assert gbp > 0
    try:
        get_currency_rates("FOO")
        raise AssertionError("expected error")
    except CurrencyApiError:
        pass
    path.unlink(missing_ok=True)
    print("OK: API, cache, USD->RUB, EUR->GBP, invalid code")


if __name__ == "__main__":
    _run()