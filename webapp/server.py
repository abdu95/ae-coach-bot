import base64
import hashlib
import hmac
import json
import logging
import os
from pathlib import Path
from urllib.parse import parse_qsl

from dotenv import load_dotenv
from fastapi import FastAPI, File, Form, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

load_dotenv()

import cv_analysis  # local to this folder
import cv_fixes  # local to this folder
import cv_parser  # local to this folder
import db  # local to this folder
import hypothesis  # local to this folder
import jd_fetch  # local to this folder
import scoring  # local to this folder
import vacancy_source  # local to this folder - see its docstring

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
STATIC_DIR = Path(__file__).resolve().parent / "static"

# Payment - must match ae-coach-bot's values exactly (same Payme merchant,
# same per-check price, same `orders` table payme-webhook reads from).
PAYME_ID = os.getenv("PAYME_ID", "")
PRICE_PER_CHECK_TIYIN = int(os.getenv("PRICE_PER_CHECK_TIYIN", "1000000"))
BOT_USERNAME = os.getenv("BOT_USERNAME", "")
MIN_CHECKS_PURCHASE = 1
MAX_CHECKS_PURCHASE = 100

app = FastAPI()


def verify_init_data(init_data: str) -> dict:
    """Validate Telegram Mini App initData per Telegram's documented scheme
    (https://core.telegram.org/bots/webapps#validating-data-received-via-the-mini-app)
    and return the parsed fields. Raises HTTPException if invalid."""
    if not TELEGRAM_TOKEN:
        raise HTTPException(500, "TELEGRAM_TOKEN not configured")

    parsed = dict(parse_qsl(init_data, strict_parsing=True))
    received_hash = parsed.pop("hash", None)
    if not received_hash:
        raise HTTPException(401, "Missing hash in initData")

    data_check_string = "\n".join(f"{k}={v}" for k, v in sorted(parsed.items()))
    secret_key = hmac.new(b"WebAppData", TELEGRAM_TOKEN.encode(), hashlib.sha256).digest()
    computed_hash = hmac.new(secret_key, data_check_string.encode(), hashlib.sha256).hexdigest()

    if not hmac.compare_digest(computed_hash, received_hash):
        raise HTTPException(401, "Invalid initData signature")

    return parsed


def authenticate(init_data: str) -> dict:
    """Validates initData and ensures a `users` row exists for this
    telegram_id (needed before any write to `applications`, which has a
    foreign key to `users`). Returns the Telegram user dict (id,
    first_name, username)."""
    parsed = verify_init_data(init_data)
    try:
        user = json.loads(parsed.get("user", "{}"))
    except json.JSONDecodeError:
        raise HTTPException(400, "Malformed user data in initData")
    telegram_id = user.get("id")
    if not telegram_id:
        raise HTTPException(400, "Missing user id in initData")
    db.ensure_user(telegram_id, user.get("username"), user.get("first_name"))
    return user


class SearchRequest(BaseModel):
    init_data: str
    job_title: str
    location: str = "Any"
    work_setup: str = "Any"
    industry: str = "Any"
    seen_companies: list[str] = []


@app.post("/api/search")
async def search(req: SearchRequest):
    verify_init_data(req.init_data)  # confirms the request really came from Telegram

    try:
        vacancies = await vacancy_source.search_vacancies(
            req.job_title, req.location, req.work_setup, req.industry,
            seen_companies=req.seen_companies or None,
        )
    except Exception:
        logger.exception("Vacancy search failed")
        raise HTTPException(502, "Search failed, try again")

    return {"vacancies": vacancies}


class CVStatusRequest(BaseModel):
    init_data: str


@app.post("/api/cv-status")
async def cv_status(req: CVStatusRequest):
    user = authenticate(req.init_data)
    cv_text = db.get_cv_text(user["id"])
    lang = db.get_user_language(user["id"])
    return {"has_cv": bool(cv_text), "lang": lang}


