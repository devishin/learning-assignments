"""Тестовый модуль для ручных GET/POST запросов из консоли."""

from __future__ import annotations

import json
import sys

import requests

from api_client import fetch_countries_by_name, lesson_country_url

# Примеры URL с урока
URL_DOG_PHOTO = "https://dog.ceo/api/breeds/image/random"
URL_HTTPBIN_POST = "https://httpbin.org/post"


def make_get_request(url: str) -> None:
    """Выполнить GET-запрос и вывести тело ответа."""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        print(f"Статус: {response.status_code}")
        try:
            data = response.json()
            print(json.dumps(data, ensure_ascii=False, indent=2))
        except ValueError:
            print(response.text)
    except requests.RequestException as exc:
        print(f"Ошибка запроса: {exc}", file=sys.stderr)


def make_post_request(url: str, payload: dict | None = None) -> None:
    """Выполнить POST-запрос (JSON) и вывести тело ответа."""
    body = payload or {"hello": "world", "source": "learning-assignments"}
    try:
        response = requests.post(url, json=body, timeout=30)
        response.raise_for_status()
        print(f"Статус: {response.status_code}")
        try:
            data = response.json()
            print(json.dumps(data, ensure_ascii=False, indent=2))
        except ValueError:
            print(response.text)
    except requests.RequestException as exc:
        print(f"Ошибка запроса: {exc}", file=sys.stderr)


def make_get_country_request(country: str) -> None:
    """GET к restcountries.com по названию страны (URL с урока)."""
    url = lesson_country_url(country)
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        print(f"Статус: {response.status_code}")
        payload = response.json()
        print(json.dumps(payload, ensure_ascii=False, indent=2))
        if isinstance(payload, dict) and payload.get("success") is False:
            print(
                "\nAPI v3.1 помечен как устаревший. "
                "Ниже — тот же поиск по имени из резервного JSON:\n"
            )
            data = fetch_countries_by_name(country)
            print(json.dumps(data, ensure_ascii=False, indent=2))
    except requests.RequestException as exc:
        print(f"Ошибка запроса: {exc}", file=sys.stderr)


def print_menu() -> None:
    print()
    print("=== Тестовые HTTP-запросы ===")
    print("1 — GET (ввести URL)")
    print("2 — POST (ввести URL, демо-JSON)")
    print("3 — GET информация о стране (restcountries)")
    print("4 — Выйти")
    print(f"   Подсказка для п.1: {URL_DOG_PHOTO}")


def main() -> None:
    while True:
        print_menu()
        choice = input("Выберите пункт (1–4): ").strip()
        if choice == "1":
            url = input("Введите URL для GET: ").strip()
            if url:
                make_get_request(url)
        elif choice == "2":
            url = input(
                f"Введите URL для POST (Enter — {URL_HTTPBIN_POST}): "
            ).strip()
            make_post_request(url or URL_HTTPBIN_POST)
        elif choice == "3":
            country = input("Введите страну (например, Italy, Russia): ").strip()
            if country:
                make_get_country_request(country)
        elif choice == "4":
            print("Выход.")
            break
        else:
            print("Неверный пункт. Введите число от 1 до 4.")


if __name__ == "__main__":
    main()