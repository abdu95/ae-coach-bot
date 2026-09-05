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
os.environ["PAYME_ID"] = "test_merchant_id"
os.environ["PRICE_PER_CHECK_TIYIN"] = "1000000"
os.environ["BOT_USERNAME"] = "acceptedai_bot"

import server  # noqa: E402
import db  # noqa: E402
import cv_analysis  # noqa: E402
import jd_fetch  # noqa: E402
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

FAKE_ANALYSIS = {
    "ats": {"score": 72, "matched": ["SQL"], "missing": ["dbt"], "verdict": "Decent match."},
    "xyz": {"passing": [], "failing": ["Did stuff"], "rewrites": []},
    "tools": {"SQL": "strong", "dbt": "not_found"},
    "level": {"assessment": "Mid", "reasoning": "Owns projects end to end."},
}

# --- Test 1: no CV on file -> 400, no Claude call ---
with mock.patch.object(db, "ensure_user"), \
     mock.patch.object(db, "get_cv_text", return_value=None), \
     mock.patch.object(cv_analysis, "analyze_cv") as m_analyze:
    resp = client.post("/api/cv-jd-analysis", json={"init_data": init_data, "jd": "x" * 150})
    assert resp.status_code == 400, resp.text
    m_analyze.assert_not_called()
print("PASS: cv-jd-analysis without a CV on file returns 400, no API call made")

# --- Test 2: JD too short -> 400, no Claude call ---
with mock.patch.object(db, "ensure_user"), \
     mock.patch.object(db, "get_cv_text", return_value="Some CV text"), \
     mock.patch.object(cv_analysis, "analyze_cv") as m_analyze:
    resp = client.post("/api/cv-jd-analysis", json={"init_data": init_data, "jd": "too short"})
    assert resp.status_code == 400, resp.text
    m_analyze.assert_not_called()
print("PASS: cv-jd-analysis rejects a JD under 100 chars, no API call made")

# --- Test 3: quota exhausted -> limit_reached, no Claude call, no increment, logs limit_reached ---
with mock.patch.object(db, "ensure_user"), \
     mock.patch.object(db, "get_cv_text", return_value="Some CV text"), \
     mock.patch.object(db, "get_quota_status", return_value=(2, 2)), \
     mock.patch.object(cv_analysis, "analyze_cv") as m_analyze, \
     mock.patch.object(db, "increment_usage_count") as m_incr, \
     mock.patch.object(db, "log_event") as m_log:
    resp = client.post("/api/cv-jd-analysis", json={"init_data": init_data, "jd": "x" * 150})
    assert resp.status_code == 200, resp.text
    assert resp.json() == {"limit_reached": True, "remaining": 0, "quota": 2}
    m_analyze.assert_not_called()
    m_incr.assert_not_called()
    m_log.assert_called_once_with(777, "limit_reached")
print("PASS: cv-jd-analysis at quota returns limit_reached, logs the event, no Claude call")

# --- Test 4: successful analysis increments usage exactly once, logs check_completed, returns outputs ---
with mock.patch.object(db, "ensure_user"), \
     mock.patch.object(db, "get_cv_text", return_value="Some CV text"), \
     mock.patch.object(db, "get_quota_status", side_effect=[(0, 2), (1, 2)]), \
     mock.patch.object(cv_analysis, "analyze_cv", new=mock.AsyncMock(return_value=FAKE_ANALYSIS)), \
     mock.patch.object(db, "increment_usage_count") as m_incr, \
     mock.patch.object(db, "log_event") as m_log:
    resp = client.post("/api/cv-jd-analysis", json={"init_data": init_data, "jd": "x" * 150})
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["limit_reached"] is False
    assert body["remaining"] == 1 and body["quota"] == 2
    assert body["ats"]["score"] == 72
    assert body["level"]["assessment"] == "Mid"
    m_incr.assert_called_once_with(777)
    m_log.assert_called_once_with(777, "check_completed")
print("PASS: a successful analysis increments usage once, logs check_completed (same name bot.py's /stats already reads), and returns the full outputs + quota")

# --- Test 5: analysis failure doesn't increment usage ---
with mock.patch.object(db, "ensure_user"), \
     mock.patch.object(db, "get_cv_text", return_value="Some CV text"), \
     mock.patch.object(db, "get_quota_status", return_value=(0, 2)), \
     mock.patch.object(cv_analysis, "analyze_cv", new=mock.AsyncMock(side_effect=ValueError("bad json"))), \
     mock.patch.object(db, "increment_usage_count") as m_incr:
    resp = client.post("/api/cv-jd-analysis", json={"init_data": init_data, "jd": "x" * 150})
    assert resp.status_code == 502, resp.text
    m_incr.assert_not_called()
print("PASS: a failed analysis does not consume quota")

# --- Test 6: roadmap item 1 for Junior routes to generate_cv_fixes, logs roadmap_requested once ---
with mock.patch.object(db, "ensure_user"), \
     mock.patch.object(db, "get_cv_text", return_value="Some CV text"), \
     mock.patch.object(cv_analysis, "generate_cv_fixes", new=mock.AsyncMock(
         return_value=[{"issue": "x", "before": "", "after": "y"}])) as m_fixes, \
     mock.patch.object(cv_analysis, "generate_roadmap_item") as m_roadmap, \
     mock.patch.object(db, "log_event") as m_log:
    resp = client.post("/api/roadmap-item", json={
        "init_data": init_data, "jd": "x" * 150, "level": "Junior", "item": 1,
    })
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["title"] == "CV Fixes"
    assert body["fixes"][0]["after"] == "y"
    assert body["is_last"] is False
    m_fixes.assert_called_once()
    m_roadmap.assert_not_called()
    m_log.assert_called_once_with(777, "roadmap_requested")