@app.post("/api/upload-cv")
async def upload_cv(init_data: str = Form(...), file: UploadFile = File(...)):
    user = authenticate(init_data)

    if not file.filename.lower().endswith((".pdf", ".docx")):
        raise HTTPException(400, "Only PDF and DOCX files are accepted")

    file_bytes = await file.read()
    try:
        cv_text = cv_parser.parse_cv(file.filename, file_bytes)
    except Exception:
        logger.exception("CV parsing failed")
        raise HTTPException(400, "Could not read that file - try a different PDF/DOCX")

    if not cv_text.strip():
        raise HTTPException(400, "Could not find any text in that file")

    db.save_cv_text(user["id"], cv_text)
    db.log_event(user["id"], "cv_uploaded")
    return {"saved": True}


class SuggestTitlesRequest(BaseModel):
    init_data: str


@app.post("/api/suggest-titles")
async def suggest_titles(req: SuggestTitlesRequest):
    user = authenticate(req.init_data)
    cv_text = db.get_cv_text(user["id"])
    if not cv_text:
        raise HTTPException(400, "No CV on file - upload one first")

    try:
        titles = await hypothesis.suggest_job_titles(cv_text)
    except Exception:
        logger.exception("Title suggestion failed")
        raise HTTPException(502, "Couldn't generate suggestions, try again")

    return {"titles": titles}


class Vacancy(BaseModel):
    title: str
    company: str
    location: str = ""
    url: str = ""
    summary: str = ""


class ScoreRequest(BaseModel):
    init_data: str
    vacancy: Vacancy


@app.post("/api/score-vacancy")
async def score_vacancy_endpoint(req: ScoreRequest):
    user = authenticate(req.init_data)
    cv_text = db.get_cv_text(user["id"])
    if not cv_text:
        raise HTTPException(400, "No CV on file - upload one first")

    try:
        score = await scoring.score_vacancy(cv_text, req.vacancy.model_dump())
    except Exception:
        logger.exception("Scoring failed")
        raise HTTPException(502, "Couldn't score your CV, try again")

    return score


class RecommendationsRequest(BaseModel):
    init_data: str
    vacancy: Vacancy
    level: str


@app.post("/api/cv-recommendations")
async def cv_recommendations(req: RecommendationsRequest):
    user = authenticate(req.init_data)
    cv_text = db.get_cv_text(user["id"])
    if not cv_text:
        raise HTTPException(400, "No CV on file - upload one first")

    try:
        fixes = await cv_fixes.generate_cv_fixes(req.level, req.vacancy.model_dump(), cv_text)
    except Exception:
        logger.exception("CV fix generation failed")
        raise HTTPException(502, "Couldn't generate recommendations, try again")

    return {"fixes": fixes}


class ApplyRequest(BaseModel):
    init_data: str
    vacancy: Vacancy
    score: dict | None = None


@app.post("/api/apply")
async def apply(req: ApplyRequest):
    user = authenticate(req.init_data)
    cv_text = db.get_cv_text(user["id"]) or ""

    try:
        db.save_application(user["id"], req.vacancy.model_dump(), cv_text, req.score)
    except Exception:
        logger.exception("Saving application failed")
        raise HTTPException(500, "Couldn't save your application, try again")

    return {"saved": True}


class ApplicationsRequest(BaseModel):
    init_data: str


@app.post("/api/applications")
async def list_applications(req: ApplicationsRequest):
    user = authenticate(req.init_data)
    try:
        applications = db.list_applications(user["id"])
    except Exception:
        logger.exception("Listing applications failed")
        raise HTTPException(500, "Couldn't load your applications, try again")
    return {"applications": applications}


class UpdateApplicationStatusRequest(BaseModel):
    init_data: str
    application_id: int
    status: str


@app.post("/api/applications/update-status")
async def update_application_status(req: UpdateApplicationStatusRequest):
    user = authenticate(req.init_data)
    if req.status not in db.VALID_STATUSES:
        raise HTTPException(400, "Invalid status")
    found = db.update_application_status(user["id"], req.application_id, req.status)
    if not found:
        raise HTTPException(404, "Application not found")
    return {"updated": True}


class DeleteApplicationRequest(BaseModel):
    init_data: str
    application_id: int


@app.post("/api/applications/delete")
async def delete_application(req: DeleteApplicationRequest):
    user = authenticate(req.init_data)
    found = db.delete_application(user["id"], req.application_id)
    if not found:
        raise HTTPException(404, "Application not found")
    return {"deleted": True}


class AnalyzeRequest(BaseModel):
    init_data: str
    jd: str


