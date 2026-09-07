"""
Per-user state, cached in memory and persisted to Postgres. The
in-memory dict is the fast path; every wrapped handler flushes it to the
DB after running, so a restart/redeploy doesn't lose state.

Split into modules by responsibility (2026-09-07), mirroring the
vacancy-webapp app/db/ split done the same day - this __init__
re-exports every public name so `import state; state.foo(...)` (bot.py's
only usage pattern) and every existing test's mock.patch.object(state,
"foo", ...) keep working unchanged. _pool and init_db() stay directly on
this module rather than their own submodule: test_checks_used_not_
clobbered.py and test_payment_stats.py patch `state._pool` as a bare
module attribute, and every submodule reaches it via `state._pool`
(through `import state`, not a direct value import) at call time - that
indirection is what makes the patch actually intercept their queries too,
regardless of which submodule a given query now lives in.
"""

import os

from psycopg2.pool import SimpleConnectionPool

from state import schema

_pool: SimpleConnectionPool | None = None


def init_db() -> None:
    global _pool
    dsn = os.getenv("DATABASE_URL")
    if not dsn:
        raise ValueError("DATABASE_URL not set")

    _pool = SimpleConnectionPool(1, 5, dsn)
    conn = _pool.getconn()
    try:
        with conn, conn.cursor() as cur:
            schema.create_tables(cur)
            schema.migrate_legacy_state(cur)
            schema.migrate_legacy_cv_text(cur)
    finally:
        _pool.putconn(conn)


from state.session import get, reset, persisting, _empty, _save  # noqa: E402
from state.accounts import join_waitlist, get_quota_override, set_quota_override, set_source, get_source  # noqa: E402
from state.payments import get_or_create_order, payment_stats  # noqa: E402
from state.events import log_event, event_stats  # noqa: E402
from state.stats import (  # noqa: E402
    waitlist_count,
    source_count,
    pilot_count,
    pilot_stats,
    reset_with_cv_count,
    account_stats,
)

__all__ = [
    "init_db",
    "get", "reset", "persisting",
    "join_waitlist", "get_quota_override", "set_quota_override", "set_source", "get_source",
    "get_or_create_order", "payment_stats",
    "log_event", "event_stats",
    "waitlist_count", "source_count", "pilot_count", "pilot_stats", "reset_with_cv_count", "account_stats",
]
