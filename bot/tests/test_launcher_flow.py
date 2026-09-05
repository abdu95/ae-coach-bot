import asyncio
import os
import sys
import unittest.mock as mock

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent.parent))
os.environ["TELEGRAM_TOKEN"] = "dummy:token"
os.environ["ANTHROPIC_API_KEY"] = "dummy"
os.environ["MINI_APP_URL"] = "https://example.test/app"

import state  # noqa: E402

_fake_users = {}
state.get = lambda uid: _fake_users.setdefault(uid, state._empty())


def _fake_reset(uid):
    current = _fake_users.get(uid, state._empty())
    fresh = state._empty()
    for key in ("lang", "usage_count", "waitlisted", "name"):
        fresh[key] = current.get(key, fresh[key])
    _fake_users[uid] = fresh
    return fresh


state.reset = _fake_reset
state.log_event = lambda *a, **k: None
state.persisting = lambda f: f
state.set_source = mock.Mock()

import bot  # noqa: E402


class FakeMessage:
    def __init__(self):
        self.sent = []

    async def reply_text(self, text, parse_mode=None, reply_markup=None):
        self.sent.append({"text": text, "markup": reply_markup})


def buttons_of(markup):
    if markup is None:
        return []
    return [(b.text, getattr(b, "web_app", None)) for row in markup.inline_keyboard for b in row]


async def main():
    uid = 4242
    update = mock.Mock()
    update.effective_user.id = uid
    update.effective_user.language_code = "en"
    context = mock.Mock()
    context.args = []

    # 1. /start with no language yet -> language picker, no launcher sent
    _fake_users[uid] = state._empty()
    update.message = FakeMessage()
    await bot.start(update, context)
    assert "language" in update.message.sent[-1]["text"].lower() or "til" in update.message.sent[-1]["text"].lower() \
        or "язык" in update.message.sent[-1]["text"].lower()
    print("PASS: /start with no language shows the language picker")

    # 2. /start with language but no name -> asks for name
    _fake_users[uid]["lang"] = "en"
    update.message = FakeMessage()
    await bot.start(update, context)
    assert _fake_users[uid]["phase"] == "waiting_name"
    print("PASS: /start with a language but no name asks for a name")

    # 3. /start with language+name -> sends the launcher (explainer + app button)
    _fake_users[uid]["name"] = "Test"
    update.message = FakeMessage()
    await bot.start(update, context)
    sent = update.message.sent[-1]
    labels = buttons_of(sent["markup"])
    assert len(labels) == 1 and labels[0][1] is not None and labels[0][1].url == "https://example.test/app"
    print("PASS: /start with language+name sends the launcher with a working Mini App button")

    # 4. Launcher gracefully degrades when MINI_APP_URL isn't configured
    with mock.patch.object(bot, "MINI_APP_URL", ""):
        update.message = FakeMessage()
        await bot.send_launcher(update.message, _fake_users[uid])
        assert update.message.sent[-1]["markup"] is None
    print("PASS: launcher shows a plain message (no button) when MINI_APP_URL is unset")

    # 5. Language callback with no name yet -> asks for name, not the launcher
    _fake_users[uid] = state._empty()
    fake_query = mock.Mock()
    fake_query.data = "lang_uz"
    fake_query.message = FakeMessage()
    fake_query.answer = mock.AsyncMock()
    fake_query.edit_message_reply_markup = mock.AsyncMock()
    cb_update = mock.Mock()
    cb_update.callback_query = fake_query
    cb_update.effective_user.id = uid
    await bot.handle_callback(cb_update, context)
    assert _fake_users[uid]["lang"] == "uz"
    assert _fake_users[uid]["phase"] == "waiting_name"
    print("PASS: picking a language with no name yet asks for a name")

    # 6. Language callback with a name already set -> sends the launcher directly
    _fake_users[uid]["name"] = "Test"
    fake_query2 = mock.Mock()
    fake_query2.data = "lang_ru"
    fake_query2.message = FakeMessage()
    fake_query2.answer = mock.AsyncMock()
    fake_query2.edit_message_reply_markup = mock.AsyncMock()
    cb_update2 = mock.Mock()
    cb_update2.callback_query = fake_query2
    cb_update2.effective_user.id = uid
    await bot.handle_callback(cb_update2, context)
    assert buttons_of(fake_query2.message.sent[-1]["markup"])
    print("PASS: picking a language with a name already set sends the launcher directly")

    # 7. Text while waiting_name -> stores name, greets, then sends the launcher
    _fake_users[uid] = state._empty()
    _fake_users[uid]["lang"] = "en"
    _fake_users[uid]["phase"] = "waiting_name"
    text_update = mock.Mock()
    text_update.effective_user.id = uid
    text_update.message = FakeMessage()
    text_update.message.text = "Alice"
    await bot.handle_text(text_update, context)
    assert _fake_users[uid]["name"] == "Alice"
    assert _fake_users[uid]["phase"] == "idle"
    assert len(text_update.message.sent) == 2
    assert buttons_of(text_update.message.sent[-1]["markup"])
    print("PASS: providing a name stores it and sends the launcher")

    # 8. Any stray text once idle just redirects to the launcher (no chat flow left)
    text_update2 = mock.Mock()
    text_update2.effective_user.id = uid
    text_update2.message = FakeMessage()
    text_update2.message.text = "hello is anyone there"
    await bot.handle_text(text_update2, context)
    assert buttons_of(text_update2.message.sent[-1]["markup"])
    print("PASS: stray text messages redirect to the launcher, no dead chat flow")

    # 9. /app ensures a users row exists (via state.get) and sends the launcher
    get_calls = []
    original_get = state.get
    state.get = lambda uid_: get_calls.append(uid_) or original_get(uid_)
    app_update = mock.Mock()
    app_update.effective_user.id = uid
    app_update.message = FakeMessage()
    await bot.app_cmd(app_update, context)
    assert get_calls == [uid]
    assert buttons_of(app_update.message.sent[-1]["markup"])
    state.get = original_get
    print("PASS: /app ensures a users row exists and sends the launcher")

    # 10. /reset clears session and sends the launcher afterward
    reset_update = mock.Mock()
    reset_update.effective_user.id = uid
    reset_update.message = FakeMessage()
    await bot.reset_cmd(reset_update, context)
    assert len(reset_update.message.sent) == 2
    assert buttons_of(reset_update.message.sent[-1]["markup"])
    print("PASS: /reset confirms and re-sends the launcher")

    print("\nALL LAUNCHER FLOW CHECKS PASSED")


asyncio.run(main())
