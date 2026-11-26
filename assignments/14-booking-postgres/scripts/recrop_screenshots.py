"""Обрезка скриншотов до окна приложения (по заголовку)."""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

import mss
import mss.tools
from pywinauto import Desktop

ROOT = Path(__file__).resolve().parents[1]
SHOTS = ROOT / "screenshots"
PY = ROOT / "venv" / "Scripts" / "python.exe"


def capture_window_title_contains(
    substring: str,
    out: Path,
    *,
    timeout: float = 30.0,
) -> None:
    deadline = time.time() + timeout
    while time.time() < deadline:
        for win in Desktop(backend="uia").windows():
            title = win.window_text() or ""
            if substring in title and win.is_visible():
                r = win.rectangle()
                w = max(1, r.width())
                h = max(1, r.height())
                with mss.MSS() as sct:
                    shot = sct.grab(
                        {
                            "left": r.left,
                            "top": r.top,
                            "width": w,
                            "height": h,
                        }
                    )
                    mss.tools.to_png(shot.rgb, shot.size, output=str(out))
                print(f"OK {out.name} ← «{title}» {w}x{h}")
                return
        time.sleep(0.3)
    raise RuntimeError(f"Окно с «{substring}» не найдено за {timeout}s")


def main() -> None:
    procs: list[subprocess.Popen] = []

    procs.append(
        subprocess.Popen(
            [
                "cmd.exe",
                "/k",
                f"title BOOKINGS_CLI && {PY} main.py bookings",
            ],
            cwd=ROOT,
            creationflags=subprocess.CREATE_NEW_CONSOLE,
        )
    )
    time.sleep(2)
    capture_window_title_contains(
        "BOOKINGS_CLI",
        SHOTS / "02_bookings_list.png",
    )

    procs.append(
        subprocess.Popen(
            [str(PY), "app.py"],
            cwd=ROOT,
            creationflags=subprocess.CREATE_NEW_CONSOLE,
        )
    )
    time.sleep(2.5)
    capture_window_title_contains(
        "Бронирование столиков",
        SHOTS / "03_gui_or_cli.png",
    )

    for p in procs:
        try:
            p.terminate()
        except Exception:
            pass
    print("Готово.")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(exc, file=sys.stderr)
        sys.exit(1)