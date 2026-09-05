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
state.log_event = lambda *a, **k: None
state.persisting = lambda f: f
state.get_quota_override = lambda uid: None

import bot  # noqa: E402


class FakeMessage:
    def __init__(self, name):
        self.name = name
        self.sent = []
        self.document = mock.Mock(file_name="cv.pdf", file_id="abc")

    async def reply_text(self, text, parse_mode=None, reply_markup=None):
        self.sent.append({"text": text, "markup": reply_markup})
        return FakeMessage(f"{self.name}->loading")

    async def edit_text(self, text):
        self.sent.append({"edited": text})

    async def delete(self):
        pass


async def main():
    uid = 42
    user = state.get(uid)
    user["phase"] = "idle"  # normal /start -> upload CV path, not the /jobs path
    user["usage_count"] = 0

    msg = FakeMessage("cv_upload")
    update = mock.Mock()
    update.effective_user.id = uid
    update.message = msg

    fake_file = mock.Mock()
    fake_file.download_as_bytearray = mock.AsyncMock(return_value=b"%PDF-fake-bytes")
    context = mock.Mock()
    context.bot.get_file = mock.AsyncMock(return_value=fake_file)

    fake_page = mock.Mock()
    fake_page.extract_text.return_value = "John Doe - Data Analyst - SQL, Python"
    fake_reader = mock.Mock()
    fake_reader.pages = [fake_page]

    with mock.patch.object(bot, "PdfReader", return_value=fake_reader):
        await bot.handle_document(update, context)

    assert user["phase"] == "waiting_jd", f"expected waiting_jd, got {user['phase']}"
    assert user["cv_text"] == "John Doe - Data Analyst - SQL, Python", user["cv_text"]
    assert "cv_received" not in str(msg.sent)  # sanity - real key text, not the literal i18n key
    print("Sent messages:", [m.get("text") for m in msg.sent])
    print("PASS: normal (non-/jobs) CV upload still sets phase=waiting_jd and stores cv_text")


asyncio.run(main())