print("PASS: roadmap item 1 (Junior/Mid/Senior) routes to generate_cv_fixes and logs roadmap_requested")

# --- Test 7: roadmap item 4 for Junior is the last item and returns raw text ---
with mock.patch.object(db, "ensure_user"), \
     mock.patch.object(db, "get_cv_text", return_value="Some CV text"), \
     mock.patch.object(cv_analysis, "generate_roadmap_item", new=mock.AsyncMock(
         return_value="### Target Companies\n...")) as m_roadmap:
    resp = client.post("/api/roadmap-item", json={
        "init_data": init_data, "jd": "x" * 150, "level": "Junior", "item": 4,
    })
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["title"] == "Target Companies"
    assert "Target Companies" in body["text"]
    assert body["is_last"] is True
    m_roadmap.assert_called_once()
print("PASS: roadmap item 4 (Junior) is flagged as the last item and returns raw text")

# --- Test 8: Pre-Junior roadmap has only 3 items, item 3 is last, item 1 is not CV Fixes ---
with mock.patch.object(db, "ensure_user"), \
     mock.patch.object(db, "get_cv_text", return_value="Some CV text"), \
     mock.patch.object(cv_analysis, "generate_roadmap_item", new=mock.AsyncMock(
         return_value="### Stepping-Stone Roles\n...")):
    resp = client.post("/api/roadmap-item", json={
        "init_data": init_data, "jd": "x" * 150, "level": "Pre-Junior", "item": 3,
    })
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["title"] == "Stepping-Stone Roles"
    assert body["is_last"] is True
print("PASS: Pre-Junior's 3-item roadmap ends at item 3, with different content than Junior")

# --- Test 9: quota-status reports remaining/quota/price ---
with mock.patch.object(db, "ensure_user"), \
     mock.patch.object(db, "get_quota_status", return_value=(1, 3)):
    resp = client.post("/api/quota-status", json={"init_data": init_data})
    assert resp.status_code == 200, resp.text
    assert resp.json() == {"remaining": 2, "quota": 3, "price_per_check_tiyin": 1_000_000}
print("PASS: quota-status reports remaining/quota/price correctly")

# --- Test 10: checkout builds a correctly-priced order and a real Payme URL ---
with mock.patch.object(db, "ensure_user"), \
     mock.patch.object(db, "get_or_create_order", return_value=555) as m_order:
    resp = client.post("/api/checkout", json={"init_data": init_data, "checks": 10})
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["amount"] == 10_000_000
    assert body["checks"] == 10
    assert "checkout.paycom.uz" in body["checkout_url"]
    m_order.assert_called_once_with(777, 10_000_000, "10_checks")
print("PASS: checkout creates a correctly-priced order and a real Payme checkout URL")

# --- Test 11: checkout rejects out-of-range quantities ---
with mock.patch.object(db, "ensure_user"):
    for bad in (0, 101, -5):
        resp = client.post("/api/checkout", json={"init_data": init_data, "checks": bad})
        assert resp.status_code == 400, (bad, resp.text)
print("PASS: checkout rejects quantities outside 1-100")

# --- Test 12: jd_fetch.looks_like_url basic sanity ---
assert jd_fetch.looks_like_url("https://boards.greenhouse.io/acme/jobs/123") is True
assert jd_fetch.looks_like_url("http://example.com") is True
assert jd_fetch.looks_like_url("We are looking for a Data Analyst...") is False
assert jd_fetch.looks_like_url("check out https://example.com for details") is False
print("PASS: looks_like_url correctly distinguishes a bare URL from JD text")

# --- Test 13: a pasted URL is fetched and the extracted text is analyzed, not the URL itself ---
with mock.patch.object(db, "ensure_user"), \
     mock.patch.object(db, "get_cv_text", return_value="Some CV text"), \
     mock.patch.object(db, "get_quota_status", side_effect=[(0, 2), (1, 2)]), \
     mock.patch.object(jd_fetch, "fetch_jd_text", new=mock.AsyncMock(
         return_value="Extracted job posting text " * 10)) as m_fetch, \
     mock.patch.object(cv_analysis, "analyze_cv", new=mock.AsyncMock(return_value=FAKE_ANALYSIS)) as m_analyze, \
     mock.patch.object(db, "increment_usage_count"), \
     mock.patch.object(db, "log_event"):
    resp = client.post("/api/cv-jd-analysis", json={
        "init_data": init_data, "jd": "https://boards.greenhouse.io/acme/jobs/123",
    })
    assert resp.status_code == 200, resp.text
    body = resp.json()
    m_fetch.assert_called_once_with("https://boards.greenhouse.io/acme/jobs/123")
    analyzed_jd = m_analyze.call_args[0][0]
    assert analyzed_jd.startswith("Extracted job posting text"), analyzed_jd
    assert body["jd_text"] == analyzed_jd
print("PASS: a pasted URL is fetched and the extracted page text (not the URL) is analyzed")

# --- Test 14: a URL that fails to fetch returns a friendly 400, no Claude call ---
with mock.patch.object(db, "ensure_user"), \
     mock.patch.object(db, "get_cv_text", return_value="Some CV text"), \
     mock.patch.object(jd_fetch, "fetch_jd_text", new=mock.AsyncMock(side_effect=Exception("connection refused"))), \
     mock.patch.object(cv_analysis, "analyze_cv") as m_analyze:
    resp = client.post("/api/cv-jd-analysis", json={
        "init_data": init_data, "jd": "https://example.com/dead-link",
    })
    assert resp.status_code == 400, resp.text
    assert "link" in resp.json()["detail"].lower()
    m_analyze.assert_not_called()
print("PASS: a link that fails to fetch returns a friendly error, no Claude call made")

print("\nALL CV-ANALYSIS FLOW CHECKS PASSED")
