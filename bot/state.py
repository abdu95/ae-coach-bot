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
            # user_state holds the session/flow fields (see _ACCOUNT_KEYS split
            # in _save) — actively read/written on every request, not legacy.
            cur.execute("""
                CREATE TABLE IF NOT EXISTS user_state (
                    user_id BIGINT PRIMARY KEY,
                    data JSONB NOT NULL,
                    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
                )
            """)
            cur.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    telegram_id     BIGINT PRIMARY KEY,
                    username        TEXT,
                    name            TEXT,
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
            cur.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS name TEXT")
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
            # One row per tracked application. cv_snapshot/match_score/matched_keywords/
            # missing_keywords capture which CV version was used and how it scored
            # against this vacancy at the moment of applying - the exact link a
            # spreadsheet can't give you (see backlog doc §5, Application Tracking).
            cur.execute("""
                CREATE TABLE IF NOT EXISTS applications (
                    id                 BIGSERIAL PRIMARY KEY,
                    telegram_id        BIGINT NOT NULL REFERENCES users(telegram_id),
                    vacancy_title      TEXT NOT NULL,
                    vacancy_company    TEXT NOT NULL,
                    vacancy_location   TEXT,
                    vacancy_url        TEXT,
                    vacancy_summary    TEXT,
                    cv_snapshot        TEXT,
                    match_score        INT,
                    matched_keywords   JSONB,
                    missing_keywords   JSONB,
                    status             TEXT NOT NULL DEFAULT 'applied',
                    recruiter_contacted BOOLEAN NOT NULL DEFAULT FALSE,
                    notes              TEXT,
                    source             TEXT,
                    created_at         TIMESTAMPTZ NOT NULL DEFAULT now(),
                    updated_at         TIMESTAMPTZ NOT NULL DEFAULT now()
                )
            """)
            cur.execute("CREATE INDEX IF NOT EXISTS idx_applications_telegram_id ON applications (telegram_id)")
            # Replaces the hand-maintained COMPANIES list that used to be
            # hardcoded (and duplicated between bot/ and webapp/, until the
            # bot/ copy was deleted as dead code) in greenhouse_source.py.
            # Edit webapp/greenhouse_companies.csv
            # and run webapp/scripts/sync_greenhouse_companies.py to add/
            # remove/rename a verified company - no deploy needed, takes
            # effect within webapp/db.py's cache TTL. Never delete a row on
            # removal, only deactivate - keeps history of what was tried.
            cur.execute("""
                CREATE TABLE IF NOT EXISTS greenhouse_companies (
                    slug         TEXT PRIMARY KEY,
                    display_name TEXT NOT NULL,
                    domain       TEXT,
                    active       BOOLEAN NOT NULL DEFAULT TRUE,
                    created_at   TIMESTAMPTZ NOT NULL DEFAULT now()
                )
            """)
            # Multiple saved CVs per user (the "My CVs" page), replacing the
            # single user_state.data->>'cv_text' field. Exactly one row per
            # user may have is_active=true at a time - that's the CV every
            # other feature (analysis, vacancy scoring, applications) reads
            # via webapp/db.py's get_active_cv_text(), so uploading a new CV
            # or switching the active one needs no changes anywhere else.
            cur.execute("""
                CREATE TABLE IF NOT EXISTS cvs (
                    id                 BIGSERIAL PRIMARY KEY,
                    telegram_id        BIGINT NOT NULL REFERENCES users(telegram_id),
                    label              TEXT NOT NULL,
                    cv_text            TEXT NOT NULL,
                    is_active          BOOLEAN NOT NULL DEFAULT FALSE,
                    extracted_position TEXT,
                    created_at         TIMESTAMPTZ NOT NULL DEFAULT now()
                )
            """)
            cur.execute("ALTER TABLE cvs ADD COLUMN IF NOT EXISTS extracted_position TEXT")
            cur.execute("CREATE INDEX IF NOT EXISTS idx_cvs_telegram_id ON cvs (telegram_id)")
            cur.execute("""
                CREATE UNIQUE INDEX IF NOT EXISTS idx_cvs_one_active_per_user
                ON cvs (telegram_id) WHERE is_active
            """)
            _migrate_legacy_state(cur)
            _migrate_legacy_cv_text(cur)
    finally:
        _pool.putconn(conn)


