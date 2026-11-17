#!/usr/bin/env python3
"""Render a simple ER diagram to erd.png (no extra deps beyond Pillow)."""
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    raise SystemExit("Install Pillow: pip install pillow")

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "erd.png"

TABLES = [
    ("members", ["id PK", "email UNIQUE", "birth_date CHECK age>=14"]),
    ("trainers", ["id PK", "email UNIQUE"]),
    ("membership_types", ["id PK", "price CHECK>0"]),
    ("memberships", ["id PK", "member_id FK", "membership_type_id FK"]),
    ("classes", ["id PK", "trainer_id FK", "capacity CHECK>0"]),
    ("class_enrollments", ["id PK", "member_id FK", "class_id FK"]),
    ("visits", ["id PK", "member_id FK", "class_id FK"]),
    ("payments", ["id PK", "member_id FK", "membership_id FK"]),
]

EDGES = [
    ("trainers", "classes", "1:N"),
    ("members", "memberships", "1:N"),
    ("membership_types", "memberships", "1:N"),
    ("members", "class_enrollments", "1:N"),
    ("classes", "class_enrollments", "1:N"),
    ("members", "visits", "1:N"),
    ("classes", "visits", "1:N"),
    ("members", "payments", "1:N"),
    ("memberships", "payments", "1:N"),
]


def main() -> None:
    w, h = 1400, 900
    img = Image.new("RGB", (w, h), "#F0F4FF")
    draw = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype("arial.ttf", 16)
        font_sm = ImageFont.truetype("arial.ttf", 13)
        font_title = ImageFont.truetype("arial.ttf", 22)
    except OSError:
        font = font_sm = font_title = ImageFont.load_default()

    draw.text((40, 20), "Sports Club — ER diagram (SQLite)", fill="#1C1638", font=font_title)

    positions = {
        "membership_types": (80, 120),
        "members": (80, 320),
        "memberships": (380, 220),
        "trainers": (780, 120),
        "classes": (780, 320),
        "class_enrollments": (1050, 420),
        "visits": (380, 520),
        "payments": (80, 620),
    }
    box_w, line_h = 260, 22

    for name, cols in TABLES:
        x, y = positions[name]
        box_h = 36 + len(cols) * line_h
        draw.rectangle([x, y, x + box_w, y + box_h], fill="white", outline="#009AC8", width=2)
        draw.text((x + 8, y + 6), name, fill="#1C1638", font=font)
        for i, col in enumerate(cols):
            draw.text((x + 12, y + 32 + i * line_h), col, fill="#303030", font=font_sm)

    for a, b, label in EDGES:
        x1, y1 = positions[a]
        x2, y2 = positions[b]
        draw.line(
            (x1 + box_w // 2, y1 + 40, x2 + box_w // 2, y2 + 40),
            fill="#4C52A3",
            width=2,
        )
        mx, my = (x1 + x2) // 2 + box_w // 2, (y1 + y2) // 2 + 30
        draw.text((mx, my), label, fill="#4C52A3", font=font_sm)

    img.save(OUT)
    print(f"Wrote {OUT}")


if __name__ == "__main__":
    main()