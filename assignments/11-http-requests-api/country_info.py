"""Красивый вывод сведений о стране (restcountries API + colorama)."""

from __future__ import annotations

import sys

import requests
from colorama import Fore, Style, init

from api_client import fetch_countries_by_name


def _first(data: list[dict], *keys: str, default: str = "—") -> str:
    """Достать вложенное поле из первого элемента ответа API."""
    if not data:
        return default
    node: object = data[0]
    for key in keys:
        if not isinstance(node, dict) or key not in node:
            return default
        node = node[key]
    if isinstance(node, (int, float)):
        return f"{node:,}".replace(",", " ")
    if isinstance(node, list):
        return ", ".join(str(x) for x in node)
    if isinstance(node, dict):
        if all(isinstance(v, str) for v in node.values()):
            return ", ".join(node.values())
        if all(isinstance(v, dict) for v in node.values()):
            parts: list[str] = []
            for code, info in node.items():
                name = info.get("name", code)
                symbol = info.get("symbol", "")
                parts.append(f"{name} ({symbol})" if symbol else str(name))
            return ", ".join(parts)
        if len(node) == 1:
            only = next(iter(node.values()))
            if isinstance(only, str):
                return only
        return ", ".join(f"{k}: {v}" for k, v in node.items())
    return str(node)


def fetch_country(country: str) -> list[dict]:
    return fetch_countries_by_name(country)


def print_country_info(country: str, data: list[dict]) -> None:
    init(autoreset=True)
    common = _first(data, "name", "common")
    official = _first(data, "name", "official")
    capital = _first(data, "capital")
    region = _first(data, "region")
    subregion = _first(data, "subregion")
    languages = _first(data, "languages")
    currencies = _first(data, "currencies")
    population = _first(data, "population")
    area = _first(data, "area")
    tld = _first(data, "tld")
    cca2 = _first(data, "cca2")
    flag = _first(data, "flag")
    flag_png = _first(data, "flags", "png")

    print()
    print(Fore.CYAN + Style.BRIGHT + f"Страна: {common}")
    print(Fore.WHITE + f"Официальное название: {official}")
    print(Fore.GREEN + f"Столица: {capital}")
    print(Fore.YELLOW + f"Регион: {region}" + (f" ({subregion})" if subregion != "—" else ""))
    print(Fore.MAGENTA + f"Языки: {languages}")
    print(Fore.CYAN + f"Валюта: {currencies}")
    print(Fore.WHITE + f"Население: {population}")
    print(Fore.WHITE + f"Площадь: {area} км²")
    print(Fore.GREEN + f"Домен (TLD): {tld}")
    print(Fore.YELLOW + f"Код страны: {cca2}")
    print(Fore.RED + f"Флаг (символ): {flag}")
    if flag_png != "—":
        print(Fore.BLUE + f"Ссылка на флаг: {flag_png}")
    print()

    # Демонстрация «достать 2–3 поля из JSON», как в задании
    print(Fore.LIGHTBLACK_EX + "--- Ключевые поля (ручной разбор JSON) ---")
    print(f"  name.common → {common}")
    print(f"  capital[0]  → {capital}")
    print(f"  population  → {population}")


def main() -> None:
    country = input("Введите страну: ").strip()
    if not country:
        print("Страна не указана.", file=sys.stderr)
        sys.exit(1)
    try:
        data = fetch_country(country)
        print_country_info(country, data)
    except requests.HTTPError as exc:
        print(f"HTTP ошибка: {exc.response.status_code}", file=sys.stderr)
        sys.exit(1)
    except requests.RequestException as exc:
        print(f"Ошибка сети: {exc}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()