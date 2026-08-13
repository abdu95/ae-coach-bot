# Per-user state, cached in memory and persisted to Postgres.
# The in-memory dict is the fast path; every wrapped handler flushes
# it to the DB after running, so a restart/redeploy doesn't lose state.

import functools
import json
import os

import psycopg2
from psycopg2.pool import SimpleConnectionPool

_users: dict = {}
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
            # Legacy tables — kept only as the source for the one-time backfill
            # below. Nothing writes to `waitlist` anymore; `user_state` still
            # holds the session/flow fields (see _ACCOUNT_KEYS split in _save).
            cur.execute("""
                CREATE TABLE IF NOT EXISTS user_state (
                    user_id BIGINT PRIMARY KEY,
                    data JSONB NOT NULL,
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS waitlist (
                    user_id BIGINT PRIMARY KEY,
                    username TEXT,
                    joined_at TIMESTAMPTZ NOT NULL DEFAULT now()
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    telegram_id     BIGINT PRIMARY KEY,
                    username        TEXT,
                    language        TEXT,
                    source          TEXT DEFAULT 'organic',
                    checks_used     INT  NOT NULL DEFAULT 0,
                    quota_override  INT,
                    joined_waitlist BOOLEAN NOT NULL DEFAULT FALSE,
                    waitlist_at     TIMESTAMPTZ,
                    first_seen_at   TIMESTAMPTZ NOT NULL DEFAULT now(),
                    last_seen_at    TIMESTAMPTZ NOT NULL DEFAULT now()
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS events (
                    id          BIGSERIAL PRIMARY KEY,
                    telegram_id BIGINT NOT NULL,
                    event_type  TEXT   NOT NULL,
                    metadata    JSONB,
                    created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
                )
            """)
            cur.execute("CREATE INDEX IF NOT EXISTS idx_events_type_time ON events (event_type, created_at)")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_events_user ON events (telegram_id)")
            _migrate_legacy_state(cur)
    finally:
        _pool.putconn(conn)


def _migrate_legacy_state(cur) -> None:
    """Backfill users from the legacy user_state/waitlist tables. Safe to run
    on every startup: ON CONFLICT DO NOTHING means an already-migrated user
    (one with a `users` row) is left untouched, so this is a no-op once
    every pre-existing user has been copied over exactly once."""
    cur.execute("""
        INSERT INTO users (telegram_id, language, checks_used, joined_waitlist, first_seen_at, last_seen_at)
        SELECT
            user_id,
            NULLIF(data->>'lang', ''),
            COALESCE((data->>'usage_count')::int, 0),
            COALESCE((data->>'waitlisted')::boolean, false),
            updated_at,
            updated_at
        FROM user_state
        ON CONFLICT (telegram_id) DO NOTHING
    """)
    cur.execute("""
        INSERT INTO users (telegram_id, username, joined_waitlist, waitlist_at)
        SELECT user_id, username, true, joined_at
        FROM waitlist
        ON CONFLICT (telegram_id) DO UPDATE
        SET username = COALESCE(users.username, EXCLUDED.username),
            joined_waitlist = true,
            waitlist_at = COALESCE(users.waitlist_at, EXCLUDED.waitlist_at)
    """)


def get(user_id: int) -> dict:
    if user_id not in _users:
        loaded = _load(user_id)
        merged = _empty()
        if loaded:
            merged.update(loaded)
        account = _upsert_and_load_account(user_id)
        merged["lang"] = account["language"] or ""
        merged["usage_count"] = account["checks_used"]
        merged["waitlisted"] = account["joined_waitlist"]
        _users[user_id] = merged
    return _users[user_id]


def reset(user_id: int) -> None:
    current = get(user_id)
    fresh = _empty()
    fresh["lang"] = current.get("lang", "")
    fresh["usage_count"] = current.get("usage_count", 0)
    fresh["waitlisted"] = current.get("waitlisted", False)
    _users[user_id] = fresh
    _save(user_id, fresh)


def persisting(handler):
    """Decorator for telegram handlers: flushes the user's state to
    Postgres after the handler runs, regardless of how it was mutated
    (dict assignment, list.append, etc)."""
    @functools.wraps(handler)
    async def wrapper(update, context):
        try:
            return await handler(update, context)
        finally:
            user = getattr(update, "effective_user", None)
            if user is not None and user.id in _users:
                _save(user.id, _users[user.id])
    return wrapper


def _load(user_id: int) -> dict | None:
    conn = _pool.getconn()
    try:
        with conn, conn.cursor() as cur:
            cur.execute("SELECT data FROM user_state WHERE user_id = %s", (user_id,))
            row = cur.fetchone()
            return row[0] if row else None
    finally:
        _pool.putconn(conn)


# Fields sourced from `users`, not persisted into the user_state JSONB blob.
_ACCOUNT_KEYS = {"lang", "usage_count", "waitlisted"}


