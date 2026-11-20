"""Run one of the SQL files in queries/ against store.db and print the result.

    python seed.py                       # build store.db once
    python run_query.py --list           # show every query and its question
    python run_query.py q01_top_customers
    python run_query.py q04_frequent_customers --param min_orders=40
"""
import argparse
import sys

import db

DEFAULT_PARAMS = {"min_orders": 40}


def parse_params(pairs):
    params = dict(DEFAULT_PARAMS)
    for pair in pairs:
        key, _, value = pair.partition("=")
        params[key] = int(value) if value.lstrip("-").isdigit() else value
    return params


def format_table(columns, rows):
    cells = [[str(v) for v in row] for row in rows]
    widths = [max([len(c)] + [len(r[i]) for r in cells]) for i, c in enumerate(columns)]
    line = "  ".join(c.ljust(w) for c, w in zip(columns, widths))
    out = [line, "  ".join("-" * w for w in widths)]
    out += ["  ".join(v.ljust(w) for v, w in zip(row, widths)) for row in cells]
    return "\n".join(out)


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("query", nargs="?", help="query name, for example q01_top_customers")
    parser.add_argument("--list", action="store_true", help="list the available queries")
    parser.add_argument("--db", default="store.db", help="database file (default: store.db)")
    parser.add_argument("--param", action="append", default=[], metavar="NAME=VALUE")
    args = parser.parse_args(argv)

    if args.list or not args.query:
        for name in db.query_names():
            question = db.query_text(name).splitlines()[0].removeprefix("-- Question: ")
            print(f"{name}\n    {question}")
        return 0

    if args.query not in db.query_names():
        print(f"Unknown query: {args.query}. Use --list to see the names.", file=sys.stderr)
        return 1

    conn = db.connect(args.db)
    cursor = conn.execute(db.query_text(args.query), parse_params(args.param))
    columns = [d[0] for d in cursor.description]
    rows = cursor.fetchall()
    print(format_table(columns, rows))
    print(f"\n{len(rows)} row(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
