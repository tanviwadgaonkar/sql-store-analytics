# sql-store-analytics

An online-store database in SQLite with 12 SQL queries that answer business questions about customers, products and revenue. A small Python command-line tool runs the queries, and pytest tests check every query against a dataset small enough to add up by hand.

Built with Claude as a coding assistant.

## What it shows

- A normalized schema with primary keys, foreign keys and `CHECK` constraints
- Joins, `GROUP BY` / `HAVING`, subqueries, CTEs, window functions (`SUM() OVER`, `RANK()`, `ROW_NUMBER()`), conditional aggregation
- A view, and indexes with query plans that prove they are used
- Parameterized queries (values are passed as parameters, never pasted into the SQL text)

## Schema

```
customers (customer_id PK, name, city, signup_date)
    |
    | 1 customer : many orders
    v
orders (order_id PK, customer_id FK, order_date, status)
    |
    | 1 order : many items
    v
order_items (order_id FK, product_id FK, quantity, unit_price)   PK = (order_id, product_id)
    ^
    | many items : 1 product
products (product_id PK, name UNIQUE, category, price)
```

`unit_price` is copied into `order_items` when the sale happens, so changing a product's price later does not change past revenue. `orders.status` is limited to placed, shipped, delivered or cancelled. Revenue queries leave out cancelled orders.

## Run it

```
pip install -r requirements-dev.txt     # only needed for the tests
python seed.py                          # builds store.db (1,000 customers, 100 products, 30,000 orders)
python run_query.py --list              # every query with its question
python run_query.py q01_top_customers
python run_query.py q04_frequent_customers --param min_orders=40
python -m pytest -q                     # 15 tests
python bench_index.py                   # query plans and timing without and with indexes
```

The sample data is generated from a fixed random seed, so it is repeatable. About 5% of customers never order and 5% of products never sell, so those queries have answers.

## The queries

| File | Question | Main concepts |
|---|---|---|
| q01_top_customers | Top 10 customers by spend | 3-table JOIN, GROUP BY, ORDER BY, LIMIT |
| q02_monthly_revenue | Revenue per month | strftime, GROUP BY expression |
| q03_products_never_sold | Products in no order | LEFT JOIN ... IS NULL |
| q04_frequent_customers | Customers with at least N orders | HAVING, named parameter |
| q05_category_share | Share of revenue per category | CTE, scalar subquery |
| q06_running_revenue | Cumulative revenue by month | window SUM() OVER |
| q07_top_products_per_category | Top 3 products per category | RANK() OVER (PARTITION BY) |
| q08_customers_never_ordered | Customers with no orders | LEFT JOIN ... IS NULL |
| q09_avg_order_value_by_city | Average order value per city | view, AVG, GROUP BY |
| q10_orders_above_average | Biggest orders above the average | subquery, view |
| q11_latest_order_per_customer | Most recent order per customer | ROW_NUMBER() OVER |
| q12_cancellation_rate_by_month | Cancelled share of orders per month | CASE WHEN aggregation |

## Indexes

`indexes.sql` adds indexes on `orders(customer_id)`, `orders(order_date)` and `order_items(product_id)`. A test checks the query plan for "orders of one customer":

- without the index: `SCAN orders` (reads every row)
- with the index: `SEARCH orders USING ... INDEX idx_orders_customer` (jumps to the matching rows)

`python bench_index.py` prints both plans and the timings on your machine.

## Tests

`tests/test_queries.py` loads 4 customers, 4 products and 5 orders (one cancelled, one customer who never orders, one product never sold) and checks every query result against numbers worked out by hand. Other tests check that the constraints reject bad data (zero quantity, unknown customer, unknown status, duplicate product name), that the index changes the query plan, and that the seed data is repeatable.

## Limits

- SQLite only. Date functions such as `strftime` are SQLite-specific; MySQL uses `DATE_FORMAT` and PostgreSQL uses `to_char`. The joins, grouping, CTEs and window functions are standard SQL.
- The data is generated, not real.
