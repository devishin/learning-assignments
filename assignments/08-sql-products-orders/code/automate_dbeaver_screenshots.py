#!/usr/bin/env python3
"""Capture real DBeaver window screenshots (mss), after connecting SQLite DB."""
from __future__ import annotations

import json
import subprocess
import time
from pathlib import Path

import mss
import pyautogui
import pygetwindow as gw

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "screenshots"
DB = ROOT / "products_orders.db"
EXE = Path(r"C:\Users\a.devishin\AppData\Local\DBeaver\dbeaver.exe")
DS_JSON = Path(
    r"C:\Users\a.devishin\AppData\Roaming\DBeaverData\workspace6\General\.dbeaver\data-sources.json"
)

pyautogui.FAILSAFE = False
pyautogui.PAUSE = 0.35


def kill_dbeaver() -> None:
    subprocess.run(["taskkill", "/F", "/IM", "dbeaver.exe"], capture_output=True)


def dbeaver_win():
    wins = [w for w in gw.getAllWindows() if w.title.startswith("DBeaver 2")]
    if not wins:
        raise RuntimeError("DBeaver main window not found")
    w = max(wins, key=lambda x: x.width * x.height)
    w.restore()
    time.sleep(0.2)
    try:
        w.activate()
    except Exception:
        pass
    time.sleep(0.4)
    if not w.isMaximized:
        w.maximize()
    time.sleep(0.5)
    return w


def capture_dbeaver(name: str) -> Path:
    w = dbeaver_win()
    path = OUT / name
    bbox = {
        "left": max(w.left, 0),
        "top": max(w.top, 0),
        "width": w.width,
        "height": w.height,
    }
    with mss.MSS() as sct:
        shot = sct.grab(bbox)
        mss.tools.to_png(shot.rgb, shot.size, output=str(path))
    print("saved", path, "from", w.title)
    return path


def finish_wizard_if_any() -> None:
    for _ in range(10):
        wiz = [w for w in gw.getAllWindows() if "Product Configuration" in w.title]
        if not wiz:
            return
        w = wiz[0]
        pyautogui.click(w.left + w.width - 100, w.top + w.height - 45)
        time.sleep(0.7)
    wiz = [w for w in gw.getAllWindows() if "Product Configuration" in w.title]
    if wiz:
        w = wiz[0]
        pyautogui.click(w.left + w.width - 195, w.top + w.height - 45)


def patch_datasources() -> None:
    data = json.loads(DS_JSON.read_text(encoding="utf-8"))
    data["connections"]["products-orders-hw"] = {
        "provider": "sqlite",
        "driver": "sqlite_jdbc",
        "name": "products_orders (homework)",
        "save-password": True,
        "configuration": {
            "database": str(DB),
            "url": f"jdbc:sqlite:{DB}",
            "configurationType": "MANUAL",
            "type": "dev",
        },
    }
    DS_JSON.write_text(json.dumps(data, indent="\t", ensure_ascii=False), encoding="utf-8")


def dismiss_dialogs() -> None:
    for w in gw.getAllWindows():
        if w.title in ("Go to object",) or "Переход к" in w.title:
            pyautogui.click(w.left + w.width // 2, w.top + w.height - 35)


def open_sql_editor_with_connection() -> None:
    dbeaver_win()
    dismiss_dialogs()
    # Database -> SQL Editor (RU: База данных -> Редактор SQL)
    pyautogui.hotkey("alt", "b")
    time.sleep(0.4)
    pyautogui.press("e")
    time.sleep(1.5)
    # Choose connection dialog: type homew
    pyautogui.write("products_orders", interval=0.05)
    time.sleep(0.5)
    pyautogui.press("enter")
    time.sleep(1)


def exec_sql(sql: str) -> None:
    pyautogui.hotkey("ctrl", "a")
    time.sleep(0.15)
    pyautogui.typewrite(sql, interval=0.008) if sql.isascii() else pyautogui.write(sql)
    time.sleep(0.3)
    pyautogui.hotkey("ctrl", "enter")
    time.sleep(2.2)


def open_table_data() -> None:
    dbeaver_win()
    # Navigator: Ctrl+Shift+N then search table
    pyautogui.hotkey("ctrl", "f7")  # Database search / sometimes map
    time.sleep(0.3)
    pyautogui.hotkey("ctrl", "shift", "d")
    time.sleep(0.5)


def main() -> None:
    if not DB.exists():
        subprocess.check_call(["python", str(ROOT / "code" / "seed.py")])
    OUT.mkdir(exist_ok=True)
    patch_datasources()

    kill_dbeaver()
    time.sleep(1)
    subprocess.Popen([str(EXE), "-nosplash"])
    time.sleep(12)
    finish_wizard_if_any()
    time.sleep(2)

    # Connect: F3 on navigator item — try context menu at fixed offset from left
    w = dbeaver_win()
    pyautogui.click(w.left + 120, w.top + 180, button="right")
    time.sleep(0.5)
    pyautogui.press("down", presses=3, interval=0.1)
    pyautogui.press("enter")
    time.sleep(2)
    capture_dbeaver("01_navigator_connected.png")

    open_sql_editor_with_connection()

    queries = [
        ("02_join_orders.png", "SELECT o.id, p.sku, p.name, ROUND(o.quantity*p.price,2) AS line_total FROM orders o JOIN products p ON p.id=o.product_id ORDER BY o.order_date DESC LIMIT 12"),
        ("03_aggregate_category.png", "SELECT category, COUNT(*) AS cnt, ROUND(AVG(price),2) AS avg_price FROM products GROUP BY category HAVING COUNT(*)>5"),
        ("04_like_abc.png", "SELECT id, sku, name FROM products WHERE UPPER(name) LIKE 'ABC%'"),
        ("05_top_price.png", "SELECT sku, name, price FROM products WHERE category='electronics' ORDER BY price DESC LIMIT 10"),
    ]
    for fname, sql in queries:
        exec_sql(sql + ";")
        capture_dbeaver(fname)

    # ER/diagram: open products table properties
    dbeaver_win()
    pyautogui.click(w.left + 150, w.top + 260, clicks=2, interval=0.2)
    time.sleep(1.5)
    capture_dbeaver("06_tables_data_products.png")

    print("Done")


if __name__ == "__main__":
    main()