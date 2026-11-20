-- Question: Which 10 customers have spent the most? (cancelled orders excluded)
-- Concepts: JOIN across three tables, GROUP BY, SUM, ORDER BY, LIMIT
SELECT c.customer_id,
       c.name,
       c.city,
       ROUND(SUM(oi.quantity * oi.unit_price), 2) AS total_spent
FROM customers c
JOIN orders o       ON o.customer_id = c.customer_id
JOIN order_items oi ON oi.order_id   = o.order_id
WHERE o.status <> 'cancelled'
GROUP BY c.customer_id, c.name, c.city
ORDER BY total_spent DESC, c.customer_id
LIMIT 10;
