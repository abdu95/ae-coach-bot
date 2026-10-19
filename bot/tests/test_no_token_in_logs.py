import io
import logging
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ["TELEGRAM_TOKEN"] = "123456:SECRET_TOKEN_VALUE"

import bot  # noqa: E402,F401 - importing it applies the logging config
import httpx  # noqa: E402

# python-telegram-bot polls /bot<TOKEN>/getUpdates through httpx, which logs
# every request URL at INFO - that once put the real token in Railway's
# logs every ~10 seconds.
captured = io.StringIO()
logging.getLogger().addHandler(logging.StreamHandler(captured))
with httpx.Client(transport=httpx.MockTransport(lambda request: httpx.Response(200, json={"ok": True}))) as client:
    client.post(f"https://api.telegram.org/bot{os.environ['TELEGRAM_TOKEN']}/getUpdates")
assert "SECRET_TOKEN_VALUE" not in captured.getvalue(), captured.getvalue()
print("PASS: polling Telegram doesn't write the bot token to the logs")

print("\nALL TOKEN-LOGGING CHECKS PASSED")
