"""Telegram-бот для хранения задач (aiogram + SQLite)."""

import asyncio
import csv
import logging
import tempfile
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.filters import Command, CommandObject
from aiogram.types import BotCommand, ErrorEvent, FSInputFile, Message

from config import BOT_TOKEN, DB_PATH, TELEGRAM_PROXY, check_token
from database import add_task, get_connection, init_db, list_tasks

# Глобальное соединение с БД на время работы бота
db = get_connection(DB_PATH)


def format_task_list(rows: list) -> str:
    """Собираем текст для команды /list."""
    if not rows:
        return "Задач пока нет. Добавьте: /add купить молоко"
    lines = ["Ваши задачи (по порядку добавления):", ""]
    for row in rows:
        extra = ""
        if row["status"] or row["category"]:
            extra = f" [{row['status']}|{row['category']}]"
        lines.append(f"{row['id']}. {row['text']}{extra}")
    return "\n".join(lines)


def build_csv_file(rows: list, path: Path) -> None:
    """Пишем CSV с BOM, чтобы Excel корректно открыл кириллицу."""
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle, delimiter=";")
        writer.writerow(["id", "text", "user", "created_at", "status", "category"])
        for row in rows:
            writer.writerow(
                [
                    row["id"],
                    row["text"],
                    row["user"],
                    row["created_at"],
                    row["status"],
                    row["category"],
                ]
            )


async def cmd_start(message: Message, bot: Bot) -> None:
    """Команда /start — приветствие."""
    me = await bot.me()
    bot_label = f"@{me.username}" if me.username else "этот бот"
    name = message.from_user.first_name if message.from_user else "друг"
    await message.answer(
        f"Привет, {name}!\n\n"
        f"Это {bot_label} — бот списка задач (учебный проект 06).\n"
        "Команды:\n"
        "/add текст — новая задача\n"
        "/list — список\n"
        "/list_csv — выгрузка в CSV"
    )


async def cmd_add(message: Message, command: CommandObject) -> None:
    """Команда /add — добавление задачи (текст после команды)."""
    if not message.from_user:
        return
    text = (command.args or "").strip()
    if not text:
        await message.answer("Напишите задачу после команды.\nПример: /add сделать лабораторную")
        return
    task_id = add_task(db, message.from_user.id, text)
    await message.answer(f"Задача #{task_id} сохранена.")


async def cmd_list(message: Message) -> None:
    """Команда /list — показать все задачи пользователя."""
    if not message.from_user:
        return
    rows = list_tasks(db, message.from_user.id)
    await message.answer(format_task_list(rows))


async def cmd_list_csv(message: Message) -> None:
    """Команда /list_csv — отправить файл CSV в чат."""
    if not message.from_user:
        return
    rows = list_tasks(db, message.from_user.id)
    if not rows:
        await message.answer("Нет задач для выгрузки.")
        return

    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".csv", delete=False, encoding="utf-8-sig"
    ) as tmp:
        tmp_path = Path(tmp.name)
    build_csv_file(rows, tmp_path)

    document = FSInputFile(tmp_path, filename="tasks.csv")
    await message.answer_document(document, caption="Выгрузка задач (откройте в Excel)")
    tmp_path.unlink(missing_ok=True)


def create_bot() -> Bot:
    """Создаёт Bot; при TELEGRAM_PROXY в .env ходит в Telegram через прокси."""
    if TELEGRAM_PROXY:
        session = AiohttpSession(proxy=TELEGRAM_PROXY)
        return Bot(token=BOT_TOKEN, session=session)
    return Bot(token=BOT_TOKEN)


async def on_handler_error(event: ErrorEvent) -> None:
    logging.exception("Ошибка обработчика: %s", event.exception)
    update = event.update
    if update.message:
        await update.message.answer(
            "Не удалось выполнить команду. Посмотрите traceback в консоли, где запущен bot.py."
        )


async def main() -> None:
    """Точка входа: регистрация команд и запуск polling."""
    check_token()
    init_db(db)

    bot = create_bot()
    dp = Dispatcher()
    dp.errors.register(on_handler_error)
    # list_csv раньше list; ignore_mention — команды с чужим @ботом в группе
    def cmd(name: str) -> Command:
        return Command(name, ignore_mention=True)

    dp.message.register(cmd_start, cmd("start"))
    dp.message.register(cmd_add, cmd("add"))
    dp.message.register(cmd_list_csv, cmd("list_csv"))
    dp.message.register(cmd_list, cmd("list"))

    me = await bot.get_me()
    await bot.set_my_commands(
        [
            BotCommand(command="start", description="Приветствие"),
            BotCommand(command="add", description="Добавить задачу"),
            BotCommand(command="list", description="Список задач"),
            BotCommand(command="list_csv", description="Скачать CSV"),
        ]
    )
    if TELEGRAM_PROXY:
        print(f"Прокси для Telegram: {TELEGRAM_PROXY}")
    username = f"@{me.username}" if me.username else f"id={me.id}"
    print(f"Бот {username} слушает команды. В Telegram откройте именно {username}")
    print(f"База задач: {DB_PATH}")
    print("Остановка: Ctrl+C")
    await dp.start_polling(bot, drop_pending_updates=True)


if __name__ == "__main__":
    asyncio.run(main())
