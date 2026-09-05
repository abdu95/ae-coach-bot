"""
Minimal DB access for vacancy-webapp, sharing the same Postgres the bot
uses (tables are created by bot/state.py's init_db() - this module only
reads/writes, never creates schema).
"""

import os

import psycopg2
from psycopg2.pool import SimpleConnectionPool

_pool: SimpleConnectionPool | None = None


def get_pool() -> SimpleConnectionPool:
    global _pool
    if _pool is None:
        dsn = os.getenv("DATABASE_URL")
        if not dsn:
            raise ValueError("DATABASE_URL not set")
        _pool = SimpleConnectionPool(1, 5, dsn)
    return _pool


def check_connection() -> dict:
    """Health check: confirms we can reach Postgres and that the
    applications table (created by the bot) is visible from here."""
    pool = get_pool()
    conn = pool.getconn()
    try:
        with conn, conn.cursor() as cur:
            cur.execute("SELECT 1")
            cur.execute("""
                SELECT column_name FROM information_schema.columns
                WHERE table_name = 'applications' ORDER BY ordinal_position
            """)
            columns = [r[0] for r in cur.fetchall()]
        return {"connected": True, "applications_columns": columns}
    finally:
        pool.putconn(conn)
