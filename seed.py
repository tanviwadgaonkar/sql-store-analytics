"""Generate repeatable sample data for the online-store database.

The same rng_seed always produces the same data, so results can be reproduced.
Run `python seed.py` to build store.db.
"""
import random
from datetime import date, timedelta

CITIES = ["Pune", "Mumbai", "Delhi", "Bengaluru", "Chennai", "Hyderabad", "Kolkata", "Ahmedabad"]
CATEGORY_PRICE_RANGE = {
    "Stationery": (10, 200),
    "Electronics": (300, 5000),
    "Books": (150, 900),
    "Home": (200, 3000),
    "Sports": (250, 4000),
    "Toys": (100, 1500),
}
STATUSES = ["delivered", "shipped", "placed", "cancelled"]
STATUS_WEIGHTS = [70, 12, 8, 10]
FIRST_NAMES = ["Asha", "Bhavin", "Chitra", "Dev", "Esha", "Farhan", "Gauri", "Hari", "Isha", "Jay"]
LAST_NAMES = ["Patil", "Shah", "Rao", "Khan", "Joshi", "Nair", "Mehta", "Iyer", "Kulkarni", "Singh"]


def seed(conn, n_customers=1000, n_products=100, n_orders=30000,
         inactive_share=0.05, rng_seed=42):
    rng = random.Random(rng_seed)

    customers = []
    for cid in range(1, n_customers + 1):
        name = f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)} {cid}"
        signup = date(2023, 1, 1) + timedelta(days=rng.randint(0, 364))
        customers.append((cid, name, rng.choice(CITIES), signup.isoformat()))

    categories = list(CATEGORY_PRICE_RANGE)
    products = []
    for pid in range(1, n_products + 1):
        category = categories[(pid - 1) % len(categories)]
        low, high = CATEGORY_PRICE_RANGE[category]
        products.append((pid, f"{category} item {pid}", category, float(rng.randint(low, high))))
    price_of = {pid: price for pid, _, _, price in products}

    # The first customers never order, so "customers who never ordered" has an answer.
    n_inactive = int(n_customers * inactive_share)
    active_ids = list(range(n_inactive + 1, n_customers + 1))

    # The last few products never sell, so "products never sold" has an answer too.
    n_unsold = max(1, int(n_products * 0.05))
    product_ids = [pid for pid in price_of if pid <= n_products - n_unsold]

    orders, items = [], []
    start = date(2024, 1, 1)
    for oid in range(1, n_orders + 1):
        order_day = start + timedelta(days=rng.randint(0, 729))
        status = rng.choices(STATUSES, weights=STATUS_WEIGHTS)[0]
        orders.append((oid, rng.choice(active_ids), order_day.isoformat(), status))
        for pid in rng.sample(product_ids, rng.randint(1, 4)):
            items.append((oid, pid, rng.randint(1, 5), price_of[pid]))

    conn.executemany("INSERT INTO customers VALUES (?, ?, ?, ?)", customers)
    conn.executemany("INSERT INTO products VALUES (?, ?, ?, ?)", products)
    conn.executemany("INSERT INTO orders VALUES (?, ?, ?, ?)", orders)
    conn.executemany("INSERT INTO order_items VALUES (?, ?, ?, ?)", items)
    conn.commit()
    return {"customers": len(customers), "products": len(products),
            "orders": len(orders), "order_items": len(items)}


if __name__ == "__main__":
    import db

    print(db.build_database("store.db"))
