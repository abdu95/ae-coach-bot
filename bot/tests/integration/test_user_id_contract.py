"""Phase 1 step 1.4: contract_internal_user_id() against a real Postgres.

What step 1.4 exists for - a user with no Telegram account (the browser
sign-ups of Phase 2) - plus the rules it tightens: users.id is the primary
key, every per-user row must belong to an existing user, and everything
keyed on telegram_id (the bot, the webapp's Telegram login, payme's
fallback) keeps working.
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
os.environ.setdefault("TELEGRAM_TOKEN", "dummy:token")

import psycopg2  # noqa: E402

from _pg import init_db, scratch_db  # noqa: E402
from schema_snapshot import diff, snapshot  # noqa: E402
from state import schema  # noqa: E402


def q(cur, sql, params=()):
    cur.execute(sql, params)
    return cur.fetchall() if cur.description else None


def rejected(cur, sql, params, *errors):
    cur.execute("SAVEPOINT s")
    try:
        cur.execute(sql, params)
    except errors:
        cur.execute("ROLLBACK TO SAVEPOINT s")
        return True
    cur.execute("ROLLBACK TO SAVEPOINT s")
    return False


with scratch_db() as dsn:
    init_db(dsn)
    conn = psycopg2.connect(dsn)

    with conn, conn.cursor() as cur:
        assert q(cur, """SELECT pg_get_constraintdef(oid) FROM pg_constraint
                         WHERE conrelid = 'users'::regclass AND contype IN ('p', 'u') ORDER BY contype""") == \
            [("PRIMARY KEY (id)",), ("UNIQUE (telegram_id)",)]
        for t in schema.USER_CHILD_TABLES:
            assert q(cur, """SELECT is_nullable FROM information_schema.columns
                             WHERE table_name = %s AND column_name = 'user_id'""", (t,)) == [("NO",)], t
            assert q(cur, "SELECT pg_get_constraintdef(oid) FROM pg_constraint WHERE conname = %s", (f"{t}_user_id_fkey",)) == \
                [("FOREIGN KEY (user_id) REFERENCES users(id)",)], t
    print("PASS: users.id is the primary key, telegram_id unique; every per-user table requires an existing user")

    # A browser user: no Telegram account at all.
    with conn, conn.cursor() as cur:
        web1 = q(cur, "INSERT INTO users (name, language) VALUES ('Sarah', 'en') RETURNING id")[0][0]
        web2 = q(cur, "INSERT INTO users (name) VALUES ('Tom') RETURNING id")[0][0]
        assert web1 != web2, "two users without a telegram_id must not collide"
        cur.execute("INSERT INTO cvs (user_id, label, cv_text, is_active) VALUES (%s, 'cv.pdf', 'cv', true)", (web1,))
        cur.execute("INSERT INTO applications (user_id, vacancy_title, vacancy_company) VALUES (%s, 'PM', 'Acme')", (web1,))
        cur.execute("INSERT INTO cv_analyses (user_id, jd_text, ats, xyz, tools, level) VALUES (%s, 'jd', '{}', '{}', '{}', '{}')", (web1,))
        cur.execute("INSERT INTO alerted_vacancies (user_id, vacancy_url) VALUES (%s, 'https://x/1')", (web1,))
        cur.execute("INSERT INTO events (user_id, event_type) VALUES (%s, 'user_seen')", (web1,))
        cur.execute("INSERT INTO orders (user_id, amount) VALUES (%s, 1000000)", (web1,))
        for t in schema.USER_CHILD_TABLES:
            assert q(cur, f"SELECT telegram_id FROM {t} WHERE user_id = %s", (web1,)) == [(None,)], t
        assert rejected(cur, "INSERT INTO cvs (user_id, label, cv_text, is_active) VALUES (%s, 'b.pdf', 'cv', true)", (web1,),
                        psycopg2.errors.UniqueViolation), "one active CV per browser user too"
        cur.execute("INSERT INTO alerted_vacancies (user_id, vacancy_url) VALUES (%s, 'https://x/1') ON CONFLICT (user_id, vacancy_url) DO NOTHING", (web1,))
        assert q(cur, "SELECT count(*) FROM alerted_vacancies WHERE user_id = %s", (web1,)) == [(1,)]
    print("PASS: a user with no Telegram account can own every kind of row; per-user rules still hold")

    with conn, conn.cursor() as cur:
        for t, cols, vals in [
            ("cvs", "user_id, label, cv_text", "%s, 'a', 'b'"),
            ("applications", "user_id, vacancy_title, vacancy_company", "%s, 't', 'c'"),
            ("cv_analyses", "user_id, jd_text, ats, xyz, tools, level", "%s, 'j', '{}', '{}', '{}', '{}'"),
            ("alerted_vacancies", "user_id, vacancy_url", "%s, 'https://x/2'"),
            ("events", "user_id, event_type", "%s, 'e'"),
            ("orders", "user_id, amount", "%s, 1"),
        ]:
            assert rejected(cur, f"INSERT INTO {t} ({cols}) VALUES ({vals})", (999_999,),
                            psycopg2.errors.ForeignKeyViolation), f"{t} accepted a non-existent user_id"
        assert rejected(cur, "DELETE FROM users WHERE id = %s", (web1,), psycopg2.errors.ForeignKeyViolation), \
            "a user with rows can't be deleted out from under them"
    print("PASS: no table accepts a row for a user that doesn't exist; users with data can't be deleted")

    # Everything keyed on telegram_id keeps working.
    with conn, conn.cursor() as cur:
        # bot/state/session.py, the webapp's ensure_user, payme-webhook's credit fallback
        a = q(cur, "INSERT INTO users (telegram_id) VALUES (9101) ON CONFLICT (telegram_id) DO UPDATE SET last_seen_at = now() RETURNING id")[0][0]
        b = q(cur, "INSERT INTO users (telegram_id, username, name) VALUES (9101, 'u', 'N') ON CONFLICT (telegram_id) DO UPDATE SET username = EXCLUDED.username RETURNING id")[0][0]
        c = q(cur, "INSERT INTO users (telegram_id, quota_override) VALUES (9101, 3) ON CONFLICT (telegram_id) DO UPDATE SET quota_override = 3 RETURNING id")[0][0]
        assert a == b == c
        assert rejected(cur, "INSERT INTO users (telegram_id) VALUES (9101)", (), psycopg2.errors.UniqueViolation)
        # Code that only writes telegram_id still gets linked rows.
        cur.execute("INSERT INTO cvs (telegram_id, label, cv_text) VALUES (9101, 'c', 'v')")
        assert q(cur, "SELECT user_id FROM cvs WHERE telegram_id = 9101") == [(a,)]
        # ...and an event/order for an unknown Telegram id is accepted (orphan user), as it always was.
        cur.execute("INSERT INTO events (telegram_id, event_type) VALUES (9202, 'x')")
        cur.execute("INSERT INTO orders (telegram_id, amount) VALUES (9202, 1)")
        assert q(cur, "SELECT count(*), min(source) FROM users WHERE telegram_id = 9202") == [(1, "backfill_orphan")]
        # A CV for an unknown Telegram id is still rejected, as before.
        assert rejected(cur, "INSERT INTO cvs (telegram_id, label, cv_text) VALUES (9303, 'c', 'v')", (),
                        psycopg2.errors.NotNullViolation, psycopg2.errors.ForeignKeyViolation)
    print("PASS: telegram_id upserts, telegram_id-only writes and the orphan rule all still work")

    # Legacy single-CV backfill keeps working once browser users' CVs (telegram_id NULL) exist.
    with conn, conn.cursor() as cur:
        cur.execute("""INSERT INTO user_state (user_id, data) VALUES (9404, '{"cv_text": "old CV"}')""")
    init_db(dsn)
    with conn, conn.cursor() as cur:
        assert q(cur, "SELECT c.cv_text, u.id IS NOT NULL FROM cvs c JOIN users u ON u.id = c.user_id WHERE u.telegram_id = 9404") == [("old CV", True)], \
            "NOT IN against a NULL telegram_id would have silently skipped this"
    print("PASS: the legacy CV backfill still runs with browser users' NULL telegram_ids present")

    # Idempotent: every redeploy re-runs init_db.
    with conn, conn.cursor() as cur:
        before = snapshot(cur)
    init_db(dsn)
    init_db(dsn)
    with conn, conn.cursor() as cur:
        assert diff(before, snapshot(cur)) == [], diff(before, snapshot(cur))
        assert q(cur, "SELECT count(*) FROM pg_indexes WHERE tablename = 'users' AND indexdef LIKE '%%(id)'") == [(1,)], \
            "only the primary key index on users.id - no duplicate recreated on restart"
    print("PASS: re-running init_db changes nothing (no duplicate index on users.id)")
    conn.close()

print("\nALL USER-ID CONTRACT CHECKS PASSED")
