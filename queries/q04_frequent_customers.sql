-- Question: Which customers placed at least :min_orders orders (cancelled excluded)?
-- Concepts: HAVING (filter after grouping), named parameter instead of string pasting
SELECT c.customer_id,
       c.name,
       COUNT(*) AS order_count
FROM customers c
JOIN orders o ON o.customer_id = c.customer_id
WHERE o.status <> 'cancelled'
GROUP BY c.customer_id, c.name
HAVING COUNT(*) >= :min_orders
ORDER BY order_count DESC, c.customer_id;
