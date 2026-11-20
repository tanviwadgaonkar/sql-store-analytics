-- Question: Which products have never appeared in any order?
-- Concepts: LEFT JOIN with IS NULL (anti-join)
SELECT p.product_id, p.name, p.category
FROM products p
LEFT JOIN order_items oi ON oi.product_id = p.product_id
WHERE oi.product_id IS NULL
ORDER BY p.product_id;