@app.post("/api/cv-jd-analysis")
async def cv_jd_analysis(req: AnalyzeRequest):
    user = authenticate(req.init_data)
    cv_text = db.get_cv_text(user["id"])
    if not cv_text:
        raise HTTPException(400, "No CV on file - upload one first")

    jd_input = req.jd.strip()
    if jd_fetch.looks_like_url(jd_input):
        try:
            jd_text = await jd_fetch.fetch_jd_text(jd_input)
        except Exception:
            logger.exception("Fetching JD from URL failed")
            raise HTTPException(400, "Couldn't read that link - try pasting the job description text instead")
    else:
        jd_text = jd_input

    if len(jd_text) < 100:
        raise HTTPException(400, "Job description looks too short")

    usage_count, quota = db.get_quota_status(user["id"])
    if usage_count >= quota:
        db.log_event(user["id"], "limit_reached")
        return {"limit_reached": True, "remaining": 0, "quota": quota}

    try:
        outputs = await cv_analysis.analyze_cv(jd_text, cv_text)
    except Exception:
        logger.exception("CV/JD analysis failed")
        raise HTTPException(502, "Analysis failed, try again")

    db.increment_usage_count(user["id"])
    db.log_event(user["id"], "check_completed")
    usage_count, quota = db.get_quota_status(user["id"])
    remaining = max(0, quota - usage_count)
    return {"limit_reached": False, "remaining": remaining, "quota": quota, "jd_text": jd_text, **outputs}


class RoadmapItemRequest(BaseModel):
    init_data: str
    jd: str
    level: str
    item: int


@app.post("/api/roadmap-item")
async def roadmap_item(req: RoadmapItemRequest):
    user = authenticate(req.init_data)
    cv_text = db.get_cv_text(user["id"])
    if not cv_text:
        raise HTTPException(400, "No CV on file - upload one first")

    title = cv_analysis.roadmap_block_title(req.level, req.item)
    max_item = cv_analysis.roadmap_max_item(req.level)
    if req.item == 1:
        db.log_event(user["id"], "roadmap_requested")

    try:
        if title == "CV Fixes":
            fixes = await cv_analysis.generate_cv_fixes(req.level, req.jd, cv_text)
            return {"title": title, "fixes": fixes, "is_last": req.item >= max_item}
        text = await cv_analysis.generate_roadmap_item(req.level, req.item, req.jd, cv_text)
        return {"title": title, "text": text, "is_last": req.item >= max_item}
    except Exception:
        logger.exception("Roadmap item generation failed")
        raise HTTPException(502, "Couldn't generate this section, try again")


class QuotaStatusRequest(BaseModel):
    init_data: str


@app.post("/api/quota-status")
async def quota_status(req: QuotaStatusRequest):
    user = authenticate(req.init_data)
    usage_count, quota = db.get_quota_status(user["id"])
    return {
        "remaining": max(0, quota - usage_count),
        "quota": quota,
        "price_per_check_tiyin": PRICE_PER_CHECK_TIYIN,
    }


class CheckoutRequest(BaseModel):
    init_data: str
    checks: int


@app.post("/api/checkout")
async def checkout(req: CheckoutRequest):
    user = authenticate(req.init_data)
    if not (MIN_CHECKS_PURCHASE <= req.checks <= MAX_CHECKS_PURCHASE):
        raise HTTPException(400, f"Choose between {MIN_CHECKS_PURCHASE} and {MAX_CHECKS_PURCHASE} checks")
    if not PAYME_ID:
        raise HTTPException(500, "Payment is not configured")

    amount = req.checks * PRICE_PER_CHECK_TIYIN
    order_id = db.get_or_create_order(user["id"], amount, f"{req.checks}_checks")
    raw = f"m={PAYME_ID};ac.order_id={order_id};a={amount};c=https://t.me/{BOT_USERNAME}"
    checkout_url = "https://checkout.paycom.uz/" + base64.b64encode(raw.encode()).decode()
    return {"checkout_url": checkout_url, "amount": amount, "checks": req.checks}


@app.get("/api/health")
async def health():
    try:
        return db.check_connection()
    except Exception:
        logger.exception("DB health check failed")
        raise HTTPException(500, "DB connection failed")


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
async def index():
    return FileResponse(STATIC_DIR / "index.html")
