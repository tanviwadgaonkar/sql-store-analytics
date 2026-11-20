"""Tests: every query is checked against a tiny dataset small enough to add up by hand."""
import sqlite3
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import db  # noqa: E402
from seed import seed  # noqa: E402

CUSTOMERS = [
    (1, "Asha", "Pune", "2023-01-10"),
    (2, "Bhavin", "Mumbai", "2023-02-11"),
    (3, "Chitra", "Pune", "2023-03-12"),
    (4, "Dev", "Delhi", "2023-04-13"),  # never orders
]
PRODUCTS = [
    (1, "Pen", "Stationery", 10.0),
    (2, "Notebook", "Stationery", 50.0),
    (3, "Mouse", "Electronics", 500.0),
    (4, "Keyboard", "Electronics", 1000.0),  # never sold
]
ORDERS = [
    (1, 1, "2024-01-05", "delivered"),
    (2, 1, "2024-02-07", "delivered"),
    (3, 2, "2024-02-15", "shipped"),
    (4, 3, "2024-03-02", "cancelled"),
    (5, 2, "2024-03-20", "delivered"),
]
ITEMS = [
    (1, 1, 3, 10.0), (1, 2, 2, 50.0),    # order 1 = 130
    (2, 3, 1, 500.0),                    # order 2 = 500
    (3, 1, 10, 10.0), (3, 2, 1, 50.0),   # order 3 = 150
    (4, 3, 2, 500.0),                    # order 4 = 1000, cancelled
    (5, 2, 4, 50.0),                     # order 5 = 200
]


@pytest.fixture
def tiny():
    conn = db.connect()
    db.init_schema(conn)
    conn.executemany("INSERT INTO customers VALUES (?, ?, ?, ?)", CUSTOMERS)
    conn.executemany("INSERT INTO products VALUES (?, ?, ?, ?)", PRODUCTS)
    conn.executemany("INSERT INTO orders VALUES (?, ?, ?, ?)", ORDERS)
    conn.executemany("INSERT INTO order_items VALUES (?, ?, ?, ?)", ITEMS)
    conn.commit()
    return conn


def rows(conn, name, params=None):
    return [tuple(r) for r in db.run_query(conn, name, params)]


def test_top_customers_exclude_cancelled(tiny):
    assert rows(tiny, "q01_top_customers") == [
        (1, "Asha", "Pune", 630.0),
        (2, "Bhavin", "Mumbai", 350.0),
    ]


def test_monthly_revenue(tiny):
    assert rows(tiny, "q02_monthly_revenue") == [
        ("2024-01", 130.0), ("2024-02", 650.0), ("2024-03", 200.0),
    ]


def test_products_never_sold(tiny):
    assert rows(tiny, "q03_products_never_sold") == [(4, "Keyboard", "Electronics")]


def test_frequent_customers_uses_the_parameter(tiny):
    assert rows(tiny, "q04_frequent_customers", {"min_orders": 2}) == [
        (1, "Asha", 2), (2, "Bhavin", 2),
    ]
    assert rows(tiny, "q04_frequent_customers", {"min_orders": 3}) == []


def test_category_share(tiny):
    result = rows(tiny, "q05_category_share")
    assert result == [("Electronics", 500.0, 51.0), ("Stationery", 480.0, 49.0)]
    assert sum(r[2] for r in result) == pytest.approx(100.0, abs=0.2)


def test_running_revenue(tiny):
    assert rows(tiny, "q06_running_revenue") == [
        ("2024-01", 130.0, 130.0), ("2024-02", 650.0, 780.0), ("2024-03", 200.0, 980.0),
    ]


def test_top_products_per_category(tiny):
    assert rows(tiny, "q07_top_products_per_category") == [
        ("Electronics", "Mouse", 1, 1),
        ("Stationery", "Pen", 13, 1),
        ("Stationery", "Notebook", 7, 2),
    ]


def test_customers_never_ordered(tiny):
    assert rows(tiny, "q08_customers_never_ordered") == [(4, "Dev", "Delhi")]


def test_avg_order_value_by_city(tiny):
    assert rows(tiny, "q09_avg_order_value_by_city") == [("Pune", 315.0), ("Mumbai", 175.0)]


def test_orders_above_average(tiny):
    assert rows(tiny, "q10_orders_above_average") == [(2, 500.0)]


def test_latest_order_per_customer(tiny):
    assert rows(tiny, "q11_latest_order_per_customer") == [
        (1, "Asha", 2, "2024-02-07"),
        (2, "Bhavin", 5, "2024-03-20"),
        (3, "Chitra", 4, "2024-03-02"),
    ]


def test_cancellation_rate_by_month(tiny):
    assert rows(tiny, "q12_cancellation_rate_by_month") == [
        ("2024-01", 1, 0, 0.0), ("2024-02", 2, 0, 0.0), ("2024-03", 2, 1, 50.0),
    ]


def test_constraints_reject_bad_data(tiny):
    with pytest.raises(sqlite3.IntegrityError):   # quantity must be positive
        tiny.execute("INSERT INTO order_items VALUES (1, 3, 0, 500.0)")
    with pytest.raises(sqlite3.IntegrityError):   # customer 999 does not exist
        tiny.execute("INSERT INTO orders VALUES (6, 999, '2024-04-01', 'placed')")
    with pytest.raises(sqlite3.IntegrityError):   # unknown status
        tiny.execute("INSERT INTO orders VALUES (6, 1, '2024-04-01', 'lost')")
    with pytest.raises(sqlite3.IntegrityError):   # duplicate product name
        tiny.execute("INSERT INTO products VALUES (9, 'Pen', 'Stationery', 5.0)")


def plan_text(conn):
    sql = "EXPLAIN QUERY PLAN SELECT COUNT(*) FROM orders WHERE customer_id = 1"
    return " ".join(r["detail"] for r in conn.execute(sql))


def test_index_changes_query_plan_from_scan_to_search():
    without, with_index = db.connect(), db.connect()
    db.init_schema(without, with_indexes=False)
    db.init_schema(with_index, with_indexes=True)
    assert "SCAN" in plan_text(without) and "idx_orders_customer" not in plan_text(without)
    assert "SEARCH" in plan_text(with_index) and "idx_orders_customer" in plan_text(with_index)


def test_seed_is_repeatable_and_leaves_unused_rows():
    sizes = dict(n_customers=100, n_products=20, n_orders=5000)  # enough orders that every active customer orders
    totals = []
    for _ in range(2):
        conn = db.connect()
        db.init_schema(conn)
        seed(conn, **sizes)
        totals.append(conn.execute("SELECT SUM(quantity * unit_price) FROM order_items").fetchone()[0])
        assert len(db.run_query(conn, "q08_customers_never_ordered")) == 5  # 5% of 100
        assert len(db.run_query(conn, "q03_products_never_sold")) == 1      # 5% of 20
    assert totals[0] == totals[1]
