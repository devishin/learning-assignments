"""Снять 3 скриншота для сдачи (mss + subprocess)."""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

try:
    import mss
    import mss.tools
except ImportError:
    subprocess.check_call(
        [sys.executable, "-m", "pip", "install", "mss"],
    )
    import mss
    import mss.tools

ROOT = Path(__file__).resolve().parents[1]
SHOTS = ROOT / "screenshots"


def grab(path: Path, delay: float = 1.0) -> None:
    time.sleep(delay)
    with mss.mss() as sct:
        shot = sct.grab(sct.monitors[1])
        mss.tools.to_png(shot.rgb, shot.size, output=str(path))
    print("saved", path.name)


def main() -> None:
    SHOTS.mkdir(parents=True, exist_ok=True)
    py = ROOT / "venv" / "Scripts" / "python.exe"
    if not py.is_file():
        py = Path(sys.executable)

    # 2 — список бронирований в консоли
    proc = subprocess.Popen(
        ["cmd.exe", "/k", str(py), "main.py", "bookings"],
        cwd=ROOT,
        creationflags=subprocess.CREATE_NEW_CONSOLE,
    )
    grab(SHOTS / "02_bookings_list.png", 3.0)
    proc.terminate()

    # 3 — GUI
    gui = subprocess.Popen(
        [str(py), "app.py"],
        cwd=ROOT,
        creationflags=subprocess.CREATE_NEW_CONSOLE,
    )
    grab(SHOTS / "03_gui_or_cli.png", 4.0)
    gui.terminate()

    print("Готово: 02 и 03. Снимок 01 — вручную в pgAdmin (см. README).")


if __name__ == "__main__":
    main()