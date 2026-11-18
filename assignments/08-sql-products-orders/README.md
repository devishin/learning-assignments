# ДЗ: SQLite — products и orders (DBeaver)

Учебная БД интернет-витрины: товары и заказы, базовые DML/SELECT, JOIN, агрегаты, LIKE, мини-демо SQL-инъекций.

## Структура

```
08-sql-products-orders/
├── sql/
│   ├── schema.sql      — таблицы products, orders
│   └── queries.sql     — INSERT / UPDATE / DELETE / SELECT (с комментариями)
├── code/
│   ├── seed.py         — ≥120 товаров + заказы
│   ├── run_checks.py   — выгрузка результатов в screenshots/
│   ├── sql_injection_demo.py — небезопасный SQL vs ?
│   └── insert_products_explained.md
├── screenshots/        — скрины DBeaver + *.txt выгрузки
└── products_orders.db  — готовая база (после seed)
```

## Таблицы

| Таблица | Поля (кратко) |
|---------|----------------|
| `products` | `id`, `sku` UNIQUE, `name`, `category`, `price`, `in_stock` |
| `orders` | `id`, `product_id` FK, `quantity`, `order_date`, `is_test` |

## Ограничения

- `CHECK` на цену и количество; FK `orders → products`.
- Индексы: `category`, `sku`, `product_id`, `order_date`.

## Как запустить (4 шага)

1. Клонируйте [learning-assignments](https://github.com/devishin/learning-assignments).
2. `cd assignments/08-sql-products-orders`
3. `python code/seed.py` — создаёт `products_orders.db`.
4. DBeaver: **SQLite** → указать путь к `products_orders.db` → выполнить блоки из `sql/queries.sql`.

Самопроверка:

```powershell
python code/run_checks.py
python code/sql_injection_demo.py
```

## Что в queries.sql

| Блок | Содержание |
|------|------------|
| INSERT ×3 | Ручные товар и заказ |
| INSERT bulk | 5 promo-товаров |
| UPDATE ×3 | Скидка категории, цена по SKU, снятие с продажи |
| DELETE ×1 | `WHERE is_test = 1` |
| SELECT | TOP-N по цене |
| Агрегат | `GROUP BY category HAVING COUNT(*) > 5` |
| LIKE | `UPPER(name) LIKE 'ABC%'` |
| JOIN | Заказы + товар + `line_total` |
| JOIN+GROUP | Выручка по категориям |

## Безопасность

`code/sql_injection_demo.py` — **небезопасная** f-string конкатенация рядом с **`?` placeholders** (`sqlite3`). Риск: подмена SQL-логики через ввод пользователя.

## Критерии сдачи

- Все запросы без ошибок; `UPDATE`/`DELETE` только с `WHERE`.
- Есть JOIN и агрегирующая выборка.
- Параметризация показана в коде.
- В репозитории: `/sql`, `/screenshots`, `/code`.

## Ссылка на этот проект

https://github.com/devishin/learning-assignments/tree/main/assignments/08-sql-products-orders