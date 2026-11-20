"""Show what the indexes change: query plans and lookup time, without and with indexes.

    python bench_index.py

Timings depend on your machine; the query plans do not.
"""
import random
import statistics
import time

import db
from seed import seed

LOOKUP_SQL = "SELECT COUNT(*) FROM orders WHERE customer_id = ?"
RANGE_SQL = "SELECT COUNT(*) FROM orders WHERE order_date BETWEEN '2025-03-01' AND '2025-03-31'"


def build(with_indexes):
    conn = db.connect()
    db.init_schema(conn, with_indexes=with_indexes)
    seed(conn)
    return conn


def plan(conn, sql, params=()):
    return [row["detail"] for row in conn.execute("EXPLAIN QUERY PLAN " + sql, params)]


def median_ms(conn, sql, param_list, repeats=5):
    runs = []
    for _ in range(repeats):
        start = time.perf_counter()
        for params in param_list:
            conn.execute(sql, params).fetchone()
        runs.append((time.perf_counter() - start) * 1000 / len(param_list))
    return statistics.median(runs)


def main():
    rng = random.Random(1)
    customer_ids = [(rng.randint(51, 1000),) for _ in range(200)]
    for label, with_indexes in (("WITHOUT indexes", False), ("WITH indexes", True)):
        conn = build(with_indexes)
        print(f"\n=== {label} ===")
        print("orders for one customer:", plan(conn, LOOKUP_SQL, (customer_ids[0][0],)))
        print("orders in one month    :", plan(conn, RANGE_SQL))
        print(f"median time, customer lookup: {median_ms(conn, LOOKUP_SQL, customer_ids):.3f} ms per query")
        print(f"median time, month range    : {median_ms(conn, RANGE_SQL, [()]):.3f} ms per query")
        conn.close()


if __name__ == "__main__":
    main()
