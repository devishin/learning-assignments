SELECT category, COUNT(*) AS cnt, ROUND(AVG(price), 2) AS avg_price
FROM products
GROUP BY category
HAVING COUNT(*) > 5;