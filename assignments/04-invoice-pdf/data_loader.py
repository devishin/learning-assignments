"""Load invoice data from CSV and JSON files."""

from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

import pandas as pd


def list_data_files(data_dir: Path) -> list[Path]:
    files: list[Path] = []
    for pattern in ("*.csv", "*.json"):
        files.extend(sorted(data_dir.glob(pattern)))
    return files


def _normalize_invoice(raw: dict[str, Any]) -> dict[str, Any]:
    invoice_id = raw.get("invoice_id") or raw.get("id") or raw.get("invoiceId")
    if not invoice_id:
        raise ValueError("Не найден invoice_id в записи.")

    items = raw.get("items")
    if items is None:
        items = [
            {
                "description": raw.get("item_description") or raw.get("description") or "",
                "quantity": float(raw.get("quantity") or 1),
                "price": float(raw.get("price") or 0),
            }
        ]

    total = raw.get("total")
    if total is None:
        total = sum(float(item["quantity"]) * float(item["price"]) for item in items)

    return {
        "invoice_id": str(invoice_id),
        "customer_name": str(raw.get("customer_name") or raw.get("customer") or "—"),
        "date": str(raw.get("date") or "—"),
        "items": items,
        "total": float(total),
    }


def load_invoices_from_csv(path: Path) -> list[dict[str, Any]]:
    df = pd.read_csv(path)
    records = df.to_dict(orient="records")
    return [_normalize_invoice(record) for record in records]


def load_invoices_from_json(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, dict):
        payload = payload.get("invoices") or payload.get("data") or [payload]
    if not isinstance(payload, list):
        raise ValueError("JSON должен содержать список счетов.")
    return [_normalize_invoice(item) for item in payload]


def load_invoices(path: Path) -> list[dict[str, Any]]:
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return load_invoices_from_csv(path)
    if suffix == ".json":
        return load_invoices_from_json(path)
    raise ValueError(f"Неподдерживаемый формат: {path.name}")
