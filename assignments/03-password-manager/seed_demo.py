"""Seed demo passwords for homework (non-interactive)."""

from __future__ import annotations

from pathlib import Path

from demo_constants import MASTER_PASSWORD
from password_manager import PasswordGenerator, PasswordManagerApp

BASE = Path(__file__).resolve().parent
DB_PATH = BASE / "passwords.db"
KEY_PATH = BASE / ".key"


def main() -> None:
    for path in (DB_PATH, KEY_PATH):
        if path.exists():
            try:
                path.unlink()
            except PermissionError:
                print(f"Не удалось удалить {path.name}: файл занят. Закройте password_manager.py и повторите.")
                return

    app = PasswordManagerApp(str(DB_PATH), str(KEY_PATH))
    app.db.set_master_password(MASTER_PASSWORD)
    app.add_password("Gmail", "user@gmail.com", PasswordGenerator(length=16).generate(), reveal=True)
    app.add_password("Telegram", "devishin", PasswordGenerator(length=16).generate(), reveal=True)
    print("Созданы записи Gmail и Telegram.")
    print(f"Мастер-пароль для демо: {MASTER_PASSWORD}")


if __name__ == "__main__":
    main()
