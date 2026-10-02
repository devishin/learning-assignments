"""Cross-platform helpers."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path


def ensure_gtk_on_path_windows() -> None:
    """WeasyPrint on Windows needs GTK3 Runtime DLLs on PATH."""
    if not sys.platform.startswith("win"):
        return
    candidates = [
        Path(r"C:\Program Files\GTK3-Runtime Win64\bin"),
        Path(r"C:\Program Files (x86)\GTK3-Runtime Win32\bin"),
    ]
    for bin_dir in candidates:
        if not bin_dir.is_dir():
            continue
        path_str = str(bin_dir)
        if path_str not in os.environ.get("PATH", ""):
            os.environ["PATH"] = path_str + os.pathsep + os.environ.get("PATH", "")
        return


def open_pdf(path: Path) -> None:
    if not path.exists():
        raise FileNotFoundError(path)
    if sys.platform.startswith("win"):
        os.startfile(path)  # type: ignore[attr-defined]
        return
    if sys.platform == "darwin":
        subprocess.run(["open", str(path)], check=False)
        return
    subprocess.run(["xdg-open", str(path)], check=False)
