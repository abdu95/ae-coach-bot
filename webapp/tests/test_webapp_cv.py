import hashlib
import hmac
import io
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

# --- Test 1: cv-status with no CV -> has_cv False, ensure_user called ---
with mock.patch.object(db, "ensure_user") as m_ensure, \
     mock.patch.object(db, "get_cv_text", return_value=None) as m_get, \
     mock.patch.object(db, "get_user_language", return_value="en"):
    resp = client.post("/api/cv-status", json={"init_data": init_data})
    assert resp.status_code == 200, resp.text
    assert resp.json() == {"has_cv": False, "lang": "en"}
    m_ensure.assert_called_once_with(777, "testuser", "Test")
    m_get.assert_called_once_with(777)
print("PASS: cv-status (no CV) ensures user and returns has_cv=False")

# --- Test 2: cv-status with a CV on file -> has_cv True ---
with mock.patch.object(db, "ensure_user"), \
     mock.patch.object(db, "get_cv_text", return_value="Some CV text"), \
     mock.patch.object(db, "get_user_language", return_value="ru"):
    resp = client.post("/api/cv-status", json={"init_data": init_data})
    assert resp.json() == {"has_cv": True, "lang": "ru"}
print("PASS: cv-status (has CV) returns has_cv=True and the user's language")

# --- Test 3: cv-status with tampered signature -> 401 ---
tampered = init_data.replace("Test", "Evil")
resp = client.post("/api/cv-status", json={"init_data": tampered})
assert resp.status_code == 401, resp.text
print("PASS: cv-status rejects tampered signature")

# --- Test 4: upload-cv with a fake PDF -> parses, saves, returns saved:true ---
import cv_parser  # noqa: E402
with mock.patch.object(db, "ensure_user") as m_ensure, \
     mock.patch.object(db, "save_cv_text") as m_save, \
     mock.patch.object(cv_parser, "parse_cv", return_value="Extracted CV text here") as m_parse:
    resp = client.post(
        "/api/upload-cv",
        data={"init_data": init_data},
        files={"file": ("resume.pdf", io.BytesIO(b"%PDF-fake"), "application/pdf")},
    )
    assert resp.status_code == 200, resp.text
    assert resp.json() == {"saved": True}
    m_ensure.assert_called_once_with(777, "testuser", "Test")
    m_parse.assert_called_once()
    m_save.assert_called_once_with(777, "Extracted CV text here")
print("PASS: upload-cv parses and saves correctly")

# --- Test 5: upload-cv rejects non-PDF/DOCX file types ---
with mock.patch.object(db, "ensure_user"):
    resp = client.post(
        "/api/upload-cv",
        data={"init_data": init_data},
        files={"file": ("resume.txt", io.BytesIO(b"hello"), "text/plain")},
    )
    assert resp.status_code == 400, resp.text
    assert "PDF and DOCX" in resp.json()["detail"]
print("PASS: upload-cv rejects unsupported file types")

# --- Test 6: upload-cv with a file that extracts to empty text -> 400 ---
with mock.patch.object(db, "ensure_user"), \
     mock.patch.object(cv_parser, "parse_cv", return_value="   "):
    resp = client.post(
        "/api/upload-cv",
        data={"init_data": init_data},
        files={"file": ("resume.pdf", io.BytesIO(b"%PDF-fake"), "application/pdf")},
    )
    assert resp.status_code == 400, resp.text
    assert "any text" in resp.json()["detail"].lower()
print("PASS: upload-cv rejects empty-text extraction")

# --- Test 7: suggest-titles with a CV on file -> returns titles ---
import hypothesis  # noqa: E402
with mock.patch.object(db, "ensure_user"), \
     mock.patch.object(db, "get_cv_text", return_value="Some CV text"), \
     mock.patch.object(hypothesis, "suggest_job_titles", new=mock.AsyncMock(
         return_value=["Data Analyst", "BI Developer", "Analytics Engineer", "Data Engineer", "Data Scientist"])):
    resp = client.post("/api/suggest-titles", json={"init_data": init_data})
    assert resp.status_code == 200, resp.text
    assert len(resp.json()["titles"]) == 5
print("PASS: suggest-titles returns 5 titles when a CV is on file")

# --- Test 8: suggest-titles with no CV on file -> 400 ---
with mock.patch.object(db, "ensure_user"), \
     mock.patch.object(db, "get_cv_text", return_value=None):
    resp = client.post("/api/suggest-titles", json={"init_data": init_data})
    assert resp.status_code == 400, resp.text
print("PASS: suggest-titles requires a CV on file")

# --- Test 9: search passes seen_companies through to vacancy_source ---
import vacancy_source  # noqa: E402
with mock.patch.object(vacancy_source, "search_vacancies", new=mock.AsyncMock(return_value=[])) as m_search:
    resp = client.post("/api/search", json={
        "init_data": init_data, "job_title": "Data Analyst", "location": "Remote",
        "seen_companies": ["Acme", "Globex"],
    })
    assert resp.status_code == 200, resp.text
    m_search.assert_called_once_with("Data Analyst", "Remote", "Any", "Any", seen_companies=["Acme", "Globex"])
