"""The safety net under every schema migration: a fresh database built by
the bot's real init_db() must have exactly prod's structure
(prod_schema.json), and re-running init_db (which happens on every deploy)
must be harmless.

When a migration intentionally changes the schema, this test fails until
prod_schema.json is re-captured after that migration reaches prod (see
schema_snapshot.py for the command). Until then, the failing diff is the
exact list of what the migration will change in prod.
"""

import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
os.environ.setdefault("TELEGRAM_TOKEN", "dummy:token")

import psycopg2  # noqa: E402

from _pg import init_db, scratch_db  # noqa: E402
from schema_snapshot import diff, snapshot  # noqa: E402

PROD = json.loads((Path(__file__).resolve().parent / "prod_schema.json").read_text())


def take(dsn):
    with psycopg2.connect(dsn) as conn, conn.cursor() as cur:
        return snapshot(cur)


with scratch_db() as dsn:
    init_db(dsn)
    first = take(dsn)
    problems = diff(PROD, first)
    assert not problems, "fresh init_db() schema differs from prod:\n  " + "\n  ".join(problems)
    print("PASS: a fresh init_db() produces exactly prod's schema")

    init_db(dsn)
    problems = diff(first, take(dsn))
    assert not problems, "second init_db() changed the schema:\n  " + "\n  ".join(problems)
    print("PASS: running init_db() a second time (every redeploy) changes nothing")

    # Legacy backfills: a pre-`users`-table user whose state (language,
    # usage, waitlist, single CV) only lives in user_state's JSON blob.
    with psycopg2.connect(dsn) as conn, conn.cursor() as cur:
        cur.execute("""
            INSERT INTO user_state (user_id, data) VALUES
            (1001, '{"lang": "uz", "usage_count": 2, "waitlisted": true, "cv_text": "Legacy CV"}'),
            (1002, '{"lang": "", "usage_count": 0}')
        """)
    init_db(dsn)
    init_db(dsn)  # twice: backfills must not duplicate on later deploys
    with psycopg2.connect(dsn) as conn, conn.cursor() as cur:
        cur.execute("SELECT telegram_id, language, checks_used, joined_waitlist FROM users ORDER BY 1")
        assert cur.fetchall() == [(1001, "uz", 2, True), (1002, None, 0, False)]
        cur.execute("SELECT telegram_id, label, cv_text, is_active FROM cvs")
        assert cur.fetchall() == [(1001, "My CV", "Legacy CV", True)]
    print("PASS: legacy user_state rows backfill into users/cvs exactly once")

    # Things today's code depends on, checked as behavior rather than DDL text.
    with psycopg2.connect(dsn) as conn, conn.cursor() as cur:
        cur.execute("INSERT INTO cvs (telegram_id, label, cv_text, is_active) VALUES (1002, 'a', 'x', true)")
        try:
            cur.execute("SAVEPOINT s")
            cur.execute("INSERT INTO cvs (telegram_id, label, cv_text, is_active) VALUES (1002, 'b', 'y', true)")
            raise AssertionError("a second active CV for the same user was accepted")
        except psycopg2.errors.UniqueViolation:
            cur.execute("ROLLBACK TO SAVEPOINT s")
        try:
            cur.execute("SAVEPOINT s")
            cur.execute("INSERT INTO applications (telegram_id, vacancy_title, vacancy_company) VALUES (424242, 't', 'c')")
            raise AssertionError("an application for a non-existent user was accepted")
        except psycopg2.errors.ForeignKeyViolation:
            cur.execute("ROLLBACK TO SAVEPOINT s")
        cur.execute("INSERT INTO orders (telegram_id, amount) VALUES (1002, 9900000) RETURNING package, state")
        assert cur.fetchone() == ("10_checks", "pending")
    print("PASS: one-active-CV rule, users foreign key and orders defaults hold")

print("\nALL SCHEMA CHECKS PASSED")
