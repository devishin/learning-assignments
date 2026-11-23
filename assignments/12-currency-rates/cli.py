"""Мини-CLI: курсы, конвертер, валидация кодов."""

from __future__ import annotations

import sys

from api_client import CurrencyApiError, get_currency_rates
from storage import DEFAULT_PATH, load_fresh_rates, save_to_file

DISPLAY_CODES = ("RUB", "EUR", "GBP")


def validate_currency(code: str, rates: dict) -> str:
    """Проверить код по conversion_rates / rates."""
    key = code.strip().upper()
    table = rates.get("rates") or {}
    if key not in table:
        supported = ", ".join(sorted(table.keys())[:12])
        raise CurrencyApiError(
            f"Валюта «{key}» отсутствует в ответе. "
            f"Примеры доступных кодов: {supported}…"
        )
    return key


def convert_amount(
    amount: float,
    from_code: str,
    to_code: str,
    rates: dict,
) -> float:
    """Конвертация через базу base_code из ответа API."""
    table = rates["rates"]
    base = rates["base_code"].upper()
    src = validate_currency(from_code, rates)
    dst = validate_currency(to_code, rates)
    if src == dst:
        return amount
    # Все курсы: 1 base = table[code] единиц валюты code
    in_base = amount / table[src] if src != base else amount
    if dst == base:
        return in_base
    return in_base * table[dst]


def fetch_rates(base: str, path: str | None = None) -> tuple[dict, str]:
    """Кэш < 24 ч или новый запрос."""
    cache_path = path or DEFAULT_PATH
    code = base.strip().upper()
    cached, from_cache = load_fresh_rates(code, cache_path)
    if from_cache and cached:
        return cached, "кэш (файл < 24 ч)"
    data = get_currency_rates(code)
    save_to_file(data, cache_path)
    return data, "свежий ответ API"


def print_header(data: dict, source: str) -> None:
    print(f"Источник: {source}")
    print(f"База: {data.get('base_code')}")
    print(f"Обновление (UTC): {data.get('time_last_update_utc')}")
    print(f"Следующее обновление (UTC): {data.get('time_next_update_utc')}")
    print()


def print_rates_for_display(data: dict) -> None:
    table = data.get("rates") or {}
    for code in DISPLAY_CODES:
        value = table.get(code)
        if value is not None:
            print(f"  {code}: {value}")


def run_converter(data: dict) -> None:
    try:
        raw_amount = input("Сумма для конвертации (Enter — пропустить): ").strip()
        if not raw_amount:
            return
        amount = float(raw_amount.replace(",", "."))
        from_code = input("Из валюты (например USD): ").strip()
        to_code = input("В валюту (например RUB): ").strip()
        result = convert_amount(amount, from_code, to_code, data)
        print(
            f"{amount} {from_code.upper()} = {result:.4f} {to_code.upper()} "
            f"(база ответа: {data['base_code']})"
        )
    except ValueError:
        print("Не удалось разобрать сумму. Введите число.", file=sys.stderr)
    except CurrencyApiError as exc:
        print(exc, file=sys.stderr)


def main() -> None:
    base = input("Базовая валюта (например USD): ").strip().upper()
    if not base:
        print("Валюта не введена.", file=sys.stderr)
        sys.exit(1)
    try:
        data, source = fetch_rates(base)
        print_header(data, source)
        print("Курсы (1 единица базы):")
        print_rates_for_display(data)
        run_converter(data)
    except CurrencyApiError as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)
    except OSError as exc:
        print(f"Ошибка файла кэша: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()