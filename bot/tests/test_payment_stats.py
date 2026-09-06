import os
import sys
import unittest.mock as mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ["TELEGRAM_TOKEN"] = "dummy:token"

import state  # noqa: E402


def make_fake_pool(row):
    fake_cursor = mock.MagicMock()
    fake_cursor.fetchone = mock.Mock(return_value=row)
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


# 3 paid orders, 2 unique payers, 3_000_000 tiyin = 30,000 UZS total
pool, cursor = make_fake_pool((3, 2, 3_000_000))
with mock.patch.object(state, "_pool", pool):
    result = state.payment_stats()
    assert result == {"count": 3, "unique_payers": 2, "total_uzs": 30_000}, result
    query_text = cursor.execute.call_args.args[0]
    assert "orders" in query_text and "state = 'paid'" in query_text, query_text
print("PASS: payment_stats reads paid orders and converts tiyin to UZS correctly")

print("\nALL PAYMENT STATS CHECKS PASSED")
