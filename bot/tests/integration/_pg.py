"""Scratch-database scaffolding for the integration tests (not a test
itself). Unlike the rest of bot/tests/, which fake the pool, these run
real SQL against a real local Postgres, so they catch a broken statement or
a migration that doesn't do what it says.

Each scratch_db() creates a fresh, uniquely named database and drops it
afterwards. It refuses to run against anything but a local server, so a
stray DATABASE_URL can never point a test that drops databases at prod.
"""

import os
import sys
from contextlib import contextmanager
from pathlib import Path

import psycopg2
from psycopg2.extensions import make_dsn, parse_dsn

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))  # bot/, for `import state`

# Local socket by default (Homebrew Postgres: `brew services start postgresql@18`).
ADMIN_URL = os.getenv("TEST_DATABASE_ADMIN_URL", "postgresql:///postgres")
_LOCAL_HOSTS = {"", "localhost", "127.0.0.1", "::1"}


def _check_local(url: str) -> None:
    host = parse_dsn(url).get("host", "")
    if host not in _LOCAL_HOSTS and not host.startswith("/"):
        sys.exit(f"Refusing to run integration tests against non-local host {host!r}")


def connect_admin():
    _check_local(ADMIN_URL)
    try:
        conn = psycopg2.connect(ADMIN_URL)
    except psycopg2.OperationalError as e:
        sys.exit(f"Can't reach local Postgres at {ADMIN_URL!r} ({e}).\n"
                 "Start it with: brew services start postgresql@18")
    conn.autocommit = True
    return conn


@contextmanager
def scratch_db():
    """Yields a DSN for a brand-new empty database, dropped on exit."""
    name = f"chashma_test_{os.getpid()}"
    admin = connect_admin()
    with admin.cursor() as cur:
        cur.execute(f'DROP DATABASE IF EXISTS "{name}"')
        cur.execute(f'CREATE DATABASE "{name}"')
    try:
        yield make_dsn(ADMIN_URL, dbname=name)
    finally:
        import state
        if state._pool is not None:
            state._pool.closeall()
            state._pool = None
        with admin.cursor() as cur:
            cur.execute(f'DROP DATABASE IF EXISTS "{name}" WITH (FORCE)')
        admin.close()


def init_db(dsn: str) -> None:
    """Runs the bot's real startup init_db() against `dsn`."""
    import state
    if state._pool is not None:
        state._pool.closeall()
    os.environ["DATABASE_URL"] = dsn
    state.init_db()