def _upsert_and_load_account(user_id: int) -> dict:
    """Ensure a `users` row exists for this telegram id, bump last_seen_at,
    and return their account fields. Logs a `user_seen` event exactly once,
    the moment a user's row is first created (xmax = 0 is the standard
    Postgres idiom for "this row was inserted, not updated, by this
    statement")."""
    conn = _pool.getconn()
    try:
        with conn, conn.cursor() as cur:
            cur.execute("""
                INSERT INTO users (telegram_id) VALUES (%s)
                ON CONFLICT (telegram_id) DO UPDATE SET last_seen_at = now()
                RETURNING language, checks_used, joined_waitlist, (xmax = 0) AS is_new
            """, (user_id,))
            language, checks_used, joined_waitlist, is_new = cur.fetchone()
            if is_new:
                cur.execute(
                    "INSERT INTO events (telegram_id, event_type) VALUES (%s, 'user_seen')",
                    (user_id,),
                )
            return {"language": language, "checks_used": checks_used, "joined_waitlist": joined_waitlist}
    finally:
        _pool.putconn(conn)


def _save(user_id: int, data: dict) -> None:
    session = {k: v for k, v in data.items() if k not in _ACCOUNT_KEYS}
    conn = _pool.getconn()
    try:
        with conn, conn.cursor() as cur:
            cur.execute("""
                INSERT INTO user_state (user_id, data, updated_at)
                VALUES (%s, %s, now())
                ON CONFLICT (user_id) DO UPDATE
                SET data = EXCLUDED.data, updated_at = now()
            """, (user_id, json.dumps(session)))
            cur.execute("""
                UPDATE users
                SET language = %s,
                    checks_used = %s,
                    joined_waitlist = %s,
                    waitlist_at = CASE WHEN %s AND waitlist_at IS NULL THEN now() ELSE waitlist_at END,
                    last_seen_at = now()
                WHERE telegram_id = %s
            """, (data["lang"] or None, data["usage_count"], data["waitlisted"], data["waitlisted"], user_id))
    finally:
        _pool.putconn(conn)


def _empty() -> dict:
    return {
        "phase": "idle",
        "cv_b64": "",
        "cv_text": "",
        "job_title": "",
        "location": "",
        "work_setup": "",
        "industry": "",
        "suggested_titles": [],
        "current_vacancy": None,    # the one being shown
        "seen_companies": [],       # companies already shown
        "search_count": 0,          # capped at 3
        "chosen_vacancy": None,
        "outputs": None,
        "level": "",
        "lang": "",                 # "uz" or "ru", empty until chosen
        "usage_count": 0,           # successful analyses run, lifetime
        "waitlisted": False,
    }


def join_waitlist(user_id: int, username: str | None) -> bool:
    """Add user to the waitlist. Returns True if newly added, False if already on it."""
    conn = _pool.getconn()
    try:
        with conn, conn.cursor() as cur:
            cur.execute("""
                UPDATE users
                SET joined_waitlist = true,
                    waitlist_at = COALESCE(waitlist_at, now()),
                    username = COALESCE(%s, username)
                WHERE telegram_id = %s AND NOT joined_waitlist
            """, (username, user_id))
            return cur.rowcount > 0
    finally:
        _pool.putconn(conn)


def get_quota_override(user_id: int) -> int | None:
    """Read quota_override fresh from the DB rather than the in-memory cache
    — it can be written by an entirely different process (the Payme webhook
    service, an admin /grant), so a per-process cache would miss updates
    until this bot restarts."""
    conn = _pool.getconn()
    try:
        with conn, conn.cursor() as cur:
            cur.execute("SELECT quota_override FROM users WHERE telegram_id = %s", (user_id,))
            row = cur.fetchone()
            return row[0] if row else None
    finally:
        _pool.putconn(conn)


def waitlist_count() -> int:
    conn = _pool.getconn()
    try:
        with conn, conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM users WHERE joined_waitlist")
            return cur.fetchone()[0]
    finally:
        _pool.putconn(conn)


def log_event(telegram_id: int, event_type: str, metadata: dict | None = None) -> None:
    conn = _pool.getconn()
    try:
        with conn, conn.cursor() as cur:
            cur.execute(
                "INSERT INTO events (telegram_id, event_type, metadata) VALUES (%s, %s, %s)",
                (telegram_id, event_type, json.dumps(metadata) if metadata is not None else None),
            )
    finally:
        _pool.putconn(conn)


def event_stats(event_types: list[str]) -> dict[str, tuple[int, int]]:
    """Returns {event_type: (total_count, unique_users)} for each requested type."""
    conn = _pool.getconn()
    try:
        with conn, conn.cursor() as cur:
            cur.execute("""
                SELECT event_type, count(*), count(DISTINCT telegram_id)
                FROM events
                WHERE event_type = ANY(%s)
                GROUP BY event_type
            """, (event_types,))
            rows = {row[0]: (row[1], row[2]) for row in cur.fetchall()}
    finally:
        _pool.putconn(conn)
    return {et: rows.get(et, (0, 0)) for et in event_types}


def account_stats() -> dict:
    conn = _pool.getconn()
    try:
        with conn, conn.cursor() as cur:
            cur.execute("""
                SELECT
                    count(*),
                    count(*) FILTER (WHERE checks_used > 0),
                    coalesce(sum(checks_used), 0),
                    count(*) FILTER (WHERE joined_waitlist)
                FROM users
            """)
            unique_users, activated_users, total_checks, waitlist = cur.fetchone()
    finally:
        _pool.putconn(conn)
    return {
        "unique_users": unique_users,
        "activated_users": activated_users,
        "total_checks": total_checks,
        "waitlist": waitlist,
    }
