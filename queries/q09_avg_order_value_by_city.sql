-- Question: What is the average order value in each city? (cancelled excluded)
-- Concepts: using a view (v_order_totals), AVG, JOIN, GROUP BY
SELECT c.city,
       ROUND(AVG(t.order_total), 2) AS avg_order_value
FROM v_order_totals t
JOIN customers c ON c.customer_id = t.customer_id
WHERE t.status <> 'cancelled'
GROUP BY c.city
ORDER BY avg_order_value DESC, c.city;
