"""«Мой город» — хранение в JSON (без БД, для домашнего задания)."""

from __future__ import annotations

import json
from pathlib import Path

STORE_PATH = Path(__file__).resolve().parent / "user_cities.json"


def _load() -> dict[str, str]:
    if not STORE_PATH.is_file():
        return {}
    try:
        with STORE_PATH.open(encoding="utf-8") as fh:
            data = json.load(fh)
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def _save(data: dict[str, str]) -> None:
    with STORE_PATH.open("w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)


def get_my_city(peer_id: int) -> str | None:
    return _load().get(str(peer_id))


def set_my_city(peer_id: int, city: str) -> None:
    data = _load()
    data[str(peer_id)] = city.strip()
    _save(data)


def remember_from_weather(peer_id: int, weather: dict, fallback_city: str = "") -> None:
    name = (weather.get("name") or fallback_city or "").strip()
    if name:
        set_my_city(peer_id, name)