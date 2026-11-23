"""Публичный API задания и точка входа."""

from __future__ import annotations

from api_client import CurrencyApiError, get_currency_rates
from cli import main as run_cli
from storage import read_from_file, save_to_file

__all__ = [
    "CurrencyApiError",
    "get_currency_rates",
    "save_to_file",
    "read_from_file",
    "run_cli",
]

if __name__ == "__main__":
    run_cli()