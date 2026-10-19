"""Phase 1 step 1.2: migrate_internal_user_id() against a real Postgres.

Builds the pre-migration schema (everything init_db ran before the
migration existed), fills it the way prod looks - including an orphan
order/event and the e2e harness's negative-id users - then checks the
migration links every row, is idempotent, and that today's INSERT
statements (which only know telegram_id) keep producing linked rows.
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
os.environ.setdefault("TELEGRAM_TOKEN", "dummy:token")

import psycopg2  # noqa: E402

from _pg import init_db, scratch_db  # noqa: E402
from state import schema  # noqa: E402

CHILDREN = schema.USER_CHILD_TABLES
ALICE, BOB, E2E, ORPHAN = 7001, 7002, -1798134001, 99999003


def q(cur, sql, params=()):
    cur.execute(sql, params)
    return cur.fetchall()


def unlinked(cur):
    """Rows whose user_id is missing or doesn't match their telegram_id's user."""
    out = {}
    for t in CHILDREN:
        out[t] = q(cur, f"""
            SELECT count(*) FROM {t} c LEFT JOIN users u ON u.id = c.user_id
            WHERE c.user_id IS NULL OR u.telegram_id IS DISTINCT FROM c.telegram_id
        """)[0][0]
    return {t: n for t, n in out.items() if n}


with scratch_db() as dsn:
    conn = psycopg2.connect(dsn)
    with conn, conn.cursor() as cur:
        # Pre-migration schema, exactly as init_db built it before step 1.2.
        schema.create_tables(cur)
        schema.migrate_legacy_state(cur)
        schema.migrate_legacy_cv_text(cur)
        # Data shaped like prod. Statements copied from today's code paths.
        for tid in (ALICE, BOB, E2E):
            cur.execute("INSERT INTO users (telegram_id) VALUES (%s)", (tid,))
        cur.execute("INSERT INTO cvs (telegram_id, label, cv_text, is_active) VALUES (%s, 'a.pdf', 'cv a', false), (%s, 'b.pdf', 'cv b', true), (%s, 'c.pdf', 'cv c', true)", (ALICE, ALICE, BOB))
        cur.execute("INSERT INTO applications (telegram_id, vacancy_title, vacancy_company) VALUES (%s, 'Analyst', 'Acme')", (ALICE,))
        cur.execute("INSERT INTO cv_analyses (telegram_id, jd_text, ats, xyz, tools, level) VALUES (%s, 'jd', '{}', '{}', '{}', '{}')", (BOB,))
        cur.execute("INSERT INTO alerted_vacancies (telegram_id, vacancy_url) VALUES (%s, 'https://x/1')", (ALICE,))
        cur.execute("INSERT INTO events (telegram_id, event_type) VALUES (%s, 'started'), (%s, 'started'), (%s, 'user_seen'), (%s, 'payme_test')", (ALICE, BOB, E2E, ORPHAN))
        cur.execute("INSERT INTO orders (telegram_id, amount) VALUES (%s, 9900000), (%s, 9900000)", (BOB, ORPHAN))
        cur.execute("INSERT INTO payme_transactions (payme_id, order_id, amount) SELECT 'p1', id, amount FROM orders WHERE telegram_id = %s", (ORPHAN,))
        before = {t: q(cur, f"SELECT count(*) FROM {t}")[0][0] for t in CHILDREN + ("users", "payme_transactions")}

    # Run the real startup path (init_db = create_tables + backfills + migration).
    init_db(dsn)
    with conn, conn.cursor() as cur:
        assert unlinked(cur) == {}, f"rows not linked to their user: {unlinked(cur)}"
        after = {t: q(cur, f"SELECT count(*) FROM {t}")[0][0] for t in before}
        assert after == {**before, "users": before["users"] + 1}, (before, after)
        assert q(cur, "SELECT source FROM users WHERE telegram_id = %s", (ORPHAN,)) == [("backfill_orphan",)]
        assert q(cur, "SELECT count(*) FROM users WHERE id IS NULL") == [(0,)]
        assert q(cur, "SELECT count(*), count(DISTINCT id) FROM users")[0] == (4, 4)
        ids = dict(q(cur, "SELECT telegram_id, id FROM users"))
    print("PASS: every existing row is linked to its user; no rows added or lost except the one orphan's user")

    init_db(dsn)  # every redeploy runs it again
    with conn, conn.cursor() as cur:
        assert dict(q(cur, "SELECT telegram_id, id FROM users")) == ids, "user ids must be stable across restarts"
        assert {t: q(cur, f"SELECT count(*) FROM {t}")[0][0] for t in before} == after
        assert unlinked(cur) == {}
    print("PASS: re-running is a no-op and internal ids never change")

    # Today's code only writes telegram_id; the trigger must link new rows.
    with conn, conn.cursor() as cur:
        cur.execute("INSERT INTO users (telegram_id) VALUES (7003) ON CONFLICT (telegram_id) DO UPDATE SET last_seen_at = now() RETURNING id")
        carol_id = cur.fetchone()[0]
        assert carol_id is not None and carol_id not in ids.values()
        cur.execute("INSERT INTO cvs (telegram_id, label, cv_text, is_active) VALUES (7003, 'c.pdf', 'cv', true)")
        cur.execute("INSERT INTO applications (telegram_id, vacancy_title, vacancy_company) VALUES (7003, 't', 'c')")
        cur.execute("INSERT INTO cv_analyses (telegram_id, jd_text, ats, xyz, tools, level) VALUES (7003, 'jd', '{}', '{}', '{}', '{}')")
        cur.execute("INSERT INTO alerted_vacancies (telegram_id, vacancy_url) VALUES (7003, 'https://x/2')")
        cur.execute("INSERT INTO events (telegram_id, event_type) VALUES (7003, 'user_seen')")
        cur.execute("INSERT INTO orders (telegram_id, amount, package) VALUES (7003, 1000000, '1_checks')")
        assert unlinked(cur) == {}, unlinked(cur)
        # The webapp's ensure_user and payme's credit_user upserts still work as before.
        cur.execute("INSERT INTO users (telegram_id, username, name) VALUES (7003, 'carol', 'Carol') ON CONFLICT (telegram_id) DO UPDATE SET username = EXCLUDED.username")
        cur.execute("INSERT INTO users (telegram_id, quota_override) VALUES (7003, 12) ON CONFLICT (telegram_id) DO UPDATE SET quota_override = 12")
        assert q(cur, "SELECT id, username, quota_override FROM users WHERE telegram_id = 7003") == [(carol_id, "carol", 12)]
    print("PASS: inserts that only know telegram_id still get the right user_id (all 6 tables)")

    # Step 1.3 direction: code switched to the internal id writes only user_id.
    with conn, conn.cursor() as cur:
        dave_id = q(cur, "INSERT INTO users (telegram_id) VALUES (7004) RETURNING id")[0][0]
        cur.execute("INSERT INTO cvs (user_id, label, cv_text, is_active) VALUES (%s, 'd.pdf', 'cv', true)", (dave_id,))
        cur.execute("INSERT INTO applications (user_id, vacancy_title, vacancy_company) VALUES (%s, 't', 'c')", (dave_id,))
        cur.execute("INSERT INTO cv_analyses (user_id, jd_text, ats, xyz, tools, level) VALUES (%s, 'jd', '{}', '{}', '{}', '{}')", (dave_id,))
        cur.execute("INSERT INTO alerted_vacancies (user_id, vacancy_url) VALUES (%s, 'https://x/3')", (dave_id,))
        cur.execute("INSERT INTO events (user_id, event_type) VALUES (%s, 'user_seen')", (dave_id,))
        cur.execute("INSERT INTO orders (user_id, amount) VALUES (%s, 1000000)", (dave_id,))
        assert unlinked(cur) == {}, unlinked(cur)
        for t in CHILDREN:
            assert q(cur, f"SELECT telegram_id FROM {t} WHERE user_id = %s", (dave_id,)) == [(7004,)], t
        # The same rules, keyed by user_id.
        cur.execute("INSERT INTO alerted_vacancies (user_id, vacancy_url) VALUES (%s, 'https://x/3') ON CONFLICT (user_id, vacancy_url) DO NOTHING", (dave_id,))
        assert q(cur, "SELECT count(*) FROM alerted_vacancies WHERE user_id = %s", (dave_id,)) == [(1,)]
        try:
            cur.execute("SAVEPOINT s")
            cur.execute("INSERT INTO cvs (user_id, label, cv_text, is_active) VALUES (%s, 'e.pdf', 'cv', true)", (dave_id,))
            raise AssertionError("second active CV accepted when written by user_id")
        except psycopg2.errors.UniqueViolation:
            cur.execute("ROLLBACK TO SAVEPOINT s")
    print("PASS: inserts that only know user_id get telegram_id filled in, and per-user rules still hold")

    with conn, conn.cursor() as cur:
        # An event for a telegram_id with no users row is still accepted, as before;
        # since step 1.4 (user_id NOT NULL) it gets a bare backfill_orphan user.
        cur.execute("INSERT INTO events (telegram_id, event_type) VALUES (424242, 'x') RETURNING user_id")
        orphan_id = cur.fetchone()[0]
        assert q(cur, "SELECT telegram_id, source FROM users WHERE id = %s", (orphan_id,)) == [(424242, "backfill_orphan")]
        # The one-active-CV rule and the users FK are unchanged.
        try:
            cur.execute("SAVEPOINT s")
            cur.execute("INSERT INTO cvs (telegram_id, label, cv_text, is_active) VALUES (%s, 'z', 'z', true)", (BOB,))
            raise AssertionError("second active CV accepted")
        except psycopg2.errors.UniqueViolation:
            cur.execute("ROLLBACK TO SAVEPOINT s")
        try:
            cur.execute("SAVEPOINT s")
            cur.execute("INSERT INTO cvs (telegram_id, label, cv_text) VALUES (515151, 'z', 'z')")
            raise AssertionError("cv for unknown user accepted")
        except (psycopg2.errors.ForeignKeyViolation, psycopg2.errors.NotNullViolation):
            # Before step 1.4 the telegram_id FK rejected it; since then user_id NOT NULL does.
            cur.execute("ROLLBACK TO SAVEPOINT s")
        conn.rollback()
    print("PASS: existing rules unchanged (unknown-user events allowed, one active CV, users FK)")
    conn.close()

print("\nALL USER-ID MIGRATION CHECKS PASSED")
