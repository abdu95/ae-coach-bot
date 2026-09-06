"""
Regression test for a real incident (2026-09-06): a user's checks_used
got silently rolled back because state.py's per-process in-memory cache
went stale relative to a webapp-side increment, and _save() (called
after every bot handler via the persisting() decorator) unconditionally
wrote that stale cached value back over the DB's correct one.

Root cause: usage_count/checks_used is now incremented by TWO
processes (bot.py historically, webapp/db.py since the Stage 3
migration) but bot.py's cache was never designed to defer to an
out-of-process writer for that field the way it already does for
quota_override (see state.get_quota_override's docstring). Fix:
_save() no longer writes checks_used at all - bot.py hasn't
incremented it since Stage 3, so there's nothing for the bot to
legitimately persist there; only the webapp increments it now.
"""
import os
import sys
import unittest.mock as mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ["TELEGRAM_TOKEN"] = "dummy:token"

import state  # noqa: E402


def make_fake_pool():
    fake_cursor = mock.MagicMock()
    fake_cursor.__enter__ = mock.Mock(return_value=fake_cursor)
    fake_cursor.__exit__ = mock.Mock(return_value=False)

    fake_conn = mock.MagicMock()
    fake_conn.cursor = mock.Mock(return_value=fake_cursor)
    fake_conn.__enter__ = mock.Mock(return_value=fake_conn)
    fake_conn.__exit__ = mock.Mock(return_value=False)

    fake_pool = mock.MagicMock()
    fake_pool.getconn = mock.Mock(return_value=fake_conn)
    fake_pool.putconn = mock.Mock()
    return fake_pool, fake_cursor


pool, cursor = make_fake_pool()
with mock.patch.object(state, "_pool", pool):
    # Simulate exactly the incident: the bot's in-memory copy is stale
    # (usage_count=1) while the real DB value (mutated by the webapp,
    # out-of-process) is already 2. _save() must never touch checks_used
    # at all, regardless of what stale value the cached dict is holding.
    stale_cached_data = state._empty()
    stale_cached_data["lang"] = "ru"
    stale_cached_data["name"] = "Anatoliy"
    stale_cached_data["usage_count"] = 1  # stale - real DB value is 2

    state._save(5843532358, stale_cached_data)

    users_update_calls = [
        call for call in cursor.execute.call_args_list
        if "UPDATE users" in call.args[0]
    ]
    assert len(users_update_calls) == 1, users_update_calls
    query_text, params = users_update_calls[0].args
    assert "checks_used" not in query_text, \
        "checks_used must never be written by the bot's cache - it's webapp-owned since Stage 3"
    assert 1 not in params, \
        f"the stale cached usage_count (1) must not appear in the UPDATE params at all: {params}"

print("PASS: _save() never writes checks_used, even when the in-memory cache holds a stale value")
print("\nALL CHECKS_USED CLOBBER-PREVENTION CHECKS PASSED")
