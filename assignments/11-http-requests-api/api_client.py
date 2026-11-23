"""Запросы к API стран (URL с урока + резервный JSON при deprecation)."""

from __future__ import annotations

import requests

# URL из урока
LESSON_COUNTRY_URL = "https://restcountries.com/v3.1/name/{country}"

# Структура полей близка к v3.1 (Open Data)
BACKUP_COUNTRIES_JSON = (
    "https://raw.githubusercontent.com/mledoze/countries/master/countries.json"
)

_cache: list[dict] | None = None


def _load_backup_cache() -> list[dict]:
    global _cache
    if _cache is None:
        response = requests.get(BACKUP_COUNTRIES_JSON, timeout=60)
        response.raise_for_status()
        data = response.json()
        if not isinstance(data, list):
            raise ValueError("Резервный JSON стран: неожиданный формат")
        _cache = data
    return _cache


def _match_country_name(entry: dict, query: str) -> bool:
    name = entry.get("name") or {}
    if not isinstance(name, dict):
        return False
    q = query.strip().lower()
    for key in ("common", "official"):
        val = name.get(key)
        if isinstance(val, str) and q in val.lower():
            return True
    native = name.get("native")
    if isinstance(native, dict):
        for block in native.values():
            if isinstance(block, dict):
                for val in block.values():
                    if isinstance(val, str) and q in val.lower():
                        return True
    return False


def _fetch_from_backup(country: str) -> list[dict]:
    matches = [c for c in _load_backup_cache() if _match_country_name(c, country)]
    if not matches:
        raise requests.HTTPError(f"Страна не найдена: {country}")
    return matches[:3]


def fetch_countries_by_name(country: str) -> list[dict]:
    """
    GET по имени страны.

    Сначала — адрес с урока (restcountries v3.1).
    Если API отвечает обёрткой deprecation — используется резервный JSON.
    """
    url = LESSON_COUNTRY_URL.format(country=country.strip())
    response = requests.get(url, timeout=30)
    response.raise_for_status()
    payload = response.json()

    if isinstance(payload, list) and payload:
        return payload

    if isinstance(payload, dict):
        if payload.get("success") is False or payload.get("errors"):
            return _fetch_from_backup(country)
        data = payload.get("data")
        if isinstance(data, list) and data:
            return data

    return _fetch_from_backup(country)


def lesson_country_url(country: str) -> str:
    """Полный URL для пунктa меню «как на уроке»."""
    return LESSON_COUNTRY_URL.format(country=country.strip())