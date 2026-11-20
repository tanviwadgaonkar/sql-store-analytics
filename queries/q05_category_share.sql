-- Question: What share of total revenue does each product category bring in?
-- Concepts: CTE (WITH), scalar subquery, percentage arithmetic
WITH category_revenue AS (
    SELECT p.category,
           SUM(oi.quantity * oi.unit_price) AS revenue
    FROM order_items oi
    JOIN products p ON p.product_id = oi.product_id
    JOIN orders o   ON o.order_id   = oi.order_id
    WHERE o.status <> 'cancelled'
    GROUP BY p.category
)
SELECT category,
       ROUND(revenue, 2) AS revenue,
       ROUND(100.0 * revenue / (SELECT SUM(revenue) FROM category_revenue), 1) AS share_pct
FROM category_revenue
ORDER BY revenue DESC;
