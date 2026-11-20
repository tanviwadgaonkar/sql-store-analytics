-- Question: What was each customer's most recent order? (first 10 customers shown)
-- Concepts: ROW_NUMBER() OVER (PARTITION BY ... ORDER BY ...), CTE
WITH numbered AS (
    SELECT c.customer_id,
           c.name,
           o.order_id,
           o.order_date,
           ROW_NUMBER() OVER (PARTITION BY c.customer_id
                              ORDER BY o.order_date DESC, o.order_id DESC) AS rn
    FROM customers c
    JOIN orders o ON o.customer_id = c.customer_id
)
SELECT customer_id, name, order_id, order_date
FROM numbered
WHERE rn = 1
ORDER BY customer_id
LIMIT 10;
