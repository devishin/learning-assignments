-- queries.sql — DBeaver / SQLite (products_orders.db)
-- Перед запуском: schema.sql + code/seed.py (или готовый products_orders.db)

-- ---------------------------------------------------------------------------
-- INSERT: 3 «ручных» (одиночные товары)
-- ---------------------------------------------------------------------------

-- 1) Новый товар вручную
INSERT INTO products (sku, name, category, price, in_stock)
VALUES ('MAN-001', 'Manual Widget Alpha', 'electronics', 149.00, 1);

-- 2) Второй ручной товар
INSERT INTO products (sku, name, category, price, in_stock)
VALUES ('MAN-002', 'Manual Tea Set Oak', 'home', 37.50, 1);

-- 3) Заказ на существующий товар (подставьте product_id после seed, обычно id=1)
INSERT INTO orders (product_id, quantity, order_date, customer_note, is_test)
VALUES (1, 2, datetime('now'), 'manual single order', 1);

-- ---------------------------------------------------------------------------
-- INSERT: массовая вставка (категория «promo»)
-- ---------------------------------------------------------------------------
INSERT INTO products (sku, name, category, price, in_stock) VALUES
    ('PRM-010', 'Promo Cable Pack', 'electronics', 19.99, 1),
    ('PRM-011', 'Promo Yoga Band', 'sports', 9.99, 1),
    ('PRM-012', 'Promo Notebook', 'books', 4.50, 1),
    ('PRM-013', 'Promo Vitamin C', 'grocery', 6.20, 1),
    ('PRM-014', 'Promo Hand Cream', 'beauty', 11.00, 1);

-- ---------------------------------------------------------------------------
-- UPDATE: 3 осмысленных, только с WHERE
-- ---------------------------------------------------------------------------

-- Скидка 10% всем товарам категории grocery
UPDATE products
SET price = ROUND(price * 0.90, 2)
WHERE category = 'grocery';

-- Новая цена по конкретному SKU
UPDATE products
SET price = 175.00
WHERE sku = 'MAN-001';

-- Снять с продажи всё, что дороже 2000 (тестовый кейс)
UPDATE products
SET in_stock = 0
WHERE price > 2000.00 AND category = 'electronics';

-- ---------------------------------------------------------------------------
-- DELETE: безопасно — только тестовые заказы
-- ---------------------------------------------------------------------------
DELETE FROM orders
WHERE is_test = 1;

-- ---------------------------------------------------------------------------
-- SELECT: WHERE + ORDER BY + LIMIT (топ-15 по цене в electronics)
-- ---------------------------------------------------------------------------
SELECT id, sku, name, category, price
FROM products
WHERE category = 'electronics' AND in_stock = 1
ORDER BY price DESC
LIMIT 15;

-- ---------------------------------------------------------------------------
-- Агрегация + HAVING
-- ---------------------------------------------------------------------------
SELECT category,
       COUNT(*) AS product_count,
       ROUND(AVG(price), 2) AS avg_price
FROM products
GROUP BY category
HAVING COUNT(*) > 5
ORDER BY product_count DESC;

-- ---------------------------------------------------------------------------
-- LIKE: поиск без учёта регистра (имя начинается с abc)
-- ---------------------------------------------------------------------------
SELECT id, sku, name, category, price
FROM products
WHERE UPPER(name) LIKE 'ABC%'
ORDER BY name;

-- ---------------------------------------------------------------------------
-- JOIN: заказы + товар + сумма строки (qty * price)
-- ---------------------------------------------------------------------------
SELECT o.id AS order_id,
       o.order_date,
       p.sku,
       p.name AS product_name,
       p.category,
       o.quantity,
       p.price,
       ROUND(o.quantity * p.price, 2) AS line_total
FROM orders o
JOIN products p ON p.id = o.product_id
ORDER BY o.order_date DESC
LIMIT 20;

-- ---------------------------------------------------------------------------
-- JOIN + агрегат: выручка по категориям (по всем заказам)
-- ---------------------------------------------------------------------------
SELECT p.category,
       COUNT(DISTINCT o.id) AS orders_count,
       SUM(o.quantity) AS items_sold,
       ROUND(SUM(o.quantity * p.price), 2) AS revenue
FROM orders o
JOIN products p ON p.id = o.product_id
GROUP BY p.category
ORDER BY revenue DESC;