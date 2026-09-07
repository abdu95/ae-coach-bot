"""In-memory per-user session cache (the chat-flow fields left over from
before the bot became a launcher, plus lang/name/usage/waitlist), backed
by the user_state/users tables. get()/persisting() are the two things
bot.py's handlers actually touch on every request."""

import functools
import json

import state

_users: dict = {}


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
    conn = state._pool.getconn()
    try:
        with conn, conn.cursor() as cur:
            cur.execute("SELECT data FROM user_state WHERE user_id = %s", (user_id,))
            row = cur.fetchone()
            return row[0] if row else None
    finally:
        state._pool.putconn(conn)


# Fields sourced from `users`, not persisted into the user_state JSONB blob.
_ACCOUNT_KEYS = {"lang", "usage_count", "waitlisted", "name"}


def _upsert_and_load_account(user_id: int) -> dict:
    """Ensure a `users` row exists for this telegram id, bump last_seen_at,
    and return their account fields. Logs a `user_seen` event exactly once,
    the moment a user's row is first created (xmax = 0 is the standard
    Postgres idiom for "this row was inserted, not updated, by this
    statement")."""
    conn = state._pool.getconn()
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
        state._pool.putconn(conn)


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
    conn = state._pool.getconn()
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
        state._pool.putconn(conn)


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