def _migrate_legacy_state(cur) -> None:
    """Backfill users from the legacy user_state table. Safe to run on every
    startup: ON CONFLICT DO NOTHING means an already-migrated user (one with
    a `users` row) is left untouched, so this is a no-op once every
    pre-existing user has been copied over exactly once."""
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


def _migrate_legacy_cv_text(cur) -> None:
    """Backfill `cvs` from the legacy single-CV field (user_state's
    data->>'cv_text') for anyone who uploaded a CV before the multi-CV
    `cvs` table existed. Safe on every startup: only inserts for
    telegram_ids with a non-empty legacy cv_text and no `cvs` row yet,
    so it's a no-op once every pre-existing user has been copied over."""
    cur.execute("""
        INSERT INTO cvs (telegram_id, label, cv_text, is_active)
        SELECT user_id, 'My CV', data->>'cv_text', true
        FROM user_state
        WHERE data->>'cv_text' IS NOT NULL AND data->>'cv_text' != ''
          AND user_id NOT IN (SELECT telegram_id FROM cvs)
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
        merged["name"] = account["name"] or ""
        _users[user_id] = merged
    return _users[user_id]


def reset(user_id: int) -> None:
    current = get(user_id)
    fresh = _empty()
    fresh["lang"] = current.get("lang", "")
    fresh["usage_count"] = current.get("usage_count", 0)
    fresh["waitlisted"] = current.get("waitlisted", False)
    fresh["name"] = current.get("name", "")
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
_ACCOUNT_KEYS = {"lang", "usage_count", "waitlisted", "name"}


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
                RETURNING language, checks_used, joined_waitlist, name, (xmax = 0) AS is_new
            """, (user_id,))
            language, checks_used, joined_waitlist, name, is_new = cur.fetchone()
            if is_new:
                cur.execute(
                    "INSERT INTO events (telegram_id, event_type) VALUES (%s, 'user_seen')",
                    (user_id,),
                )
            return {"language": language, "checks_used": checks_used, "joined_waitlist": joined_waitlist, "name": name}
    finally:
        _pool.putconn(conn)


