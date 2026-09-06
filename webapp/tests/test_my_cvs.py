import hashlib
import hmac
import sys
import time
import unittest.mock as mock
from urllib.parse import urlencode

sys.path.insert(0, str(__import__("pathlib").Path(__file__).resolve().parent.parent))

import os
os.environ["TELEGRAM_TOKEN"] = "dummy:token"
os.environ["ANTHROPIC_API_KEY"] = "dummy"
os.environ["DATABASE_URL"] = "postgresql://fake"

import server  # noqa: E402
import db  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

TOKEN = "dummy:token"


def build_init_data(user_json: str, token: str) -> str:
    fields = {"user": user_json, "auth_date": str(int(time.time())), "query_id": "AAtest"}
    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(fields.items()))
    secret_key = hmac.new(b"WebAppData", token.encode(), hashlib.sha256).digest()
    fields["hash"] = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()
    return urlencode(fields)


client = TestClient(server.app)
init_data = build_init_data('{"id":777,"first_name":"Test","username":"testuser"}', TOKEN)

FAKE_CVS = [
    {"id": 2, "label": "resume_v2.pdf", "is_active": True, "extracted_position": "Data Analyst", "created_at": "2026-09-07T00:00:00"},
    {"id": 1, "label": "resume_v1.pdf", "is_active": False, "extracted_position": None, "created_at": "2026-09-01T00:00:00"},
]

# --- Test 1: list CVs returns the user's saved CVs ---
with mock.patch.object(db, "ensure_user"), \
     mock.patch.object(db, "list_cvs", return_value=FAKE_CVS) as m_list:
    resp = client.post("/api/cvs", json={"init_data": init_data})
    assert resp.status_code == 200, resp.text
    assert resp.json() == {"cvs": FAKE_CVS}
    m_list.assert_called_once_with(777)
print("PASS: /api/cvs lists the caller's saved CVs")

# --- Test 2: set-active succeeds for an owned CV ---
with mock.patch.object(db, "ensure_user"), \
     mock.patch.object(db, "set_active_cv", return_value=True) as m_set:
    resp = client.post("/api/cvs/set-active", json={"init_data": init_data, "cv_id": 1})
    assert resp.status_code == 200, resp.text
    assert resp.json() == {"updated": True}
    m_set.assert_called_once_with(777, 1)
print("PASS: set-active switches the active CV for a CV the caller owns")

# --- Test 3: set-active on a not-owned/nonexistent CV -> 404, no leak ---
with mock.patch.object(db, "ensure_user"), \
     mock.patch.object(db, "set_active_cv", return_value=False):
    resp = client.post("/api/cvs/set-active", json={"init_data": init_data, "cv_id": 999})
    assert resp.status_code == 404, resp.text
print("PASS: set-active on a not-owned/nonexistent CV returns 404")

# --- Test 4: delete succeeds for an owned CV ---
with mock.patch.object(db, "ensure_user"), \
     mock.patch.object(db, "delete_cv", return_value=True) as m_del:
    resp = client.post("/api/cvs/delete", json={"init_data": init_data, "cv_id": 1})
    assert resp.status_code == 200, resp.text
    assert resp.json() == {"deleted": True}
    m_del.assert_called_once_with(777, 1)
print("PASS: delete removes a CV the caller owns")

# --- Test 5: delete on a not-owned/nonexistent CV -> 404 ---
with mock.patch.object(db, "ensure_user"), \
     mock.patch.object(db, "delete_cv", return_value=False):
    resp = client.post("/api/cvs/delete", json={"init_data": init_data, "cv_id": 999})
    assert resp.status_code == 404, resp.text
print("PASS: delete on a not-owned/nonexistent CV returns 404")

print("\nALL MY CVS ENDPOINT CHECKS PASSED")
