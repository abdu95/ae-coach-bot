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
