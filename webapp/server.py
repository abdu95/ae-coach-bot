import hashlib
import hmac
import logging
import os
from pathlib import Path
from urllib.parse import parse_qsl

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

load_dotenv()

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


class SearchRequest(BaseModel):
    init_data: str
    job_title: str
    location: str = "Any"
    work_setup: str = "Any"
    industry: str = "Any"


@app.post("/api/search")
async def search(req: SearchRequest):
    verify_init_data(req.init_data)  # confirms the request really came from Telegram

    try:
        vacancies = await vacancy_source.search_vacancies(
            req.job_title, req.location, req.work_setup, req.industry
        )
    except Exception:
        logger.exception("Vacancy search failed")
        raise HTTPException(502, "Search failed, try again")

    return {"vacancies": vacancies}


app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@app.get("/")
async def index():
    return FileResponse(STATIC_DIR / "index.html")
