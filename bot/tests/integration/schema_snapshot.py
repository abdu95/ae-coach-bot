"""Structure-only snapshot of a Postgres database's public schema: tables,
columns, constraints, indexes, triggers. No row data.

Used two ways:
- imported by the integration tests, to compare a scratch DB built by
  init_db() against prod_schema.json (the committed snapshot of prod);
- run as a script to (re)capture prod_schema.json. Prod Postgres has no
  public address, so run it inside a Railway container:

    railway ssh --service vacancy-webapp -- "python -" \
        < bot/tests/integration/schema_snapshot.py \
        > bot/tests/integration/prod_schema.json

  The connection is forced read-only, so it can't change anything.
"""

import json
import os
import sys

# Owned and created at runtime by payme-webhook (main.py), not by
# init_db() - excluded so the comparison is about the schema this repo owns.
EXCLUDED_TABLES = {"payme_credentials"}


def snapshot(cur) -> dict:
    def rows(sql):
        cur.execute(sql)
        return cur.fetchall()

    tables = {}
    for (table,) in rows("SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY 1"):
        if table in EXCLUDED_TABLES:
            continue
        cur.execute("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = %s
        """, (table,))
        # Keyed by name, not ordinal: prod's column order reflects the order
        # ALTER TABLE ADD COLUMNs happened to run in, which is history, not schema.
        columns = {name: {"type": typ, "nullable": nullable == "YES", "default": default}
                   for name, typ, nullable, default in cur.fetchall()}
        cur.execute("""
            SELECT conname, pg_get_constraintdef(oid) FROM pg_constraint
            WHERE conrelid = %s::regclass AND contype <> 'n' ORDER BY 1
        """, (table,))
        constraints = dict(cur.fetchall())
        cur.execute("SELECT indexname, indexdef FROM pg_indexes WHERE schemaname = 'public' AND tablename = %s ORDER BY 1", (table,))
        indexes = dict(cur.fetchall())
        cur.execute("SELECT tgname FROM pg_trigger WHERE tgrelid = %s::regclass AND NOT tgisinternal ORDER BY 1", (table,))
        triggers = [r[0] for r in cur.fetchall()]
        tables[table] = {"columns": columns, "constraints": constraints, "indexes": indexes, "triggers": triggers}
    return tables


def diff(expected: dict, actual: dict) -> list[str]:
    """Human-readable differences, empty when the two snapshots match."""
    out = []
    for table in sorted(expected.keys() | actual.keys()):
        if table not in actual:
            out.append(f"missing table: {table}")
            continue
        if table not in expected:
            out.append(f"unexpected table: {table}")
            continue
        for part in ("columns", "constraints", "indexes"):
            exp, act = expected[table][part], actual[table][part]
            for key in sorted(exp.keys() | act.keys()):
                if exp.get(key) != act.get(key):
                    out.append(f"{table}.{part}.{key}: expected {exp.get(key)!r}, got {act.get(key)!r}")
        if expected[table]["triggers"] != actual[table]["triggers"]:
            out.append(f"{table}.triggers: expected {expected[table]['triggers']}, got {actual[table]['triggers']}")
    return out


if __name__ == "__main__":
    import psycopg2

    conn = psycopg2.connect(os.environ["DATABASE_URL"], options="-c default_transaction_read_only=on")
    with conn, conn.cursor() as cur:
        json.dump(snapshot(cur), sys.stdout, indent=2, sort_keys=True)
        sys.stdout.write("\n")
