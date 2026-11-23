"""Кэш курсов валют в JSON-файле."""

from __future__ import annotations

import json
import time
from pathlib import Path

DEFAULT_PATH = "currency_rate.json"
CACHE_TTL_SECONDS = 24 * 60 * 60


def save_to_file(data: dict, path: str = DEFAULT_PATH) -> None:
    """Сохранить dict в JSON (UTF-8, читаемый отступ)."""
    payload = dict(data)
    payload["_cached_at_unix"] = int(time.time())
    file_path = Path(path)
    with file_path.open("w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False, indent=4)


def read_from_file(path: str = DEFAULT_PATH) -> dict:
    """Прочитать dict из JSON."""
    file_path = Path(path)
    if not file_path.is_file():
        raise FileNotFoundError(f"Файл не найден: {path}")
    with file_path.open(encoding="utf-8") as fh:
        return json.load(fh)


def cache_is_fresh(data: dict, base: str, path: str = DEFAULT_PATH) -> bool:
    """Файл есть, не старше 24 ч и совпадает базовая валюта."""
    file_path = Path(path)
    if not file_path.is_file():
        return False
    if str(data.get("base_code", "")).upper() != base.strip().upper():
        return False
    cached_at = data.get("_cached_at_unix")
    if isinstance(cached_at, (int, float)):
        age = time.time() - float(cached_at)
        return age < CACHE_TTL_SECONDS
    mtime = file_path.stat().st_mtime
    return (time.time() - mtime) < CACHE_TTL_SECONDS


def load_fresh_rates(base: str, path: str = DEFAULT_PATH) -> tuple[dict, bool]:
    """
    Вернуть (данные, from_cache).
    При свежем кэше — из файла, иначе вызывающий код должен обновить API.
    """
    file_path = Path(path)
    if not file_path.is_file():
        return {}, False
    try:
        data = read_from_file(path)
    except (OSError, json.JSONDecodeError):
        return {}, False
    if cache_is_fresh(data, base, path):
        return data, True
    return data, False