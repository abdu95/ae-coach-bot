"""
Shared scaffolding for bot/tests/*.py's script-style tests (see
README.md) - not a test itself, just the bits every test file was
copy-pasting: a FakeMessage stub for Telegram's Update.message, the
state.* monkey-patching every bot.py-driving test needs so handlers run
against an in-memory dict instead of a real Postgres connection, and a
fake connection-pool builder for tests that exercise state.py's
DB-touching functions directly.
"""

import unittest.mock as mock


class FakeMessage:
    def __init__(self):
        self.sent = []

    async def reply_text(self, text, parse_mode=None, reply_markup=None):
        self.sent.append({"text": text, "markup": reply_markup})

    async def reply_photo(self, photo, caption=None, parse_mode=None, reply_markup=None):
        # Normalized into the same {"text", "markup"} shape as reply_text
        # (caption -> "text") so existing assertions against .sent work
        # unchanged regardless of which one a handler actually calls -
        # send_launcher uses this for the onboarding-screenshot message.
        self.sent.append({"text": caption, "markup": reply_markup})


def patch_state_for_bot_tests(state_module, fake_users: dict) -> None:
    """Monkey-patches state.get/reset/log_event/persisting/set_source so
    bot.py's handlers can run against `fake_users` instead of a real
    Postgres connection. Call after setting required env vars but
    before `import bot`."""
    state_module.get = lambda uid: fake_users.setdefault(uid, state_module._empty())

    def _reset(uid):
        current = fake_users.get(uid, state_module._empty())
        fresh = state_module._empty()
        for key in ("lang", "usage_count", "waitlisted", "name"):
            fresh[key] = current.get(key, fresh[key])
        fake_users[uid] = fresh
        return fresh

    state_module.reset = _reset
    state_module.log_event = lambda *a, **k: None
    state_module.persisting = lambda f: f
    state_module.set_source = mock.Mock()


def make_fake_pool(fetchone_result=None):
    fake_cursor = mock.MagicMock()
    if fetchone_result is not None:
        fake_cursor.fetchone = mock.Mock(return_value=fetchone_result)
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
