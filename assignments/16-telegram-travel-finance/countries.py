"""Страна → ISO-код валюты (учебный справочник)."""

from __future__ import annotations

_COUNTRY_MAP: dict[str, tuple[str, str]] = {
    "россия": ("Россия", "RUB"),
    "russia": ("Россия", "RUB"),
    "рф": ("Россия", "RUB"),
    "италия": ("Италия", "EUR"),
    "italy": ("Италия", "EUR"),
    "германия": ("Германия", "EUR"),
    "germany": ("Германия", "EUR"),
    "франция": ("Франция", "EUR"),
    "france": ("Франция", "EUR"),
    "испания": ("Испания", "EUR"),
    "spain": ("Испания", "EUR"),
    "турция": ("Турция", "TRY"),
    "turkey": ("Турция", "TRY"),
    "таиланд": ("Таиланд", "THB"),
    "thailand": ("Таиланд", "THB"),
    "сша": ("США", "USD"),
    "usa": ("США", "USD"),
    "америка": ("США", "USD"),
    "великобритания": ("Великобритания", "GBP"),
    "англия": ("Великобритания", "GBP"),
    "uk": ("Великобритания", "GBP"),
    "япония": ("Япония", "JPY"),
    "japan": ("Япония", "JPY"),
    "китай": ("Китай", "CNY"),
    "china": ("Китай", "CNY"),
    "оаэ": ("ОАЭ", "AED"),
    "грузия": ("Грузия", "GEL"),
    "казахстан": ("Казахстан", "KZT"),
}


class CountryError(Exception):
    """Неизвестная страна."""


def resolve_country(text: str) -> tuple[str, str]:
    key = text.strip().lower().replace("ё", "е")
    if not key:
        raise CountryError("Введите название страны")
    if key in _COUNTRY_MAP:
        return _COUNTRY_MAP[key]
    for pair in _COUNTRY_MAP.values():
        if key == pair[0].lower():
            return pair
    raise CountryError(
        f"Страна «{text.strip()}» не в справочнике. "
        "Примеры: Россия, Италия, Турция, США"
    )


def hint_countries() -> str:
    samples = sorted({v[0] for v in _COUNTRY_MAP.values()})
    return ", ".join(samples[:12]) + "…"