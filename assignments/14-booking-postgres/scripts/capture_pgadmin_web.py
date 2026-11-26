"""Скриншот интерфейса pgAdmin (Docker :5051)."""

from __future__ import annotations

import time
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "screenshots" / "01_pgadmin_tables.png"


def main() -> None:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={"width": 1600, "height": 1000})
        page.goto("http://127.0.0.1:5051/login?next=/browser/", wait_until="networkidle")
        page.locator("#inputEmail").fill("admin@local.dev")
        page.locator("#inputPassword").fill("pgadmin")
        page.get_by_role("button", name="Login").click()
        page.wait_for_url("**/browser/**", timeout=120_000)
        time.sleep(6)
        page.get_by_text("Servers", exact=True).first.click()
        time.sleep(0.5)
        page.get_by_text("booking", exact=False).first.click()
        time.sleep(0.5)
        for label in ("Schemas", "public", "Tables", "users"):
            page.get_by_text(label, exact=True).last.click(timeout=60_000)
            time.sleep(0.4)
        page.get_by_text("users", exact=True).last.click(button="right")
        page.get_by_text("View/Edit Data").first.click(timeout=30_000)
        time.sleep(3)
        page.screenshot(path=str(OUT), full_page=True)
        browser.close()
    print("saved", OUT)


if __name__ == "__main__":
    main()