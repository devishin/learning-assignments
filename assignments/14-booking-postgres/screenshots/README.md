# Скриншоты для сдачи

| Файл | Содержание |
|------|------------|
| `01_pgadmin_tables.png` | Таблицы и данные в PostgreSQL (`\dt`, выборка users/tables/bookings) |
| `02_bookings_list.png` | `python main.py bookings` |
| `03_gui_or_cli.png` | Tkinter `app.py`, вкладка «Пользователи» |

Переснять при необходимости:

```powershell
docker compose up -d
python main.py seed
python scripts\capture_screenshots.py
powershell -File scripts\show_tables.ps1
```