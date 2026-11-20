-- Indexes for the lookups the queries use most.
-- order_items already has an index on (order_id, product_id) from its primary key.
CREATE INDEX idx_orders_customer ON orders (customer_id);
CREATE INDEX idx_orders_date     ON orders (order_date);
CREATE INDEX idx_items_product   ON order_items (product_id);
