-- Online store schema (SQLite). Foreign keys are switched on in db.connect().

CREATE TABLE customers (
    customer_id INTEGER PRIMARY KEY,
    name        TEXT NOT NULL,
    city        TEXT NOT NULL,
    signup_date TEXT NOT NULL                    -- ISO date, YYYY-MM-DD
);

CREATE TABLE products (
    product_id INTEGER PRIMARY KEY,
    name       TEXT NOT NULL UNIQUE,
    category   TEXT NOT NULL,
    price      REAL NOT NULL CHECK (price >= 0)
);

CREATE TABLE orders (
    order_id    INTEGER PRIMARY KEY,
    customer_id INTEGER NOT NULL REFERENCES customers (customer_id),
    order_date  TEXT NOT NULL,                   -- ISO date, YYYY-MM-DD
    status      TEXT NOT NULL
                CHECK (status IN ('placed', 'shipped', 'delivered', 'cancelled'))
);

-- One row per product in an order. unit_price is copied from products at the
-- time of sale, so later price changes do not rewrite old revenue.
CREATE TABLE order_items (
    order_id   INTEGER NOT NULL REFERENCES orders (order_id),
    product_id INTEGER NOT NULL REFERENCES products (product_id),
    quantity   INTEGER NOT NULL CHECK (quantity > 0),
    unit_price REAL NOT NULL CHECK (unit_price >= 0),
    PRIMARY KEY (order_id, product_id)
);
