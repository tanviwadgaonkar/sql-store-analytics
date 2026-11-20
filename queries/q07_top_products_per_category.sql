-- Question: What are the 3 best-selling products (by units) in each category?
-- Concepts: RANK() OVER (PARTITION BY ...), filtering on a window result via CTE
WITH product_units AS (
    SELECT p.category,
           p.name AS product,
           SUM(oi.quantity) AS units_sold
    FROM order_items oi
    JOIN products p ON p.product_id = oi.product_id
    JOIN orders o   ON o.order_id   = oi.order_id
    WHERE o.status <> 'cancelled'
    GROUP BY p.product_id, p.category, p.name
),
ranked AS (
    SELECT category, product, units_sold,
           RANK() OVER (PARTITION BY category ORDER BY units_sold DESC) AS rank_in_category
    FROM product_units
)
SELECT category, product, units_sold, rank_in_category
FROM ranked
WHERE rank_in_category <= 3
ORDER BY category, rank_in_category, product;
