SELECT sku, name, price
FROM products
WHERE category = 'electronics'
ORDER BY price DESC
LIMIT 10;