def _save(user_id: int, data: dict) -> None:
    # checks_used is deliberately NOT written here. bot.py hasn't incremented
    # usage_count since the Stage 3 migration (the CV-analysis flow that used
    # to do that now lives entirely in the Mini App, which increments
    # checks_used itself via webapp/db.py). But this dict's cached
    # "usage_count" is only refreshed from the DB once per process (see
    # get()), so if the bot's cache went stale relative to a webapp-side
    # increment, writing it back here would silently roll back real usage -
    # exactly what happened to a real user (2026-09-06): the bot's cached
    # copy of his checks_used lagged behind two webapp-side increments, and
    # the next bot handler call (persisting() -> _save()) overwrote the
    # correct DB value with the stale cached one, letting him run one extra
    # free analysis he shouldn't have had. Treat checks_used the same way
    # quota_override already is (see get_quota_override) - owned by
    # whichever process actually changes it, never blindly written back by
    # a reader that just happens to be holding a stale in-memory copy.
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
                    joined_waitlist = %s,
                    waitlist_at = CASE WHEN %s AND waitlist_at IS NULL THEN now() ELSE waitlist_at END,
                    name = %s,
                    last_seen_at = now()
                WHERE telegram_id = %s
            """, (data["lang"] or None, data["waitlisted"], data["waitlisted"], data["name"] or None, user_id))
    finally:
        _pool.putconn(conn)


def _empty() -> dict:
    return {
        "phase": "idle",
        "name": "",
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
        "cv_fixes": [],             # parsed Top-5 CV fixes, shown one at a time
        "lang": "",                 # "uz" or "ru", empty until chosen
        "usage_count": 0,           # successful analyses run, lifetime
        "waitlisted": False,
        "awaiting_custom_checks": False,  # true while waiting for a typed check quantity
        "app_nudge_sent": False,    # one-time /app discovery nudge after first completed roadmap
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


def get_or_create_order(telegram_id: int, amount: int, package: str) -> int:
    """Reuses an existing pending order for this user+package instead of
    creating a new row every time the limit-reached message is shown, so
    repeated prompts don't pile up dead `orders` rows. Refreshes the amount
    on reuse so a reused order always matches the currently-configured
    price — otherwise a stale pending order from before a price change
    would disagree with the checkout link built from the new price,
    and Payme would reject the transaction as an amount mismatch."""
    conn = _pool.getconn()
    try:
        with conn, conn.cursor() as cur:
            cur.execute("""
                UPDATE orders SET amount = %s
                WHERE id = (
                    SELECT id FROM orders
                    WHERE telegram_id = %s AND package = %s AND state = 'pending'
                    ORDER BY created_at DESC LIMIT 1
                )
                RETURNING id
            """, (amount, telegram_id, package))
            row = cur.fetchone()
            if row:
                return row[0]
            cur.execute("""
                INSERT INTO orders (telegram_id, amount, package)
                VALUES (%s, %s, %s)
                RETURNING id
            """, (telegram_id, amount, package))
            return cur.fetchone()[0]
    finally:
        _pool.putconn(conn)


def set_quota_override(user_id: int, quota: int, source: str | None = None) -> bool:
    """Returns False if this telegram_id has no `users` row yet (never
    interacted with the bot), since UPDATE is a silent no-op in that case."""
    conn = _pool.getconn()
    try:
        with conn, conn.cursor() as cur:
            cur.execute("""
                UPDATE users
                SET quota_override = %s, source = COALESCE(%s, source)
                WHERE telegram_id = %s
            """, (quota, source, user_id))
            return cur.rowcount > 0
    finally:
        _pool.putconn(conn)


def set_source(user_id: int, source: str) -> None:
    conn = _pool.getconn()
    try:
        with conn, conn.cursor() as cur:
            cur.execute("UPDATE users SET source = %s WHERE telegram_id = %s", (source, user_id))
    finally:
        _pool.putconn(conn)


def get_source(user_id: int) -> str | None:
    conn = _pool.getconn()
    try:
        with conn, conn.cursor() as cur:
            cur.execute("SELECT source FROM users WHERE telegram_id = %s", (user_id,))
            row = cur.fetchone()
            return row[0] if row else None
    finally:
        _pool.putconn(conn)


def source_count(source: str) -> int:
    conn = _pool.getconn()
    try:
        with conn, conn.cursor() as cur:
            cur.execute("SELECT count(*) FROM users WHERE source = %s", (source,))
            return cur.fetchone()[0]
    finally:
        _pool.putconn(conn)


def pilot_count() -> int:
    conn = _pool.getconn()
    try:
        with conn, conn.cursor() as cur:
            cur.execute("SELECT count(*) FROM users WHERE source = 'school21_pilot'")
            return cur.fetchone()[0]
    finally:
        _pool.putconn(conn)


def payment_stats() -> dict:
    """Reads directly from `orders` (state='paid') rather than an event
    log, so it's accurate from day one - covers every payment ever made,
    including ones from before any payment-specific event existed."""
    conn = _pool.getconn()
    try:
        with conn, conn.cursor() as cur:
            cur.execute("""
                SELECT count(*), count(DISTINCT telegram_id), coalesce(sum(amount), 0)
                FROM orders WHERE state = 'paid'
            """)
            count, unique_payers, total_tiyin = cur.fetchone()
    finally:
        _pool.putconn(conn)
    return {"count": count, "unique_payers": unique_payers, "total_uzs": total_tiyin // 100}


def pilot_stats() -> dict:
    conn = _pool.getconn()
    try:
        with conn, conn.cursor() as cur:
            cur.execute("""
                SELECT count(*), coalesce(sum(checks_used), 0), coalesce(round(avg(checks_used), 1), 0)
                FROM users WHERE source = 'school21_pilot'
            """)
            users, checks, avg = cur.fetchone()
    finally:
        _pool.putconn(conn)
    return {"users": users, "checks": checks, "avg": float(avg)}


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


def reset_with_cv_count() -> int:
    """How many /reset invocations actually wiped a previously-stored CV
    (as opposed to a no-op reset with nothing to lose) — a proxy for how
    often people deliberately clear their CV data."""
    conn = _pool.getconn()
    try:
        with conn, conn.cursor() as cur:
            cur.execute("""
                SELECT count(*) FROM events
                WHERE event_type = 'reset' AND metadata->>'had_cv' = 'true'
            """)
            return cur.fetchone()[0]
    finally:
        _pool.putconn(conn)


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
