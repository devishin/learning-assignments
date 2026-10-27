"""Run homework demo for both projects."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def run(cwd: Path, args: list[str]) -> None:
    print(f"\n>>> {' '.join(args)} (cwd={cwd.name})")
    subprocess.run([sys.executable, *args], cwd=cwd, check=True)


def main() -> None:
    reminder = ROOT / "02-reminder-app"
    passwords = ROOT / "03-password-manager"

    run(reminder, ["-m", "pip", "install", "-r", "requirements.txt", "pillow"])
    run(passwords, ["-m", "pip", "install", "-r", "requirements.txt"])

    run(reminder, ["seed_demo.py"])
    run(reminder, ["capture_screenshot.py"])
    run(reminder, ["capture_fired_reminder.py"])
    run(passwords, ["capture_real_screenshots.py"])

    print("\nDemo data prepared. Launch manually:")
    print(f"  cd {reminder}")
    print("  python main.py")
    print(f"  cd {passwords}")
    print("  python password_manager.py menu")


if __name__ == "__main__":
    main()
