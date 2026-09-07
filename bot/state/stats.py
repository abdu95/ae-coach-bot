"""Admin/reporting queries (/stats, pilot tracking) - counts and aggregates,
nothing here mutates state."""

import state


def waitlist_count() -> int:
    conn = state._pool.getconn()
    try:
        with conn, conn.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM users WHERE joined_waitlist")
            return cur.fetchone()[0]
    finally:
        state._pool.putconn(conn)


def source_count(source: str) -> int:
    conn = state._pool.getconn()
    try:
        with conn, conn.cursor() as cur:
            cur.execute("SELECT count(*) FROM users WHERE source = %s", (source,))
            return cur.fetchone()[0]
    finally:
        state._pool.putconn(conn)


def pilot_count() -> int:
    conn = state._pool.getconn()
    try:
        with conn, conn.cursor() as cur:
            cur.execute("SELECT count(*) FROM users WHERE source = 'school21_pilot'")
            return cur.fetchone()[0]
    finally:
        state._pool.putconn(conn)


def pilot_stats() -> dict:
    conn = state._pool.getconn()
    try:
        with conn, conn.cursor() as cur:
            cur.execute("""
                SELECT count(*), coalesce(sum(checks_used), 0), coalesce(round(avg(checks_used), 1), 0)
                FROM users WHERE source = 'school21_pilot'
            """)
            users, checks, avg = cur.fetchone()
    finally:
        state._pool.putconn(conn)
    return {"users": users, "checks": checks, "avg": float(avg)}


def reset_with_cv_count() -> int:
    """How many /reset invocations actually wiped a previously-stored CV
    (as opposed to a no-op reset with nothing to lose) — a proxy for how
    often people deliberately clear their CV data."""
    conn = state._pool.getconn()
    try:
        with conn, conn.cursor() as cur:
            cur.execute("""
                SELECT count(*) FROM events
                WHERE event_type = 'reset' AND metadata->>'had_cv' = 'true'
            """)
            return cur.fetchone()[0]
    finally:
        state._pool.putconn(conn)


def account_stats() -> dict:
    conn = state._pool.getconn()
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
        state._pool.putconn(conn)
    return {
        "unique_users": unique_users,
        "activated_users": activated_users,
        "total_checks": total_checks,
        "waitlist": waitlist,
    }
