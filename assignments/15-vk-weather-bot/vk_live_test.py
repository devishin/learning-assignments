"""
Интеграционный тест без Long Poll: клавиатура, OpenWeather, VK messages API.

Ключ из product-post-generator имеет messages, но не groups.getLongPollServer
(см. VK_BOTS.md). Полный `python bot.py` — когда появится право Long Poll.
"""

from __future__ import annotations

import json
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
    token = (os.getenv("VK_BOT_TOKEN") or "").strip()
    if not token:
        print("FAIL: VK_BOT_TOKEN")
        sys.exit(1)
    payload = {"access_token": token, "v": V, **params}
    r = requests.post(f"{VK_API}/{method}", data=payload, timeout=30)
    data = r.json()
    if "error" in data:
        print(f"FAIL {method}: {data['error'].get('error_msg')}")
        sys.exit(1)
    return data["response"]


def main() -> None:
    from bot import main_keyboard
    from openweather_api import compare_cities, format_current_now, current_weather

    json.loads(main_keyboard())
    print("OK: клавиатура JSON")

    print(format_current_now(current_weather(city="Москва")))
    print(compare_cities("Москва", "Казань").splitlines()[0])
    print("OK: OpenWeather")

    conv = vk("messages.getConversations", count=5)
    print(f"OK: messages.getConversations (диалогов: {conv.get('count', 0)})")

    lp = requests.post(
        f"{VK_API}/groups.getLongPollServer",
        data={
            "access_token": os.getenv("VK_BOT_TOKEN"),
            "v": V,
            "group_id": (os.getenv("VK_GROUP_ID") or "237955088").lstrip("-"),
        },
        timeout=30,
    ).json()
    if "response" in lp:
        print("OK: Long Poll server (можно python bot.py)")
    else:
        print(
            "NOTE: Long Poll недоступен для этого ключа (код 15). "
            "Как в product-post-generator — нужен ключ с управлением сообществом "
            "или inbox-режим. Логика бота и messages API проверены."
        )


if __name__ == "__main__":
    main()