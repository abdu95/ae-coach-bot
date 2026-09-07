import os
import sys
import unittest.mock as mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
sys.path.insert(0, str(Path(__file__).resolve().parent))
os.environ["TELEGRAM_TOKEN"] = "dummy:token"

import state  # noqa: E402
from _helpers import make_fake_pool  # noqa: E402

# 3 paid orders, 2 unique payers, 3_000_000 tiyin = 30,000 UZS total
pool, cursor = make_fake_pool((3, 2, 3_000_000))
with mock.patch.object(state, "_pool", pool):
    result = state.payment_stats()
    assert result == {"count": 3, "unique_payers": 2, "total_uzs": 30_000}, result
    query_text = cursor.execute.call_args.args[0]
    assert "orders" in query_text and "state = 'paid'" in query_text, query_text
print("PASS: payment_stats reads paid orders and converts tiyin to UZS correctly")

print("\nALL PAYMENT STATS CHECKS PASSED")
