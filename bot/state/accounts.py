"""Per-user account fields on `users`: waitlist, quota override, marketing source."""

import state


def join_waitlist(user_id: int, username: str | None) -> bool:
    """Add user to the waitlist. Returns True if newly added, False if already on it."""
    conn = state._pool.getconn()
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
        state._pool.putconn(conn)


def get_quota_override(user_id: int) -> int | None:
    """Read quota_override fresh from the DB rather than the in-memory cache
    — it can be written by an entirely different process (the Payme webhook
    service, an admin /grant), so a per-process cache would miss updates
    until this bot restarts."""
    conn = state._pool.getconn()
    try:
        with conn, conn.cursor() as cur:
            cur.execute("SELECT quota_override FROM users WHERE telegram_id = %s", (user_id,))
            row = cur.fetchone()
            return row[0] if row else None
    finally:
        state._pool.putconn(conn)


def set_quota_override(user_id: int, quota: int, source: str | None = None) -> bool:
    """Returns False if this telegram_id has no `users` row yet (never
    interacted with the bot), since UPDATE is a silent no-op in that case."""
    conn = state._pool.getconn()
    try:
        with conn, conn.cursor() as cur:
            cur.execute("""
                UPDATE users
                SET quota_override = %s, source = COALESCE(%s, source)
                WHERE telegram_id = %s
            """, (quota, source, user_id))
            return cur.rowcount > 0
    finally:
        state._pool.putconn(conn)


def set_source(user_id: int, source: str) -> None:
    conn = state._pool.getconn()
    try:
        with conn, conn.cursor() as cur:
            cur.execute("UPDATE users SET source = %s WHERE telegram_id = %s", (source, user_id))
    finally:
        state._pool.putconn(conn)


def get_source(user_id: int) -> str | None:
    conn = state._pool.getconn()
    try:
        with conn, conn.cursor() as cur:
            cur.execute("SELECT source FROM users WHERE telegram_id = %s", (user_id,))
            row = cur.fetchone()
            return row[0] if row else None
    finally:
        state._pool.putconn(conn)
