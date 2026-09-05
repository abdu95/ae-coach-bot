"""
Minimal DB access for vacancy-webapp, sharing the same Postgres the bot
uses (tables are created by bot/state.py's init_db() - this module only
reads/writes, never creates schema).
"""

import json
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


def ensure_user(telegram_id: int, username: str | None, name: str | None) -> None:
    """Upserts a `users` row for this telegram_id, mirroring what
    bot/state.py's _upsert_and_load_account does. Required before any
    write to `applications`, since that table has
    telegram_id REFERENCES users(telegram_id) - a user who only ever
    opens the Mini App (never /start in chat) would otherwise have no
    `users` row and every save would fail on the FK constraint."""
    pool = get_pool()
    conn = pool.getconn()
    try:
        with conn, conn.cursor() as cur:
            cur.execute("""
                INSERT INTO users (telegram_id, username, name)
                VALUES (%s, %s, %s)
                ON CONFLICT (telegram_id) DO UPDATE
                SET last_seen_at = now(),
                    username = COALESCE(EXCLUDED.username, users.username),
                    name = COALESCE(users.name, EXCLUDED.name)
            """, (telegram_id, username, name))
    finally:
        pool.putconn(conn)


def get_user_language(telegram_id: int) -> str:
    """Returns the language the user picked in the bot (uz/ru), matching
    bot/i18n.py's fallback: empty/unset -> "en". Deliberately NOT the
    device's system language (Telegram's initData.user.language_code) -
    that reflects the phone's OS locale, not what the user actually chose
    via the bot's language picker (see bot.py's send_language_picker)."""
    pool = get_pool()
    conn = pool.getconn()
    try:
        with conn, conn.cursor() as cur:
            cur.execute("SELECT language FROM users WHERE telegram_id = %s", (telegram_id,))
            row = cur.fetchone()
            return row[0] if row and row[0] else "en"
    finally:
        pool.putconn(conn)


def get_cv_text(telegram_id: int) -> str | None:
    pool = get_pool()
    conn = pool.getconn()
    try:
        with conn, conn.cursor() as cur:
            cur.execute("SELECT data->>'cv_text' FROM user_state WHERE user_id = %s", (telegram_id,))
            row = cur.fetchone()
            return row[0] if row and row[0] else None
    finally:
        pool.putconn(conn)


def save_cv_text(telegram_id: int, cv_text: str) -> None:
    """Merges cv_text into user_state's JSONB blob without touching any
    other field (jsonb `||` is a shallow top-level merge) - safe even if
    the bot's chat flow also reads/writes this same row concurrently."""
    pool = get_pool()
    conn = pool.getconn()
    try:
        with conn, conn.cursor() as cur:
            cur.execute("""
                INSERT INTO user_state (user_id, data, updated_at)
                VALUES (%s, jsonb_build_object('cv_text', %s::text), now())
                ON CONFLICT (user_id) DO UPDATE
                SET data = user_state.data || jsonb_build_object('cv_text', %s::text),
                    updated_at = now()
            """, (telegram_id, cv_text, cv_text))
    finally:
        pool.putconn(conn)


def save_application(telegram_id: int, vacancy: dict, cv_snapshot: str,
                      score: dict | None, source: str = "webapp") -> None:
    pool = get_pool()
    conn = pool.getconn()
    try:
        with conn, conn.cursor() as cur:
            cur.execute("""
                INSERT INTO applications (
                    telegram_id, vacancy_title, vacancy_company, vacancy_location,
                    vacancy_url, vacancy_summary, cv_snapshot, match_score,
                    matched_keywords, missing_keywords, source
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                telegram_id, vacancy["title"], vacancy["company"], vacancy.get("location"),
                vacancy.get("url"), vacancy.get("summary"), cv_snapshot,
                score.get("score") if score else None,
                json.dumps(score.get("matched")) if score else None,
                json.dumps(score.get("missing")) if score else None,
                source,
            ))
    finally:
        pool.putconn(conn)


VALID_STATUSES = {"applied", "phone_screen", "tech_interview", "offer", "rejected", "ghosted"}


def update_application_status(telegram_id: int, application_id: int, status: str) -> bool:
    """Returns False if the application doesn't exist or doesn't belong to
    this telegram_id - callers must treat that as "not found", never
    leak whether some other user's application_id exists."""
    if status not in VALID_STATUSES:
        raise ValueError(f"Invalid status: {status}")
    pool = get_pool()
    conn = pool.getconn()
    try:
        with conn, conn.cursor() as cur:
            cur.execute("""
                UPDATE applications SET status = %s, updated_at = now()
                WHERE id = %s AND telegram_id = %s
            """, (status, application_id, telegram_id))
            return cur.rowcount > 0
    finally:
        pool.putconn(conn)


def delete_application(telegram_id: int, application_id: int) -> bool:
    pool = get_pool()
    conn = pool.getconn()
    try:
        with conn, conn.cursor() as cur:
            cur.execute("""
                DELETE FROM applications WHERE id = %s AND telegram_id = %s
            """, (application_id, telegram_id))
            return cur.rowcount > 0
    finally:
        pool.putconn(conn)


def list_applications(telegram_id: int) -> list[dict]:
    pool = get_pool()
    conn = pool.getconn()
    try:
        with conn, conn.cursor() as cur:
            cur.execute("""
                SELECT id, vacancy_title, vacancy_company, vacancy_location, vacancy_url,
                       match_score, status, created_at
                FROM applications
                WHERE telegram_id = %s
                ORDER BY created_at DESC
            """, (telegram_id,))
            rows = cur.fetchall()
        return [
            {
                "id": r[0], "title": r[1], "company": r[2], "location": r[3],
                "url": r[4], "match_score": r[5], "status": r[6],
                "created_at": r[7].isoformat(),
            }
            for r in rows
        ]
    finally:
        pool.putconn(conn)


# Must match ae-coach-bot's FREE_LIMIT (bot/bot.py) - same quota pool,
# shared `users.checks_used`/`quota_override` columns.
FREE_LIMIT = int(os.getenv("FREE_LIMIT", "2"))


def get_quota_status(telegram_id: int) -> tuple[int, int]:
    """Returns (usage_count, effective_quota), mirroring bot/state.py's
    get_quota_override + bot/bot.py's effective_quota exactly - a real
    quota_override (set by an admin /grant or a Payme purchase, from
    either service) always wins over FREE_LIMIT."""
    pool = get_pool()
    conn = pool.getconn()
    try:
        with conn, conn.cursor() as cur:
            cur.execute("SELECT checks_used, quota_override FROM users WHERE telegram_id = %s", (telegram_id,))
            row = cur.fetchone()
            if not row:
                return 0, FREE_LIMIT
            checks_used, quota_override = row
            return checks_used, (quota_override if quota_override is not None else FREE_LIMIT)
    finally:
        pool.putconn(conn)


def increment_usage_count(telegram_id: int) -> None:
    """Called once, only after a successful analyze_cv - matches the bot's
    exact quota semantics (roadmap/CV-fix follow-ons stay free)."""
    pool = get_pool()
    conn = pool.getconn()
    try:
        with conn, conn.cursor() as cur:
            cur.execute("UPDATE users SET checks_used = checks_used + 1 WHERE telegram_id = %s", (telegram_id,))
    finally:
        pool.putconn(conn)


def get_or_create_order(telegram_id: int, amount: int, package: str) -> int:
    """Same `orders` table and reuse-pending-order logic as
    bot/state.py's get_or_create_order - orders created here are
    indistinguishable to payme-webhook from ones created by the bot."""
    pool = get_pool()
    conn = pool.getconn()
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
        pool.putconn(conn)


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
