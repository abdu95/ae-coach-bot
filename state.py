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
    finally:
        _pool.putconn(conn)


def get(user_id: int) -> dict:
    if user_id not in _users:
        loaded = _load(user_id)
        merged = _empty()
        if loaded:
            merged.update(loaded)
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


def _save(user_id: int, data: dict) -> None:
    conn = _pool.getconn()
    try:
        with conn, conn.cursor() as cur:
            cur.execute("""
                INSERT INTO user_state (user_id, data, updated_at)
                VALUES (%s, %s, now())
                ON CONFLICT (user_id) DO UPDATE
                SET data = EXCLUDED.data, updated_at = now()
            """, (user_id, json.dumps(data)))
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
                INSERT INTO waitlist (user_id, username)
                VALUES (%s, %s)
                ON CONFLICT (user_id) DO NOTHING
            """, (user_id, username))
            return cur.rowcount > 0
    finally:
        _pool.putconn(conn)


def waitlist_count() -> int:
    conn = _pool.getconn()
    try:
        with conn, conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM waitlist")
            return cur.fetchone()[0]
    finally:
        _pool.putconn(conn)
