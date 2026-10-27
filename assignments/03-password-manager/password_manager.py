"""CLI password manager with SQLite storage and Fernet encryption."""

from __future__ import annotations

import argparse
import getpass
import hashlib
import os
import secrets
import sqlite3
import string
from pathlib import Path

from cryptography.fernet import Fernet, InvalidToken

try:
    import pyperclip

    CLIPBOARD_AVAILABLE = True
except ImportError:
    CLIPBOARD_AVAILABLE = False


def read_password(prompt: str) -> str:
    if os.environ.get("PM_DEMO_STDIN") == "1":
        print(prompt, end="", flush=True)
        return input().strip()
    return getpass.getpass(prompt)


class DatabaseManager:
    def __init__(self, db_path: str | Path = "passwords.db") -> None:
        self.db_path = Path(db_path)
        self.connection = sqlite3.connect(self.db_path)
        self.connection.row_factory = sqlite3.Row
        self.init_database()

    def init_database(self) -> None:
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS master_password (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                password_hash TEXT NOT NULL
            )
            """
        )
        self.connection.execute(
            """
            CREATE TABLE IF NOT EXISTS passwords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                service_name TEXT NOT NULL UNIQUE,
                login TEXT NOT NULL,
                encrypted_password TEXT NOT NULL
            )
            """
        )
        self.connection.commit()

    @staticmethod
    def _hash_password(password: str) -> str:
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def set_master_password(self, password: str) -> None:
        password_hash = self._hash_password(password)
        self.connection.execute("DELETE FROM master_password")
        self.connection.execute(
            "INSERT INTO master_password (id, password_hash) VALUES (1, ?)",
            (password_hash,),
        )
        self.connection.commit()

    def get_master_password(self) -> str | None:
        row = self.connection.execute("SELECT password_hash FROM master_password WHERE id = 1").fetchone()
        if row is None:
            return None
        return str(row["password_hash"])

    def verify_master_password(self, password: str) -> bool:
        stored = self.get_master_password()
        if stored is None:
            return False
        return secrets.compare_digest(stored, self._hash_password(password))

    def has_master_password(self) -> bool:
        return self.get_master_password() is not None

    def add_password(self, service_name: str, login: str, encrypted_password: str) -> None:
        self.connection.execute(
            """
            INSERT INTO passwords (service_name, login, encrypted_password)
            VALUES (?, ?, ?)
            """,
            (service_name.strip(), login.strip(), encrypted_password),
        )
        self.connection.commit()

    def get_password(self, service_name: str) -> sqlite3.Row | None:
        return self.connection.execute(
            "SELECT * FROM passwords WHERE service_name = ?",
            (service_name.strip(),),
        ).fetchone()

    def list_passwords(self) -> list[sqlite3.Row]:
        return self.connection.execute(
            "SELECT service_name, login FROM passwords ORDER BY service_name"
        ).fetchall()

    def delete_password(self, service_name: str) -> bool:
        cursor = self.connection.execute(
            "DELETE FROM passwords WHERE service_name = ?",
            (service_name.strip(),),
        )
        self.connection.commit()
        return cursor.rowcount > 0


class EncryptionManager:
    def __init__(self, key_path: str | Path = ".key") -> None:
        self.key_path = Path(key_path)
        self.key = self._load_or_create_key()
        self.fernet = Fernet(self.key)

    def _load_or_create_key(self) -> bytes:
        if self.key_path.exists():
            return self.key_path.read_bytes().strip()
        key = Fernet.generate_key()
        self.key_path.write_bytes(key)
        return key

    def encrypt(self, value: str) -> str:
        return self.fernet.encrypt(value.encode("utf-8")).decode("utf-8")

    def decrypt(self, value: str) -> str:
        try:
            return self.fernet.decrypt(value.encode("utf-8")).decode("utf-8")
        except InvalidToken as exc:
            raise ValueError("Не удалось расшифровать пароль. Проверьте файл .key") from exc


class PasswordGenerator:
    def __init__(
        self,
        length: int = 16,
        use_upper: bool = True,
        use_lower: bool = True,
        use_digits: bool = True,
        use_symbols: bool = True,
    ) -> None:
        self.length = max(4, min(length, 64))
        self.use_upper = use_upper
        self.use_lower = use_lower
        self.use_digits = use_digits
        self.use_symbols = use_symbols

    def generate(self) -> str:
        alphabet = ""
        if self.use_upper:
            alphabet += string.ascii_uppercase
        if self.use_lower:
            alphabet += string.ascii_lowercase
        if self.use_digits:
            alphabet += string.digits
        if self.use_symbols:
            alphabet += "!@#$%^&*()-_=+[]{}"
        if not alphabet:
            raise ValueError("Нужно выбрать хотя бы один набор символов.")
        return "".join(secrets.choice(alphabet) for _ in range(self.length))


class PasswordManagerApp:
    def __init__(self, db_path: str = "passwords.db", key_path: str = ".key") -> None:
        self.db = DatabaseManager(db_path)
        self.encryption = EncryptionManager(key_path)

    def setup_master_password(self) -> None:
        if self.db.has_master_password():
            return
        while True:
            password = read_password("Задайте мастер-пароль: ")
            confirm = read_password("Повторите мастер-пароль: ")
            if password != confirm:
                print("Пароли не совпали. Попробуйте снова.")
                continue
            if not password:
                print("Мастер-пароль не может быть пустым.")
                continue
            self.db.set_master_password(password)
            print("Мастер-пароль сохранён.")
            break

    def authenticate(self, master_password: str | None = None) -> bool:
        self.setup_master_password()
        if master_password is not None:
            if self.db.verify_master_password(master_password):
                return True
            print("Неверный мастер-пароль.")
            return False
        for _ in range(3):
            password = read_password("Введите мастер-пароль: ")
            if self.db.verify_master_password(password):
                return True
            print("Неверный пароль.")
        return False

    def add_password(self, service_name: str, login: str, password: str, *, reveal: bool = False) -> None:
        encrypted = self.encryption.encrypt(password)
        self.db.add_password(service_name, login, encrypted)
        print(f"Запись «{service_name}» добавлена.")
        if reveal:
            print(f"Сгенерированный пароль: {password}")
            print(f"Посмотреть снова: get {service_name}")

    def generate_password_interactive(self) -> str:
        length_raw = input("Длина пароля (16): ").strip() or "16"
        use_upper = self._ask_yes_no("Заглавные буквы? (y/n): ", default=True)
        use_lower = self._ask_yes_no("Строчные буквы? (y/n): ", default=True)
        use_digits = self._ask_yes_no("Цифры? (y/n): ", default=True)
        use_symbols = self._ask_yes_no("Спецсимволы? (y/n): ", default=True)
        generator = PasswordGenerator(
            length=int(length_raw),
            use_upper=use_upper,
            use_lower=use_lower,
            use_digits=use_digits,
            use_symbols=use_symbols,
        )
        return generator.generate()

    @staticmethod
    def _ask_yes_no(prompt: str, default: bool) -> bool:
        answer = input(prompt).strip().lower()
        if not answer:
            return default
        return answer in {"y", "yes", "д", "да"}

    def get_password(self, service_name: str, copy_to_clipboard: bool = False) -> None:
        row = self.db.get_password(service_name)
        if row is None:
            print(f"Запись «{service_name}» не найдена.")
            return
        password = self.encryption.decrypt(row["encrypted_password"])
        print(f"Сервис: {row['service_name']}")
        print(f"Логин: {row['login']}")
        print(f"Пароль: {password}")
        if copy_to_clipboard and CLIPBOARD_AVAILABLE:
            pyperclip.copy(password)
            print("Пароль скопирован в буфер обмена.")

    def list_passwords(self) -> None:
        rows = self.db.list_passwords()
        if not rows:
            print("Список пуст.")
            return
        print("Сохранённые записи:")
        for row in rows:
            print(f"- {row['service_name']} | login: {row['login']}")
        print("Пароли в list не показываются. Команда get <название> — показать пароль.")

    def delete_password(self, service_name: str) -> None:
        if self.db.delete_password(service_name):
            print(f"Запись «{service_name}» удалена.")
        else:
            print(f"Запись «{service_name}» не найдена.")

    def show_menu(self) -> None:
        print("\n=== Менеджер паролей ===")
        print("1. add — добавить запись")
        print("2. get — получить пароль")
        print("3. list — список записей")
        print("4. delete — удалить запись")
        print("5. new — сгенерировать пароль")
        print("0. exit — выход")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="CLI менеджер паролей")
    parser.add_argument(
        "--master-password",
        help="Мастер-пароль (удобно для демонстрации в терминале)",
    )
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("list", help="Показать все записи")
    subparsers.add_parser("menu", help="Интерактивное меню")

    add_parser = subparsers.add_parser("add", help="Добавить запись")
    add_parser.add_argument("service_name")
    add_parser.add_argument("login")
    add_parser.add_argument("--password", help="Пароль (если не указан — запрос ввода)")
    add_parser.add_argument(
        "--generate",
        action="store_true",
        help="Сгенерировать пароль, сохранить запись и показать пароль",
    )
    add_parser.add_argument("--length", type=int, default=16, help="Длина пароля для --generate")

    get_parser = subparsers.add_parser("get", help="Получить пароль по названию")
    get_parser.add_argument("service_name")
    get_parser.add_argument("--copy", action="store_true", help="Скопировать пароль в буфер")

    delete_parser = subparsers.add_parser("delete", help="Удалить запись")
    delete_parser.add_argument("service_name")

    new_parser = subparsers.add_parser("new", help="Сгенерировать пароль")
    new_parser.add_argument("--length", type=int, default=16)
    new_parser.add_argument("--copy", action="store_true", help="Скопировать в буфер")

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    app = PasswordManagerApp()

    if not app.authenticate(args.master_password):
        raise SystemExit("Доступ запрещён.")

    if args.command == "list":
        app.list_passwords()
        return
    if args.command == "add":
        if args.generate:
            password = PasswordGenerator(length=args.length).generate()
            app.add_password(args.service_name, args.login, password, reveal=True)
            return
        password = args.password or getpass.getpass("Пароль: ")
        app.add_password(args.service_name, args.login, password)
        return
    if args.command == "get":
        app.get_password(args.service_name, copy_to_clipboard=args.copy)
        return
    if args.command == "delete":
        app.delete_password(args.service_name)
        return
    if args.command == "new":
        generator = PasswordGenerator(length=args.length)
        password = generator.generate()
        print(password)
        if args.copy and CLIPBOARD_AVAILABLE:
            pyperclip.copy(password)
            print("Пароль скопирован в буфер обмена.")
        return
    if args.command == "menu":
        while True:
            app.show_menu()
            choice = input("Команда: ").strip().lower()
            if choice in {"0", "exit"}:
                break
            if choice == "list":
                app.list_passwords()
            elif choice == "add":
                service = input("Название: ").strip()
                login = input("Логин: ").strip()
                if app._ask_yes_no("Сгенерировать пароль автоматически? (y/n): ", default=True):
                    password = app.generate_password_interactive()
                    app.add_password(service, login, password, reveal=True)
                else:
                    password = read_password("Пароль: ")
                    app.add_password(service, login, password)
            elif choice == "get":
                service = input("Название: ").strip()
                app.get_password(service, copy_to_clipboard=True)
            elif choice == "delete":
                service = input("Название: ").strip()
                app.delete_password(service)
            elif choice == "new":
                password = app.generate_password_interactive()
                print(f"Сгенерированный пароль: {password}")
                if CLIPBOARD_AVAILABLE:
                    pyperclip.copy(password)
                    print("Пароль скопирован в буфер обмена.")
            else:
                print("Неизвестная команда.")
        return

    parser.print_help()


if __name__ == "__main__":
    main()
