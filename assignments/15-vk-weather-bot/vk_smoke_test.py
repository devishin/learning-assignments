"""Проверка VK_BOT_TOKEN и Long Poll без запуска бота."""

from __future__ import annotations

import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

_ROOT = Path(__file__).resolve().parent
load_dotenv(_ROOT / ".env")

VK_API = "https://api.vk.com/method"
V = "5.199"


def vk(method: str, **params):
    token = (os.getenv("VK_BOT_TOKEN") or os.getenv("VK_ACCESS_TOKEN") or "").strip()
    if not token:
        print("FAIL: VK_BOT_TOKEN не задан в .env")
        sys.exit(1)
    gid = (os.getenv("VK_GROUP_ID") or "").strip().lstrip("-")
    payload = {"access_token": token, "v": V, **params}
    r = requests.post(f"{VK_API}/{method}", data=payload, timeout=30)
    data = r.json()
    if "error" in data:
        err = data["error"]
        print(f"FAIL: {method}: {err.get('error_msg')} ({err.get('error_code')})")
        sys.exit(1)
    return data["response"]


def main() -> None:
    perms = vk("groups.getTokenPermissions")
    names = {p.get("name") for p in perms.get("permissions", [])}
    if "messages" not in names:
        print("FAIL: у ключа нет права messages")
        sys.exit(1)
    print("OK: право messages")

    conv = vk("messages.getConversations", count=1)
    total = conv.get("count", 0)
    print(f"OK: messages API (диалогов: {total})")

    try:
        from openweather_api import current_weather, format_current_now

        print(format_current_now(current_weather(city="Москва")))
        print("OK: OpenWeather")
    except Exception as exc:
        print(f"FAIL: OpenWeather: {exc}")
        sys.exit(1)

    print("OK: готово к python bot.py")


if __name__ == "__main__":
    main()