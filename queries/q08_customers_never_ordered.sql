-- Question: Which customers have never placed an order?
-- Concepts: LEFT JOIN with IS NULL (anti-join)
SELECT c.customer_id, c.name, c.city
FROM customers c
LEFT JOIN orders o ON o.customer_id = c.customer_id
WHERE o.order_id IS NULL
ORDER BY c.customer_id;
