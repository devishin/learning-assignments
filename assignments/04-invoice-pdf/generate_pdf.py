"""Итоговое задание: CSV -> HTML -> PDF (WeasyPrint)."""

from __future__ import annotations

import csv
from pathlib import Path

from pdf_service import html_to_pdf, resolve_font_uri
from platform_utils import open_pdf

BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "data" / "products.csv"
TEMPLATE_FILE = BASE_DIR / "templates" / "product_simple.html"
OUTPUT_DIR = BASE_DIR / "output"


def load_products(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        rows = list(reader)
    if len(rows) < 3:
        raise ValueError("В CSV должно быть минимум 3 строки данных.")
    return rows


def render_simple_template(template_path: Path, row: dict[str, str]) -> str:
    price = float(row["price"].replace(",", "."))
    qty = float(row["qty"].replace(",", "."))
    total = price * qty
    context = {
        "product": row["product"],
        "price": f"{price:.2f}",
        "qty": str(int(qty) if qty == int(qty) else qty),
        "total": f"{total:.2f}",
    }
    html = template_path.read_text(encoding="utf-8")
    for key, value in context.items():
        html = html.replace("{{ " + key + " }}", value)
    return html


def choose_row(rows: list[dict[str, str]]) -> dict[str, str]:
    print("\n=== Товары из CSV ===")
    for index, row in enumerate(rows, start=1):
        print(f"  {index}. {row['product']} | цена: {row['price']} | qty: {row['qty']}")
    print("  0. Выход")

    while True:
        raw = input("Выберите строку: ").strip()
        if raw == "0":
            raise SystemExit("Выход.")
        if raw.isdigit() and 1 <= int(raw) <= len(rows):
            return rows[int(raw) - 1]
        print("Некорректный номер.")


def main() -> None:
    if not DATA_FILE.exists():
        raise SystemExit(f"Не найден файл данных: {DATA_FILE}")
    if not TEMPLATE_FILE.exists():
        raise SystemExit(f"Не найден шаблон: {TEMPLATE_FILE}")

    rows = load_products(DATA_FILE)
    print(f"Загружено строк из CSV: {len(rows)}")
    print(f"Шаблон: {TEMPLATE_FILE.name}")
    _ = resolve_font_uri(BASE_DIR)

    row = choose_row(rows)
    html = render_simple_template(TEMPLATE_FILE, row)

    safe_name = row["product"].replace(" ", "_")[:40]
    output_path = OUTPUT_DIR / f"{safe_name}.pdf"

    try:
        html_to_pdf(html, TEMPLATE_FILE, output_path, BASE_DIR)
    except RuntimeError as exc:
        raise SystemExit(str(exc)) from exc

    print(f"\nPDF сохранён: {output_path}")
    open_pdf(output_path)
    print("PDF открыт в системной программе.")


if __name__ == "__main__":
    main()
