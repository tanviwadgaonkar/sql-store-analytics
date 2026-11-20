-- Question: Which are the 5 largest orders that are worth more than the average order?
-- Concepts: subquery in WHERE, view
SELECT order_id, ROUND(order_total, 2) AS order_total
FROM v_order_totals
WHERE status <> 'cancelled'
  AND order_total > (SELECT AVG(order_total)
                     FROM v_order_totals
                     WHERE status <> 'cancelled')
ORDER BY order_total DESC, order_id
LIMIT 5;
