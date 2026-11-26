"""Добавить сервер booking-docker в pgAdmin и снять скриншот."""

from __future__ import annotations

import time
from pathlib import Path

import mss
import mss.tools
from pywinauto import Application, Desktop
from pywinauto.keyboard import send_keys

ROOT = Path(__file__).resolve().parents[1]
SHOT = ROOT / "screenshots" / "01_pgadmin_tables.png"


def screenshot() -> None:
    time.sleep(1)
    with mss.MSS() as sct:
        shot = sct.grab(sct.monitors[1])
        mss.tools.to_png(shot.rgb, shot.size, output=str(SHOT))
    print("saved", SHOT)


def main() -> None:
    app = Application(backend="uia").connect(title_re="pgAdmin 4", timeout=30)
    main_win = app.window(title_re="pgAdmin 4")
    main_win.set_focus()
    main_win.child_window(title="Object", control_type="Button").click_input()
    time.sleep(0.5)
    # меню Register -> Server
    for item in Desktop(backend="uia").windows():
        try:
            reg = item.child_window(title="Register", control_type="MenuItem")
            if reg.exists(timeout=1):
                reg.click_input()
                break
        except Exception:
            pass
    time.sleep(0.3)
    Desktop(backend="uia").child_window(title="Server...", control_type="MenuItem").click_input()
    time.sleep(1)
    dlg = Desktop(backend="uia").window(title_re="Register - Server")
    dlg.child_window(title="Name", control_type="Edit").set_edit_text("booking-docker")
    dlg.child_window(title="Connection", control_type="TabItem").click_input()
    edits = dlg.descendants(control_type="Edit")
    # порядок: host, port, maintenance db, username, password
    host, port, maint, user = edits[0], edits[1], edits[2], edits[3]
    host.set_edit_text("localhost")
    port.set_edit_text("5433")
    maint.set_edit_text("booking")
    user.set_edit_text("admin")
    pwd = dlg.child_window(title="Password", control_type="Edit")
    pwd.set_edit_text("BookingDev2026!")
    dlg.child_window(title="Save", control_type="Button").click_input()
    time.sleep(3)
    tree = main_win.child_window(control_type="Tree")
    tree.set_focus()
    send_keys("{DOWN}^o")  # раскрыть booking-docker если сфокусировано
    time.sleep(1)
    # клик по schemas/public/tables/users через поиск
    for _ in range(8):
        send_keys("{RIGHT}")
        time.sleep(0.2)
    send_keys("{DOWN}{DOWN}{DOWN}{DOWN}{RIGHT}")
    time.sleep(1)
    send_keys("{APPS}")  # контекстное меню
    time.sleep(0.5)
    Desktop(backend="uia").child_window(title_re="View/Edit Data", control_type="MenuItem").click_input()
    time.sleep(2)
    screenshot()


if __name__ == "__main__":
    main()