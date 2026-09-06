import os
import sys
import time
import unittest.mock as mock
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
os.environ.setdefault("DATABASE_URL", "postgresql://fake")

import db  # noqa: E402


def make_fake_pool(rows):
    fake_cursor = mock.MagicMock()
    fake_cursor.fetchall = mock.Mock(return_value=rows)
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


# Reset module-level cache state so this test doesn't depend on run order.
db._companies_cache = None
db._companies_cache_at = 0.0

pool, cursor = make_fake_pool([("stripe", "Stripe"), ("airbnb", "Airbnb")])
with mock.patch.object(db, "get_pool", return_value=pool):
    result = db.get_active_companies()
    assert result == {"stripe": "Stripe", "airbnb": "Airbnb"}, result
    assert cursor.execute.call_count == 1
    print("PASS: get_active_companies queries the DB and returns {slug: display_name}")

    result2 = db.get_active_companies()
    assert result2 == result
    assert cursor.execute.call_count == 1, "a call within the TTL must be served from cache"
    print("PASS: a second call within the cache TTL does not re-query Postgres")

    db._companies_cache_at = time.monotonic() - db._COMPANIES_CACHE_TTL - 1
    result3 = db.get_active_companies()
    assert cursor.execute.call_count == 2, "a call after the TTL expires must re-query"
    print("PASS: a call after the TTL expires re-queries Postgres")

print("\nALL COMPANY CACHE CHECKS PASSED")
