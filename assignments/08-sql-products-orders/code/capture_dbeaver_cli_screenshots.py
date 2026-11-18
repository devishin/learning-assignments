#!/usr/bin/env python3
"""Real DBeaver screenshots: CLI open SQL + Ctrl+Enter + mss window capture."""
from __future__ import annotations

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
CON = f"driver=sqlite|database={DB}|name=products_orders_hw"

pyautogui.FAILSAFE = False

SHOTS = [
    ("sql/shot_join.sql", "02_join_orders.png"),
    ("sql/shot_agg.sql", "03_aggregate_category.png"),
    ("sql/shot_like.sql", "04_like_abc.png"),
    ("sql/shot_top.sql", "05_top_price.png"),
]


def dbeaver_window():
    wins = [w for w in gw.getAllWindows() if w.title.startswith("DBeaver")]
    if not wins:
        raise RuntimeError("DBeaver not running")
    w = max(wins, key=lambda t: t.width * t.height)
    w.maximize()
    try:
        w.activate()
    except Exception:
        pass
    time.sleep(0.6)
    return w


def capture(name: str) -> None:
    w = dbeaver_window()
    with mss.MSS() as sct:
        shot = sct.grab({"left": w.left, "top": w.top, "width": w.width, "height": w.height})
        mss.tools.to_png(shot.rgb, shot.size, output=str(OUT / name))


def run_one(sql_rel: str, png: str) -> None:
    subprocess.run(["taskkill", "/F", "/IM", "dbeaver.exe"], capture_output=True)
    time.sleep(2)
    subprocess.Popen([str(EXE), "-nosplash", "-f", str(ROOT / sql_rel), "-con", CON])
    time.sleep(16)
    pyautogui.hotkey("ctrl", "enter")
    time.sleep(2.5)
    capture(png)
    print(png)


def main() -> None:
    if not DB.exists():
        subprocess.check_call(["python", str(ROOT / "code" / "seed.py")])
    OUT.mkdir(parents=True, exist_ok=True)
    for sql, png in SHOTS:
        run_one(sql, png)
    subprocess.run(["taskkill", "/F", "/IM", "dbeaver.exe"], capture_output=True)
    time.sleep(1)
    subprocess.Popen([str(EXE), "-nosplash", "-con", CON])
    time.sleep(12)
    w = dbeaver_window()
    pyautogui.click(w.left + 95, w.top + 205)
    time.sleep(0.4)
    capture("01_tables_structure.png")
    print("01_tables_structure.png")


if __name__ == "__main__":
    main()