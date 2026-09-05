import os
import sys
import unittest.mock as mock

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent.parent))
os.environ["TELEGRAM_TOKEN"] = "dummy:token"
os.environ["ANTHROPIC_API_KEY"] = "dummy"

import state  # noqa: E402

_fake_users = {}
state.get = lambda uid: _fake_users.setdefault(uid, state._empty())
state.log_event = lambda *a, **k: None
state.persisting = lambda f: f

import asyncio  # noqa: E402
import bot  # noqa: E402
import i18n  # noqa: E402


class FakeBot:
    username = "acceptedai_bot"


class FakeMessage:
    def __init__(self, name="msg"):
        self.name = name
        self.sent = []

    async def reply_text(self, text, parse_mode=None, reply_markup=None):
        self.sent.append({"text": text, "markup": reply_markup})
        return FakeMessage(f"{self.name}->reply")

    def get_bot(self):
        return FakeBot()


def buttons_of(markup):
    if markup is None:
        return []
    return [b.callback_data for row in markup.inline_keyboard for b in row]


async def run_callback(uid, action, message):
    fake_query = mock.Mock()
    fake_query.data = action
    fake_query.message = message
    fake_query.answer = mock.AsyncMock()
    fake_query.edit_message_reply_markup = mock.AsyncMock()
    cb_update = mock.Mock()
    cb_update.callback_query = fake_query
    cb_update.effective_user.id = uid
    await bot.handle_callback(cb_update, mock.Mock())


async def main():
    uid = 4242
    created_orders = []

    def fake_get_or_create_order(telegram_id, amount, package):
        created_orders.append((telegram_id, amount, package))
        return 555

    with mock.patch.object(state, "get_or_create_order", side_effect=fake_get_or_create_order), \
         mock.patch.object(state, "get_quota_override", return_value=None):

        # 1. Hitting the limit shows a quantity picker, not a single fixed-package button.
        msg = FakeMessage("limit")
        await bot.send_limit_reached(msg, uid, "en")
        sent = msg.sent[-1]
        assert "10,000 UZS" in sent["text"], sent["text"]
        actions = buttons_of(sent["markup"])
        assert actions == ["buy_1", "buy_5", "buy_10", "buy_20", "buy_50", "buy_custom", "join_waitlist"], actions
        print("PASS: limit-reached shows a per-check quantity picker with presets + custom + waitlist")

        # 2. Picking a preset (10 checks) creates an order priced at 10 * PRICE_PER_CHECK and
        #    shows a real Payme checkout link with the correct amount encoded.
        msg2 = FakeMessage("buy10")
        await run_callback(uid, "buy_10", msg2)
        assert created_orders[-1] == (uid, 10 * bot.PRICE_PER_CHECK_TIYIN, "10_checks"), created_orders
        pay_sent = msg2.sent[-1]
        assert "100,000 UZS" in pay_sent["text"], pay_sent["text"]
        pay_button = pay_sent["markup"].inline_keyboard[0][0]
        assert pay_button.url is not None and "checkout.paycom.uz" in pay_button.url, pay_button.url
        print("PASS: picking a preset (10 checks) builds a correctly-priced checkout link")

        # 3. Custom amount: asks for a number, rejects out-of-range/non-numeric input,
        #    accepts a valid one and clears the awaiting flag.
        msg3 = FakeMessage("custom")
        await run_callback(uid, "buy_custom", msg3)
        user = state.get(uid)
        assert user["awaiting_custom_checks"] is True
        assert "1" in msg3.sent[-1]["text"] and "100" in msg3.sent[-1]["text"]
        print("PASS: 'custom amount' prompts for a number and sets the awaiting flag")

        for bad in ("0", "101", "abc", "-5"):
            fake_update = mock.Mock()
            fake_update.effective_user.id = uid
            bad_msg = FakeMessage(f"bad_{bad}")
            fake_update.message = bad_msg
            fake_update.message.text = bad
            await bot.handle_text(fake_update, mock.Mock())
            assert user["awaiting_custom_checks"] is True, f"flag cleared on bad input {bad!r}"
            assert created_orders[-1] == (uid, 10 * bot.PRICE_PER_CHECK_TIYIN, "10_checks"), \
                f"an order was created for invalid input {bad!r}"
        print("PASS: out-of-range/non-numeric custom amounts are rejected, no order created")

        fake_update = mock.Mock()
        fake_update.effective_user.id = uid
        good_msg = FakeMessage("good_7")
        fake_update.message = good_msg
        fake_update.message.text = "7"
        await bot.handle_text(fake_update, mock.Mock())
        assert user["awaiting_custom_checks"] is False
        assert created_orders[-1] == (uid, 7 * bot.PRICE_PER_CHECK_TIYIN, "7_checks"), created_orders
        assert "70,000 UZS" in good_msg.sent[-1]["text"], good_msg.sent[-1]["text"]
        print("PASS: a valid custom amount (7) builds a correctly-priced checkout link and clears the flag")

    # 4. i18n price math sanity: 1 check singular vs plural, ru pluralization.
    assert i18n._checks_label(1, "en") == "1 check"
    assert i18n._checks_label(5, "en") == "5 checks"
    assert i18n._checks_label(1, "ru") == "1 проверка"
    assert i18n._checks_label(3, "ru") == "3 проверки"
    assert i18n._checks_label(11, "ru") == "11 проверок"
    assert i18n._checks_label(21, "ru") == "21 проверка"
    print("PASS: check-count labels pluralize correctly in en/ru")

    print("\nALL PAYMENT FLOW CHECKS PASSED")


if __name__ == "__main__":
    asyncio.run(main())
