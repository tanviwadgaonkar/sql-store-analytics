-- Question: What percentage of orders were cancelled each month?
-- Concepts: conditional aggregation with CASE WHEN, COUNT, percentage arithmetic
SELECT strftime('%Y-%m', order_date) AS month,
       COUNT(*) AS orders,
       SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) AS cancelled,
       ROUND(100.0 * SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) / COUNT(*), 1)
           AS cancellation_rate_pct
FROM orders
GROUP BY month
ORDER BY month;
