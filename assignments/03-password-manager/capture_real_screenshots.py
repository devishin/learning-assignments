"""Capture real Windows terminal screenshots for password manager demo."""

from __future__ import annotations

import ctypes
import subprocess
import time
from ctypes import wintypes
from dataclasses import dataclass
from pathlib import Path

import mss

from demo_constants import MASTER_PASSWORD

BASE = Path(__file__).resolve().parent
SCREENSHOTS = BASE / "screenshots"
SW_RESTORE = 9

user32 = ctypes.windll.user32


@dataclass(frozen=True)
class Stage:
    filename: str
    window_title: str
    commands: str
    wait_seconds: float = 3.0
    console_lines: int = 40


def reset_for_demo() -> None:
    """Reset demo data even if DB file is locked by another process."""
    import sqlite3

    db_path = BASE / "passwords.db"
    key_path = BASE / ".key"

    for path in (db_path, key_path):
        if path.exists():
            try:
                path.unlink()
            except PermissionError:
                pass

    if db_path.exists():
        connection = sqlite3.connect(db_path)
        connection.execute("DELETE FROM passwords")
        connection.execute("DELETE FROM master_password")
        connection.commit()
        connection.close()

    if key_path.exists():
        try:
            key_path.unlink()
        except PermissionError:
            pass


def is_fresh_master() -> bool:
    import sqlite3

    db_path = BASE / "passwords.db"
    if not db_path.exists():
        return True
    connection = sqlite3.connect(db_path)
    row = connection.execute("SELECT 1 FROM master_password WHERE id = 1").fetchone()
    connection.close()
    return row is None


def _build_stages(*, fresh_db: bool) -> list[Stage]:
    master = MASTER_PASSWORD
    mp = f"--master-password {master}"

    if fresh_db:
        login_commands = (
            "echo === Этап 1: вход / установка мастер-пароля ===\r\n"
            "set PM_DEMO_STDIN=1\r\n"
            "echo python password_manager.py list\r\n"
            f"(echo {master}& echo {master}& echo {master}) | python password_manager.py list\r\n"
        )
    else:
        login_commands = (
            "echo === Этап 1: вход с мастер-паролем ===\r\n"
            "set PM_DEMO_STDIN=1\r\n"
            "echo python password_manager.py list\r\n"
            f"(echo {master}) | python password_manager.py list\r\n"
        )

    return [
        Stage(
            filename="01_master_password_login.png",
            window_title="PM-DEMO-01",
            commands=login_commands + "echo.\r\n" + "timeout /t 5 >nul\r\n",
        ),
        Stage(
            filename="02_first_account_generated.png",
            window_title="PM-DEMO-02",
            commands=(
                "echo === Этап 2: первая учётка с генерацией пароля ===\r\n"
                f"echo python password_manager.py {mp} add Gmail user@gmail.com --generate --length 16\r\n"
                f"python password_manager.py {mp} add Gmail user@gmail.com --generate --length 16\r\n"
                "echo.\r\n"
                "timeout /t 5 >nul\r\n"
            ),
        ),
        Stage(
            filename="03_two_accounts_passwords.png",
            window_title="PM-DEMO-03",
            commands=(
                "echo === Этап 3: вторая учётка + 2 пароля ===\r\n"
                f"echo python password_manager.py {mp} add Telegram devishin --generate --length 16\r\n"
                f"python password_manager.py {mp} add Telegram devishin --generate --length 16\r\n"
                "echo.\r\n"
                f"echo python password_manager.py {mp} list\r\n"
                f"python password_manager.py {mp} list\r\n"
                "echo.\r\n"
                f"echo python password_manager.py {mp} get Gmail\r\n"
                f"python password_manager.py {mp} get Gmail\r\n"
                "echo.\r\n"
                f"echo python password_manager.py {mp} get Telegram\r\n"
                f"python password_manager.py {mp} get Telegram\r\n"
                "echo.\r\n"
                "timeout /t 6 >nul\r\n"
            ),
            wait_seconds=4.5,
            console_lines=52,
        ),
    ]


def _find_window(title: str) -> int | None:
    matches: list[int] = []

    @ctypes.WINFUNCTYPE(wintypes.BOOL, wintypes.HWND, wintypes.LPARAM)
    def callback(hwnd: int, _lparam: int) -> bool:
        if not user32.IsWindowVisible(hwnd):
            return True
        length = user32.GetWindowTextLengthW(hwnd)
        if length == 0:
            return True
        buffer = ctypes.create_unicode_buffer(length + 1)
        user32.GetWindowTextW(hwnd, buffer, length + 1)
        if title in buffer.value:
            matches.append(hwnd)
        return True

    user32.EnumWindows(callback, 0)
    return matches[-1] if matches else None


def _capture_window(hwnd: int, output_path: Path) -> None:
    user32.ShowWindow(hwnd, SW_RESTORE)
    user32.SetForegroundWindow(hwnd)
    time.sleep(0.4)

    rect = wintypes.RECT()
    user32.GetWindowRect(hwnd, ctypes.byref(rect))
    monitor = {
        "left": rect.left,
        "top": rect.top,
        "width": max(1, rect.right - rect.left),
        "height": max(1, rect.bottom - rect.top),
    }

    with mss.MSS() as grabber:
        shot = grabber.grab(monitor)
        mss.tools.to_png(shot.rgb, shot.size, output=str(output_path))


def _run_stage(stage: Stage, output_path: Path) -> None:
    bat_path = SCREENSHOTS / "_tmp_demo.bat"
    bat_path.write_text(
        "@echo off\r\n"
        "chcp 65001 >nul\r\n"
        f"cd /d \"{BASE}\"\r\n"
        f"mode con: cols=132 lines={stage.console_lines}\r\n"
        + stage.commands,
        encoding="utf-8",
    )
    launch = f'start "{stage.window_title}" cmd.exe /k "{bat_path}"'
    process = subprocess.Popen(launch, shell=True)
    deadline = time.time() + 25
    hwnd = None
    while time.time() < deadline:
        hwnd = _find_window(stage.window_title)
        if hwnd:
            break
        time.sleep(0.25)

    if hwnd is None:
        raise RuntimeError(f"Не найдено окно терминала: {stage.window_title}")

    time.sleep(stage.wait_seconds)
    _capture_window(hwnd, output_path)
    user32.PostMessageW(hwnd, 0x0010, 0, 0)
    process.wait(timeout=5)
    time.sleep(0.8)
    if bat_path.exists():
        bat_path.unlink()


def _remove_legacy_screenshots() -> None:
    legacy = (
        "01_first_run_master_password.png",
        "02_generate_password.png",
        "03_add_records.png",
        "04_list_records.png",
        "05_get_password_copy.png",
    )
    for name in legacy:
        path = SCREENSHOTS / name
        if path.exists():
            path.unlink()


def main() -> None:
    SCREENSHOTS.mkdir(parents=True, exist_ok=True)
    _remove_legacy_screenshots()
    reset_for_demo()
    fresh_db = is_fresh_master()

    for stage in _build_stages(fresh_db=fresh_db):
        output = SCREENSHOTS / stage.filename
        _run_stage(stage, output)
        print(f"Saved: {output}")


if __name__ == "__main__":
    main()
