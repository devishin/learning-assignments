# CLI менеджер паролей

Приложение хранит логины и зашифрованные пароли в SQLite3. Мастер-пароль сохраняется как SHA-256 хеш.

## Установка

```powershell
cd D:\learning-assignments\assignments\03-password-manager
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Первый запуск

При первом запуске программа попросит задать мастер-пароль:

```powershell
python password_manager.py list
```

## Команды

```powershell
python password_manager.py add Gmail user@gmail.com --generate --length 16
python password_manager.py list
python password_manager.py get Gmail --copy
python password_manager.py new --length 16 --copy
python password_manager.py delete Gmail
python password_manager.py menu
```

`new` только генерирует пароль (не сохраняет). Чтобы сохранить и увидеть пароль в приложении: `add ... --generate`, затем `get <название>`. Команда `list` пароли не показывает.

## Копирование пароля

- флаг `--copy` для команд `get` и `new`;
- в интерактивном меню команда `get` копирует пароль автоматически (если установлен `pyperclip`).

## Файлы

- `passwords.db` — база SQLite;
- `.key` — ключ Fernet для шифования паролей (создаётся автоматически).

## Демонстрация для сдачи

Смотрите файл [`DEMO.md`](DEMO.md).

**Мастер-пароль после `seed_demo.py`:** `StudyDemo123!`

```powershell
python capture_real_screenshots.py
```

## Особенности

- пароли в БД хранятся только в зашифрованном виде;
- мастер-пароль не хранится в открытом виде, только хеш SHA-256;
- генератор паролей поддерживает длину до 64 символов.
