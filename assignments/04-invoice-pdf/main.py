"""CLI menu for invoice PDF generation."""

from __future__ import annotations

from pathlib import Path

from data_loader import list_data_files, load_invoices
from pdf_service import html_to_pdf, list_templates, render_invoice_html
from platform_utils import open_pdf

BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
TEMPLATES_DIR = BASE_DIR / "templates"
OUTPUT_DIR = BASE_DIR / "output"


def print_header(title: str) -> None:
    print("\n" + "=" * 60)
    print(title)
    print("=" * 60)


def choose_from_list(title: str, options: list[Path]) -> Path:
    if not options:
        raise RuntimeError(f"Нет доступных вариантов: {title}")

    print_header(title)
    for index, option in enumerate(options, start=1):
        print(f"  {index}. {option.name}")
    print("  0. Выход")

    while True:
        raw = input("Выберите номер: ").strip()
        if raw == "0":
            raise SystemExit("Завершение работы.")
        if not raw.isdigit():
            print("Введите число из списка.")
            continue
        choice = int(raw)
        if 1 <= choice <= len(options):
            return options[choice - 1]
        print("Некорректный номер.")


def choose_invoice_id(invoices: list[dict]) -> str:
    ids = [invoice["invoice_id"] for invoice in invoices]
    print_header("Доступные счета (invoice id)")
    for index, invoice_id in enumerate(ids, start=1):
        print(f"  {index}. {invoice_id}")
    print("  0. Назад")

    while True:
        raw = input("Выберите номер счета: ").strip()
        if raw == "0":
            raise SystemExit("Завершение работы.")
        if not raw.isdigit():
            print("Введите число из списка.")
            continue
        choice = int(raw)
        if 1 <= choice <= len(ids):
            return ids[choice - 1]
        print("Некорректный номер.")


def show_startup_lists() -> None:
    data_files = list_data_files(DATA_DIR)
    templates = list_templates(TEMPLATES_DIR)

    print_header("Доступные файлы данных (/data)")
    if not data_files:
        print("  (пусто)")
    for index, path in enumerate(data_files, start=1):
        print(f"  {index}. {path.name}")

    print_header("Доступные HTML-шаблоны (/templates)")
    if not templates:
        print("  (пусто)")
    for index, path in enumerate(templates, start=1):
        print(f"  {index}. {path.name}")


def main() -> None:
    show_startup_lists()

    data_files = list_data_files(DATA_DIR)
    templates = list_templates(TEMPLATES_DIR)
    if not data_files:
        raise SystemExit("В папке data нет CSV/JSON файлов.")
    if not templates:
        raise SystemExit("В папке templates нет HTML-шаблонов.")

    data_file = choose_from_list("Выбор файла данных", data_files)
    template_file = choose_from_list("Выбор HTML-шаблона", templates)

    invoices = load_invoices(data_file)
    invoice_id = choose_invoice_id(invoices)
    invoice = next(item for item in invoices if item["invoice_id"] == invoice_id)

    html = render_invoice_html(template_file, invoice)
    output_path = OUTPUT_DIR / f"{invoice_id}.pdf"
    try:
        html_to_pdf(html, template_file, output_path, BASE_DIR)
    except RuntimeError as exc:
        raise SystemExit(str(exc)) from exc

    print_header("Готово")
    print(f"PDF сохранён: {output_path}")
    open_pdf(output_path)
    print("PDF открыт в системной программе.")


if __name__ == "__main__":
    main()
