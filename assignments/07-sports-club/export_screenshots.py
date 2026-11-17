#!/usr/bin/env python3
"""Export check query results to screenshots/ for README (DBeaver-style evidence)."""
from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parent
SHOTS = ROOT / "screenshots"
SHOTS.mkdir(exist_ok=True)
DB = ROOT / "sports.db"


def format_table(rows, headers):
    widths = [len(h) for h in headers]
    lines = [headers]
    for r in rows:
        lines.append([str(x) if x is not None else "" for x in r])
        for i, cell in enumerate(lines[-1]):
            widths[i] = max(widths[i], len(cell))
    fmt = " | ".join(f"{{:{w}}}" for w in widths)
    out = [fmt.format(*headers), "-+-".join("-" * w for w in widths)]
    for row in lines[1:]:
        out.append(fmt.format(*row))
    return "\n".join(out)


def main():
  con = sqlite3.connect(DB)
  queries = [
      ("01_active_memberships.txt", "SELECT m.first_name||' '||m.last_name, mt.name, ms.end_date FROM memberships ms JOIN members m ON m.id=ms.member_id JOIN membership_types mt ON mt.id=ms.membership_type_id WHERE date('now') BETWEEN date(ms.start_date) AND date(ms.end_date)"),
      ("02_schedule_conflicts.txt", """SELECT m.first_name||' '||m.last_name, c1.name, c2.name FROM class_enrollments e1 JOIN class_enrollments e2 ON e1.member_id=e2.member_id AND e1.class_id<e2.class_id JOIN members m ON m.id=e1.member_id JOIN classes c1 ON c1.id=e1.class_id JOIN classes c2 ON c2.id=e2.class_id WHERE c1.starts_at < c2.ends_at AND c2.starts_at < c1.ends_at"""),
      ("03_top_classes.txt", "SELECT c.name, COUNT(v.id) FROM classes c LEFT JOIN visits v ON v.class_id=c.id GROUP BY c.id ORDER BY 2 DESC LIMIT 3"),
  ]
  for fname, sql in queries:
      cur = con.execute(sql)
      headers = [d[0] for d in cur.description]
      body = format_table(cur.fetchall(), headers)
      (SHOTS / fname).write_text(body + "\n", encoding="utf-8")
  readme = SHOTS / "README.md"
  readme.write_text(
      "# Скриншоты DBeaver\n\n"
      "Для сдачи добавьте в эту папку скрины из DBeaver:\n\n"
      "- список таблиц и связей (Diagram / ER);\n"
      "- данные в `members`, `classes`;\n"
      "- результаты 2–3 запросов из `checks.sql`.\n\n"
      "Файлы `01_*.txt` … — текстовый экспорт тех же запросов (контроль без GUI).\n",
      encoding="utf-8",
  )
  con.close()
  print(f"Exported to {SHOTS}")


if __name__ == "__main__":
    main()