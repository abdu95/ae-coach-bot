"""The bot's real DB functions (state.*) against a real Postgres - the
mocked tests in bot/tests/ never execute their SQL. Pins today's behavior
so each Phase 1 user-id migration step can prove it changed nothing a
Telegram user would notice.
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
os.environ.setdefault("TELEGRAM_TOKEN", "dummy:token")

import psycopg2  # noqa: E402

from _pg import init_db, scratch_db  # noqa: E402

import state  # noqa: E402
from state import session  # noqa: E402

ALICE, BOB = 5001, 5002


def one(dsn, sql, params=()):
    with psycopg2.connect(dsn) as conn, conn.cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchall()


with scratch_db() as dsn:
    init_db(dsn)

    # First contact: get() creates the users row and logs user_seen once.
    alice = state.get(ALICE)
    assert alice["lang"] == "" and alice["usage_count"] == 0 and alice["name"] == ""
    assert one(dsn, "SELECT count(*) FROM users WHERE telegram_id = %s", (ALICE,)) == [(1,)]
    session._users.clear()
    state.get(ALICE)  # a second process start must not log user_seen again
    assert one(dsn, "SELECT count(*) FROM events WHERE telegram_id = %s AND event_type = 'user_seen'", (ALICE,)) == [(1,)]
    print("PASS: get() creates the user once and logs user_seen exactly once")

    # Session + account fields persist across a restart (cache cleared).
    alice = state.get(ALICE)
    alice.update(lang="uz", name="Aziza", phase="waiting_name")
    state._save(ALICE, alice)
    session._users.clear()
    alice = state.get(ALICE)
    assert (alice["lang"], alice["name"], alice["phase"]) == ("uz", "Aziza", "waiting_name"), alice
    assert one(dsn, "SELECT language, name FROM users WHERE telegram_id = %s", (ALICE,)) == [("uz", "Aziza")]
    print("PASS: language, name and session phase survive a restart")

    # checks_used is owned by the webapp: _save must never write it back.
    one_sql = "UPDATE users SET checks_used = 3 WHERE telegram_id = %s RETURNING 1"
    one(dsn, one_sql, (ALICE,))
    alice["usage_count"] = 0  # stale cached copy
    state._save(ALICE, alice)
    assert one(dsn, "SELECT checks_used FROM users WHERE telegram_id = %s", (ALICE,)) == [(3,)]
    print("PASS: _save() never overwrites checks_used with a stale cached value")

    # reset() clears the flow but keeps who the user is.
    state.reset(ALICE)
    alice = state.get(ALICE)
    assert (alice["lang"], alice["name"], alice["phase"]) == ("uz", "Aziza", "idle"), alice
    print("PASS: reset() clears the flow, keeps language and name")

    # Waitlist: first join returns True and stamps waitlist_at; second is a no-op.
    assert state.join_waitlist(ALICE, "aziza_tg") is True
    assert state.join_waitlist(ALICE, "aziza_tg") is False
    assert one(dsn, "SELECT joined_waitlist, waitlist_at IS NOT NULL, username FROM users WHERE telegram_id = %s", (ALICE,)) == [(True, True, "aziza_tg")]
    print("PASS: join_waitlist() joins once and records the username")

    # Quota override and marketing source, read back through the same API.
    state.get(BOB)
    assert state.get_quota_override(BOB) is None
    assert state.set_quota_override(BOB, 12, source="school21_pilot") is True
    assert state.get_quota_override(BOB) == 12 and state.get_source(BOB) == "school21_pilot"
    state.set_source(BOB, "instagram")
    assert state.get_source(BOB) == "instagram"
    assert state.get_quota_override(ALICE) is None, "one user's override must not touch another's"
    print("PASS: quota override and source are per-user")

    # Events and orders keyed to the right user; a pending order is reused.
    state.log_event(BOB, "started", metadata={"x": 1})
    first = state.get_or_create_order(BOB, 9_900_000, "10_checks")
    again = state.get_or_create_order(BOB, 8_000_000, "10_checks")  # price changed since
    other = state.get_or_create_order(BOB, 1_000_000, "1_checks")
    assert first == again, "a pending order for the same package should be reused, not duplicated"
    assert other != first, "a different package gets its own order"
    assert one(dsn, "SELECT telegram_id, package, amount FROM orders ORDER BY id") == [
        (BOB, "10_checks", 8_000_000), (BOB, "1_checks", 1_000_000)]
    assert one(dsn, "SELECT count(*) FROM events WHERE telegram_id = %s AND event_type = 'started'", (BOB,)) == [(1,)]
    print("PASS: events and orders land on the right user; pending order reused per package at the current price")

    # Step 1.3: the bot writes the internal user_id itself, and stats count by it.
    bob_id = one(dsn, "SELECT id FROM users WHERE telegram_id = %s", (BOB,))[0][0]
    assert one(dsn, "SELECT DISTINCT user_id FROM orders") == [(bob_id,)]
    assert one(dsn, "SELECT count(*) FROM events WHERE user_id IS NULL OR user_id <> (SELECT id FROM users u WHERE u.telegram_id = events.telegram_id)") == [(0,)]
    with psycopg2.connect(dsn) as conn, conn.cursor() as cur:
        cur.execute("ALTER TABLE events DISABLE TRIGGER trg_events_fill_user_id")  # prove the bot sets it, not the trigger
        cur.execute("ALTER TABLE orders DISABLE TRIGGER trg_orders_fill_user_id")
    state.log_event(BOB, "check_completed")
    state.get_or_create_order(BOB, 500_000, "5_checks")
    assert one(dsn, "SELECT user_id FROM events WHERE event_type = 'check_completed'") == [(bob_id,)]
    assert one(dsn, "SELECT user_id FROM orders WHERE package = '5_checks'") == [(bob_id,)]
    state.log_event(31337, "orphan_event")  # no users row: still accepted, as before
    assert one(dsn, "SELECT user_id, telegram_id FROM events WHERE event_type = 'orphan_event'") == [(None, 31337)]
    paid = one(dsn, "UPDATE orders SET state = 'paid' RETURNING id")
    assert state.payment_stats()["unique_payers"] == 1 and len(paid) == 3
    assert state.event_stats(["started"]) == {"started": (1, 1)}
    print("PASS: bot writes user_id itself on events/orders; stats count unique users by user_id")

print("\nALL BOT DB FUNCTION CHECKS PASSED")
