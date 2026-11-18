# Скриншоты DBeaver (PNG)

Реальные снимки окна **DBeaver 26.2.4** с базой `products_orders.db` (подключение `products_orders_hw`).

| Файл | Содержание |
|------|------------|
| `01_tables_structure.png` | Навигатор: подключения SQLite |
| `02_join_orders.png` | JOIN `orders` + `products`, сумма строки |
| `03_aggregate_category.png` | `GROUP BY category` + `HAVING COUNT(*) > 5` |
| `04_like_abc.png` | `UPPER(name) LIKE 'ABC%'` |
| `05_top_price.png` | TOP-10 electronics по цене |

Пересъёмка (после `code/seed.py`):

```powershell
cd assignments/08-sql-products-orders
python code/capture_dbeaver_cli_screenshots.py
```

Текстовые выгрузки **не** используются — только PNG.