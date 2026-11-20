-- Total value of each order (sum of its line items).
CREATE VIEW v_order_totals AS
SELECT o.order_id,
       o.customer_id,
       o.order_date,
       o.status,
       SUM(oi.quantity * oi.unit_price) AS order_total
FROM orders o
JOIN order_items oi ON oi.order_id = o.order_id
GROUP BY o.order_id, o.customer_id, o.order_date, o.status;