print("PASS: search request threads seen_companies through to vacancy_source")

TEST_VACANCY = {
    "title": "Data Analyst", "company": "Acme", "location": "Remote",
    "url": "https://example.com/job", "summary": "A great analyst role.",
}

# --- Test 10: score-vacancy uses on-file CV, returns score dict ---
import scoring  # noqa: E402
with mock.patch.object(db, "ensure_user"), \
     mock.patch.object(db, "get_cv_text", return_value="Some CV text"), \
     mock.patch.object(scoring, "score_vacancy", new=mock.AsyncMock(
         return_value={"score": 75, "matched": ["SQL"], "missing": ["Tableau"], "verdict": "Decent fit"})) as m_score:
    resp = client.post("/api/score-vacancy", json={"init_data": init_data, "vacancy": TEST_VACANCY})
    assert resp.status_code == 200, resp.text
    assert resp.json()["score"] == 75
    m_score.assert_called_once_with("Some CV text", TEST_VACANCY)
print("PASS: score-vacancy scores against on-file CV")

# --- Test 11: score-vacancy with no CV on file -> 400 ---
with mock.patch.object(db, "ensure_user"), mock.patch.object(db, "get_cv_text", return_value=None):
    resp = client.post("/api/score-vacancy", json={"init_data": init_data, "vacancy": TEST_VACANCY})
    assert resp.status_code == 400, resp.text
print("PASS: score-vacancy requires a CV on file")

# --- Test 12: cv-recommendations passes level through correctly ---
import cv_fixes  # noqa: E402
fake_fixes = [{"issue": "x", "before": "y", "after": "z"}] * 5
with mock.patch.object(db, "ensure_user"), \
     mock.patch.object(db, "get_cv_text", return_value="Some CV text"), \
     mock.patch.object(cv_fixes, "generate_cv_fixes", new=mock.AsyncMock(return_value=fake_fixes)) as m_fixes:
    resp = client.post("/api/cv-recommendations", json={
        "init_data": init_data, "vacancy": TEST_VACANCY, "level": "Senior",
    })
    assert resp.status_code == 200, resp.text
    assert len(resp.json()["fixes"]) == 5
    m_fixes.assert_called_once_with("Senior", TEST_VACANCY, "Some CV text")
print("PASS: cv-recommendations passes level/vacancy/cv through correctly")

# --- Test 13: apply saves with score, reads cv_text fresh from db (not trusting client) ---
with mock.patch.object(db, "ensure_user") as m_ensure, \
     mock.patch.object(db, "get_cv_text", return_value="The current CV on file"), \
     mock.patch.object(db, "save_application") as m_save:
    resp = client.post("/api/apply", json={
        "init_data": init_data, "vacancy": TEST_VACANCY,
        "score": {"score": 90, "matched": ["SQL"], "missing": []},
    })
    assert resp.status_code == 200, resp.text
    assert resp.json() == {"saved": True}
    m_ensure.assert_called_once_with(777, "testuser", "Test")
    m_save.assert_called_once_with(777, TEST_VACANCY, "The current CV on file", {"score": 90, "matched": ["SQL"], "missing": []})
print("PASS: apply saves the application using the current on-file CV, not client-supplied text")

# --- Test 14: apply without a score (direct-apply path) ---
with mock.patch.object(db, "ensure_user"), \
     mock.patch.object(db, "get_cv_text", return_value="cv"), \
     mock.patch.object(db, "save_application") as m_save:
    resp = client.post("/api/apply", json={"init_data": init_data, "vacancy": TEST_VACANCY, "score": None})
    assert resp.status_code == 200, resp.text
    m_save.assert_called_once_with(777, TEST_VACANCY, "cv", None)
print("PASS: apply works with score=None (direct-apply path)")

# --- Test 15: applications list returns the current user's rows ---
fake_rows = [{
    "id": 1, "title": "Data Analyst", "company": "Acme", "location": "Remote",
    "url": "https://example.com", "match_score": 80, "status": "applied",
    "created_at": "2026-09-05T12:00:00+00:00",
}]
with mock.patch.object(db, "ensure_user") as m_ensure, \
     mock.patch.object(db, "list_applications", return_value=fake_rows) as m_list:
    resp = client.post("/api/applications", json={"init_data": init_data})
    assert resp.status_code == 200, resp.text
    assert resp.json() == {"applications": fake_rows}
    m_ensure.assert_called_once_with(777, "testuser", "Test")
    m_list.assert_called_once_with(777)
print("PASS: applications list returns the current user's tracked rows")

# --- Test 16: applications list rejects tampered signature (same as every other endpoint) ---
resp = client.post("/api/applications", json={"init_data": tampered})
assert resp.status_code == 401, resp.text
print("PASS: applications list rejects tampered signature")

print("\nALL CV-UPLOAD FLOW CHECKS PASSED")
