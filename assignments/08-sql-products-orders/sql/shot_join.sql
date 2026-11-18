SELECT o.id, p.sku, p.name, ROUND(o.quantity * p.price, 2) AS line_total
FROM orders o
JOIN products p ON p.id = o.product_id
ORDER BY o.order_date DESC
LIMIT 12;