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

import cv_fixes  # local to this folder
import cv_parser  # local to this folder
import db  # local to this folder
import hypothesis  # local to this folder
import scoring  # local to this folder
import vacancy_source  # local to this folder - see its docstring

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
STATIC_DIR = Path(__file__).resolve().parent / "static"

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
