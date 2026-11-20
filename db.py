"""Small helpers for opening the database and running the SQL files."""
import sqlite3
from pathlib import Path

ROOT = Path(__file__).parent


def connect(path=":memory:"):
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")  # SQLite ignores foreign keys unless asked
    return conn


def init_schema(conn, with_indexes=True):
    for name in ("schema.sql", "views.sql"):
        conn.executescript((ROOT / name).read_text())
    if with_indexes:
        conn.executescript((ROOT / "indexes.sql").read_text())


def query_names():
    return sorted(p.stem for p in (ROOT / "queries").glob("*.sql"))


def query_text(name):
    return (ROOT / "queries" / f"{name}.sql").read_text()


def run_query(conn, name, params=None):
    """Run queries/<name>.sql. Values go in as named parameters, never string-pasted."""
    return conn.execute(query_text(name), params or {}).fetchall()


def build_database(path="store.db", **seed_args):
    """Create a fresh database file with schema, indexes and sample data."""
    from seed import seed

    Path(path).unlink(missing_ok=True)
    conn = connect(path)
    init_schema(conn)
    counts = seed(conn, **seed_args)
    conn.close()
    return counts
