import asyncio
import os
import sys
import unittest.mock as mock

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent.parent))
os.environ["TELEGRAM_TOKEN"] = "dummy:token"
os.environ["ANTHROPIC_API_KEY"] = "dummy"

import state  # noqa: E402

_fake_users = {}
state.get = lambda uid: _fake_users.setdefault(uid, state._empty())
state.reset = lambda uid: _fake_users.__setitem__(uid, state._empty())
state.log_event = lambda *a, **k: None
state.persisting = lambda f: f
state.set_source = mock.Mock()

import bot  # noqa: E402


class FakeMessage:
    def __init__(self):
        self.sent = []

    async def reply_text(self, text, parse_mode=None, reply_markup=None):
        self.sent.append(text)


async def main():
    uid = 555
    user = _fake_users.setdefault(uid, state._empty())
    user["lang"] = "en"
    user["name"] = "Test"

    update = mock.Mock()
    update.effective_user.id = uid
    update.effective_user.language_code = "en"
    update.message = FakeMessage()
    context = mock.Mock()
    context.args = ["chashma"]

    await bot.start(update, context)
    state.set_source.assert_called_once_with(uid, "chashma_marathon")
    print("PASS: /start chashma tags the user with chashma_marathon source")

    # unknown arg shouldn't call set_source at all
    state.set_source.reset_mock()
    context.args = ["some_random_unrelated_arg"]
    await bot.start(update, context)
    state.set_source.assert_not_called()
    print("PASS: unrelated /start args do not tag any marketing source")

    # PILOT_CODE still takes its own branch, not marketing source
    context.args = [bot.PILOT_CODE]
    with mock.patch.object(bot, "enroll_pilot", new=mock.AsyncMock()) as m_pilot:
        await bot.start(update, context)
        m_pilot.assert_called_once()
        state.set_source.assert_not_called()
    print("PASS: PILOT_CODE still goes through enroll_pilot, not marketing-source tagging")


asyncio.run(main())
